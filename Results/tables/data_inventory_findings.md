# Data Inventory Findings

Generated from:

```text
Codes/scripts/data_inventory_xlsx.ps1
```

The PowerShell inventory was used because Python/conda is not currently available in this terminal.

## Output Files

```text
Results/tables/data_inventory_sheets.csv
Results/tables/data_inventory_columns.csv
Results/tables/data_inventory_errors.csv
```

`data_inventory_errors.csv` is empty after the successful run.

## Main Observations

### Abat Oliba Building Data

File:

```text
Data/Abat Oliba Building/Abat_Oliba/Abat_Oliba_Data.xlsx
```

Relevant sheets:

- `DH Internal Temperatures`: timestamped district-heating internal temperature signals.
- `Ground floor`: timestamp, outdoor temperature, return temperature, supply temperature.
- `First floor`: timestamp, outdoor temperature, return temperature, supply temperature.
- `DHW temperatures`: timestamped domestic hot water temperature signals, including return temperature.

Initial interpretation:

- `Ground floor` and `First floor` look useful for a first temperature-based baseline because they contain both supply and return temperature.
- These sheets appear to be cooling-loop or climatization-loop oriented based on the sample temperatures around 6 C. They may not be the best target for district-heating fault detection without further domain mapping.
- `DH Internal Temperatures` contains heating-related temperature signals but the supply/return meaning needs manual mapping from the column names.

### DHC Network Heating Data

Files:

```text
Data/DHC network/data/District Heating_updated_16_07_2025_1.xlsx
Data/DHC network/data/District Heating_updated_16_07_2025_2.xlsx
```

Relevant sheets:

- `cons_abat_oliba`
- `cons_hostatgeria_DHW_radiators`
- `cons_hostatgeria_underfloor_hea`
- `cons_nostra_senyora`
- other `cons_*` and `prod_*` sheets

Initial interpretation:

- The `INFO` sheet says the folder contains power, supply temperature, and return temperature for generation plants and buildings.
- The first preview rows in most DHC heating sheets clearly expose timestamp and return temperature.
- `cons_nostra_senyora` also exposes `flow (kg/s)`, which can be useful as a reference for validating the supervisor flow-rate formula.
- Some expected variables may be stored in columns not captured by the first preview row or may require deeper parsing/Excel inspection.

### Supervisor Flow-Rate Formula

Use:

```text
m = Power / (Cp * (Ts - Tr))
```

With:

```text
Cp = 4180 J/(kg C)
```

Important unit check:

- If power is in `kW`, convert to `W`.
- If energy is available instead of power, derive power from energy differences over time before calculating mass flow rate.

## Recommended Primary Next Dataset

For the first baseline:

1. Start with the Abat Oliba building file because it has direct building-level supply and return temperature columns.
2. Use `Ground floor` and `First floor` first for pipeline testing.
3. Then inspect `DH Internal Temperatures` and DHC network sheets to map district-heating-specific variables.

This is not yet the final thesis dataset choice. It is the safest first dataset for building the preprocessing and anomaly-detection pipeline.

## Immediate Follow-Up Questions

- Are `Ground floor` and `First floor` cooling/climatization loops rather than district-heating loops?
- Which sheets correspond exactly to the hotel/Hostatgeria and Abat Oliba district-heating substations?
- Where are the supply temperature and power columns in the new DHC heating files if the preview only shows return temperature?
- Are there fault labels, alarm logs, maintenance events, or supervisor-identified abnormal periods?

