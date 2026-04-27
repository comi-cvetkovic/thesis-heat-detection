param(
    [string]$Root = (Get-Location).Path,
    [string]$OutputDir = "Results\tables",
    [int]$MaxRowsPerSheet = 8
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$outputPath = Join-Path $rootPath $OutputDir
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$inputFiles = @(
    "Data\Abat Oliba Building\Abat_Oliba\Abat_Oliba_Data.xlsx",
    "Data\DHC network\data\District Heating_updated_16_07_2025_1.xlsx",
    "Data\DHC network\data\District Heating_updated_16_07_2025_2.xlsx",
    "Data\DHC network\data\District Cooling_updated_16_07_2025.xlsx",
    "Data\20250915_Modbus.xlsx",
    "Data\old\20240606_Data_Montserrat.xlsx",
    "Data\old\20231025_Data_Montserrat v2.xlsx"
)

$timeKeywords = @("time", "date", "timestamp", "fecha", "hora")
$supplyKeywords = @("supply", "sup", "ts", "impulsion", "impulsio", "ida")
$returnKeywords = @("return", "ret", "tr", "retorn", "retorno", "vuelta")
$flowKeywords = @("flow", "mass", "m3", "kg/s", "kg_s", "caudal", "debit")
$powerKeywords = @("power", "kw", "watt", "energia", "energy", "potencia")

function Get-ZipEntryText {
    param(
        [System.IO.Compression.ZipArchive]$Zip,
        [string]$EntryName
    )

    $entry = $Zip.GetEntry($EntryName)
    if ($null -eq $entry) {
        return $null
    }

    $stream = $entry.Open()
    try {
        $reader = [System.IO.StreamReader]::new($stream)
        try {
            return $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

function Get-ColumnName {
    param([string]$CellReference)

    if ($CellReference -match "^([A-Z]+)") {
        return $Matches[1]
    }
    return ""
}

function Get-ColumnIndex {
    param([string]$ColumnName)

    $index = 0
    foreach ($char in $ColumnName.ToCharArray()) {
        $index = ($index * 26) + ([int][char]$char - [int][char]'A' + 1)
    }
    return $index
}

function Get-KeywordCategories {
    param([string]$Name)

    $normalized = $Name.ToLowerInvariant()
    $categories = New-Object System.Collections.Generic.List[string]
    $matched = New-Object System.Collections.Generic.List[string]

    $groups = @(
        @{ Category = "timestamp_candidate"; Keywords = $timeKeywords },
        @{ Category = "supply_temperature_candidate"; Keywords = $supplyKeywords },
        @{ Category = "return_temperature_candidate"; Keywords = $returnKeywords },
        @{ Category = "flow_candidate"; Keywords = $flowKeywords },
        @{ Category = "power_or_energy_candidate"; Keywords = $powerKeywords }
    )

    foreach ($group in $groups) {
        foreach ($keyword in $group.Keywords) {
            if ($normalized.Contains($keyword)) {
                $categories.Add($group.Category)
                $matched.Add($keyword)
            }
        }
    }

    return @{
        Categories = (($categories | Sort-Object -Unique) -join ";")
        Keywords = (($matched | Sort-Object -Unique) -join ";")
    }
}

function Get-CellValue {
    param(
        [System.Xml.XmlElement]$Cell,
        [string[]]$SharedStrings
    )

    $type = $Cell.GetAttribute("t")
    $valueNode = $Cell.GetElementsByTagName("v") | Select-Object -First 1

    if ($type -eq "inlineStr") {
        $textNodes = $Cell.GetElementsByTagName("t")
        return (($textNodes | ForEach-Object { $_.InnerText }) -join "")
    }

    if ($null -eq $valueNode) {
        return ""
    }

    $raw = $valueNode.InnerText
    if ($type -eq "s") {
        $index = 0
        if ([int]::TryParse($raw, [ref]$index) -and $index -lt $SharedStrings.Length) {
            return $SharedStrings[$index]
        }
    }

    return $raw
}

function Get-SharedStrings {
    param([System.IO.Compression.ZipArchive]$Zip)

    $xmlText = Get-ZipEntryText -Zip $Zip -EntryName "xl/sharedStrings.xml"
    if ([string]::IsNullOrWhiteSpace($xmlText)) {
        return @()
    }

    [xml]$xml = $xmlText
    $strings = New-Object System.Collections.Generic.List[string]
    foreach ($si in $xml.GetElementsByTagName("si")) {
        $strings.Add((($si.GetElementsByTagName("t") | ForEach-Object { $_.InnerText }) -join ""))
    }
    return $strings.ToArray()
}

function Get-CellValueRaw {
    param(
        [System.Xml.XmlElement]$Cell
    )

    $type = $Cell.GetAttribute("t")
    $valueNode = $Cell.GetElementsByTagName("v") | Select-Object -First 1

    if ($type -eq "inlineStr") {
        $textNodes = $Cell.GetElementsByTagName("t")
        return @{
            Type = "inlineStr"
            Value = (($textNodes | ForEach-Object { $_.InnerText }) -join "")
        }
    }

    if ($null -eq $valueNode) {
        return @{
            Type = $type
            Value = ""
        }
    }

    return @{
        Type = $type
        Value = $valueNode.InnerText
    }
}

function Resolve-CellValue {
    param(
        [hashtable]$RawValue,
        [hashtable]$SharedStringMap
    )

    if ($RawValue.Type -eq "s") {
        $index = 0
        if ([int]::TryParse($RawValue.Value, [ref]$index) -and $SharedStringMap.ContainsKey($index)) {
            return $SharedStringMap[$index]
        }
    }

    return [string]$RawValue.Value
}

function Get-NeededSharedStrings {
    param(
        [System.IO.Compression.ZipArchive]$Zip,
        [int[]]$NeededIndices
    )

    $needed = @{}
    foreach ($index in $NeededIndices) {
        $needed[$index] = $true
    }

    $result = @{}
    if ($needed.Count -eq 0) {
        return $result
    }

    $entry = $Zip.GetEntry("xl/sharedStrings.xml")
    if ($null -eq $entry) {
        return $result
    }

    $settings = [System.Xml.XmlReaderSettings]::new()
    $settings.IgnoreWhitespace = $true
    $stream = $entry.Open()
    try {
        $reader = [System.Xml.XmlReader]::Create($stream, $settings)
        try {
            $index = -1
            while ($reader.Read()) {
                if ($reader.NodeType -eq [System.Xml.XmlNodeType]::Element -and $reader.LocalName -eq "si") {
                    $index += 1
                    if ($needed.ContainsKey($index)) {
                        $subtree = $reader.ReadSubtree()
                        try {
                            $textParts = New-Object System.Collections.Generic.List[string]
                            while ($subtree.Read()) {
                                if ($subtree.NodeType -eq [System.Xml.XmlNodeType]::Element -and $subtree.LocalName -eq "t") {
                                    $textParts.Add($subtree.ReadElementContentAsString())
                                }
                            }
                            $result[$index] = ($textParts -join "")
                            if ($result.Count -eq $needed.Count) {
                                break
                            }
                        }
                        finally {
                            $subtree.Dispose()
                        }
                    }
                }
            }
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    return $result
}

function Get-SheetPreview {
    param(
        [System.IO.Compression.ZipArchive]$Zip,
        [string]$EntryName,
        [int]$MaxRows
    )

    $entry = $Zip.GetEntry($EntryName)
    if ($null -eq $entry) {
        return @{
            Dimension = ""
            Rows = @()
            MaxColumnIndex = 0
            SharedStringIndices = @()
        }
    }

    $rows = New-Object System.Collections.Generic.List[object]
    $sharedStringIndices = New-Object System.Collections.Generic.List[int]
    $maxColumnIndex = 0
    $dimension = ""

    $settings = [System.Xml.XmlReaderSettings]::new()
    $settings.IgnoreWhitespace = $true
    $stream = $entry.Open()
    try {
        $reader = [System.Xml.XmlReader]::Create($stream, $settings)
        try {
            while ($reader.Read()) {
                if ($reader.NodeType -ne [System.Xml.XmlNodeType]::Element) {
                    continue
                }

                if ($reader.LocalName -eq "dimension") {
                    $dimension = $reader.GetAttribute("ref")
                }

                if ($reader.LocalName -eq "row") {
                    $rowSubtree = $reader.ReadSubtree()
                    try {
                        $valuesByColumn = @{}
                        while ($rowSubtree.Read()) {
                            if ($rowSubtree.NodeType -eq [System.Xml.XmlNodeType]::Element -and $rowSubtree.LocalName -eq "c") {
                                [xml]$cellXml = $rowSubtree.ReadOuterXml()
                                $cell = $cellXml.DocumentElement
                                $columnName = Get-ColumnName -CellReference $cell.GetAttribute("r")
                                $columnIndex = Get-ColumnIndex -ColumnName $columnName
                                if ($columnIndex -gt $maxColumnIndex) {
                                    $maxColumnIndex = $columnIndex
                                }
                                $raw = Get-CellValueRaw -Cell $cell
                                $valuesByColumn[$columnIndex] = $raw
                                if ($raw.Type -eq "s") {
                                    $sharedIndex = 0
                                    if ([int]::TryParse($raw.Value, [ref]$sharedIndex)) {
                                        $sharedStringIndices.Add($sharedIndex)
                                    }
                                }
                            }
                        }

                        $nonEmptyValues = @($valuesByColumn.Values | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.Value) })
                        if ($nonEmptyValues.Count -gt 0) {
                            $rows.Add($valuesByColumn)
                        }
                    }
                    finally {
                        $rowSubtree.Dispose()
                    }

                    if ($rows.Count -ge $MaxRows) {
                        break
                    }
                }
            }
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    return @{
        Dimension = $dimension
        Rows = $rows
        MaxColumnIndex = $maxColumnIndex
        SharedStringIndices = @($sharedStringIndices | Sort-Object -Unique)
    }
}

function Get-WorkbookSheets {
    param([System.IO.Compression.ZipArchive]$Zip)

    [xml]$workbook = Get-ZipEntryText -Zip $Zip -EntryName "xl/workbook.xml"
    [xml]$relationships = Get-ZipEntryText -Zip $Zip -EntryName "xl/_rels/workbook.xml.rels"

    $relMap = @{}
    foreach ($relationship in $relationships.Relationships.Relationship) {
        $target = [string]$relationship.Target
        if (-not $target.StartsWith("xl/")) {
            $target = "xl/$target"
        }
        $relMap[[string]$relationship.Id] = $target
    }

    $sheets = New-Object System.Collections.Generic.List[object]
    foreach ($sheet in $workbook.workbook.sheets.sheet) {
        $rid = $sheet.GetAttribute("id", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
        $sheets.Add([pscustomobject]@{
            Name = [string]$sheet.name
            Path = $relMap[$rid]
        })
    }
    return $sheets
}

$sheetRows = New-Object System.Collections.Generic.List[object]
$columnRows = New-Object System.Collections.Generic.List[object]
$errorRows = New-Object System.Collections.Generic.List[object]

foreach ($relativeFile in $inputFiles) {
    $filePath = Join-Path $rootPath $relativeFile
    if (-not (Test-Path -LiteralPath $filePath)) {
        continue
    }

    $zip = $null
    try {
        $zip = [System.IO.Compression.ZipFile]::OpenRead($filePath)
        $sheets = Get-WorkbookSheets -Zip $zip

        foreach ($sheet in $sheets) {
            $preview = Get-SheetPreview -Zip $zip -EntryName $sheet.Path -MaxRows $MaxRowsPerSheet
            $sharedStringMap = Get-NeededSharedStrings -Zip $zip -NeededIndices $preview.SharedStringIndices
            $maxColumnIndex = 0
            $firstDataRows = New-Object System.Collections.Generic.List[object]
            $headerMap = @{}
            $headerRowNumber = ""

            foreach ($row in $preview.Rows) {
                $valuesByColumn = @{}
                foreach ($columnIndex in $row.Keys) {
                    if ($columnIndex -gt $maxColumnIndex) {
                        $maxColumnIndex = $columnIndex
                    }
                    $valuesByColumn[$columnIndex] = Resolve-CellValue -RawValue $row[$columnIndex] -SharedStringMap $sharedStringMap
                }

                $nonEmptyValues = @($valuesByColumn.Values | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
                if ($nonEmptyValues.Count -gt 0) {
                    $firstDataRows.Add($valuesByColumn)
                }
            }

            if ($firstDataRows.Count -gt 0) {
                $firstRow = $firstDataRows[0]
                $headerRowNumber = "first non-empty row"
                foreach ($key in $firstRow.Keys) {
                    $headerMap[$key] = [string]$firstRow[$key]
                }
            }

            $candidateCategories = New-Object System.Collections.Generic.List[string]
            foreach ($columnIndex in ($headerMap.Keys | Sort-Object {[int]$_})) {
                $header = $headerMap[$columnIndex]
                $keywordResult = Get-KeywordCategories -Name $header
                if (-not [string]::IsNullOrWhiteSpace($keywordResult.Categories)) {
                    foreach ($category in $keywordResult.Categories.Split(";")) {
                        $candidateCategories.Add($category)
                    }
                }

                $samples = New-Object System.Collections.Generic.List[string]
                foreach ($sampleRow in ($firstDataRows | Select-Object -Skip 1 -First 5)) {
                    if ($sampleRow.ContainsKey($columnIndex)) {
                        $samples.Add([string]$sampleRow[$columnIndex])
                    }
                }

                $columnRows.Add([pscustomobject]@{
                    file = $relativeFile
                    sheet = $sheet.Name
                    column_index = $columnIndex
                    column = $header
                    candidate_categories = $keywordResult.Categories
                    matched_keywords = $keywordResult.Keywords
                    sample_values = ($samples -join " | ")
                    header_source = $headerRowNumber
                })
            }

            $sheetRows.Add([pscustomobject]@{
                file = $relativeFile
                sheet = $sheet.Name
                dimension = $preview.Dimension
                preview_rows = $firstDataRows.Count
                preview_columns = $maxColumnIndex
                candidate_categories = (($candidateCategories | Sort-Object -Unique) -join ";")
                column_preview = (($headerMap.Keys | Sort-Object {[int]$_} | Select-Object -First 20 | ForEach-Object { $headerMap[$_] }) -join " | ")
            })
        }
    }
    catch {
        $errorRows.Add([pscustomobject]@{
            file = $relativeFile
            error = $_.Exception.Message
        })
    }
    finally {
        if ($null -ne $zip) {
            $zip.Dispose()
        }
    }
}

$sheetRows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path (Join-Path $outputPath "data_inventory_sheets.csv")
$columnRows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path (Join-Path $outputPath "data_inventory_columns.csv")
$errorRows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path (Join-Path $outputPath "data_inventory_errors.csv")

Write-Host "Wrote $(Join-Path $outputPath 'data_inventory_sheets.csv')"
Write-Host "Wrote $(Join-Path $outputPath 'data_inventory_columns.csv')"
Write-Host "Wrote $(Join-Path $outputPath 'data_inventory_errors.csv')"
