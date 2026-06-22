from __future__ import annotations

import copy
import re
import shutil
import struct
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
THESIS_DIR = ROOT / "Thesis drafts"
DOCX = THESIS_DIR / "Thesis_Draft.docx"
BACKUP = THESIS_DIR / "Thesis_Draft_before_june19_revision.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W_NS, "r": R_NS}

MAX_WIDTH_EMU = int(5.7 * 914400)
MAX_HEIGHT_EMU = int(7.3 * 914400)

FIGURE_FILES = {
    "fig4": ROOT / "Results" / "figures" / "thesis_selected5_clean_reconstruction_error_grid.png",
    "cisneros": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_abat_cisneros_stabilized_log_01.png",
    "dhw": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_hostatgeria_dhw_radiators_stabilized_log_01.png",
    "garriga": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_abat_garriga_stabilized_log_01.png",
    "marcet": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_abat_marcet_stabilized_log_01.png",
    "nostra": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_nostra_senyora_stabilized_log_01.png",
    "oliba": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_abat_oliba_stabilized_log_01.png",
    "underfloor": ROOT / "Results" / "figures" / "inspect_autoencoder_cons_hostatgeria_underfloor_hea_stabilized_log_01.png",
    "feature_type": ROOT / "Results" / "figures" / "thesis_selected7_feature_type_by_sheet.png",
    "feature_space": THESIS_DIR / "thesis-manuscript" / "figures" / "anomaly_feature_space_stabilized_log.png",
    "baseline": ROOT / "Results" / "figures" / "thesis_selected7_baseline_vs_autoencoder.png",
    "low_delta": ROOT / "Results" / "figures" / "thesis_selected7_low_delta_overlap.png",
    "cluster": ROOT / "Results" / "figures" / "thesis_selected7_window_cluster_distribution.png",
    "train_test": ROOT / "Results" / "figures" / "thesis_selected7_train_vs_test_split.png",
    "summary": ROOT / "Results" / "figures" / "thesis_selected7_anomaly_summary.png",
    "profiles": ROOT / "Results" / "figures" / "thesis_selected7_retained_window_profiles.png",
    "overlay_garriga": ROOT / "Results" / "figures" / "reconstruction_overlay_cons_abat_garriga_stabilized_log_top01.png",
    "overlay_underfloor": ROOT / "Results" / "figures" / "reconstruction_overlay_cons_hostatgeria_underfloor_hea_stabilized_log_top01.png",
    "joint_vs_univariate_underfloor": ROOT / "Results" / "figures" / "autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.png",
    "threshold_dist": ROOT / "Results" / "figures" / "threshold_distribution_by_sheet_2026-06-07.png",
    "training_history": ROOT / "Results" / "figures" / "autoencoder_training_history_cons_hostatgeria_underfloor_hea_stabilized_log.png",
}


def register_openxml_namespaces() -> None:
    namespaces = {
        "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
        "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
        "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
        "cx2": "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex",
        "cx3": "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex",
        "cx4": "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex",
        "cx5": "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex",
        "cx6": "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex",
        "cx7": "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex",
        "cx8": "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex",
        "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
        "aink": "http://schemas.microsoft.com/office/drawing/2016/ink",
        "am3d": "http://schemas.microsoft.com/office/drawing/2017/model3d",
        "o": "urn:schemas-microsoft-com:office:office",
        "r": R_NS,
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
        "v": "urn:schemas-microsoft-com:vml",
        "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "w10": "urn:schemas-microsoft-com:office:word",
        "w": W_NS,
        "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
        "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
        "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
        "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
        "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
        "w16du": "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
        "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
        "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
        "w16sdtfl": "http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock",
        "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
        "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
        "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
        "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
        "rel": PKG_REL_NS,
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)


def qn(ns: str, tag: str) -> str:
    uri = {"w": W_NS, "r": R_NS, "rel": PKG_REL_NS}[ns]
    return f"{{{uri}}}{tag}"


def paragraph_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()


def read_docx(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path, "r") as zf:
        return {name: zf.read(name) for name in zf.namelist()}


def write_docx(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


def next_rel_id(rels_root: ET.Element) -> str:
    max_id = 0
    for rel in rels_root.findall(qn("rel", "Relationship")):
        rid = rel.get("Id", "")
        if rid.startswith("rId"):
            try:
                max_id = max(max_id, int(rid[3:]))
            except ValueError:
                pass
    return f"rId{max_id + 1}"


def add_relationship(rels_root: ET.Element, target: str) -> str:
    rid = next_rel_id(rels_root)
    ET.SubElement(
        rels_root,
        qn("rel", "Relationship"),
        {
            "Id": rid,
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
            "Target": target,
        },
    )
    return rid


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        sig = fh.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a PNG: {path}")
        fh.read(4)
        if fh.read(4) != b"IHDR":
            raise ValueError(f"Malformed PNG: {path}")
        return struct.unpack(">II", fh.read(8))


def scaled_emu(path: Path) -> tuple[int, int]:
    w_px, h_px = png_size(path)
    w = w_px * 9525
    h = h_px * 9525
    scale = min(MAX_WIDTH_EMU / w, MAX_HEIGHT_EMU / h, 1.0)
    return int(w * scale), int(h * scale)


def make_run(text: str, italic: bool = False) -> ET.Element:
    r = ET.Element(qn("w", "r"))
    rpr = ET.SubElement(r, qn("w", "rPr"))
    if italic:
        ET.SubElement(rpr, qn("w", "i"))
    t = ET.SubElement(r, qn("w", "t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def make_paragraph(text: str, style: str = "BodyText", italic: bool = False, centered: bool = False) -> ET.Element:
    p = ET.Element(qn("w", "p"))
    ppr = ET.SubElement(p, qn("w", "pPr"))
    ET.SubElement(ppr, qn("w", "pStyle"), {qn("w", "val"): style})
    if centered:
        ET.SubElement(ppr, qn("w", "jc"), {qn("w", "val"): "center"})
    p.append(make_run(text, italic=italic))
    return p


def make_simple_table(headers: list[str], rows: list[list[str]]) -> ET.Element:
    tbl = ET.Element(qn("w", "tbl"))
    tbl_pr = ET.SubElement(tbl, qn("w", "tblPr"))
    ET.SubElement(tbl_pr, qn("w", "tblStyle"), {qn("w", "val"): "TableGrid"})
    ET.SubElement(tbl_pr, qn("w", "tblW"), {qn("w", "w"): "0", qn("w", "type"): "auto"})
    grid = ET.SubElement(tbl, qn("w", "tblGrid"))
    for _ in headers:
        ET.SubElement(grid, qn("w", "gridCol"), {qn("w", "w"): "1600"})

    def make_cell(value: str, bold: bool = False) -> ET.Element:
        tc = ET.Element(qn("w", "tc"))
        tc_pr = ET.SubElement(tc, qn("w", "tcPr"))
        ET.SubElement(tc_pr, qn("w", "tcW"), {qn("w", "w"): "1600", qn("w", "type"): "dxa"})
        p = ET.SubElement(tc, qn("w", "p"))
        ppr = ET.SubElement(p, qn("w", "pPr"))
        ET.SubElement(ppr, qn("w", "pStyle"), {qn("w", "val"): "BodyText"})
        r = ET.SubElement(p, qn("w", "r"))
        if bold:
            rpr = ET.SubElement(r, qn("w", "rPr"))
            ET.SubElement(rpr, qn("w", "b"))
        t = ET.SubElement(r, qn("w", "t"))
        t.text = str(value)
        return tc

    header_row = ET.SubElement(tbl, qn("w", "tr"))
    for header in headers:
        header_row.append(make_cell(header, bold=True))
    for row_values in rows:
        tr = ET.SubElement(tbl, qn("w", "tr"))
        for value in row_values:
            tr.append(make_cell(value))
    return tbl


def make_image_paragraph(rid: str, width_emu: int, height_emu: int, docpr_id: int, name: str) -> ET.Element:
    xml = f"""
    <w:p xmlns:w="{W_NS}" xmlns:r="{R_NS}"
         xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
         xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
      <w:pPr>
        <w:pStyle w:val="BodyText"/>
        <w:jc w:val="center"/>
      </w:pPr>
      <w:r>
        <w:drawing>
          <wp:inline distT="0" distB="0" distL="0" distR="0">
            <wp:extent cx="{width_emu}" cy="{height_emu}"/>
            <wp:effectExtent l="0" t="0" r="0" b="0"/>
            <wp:docPr id="{docpr_id}" name="{name}"/>
            <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
            <a:graphic>
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:nvPicPr><pic:cNvPr id="{docpr_id}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>
                  <pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
                  <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    """
    return ET.fromstring(xml)


def get_body(root: ET.Element) -> ET.Element:
    return root.find(qn("w", "body"))


def paragraph_children(body: ET.Element) -> list[ET.Element]:
    return [c for c in list(body) if c.tag == qn("w", "p")]


def find_para_index(body: ET.Element, text: str) -> int:
    for idx, child in enumerate(list(body)):
        if child.tag == qn("w", "p") and paragraph_text(child) == text:
            return idx
    raise ValueError(f"Paragraph not found: {text}")


def find_all_para_indices(body: ET.Element, text: str) -> list[int]:
    indices: list[int] = []
    for idx, child in enumerate(list(body)):
        if child.tag == qn("w", "p") and paragraph_text(child) == text:
            indices.append(idx)
    return indices


def remove_between(body: ET.Element, start_text: str, end_text: str) -> None:
    start_idx = find_para_index(body, start_text)
    end_idx = find_para_index(body, end_text)
    for child in list(body)[start_idx:end_idx]:
        body.remove(child)


def safe_remove_between(body: ET.Element, start_text: str, end_text: str) -> None:
    try:
        remove_between(body, start_text, end_text)
    except ValueError:
        pass


def safe_remove_from(body: ET.Element, start_text: str) -> None:
    try:
        start_idx = find_para_index(body, start_text)
    except ValueError:
        return
    for child in list(body)[start_idx:]:
        body.remove(child)


def remove_exact_paragraphs(body: ET.Element, texts: list[str]) -> None:
    targets = set(texts)
    for child in list(body):
        if child.tag == qn("w", "p") and paragraph_text(child) in targets:
            body.remove(child)


def remove_paragraphs_containing(body: ET.Element, needles: list[str]) -> None:
    for child in list(body):
        if child.tag != qn("w", "p"):
            continue
        text = paragraph_text(child)
        if any(needle in text for needle in needles):
            body.remove(child)


def set_paragraph_containing(body: ET.Element, needle: str, new: str) -> None:
    for child in list(body):
        if child.tag != qn("w", "p"):
            continue
        text = paragraph_text(child)
        if needle in text:
            texts = child.findall(".//w:t", NS)
            if texts:
                texts[0].text = new
                for t in texts[1:]:
                    t.text = ""
            return
    raise ValueError(f"Paragraph containing text not found: {needle}")


def set_paragraph_text_node(paragraph: ET.Element, new: str) -> None:
    texts = paragraph.findall(".//w:t", NS)
    if texts:
        texts[0].text = new
        for t in texts[1:]:
            t.text = ""


def insert_block(body: ET.Element, before_text: str, elements: list[ET.Element]) -> None:
    insert_idx = find_para_index(body, before_text)
    for elem in elements:
        body.insert(insert_idx, elem)
        insert_idx += 1


def update_styles(styles_root: ET.Element) -> None:
    font_map = {
        "Normal": "Times New Roman",
        "BodyText": "Times New Roman",
        "Heading1": "Arial",
        "Heading2": "Arial",
        "Heading3": "Arial",
        "Caption": "Arial",
        "Title": "Arial",
        "Subtitle": "Arial",
    }
    for style in styles_root.findall("w:style", NS):
        style_id = style.get(qn("w", "styleId"))
        if style_id not in font_map:
            continue
        rpr = style.find("w:rPr", NS)
        if rpr is None:
            rpr = ET.SubElement(style, qn("w", "rPr"))
        fonts = rpr.find("w:rFonts", NS)
        if fonts is None:
            fonts = ET.SubElement(rpr, qn("w", "rFonts"))
        for attr in ("ascii", "hAnsi", "cs"):
            fonts.set(qn("w", attr), font_map[style_id])


def enable_update_fields(settings_root: ET.Element) -> None:
    existing = settings_root.find("w:updateFields", NS)
    if existing is None:
        existing = ET.SubElement(settings_root, qn("w", "updateFields"))
    existing.set(qn("w", "val"), "true")


def disable_update_fields(settings_root: ET.Element) -> None:
    existing = settings_root.find("w:updateFields", NS)
    if existing is not None:
        settings_root.remove(existing)


def clean_mc_ignorable(root: ET.Element) -> None:
    mc_attr = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable"
    if mc_attr in root.attrib:
        root.set(mc_attr, "w14 wp14")


def add_image_block(
    body: ET.Element,
    rels_root: ET.Element,
    files: dict[str, bytes],
    before_text: str,
    intro: str,
    figure_path: Path,
    caption: str,
    source: str,
    interpretation: str,
    docpr_id: int,
) -> int:
    media_name = f"word/media/{figure_path.stem}_june19{figure_path.suffix}"
    files[media_name] = figure_path.read_bytes()
    rid = add_relationship(rels_root, media_name.replace("word/", "", 1))
    width_emu, height_emu = scaled_emu(figure_path)
    elems = [
        make_paragraph(intro, "BodyText"),
        make_image_paragraph(rid, width_emu, height_emu, docpr_id, figure_path.stem),
        make_paragraph(caption, "Caption", centered=True),
        make_paragraph(source, "BodyText", italic=True),
        make_paragraph(interpretation, "BodyText"),
    ]
    insert_block(body, before_text, elems)
    return docpr_id + 1


def set_paragraph_text(body: ET.Element, old: str, new: str) -> None:
    idx = find_para_index(body, old)
    p = list(body)[idx]
    texts = p.findall(".//w:t", NS)
    if texts:
        texts[0].text = new
        for t in texts[1:]:
            t.text = ""


def set_paragraph_after(body: ET.Element, marker_text: str, new: str) -> None:
    idx = find_para_index(body, marker_text)
    p = list(body)[idx + 1]
    texts = p.findall(".//w:t", NS)
    if texts:
        texts[0].text = new
        for t in texts[1:]:
            t.text = ""


def expand_core_sections(body: ET.Element) -> None:
    replacements = {
        "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3].": "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3]. The practical motivation is strong: poor substation behaviour increases return temperature, degrades network efficiency, and can hide control or hydraulic problems long before a maintenance report is written. A usable thesis method therefore has to do more than produce a score. It has to isolate windows that can be discussed in engineering terms and reviewed against the original signals. This low-label setting is also what pushes the project away from classical supervised fault classification and toward unsupervised representation learning and anomaly ranking.",
        "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer.": "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer. In other words, the autoencoder answers the question 'does this daily operating pattern look unlike the historical normal behaviour of this building?', while clustering is used later to organize those detected anomalies into more interpretable groups.",
        "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns [5, 6].": "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns [5, 6]. This is one reason recent district-heating research has increasingly combined physical intuition with data-driven modelling: simple rules remain useful as references, but they are too narrow to represent the full range of possible substation faults or inefficient operating regimes. In a supervised setting, one would ideally train against confirmed labels such as fouling, valve faults, or sensor problems. In the present project those labels are not available in a sufficiently consistent way, so the method has to infer normality from historical behaviour rather than learn a direct mapping from signal pattern to named fault class.",
        "The HEAT paper proposes a hierarchical, encoder-assisted clustering approach for fault detection in district-heating substations [1]. Its central idea is to transform time-series windows into a compact representation and then use clustering to construct local peer groups that can be compared against one another. This is a sensible design in a large network with many similar substations, because the method can exploit similarities and differences between multiple operating units instead of relying only on the history of a single site.": "The HEAT paper proposes a hierarchical, encoder-assisted clustering approach for fault detection in district-heating substations [1]. Its central idea is to transform time-series windows into a compact representation and then use clustering to construct local peer groups that can be compared against one another. This is a sensible design in a large network with many similar substations, because the method can exploit similarities and differences between multiple operating units instead of relying only on the history of a single site. In the HEAT framing, the encoder is not only a compression device. It is also a way to produce a representation on which clustering becomes more meaningful than on raw high-dimensional windows. The clustering stage then supports fault discovery by locating groups of substations or windows that behave similarly and by isolating groups that look abnormal relative to their peers.",
        "In this thesis, HEAT remains the main methodological reference rather than a blueprint copied without modification. The available dataset contains far fewer usable consumer sheets than the HEAT case study, and this changes what clustering can realistically achieve. With a small number of buildings, clustering alone is less reliable as a primary fault-detection mechanism because the peer structure is weak. The practical consequence is that clustering is still useful, but its role shifts toward interpretation: it helps describe operating regimes and groups of anomalies after detection, rather than serving as the main detector by itself.": "In this thesis, HEAT remains the main methodological reference rather than a blueprint copied without modification. The available dataset contains far fewer usable consumer sheets than the HEAT case study, and this changes what clustering can realistically achieve. With a small number of buildings, clustering alone is less reliable as a primary fault-detection mechanism because the peer structure is weak. The practical consequence is that clustering is still useful, but its role shifts toward interpretation: it helps describe operating regimes and groups of anomalies after detection, rather than serving as the main detector by itself. The similarity to HEAT is therefore conceptual rather than literal. Both approaches rely on window-based representations and unsupervised analysis, but HEAT emphasizes peer comparison across a larger fleet whereas this thesis emphasizes reconstruction against each building's own historical behaviour and then uses clustering to summarize the flagged windows.",
        "An autoencoder is a neural network trained to reproduce its own input at the output layer [4]. In the thesis pipeline, each input is a 24-hour multivariate window containing three synchronized channels: supply temperature, return temperature, and a flow-related channel. The encoder compresses the window into a latent representation that retains the most important structure, and the decoder uses that representation to reconstruct the original signal sequence. If a window follows patterns that are common in the historical training data, the model usually reconstructs it well and the reconstruction error remains low. If a window contains an unusual temporal pattern, one or more channels are reconstructed less accurately and the reconstruction error increases. This makes the reconstruction error a natural anomaly score in situations where explicit fault labels are not available.": "An autoencoder is a neural network trained to reproduce its own input at the output layer [4]. In the thesis pipeline, each input is a 24-hour multivariate window containing three synchronized channels: supply temperature, return temperature, and a flow-related channel. The encoder compresses the window into a latent representation that retains the most important structure, and the decoder uses that representation to reconstruct the original signal sequence. If a window follows patterns that are common in the historical training data, the model usually reconstructs it well and the reconstruction error remains low. If a window contains an unusual temporal pattern, one or more channels are reconstructed less accurately and the reconstruction error increases. This makes the reconstruction error a natural anomaly score in situations where explicit fault labels are not available. In this thesis, anomaly detection is joint at the window level because all three channels are reconstructed together, but interpretation is feature-specific afterward because the reconstruction error is also decomposed by channel. That decomposition is what allows a flagged window to be discussed as mainly supply-related, return-related, or flow-related rather than only 'anomalous' in a generic sense.",
        "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. For the main thesis narrative, the analysis is narrowed to the five sheets with the most usable retained windows and without long faulty constant-value periods that would make anomaly interpretation ambiguous:": "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. The source data are split across two Excel workbooks. Abat Oliba and Hostatgeria Underfloor are read from District Heating_updated_16_07_2025_2.xlsx, while Abat Cisneros, Abat Garriga, and Abat Marcet are read from District Heating_updated_16_07_2025_1.xlsx. All seven reviewed heating-consumer sheets are retained in the main thesis result set. The only narrower subset is used for the reconstruction-error timeline figure, where the sheets with long faulty constant-value stretches are omitted because that specific view becomes visually misleading:",
        "The preprocessing pipeline is designed to retain daily windows that reflect meaningful heating behaviour while discarding windows that are too incomplete or too inactive to support reliable interpretation. The main decisions are:": "The preprocessing pipeline is designed to retain daily windows that reflect meaningful heating behaviour while discarding windows that are too incomplete or too inactive to support reliable interpretation. The main decisions are:",
        "Taken together, these decisions reduce the influence of missing data, long inactive periods, and weakly informative windows. The goal is not simply to maximize the number of windows, but to preserve windows that are comparable enough for reconstruction-based modelling and later interpretation.": "Taken together, these decisions reduce the influence of missing data, long inactive periods, and weakly informative windows. More precisely, each sheet is timestamp-sorted, delta-T is computed as supply minus return, non-active periods are masked using positive power and positive delta-T, the signals are resampled to 15-minute medians, and only short gaps are interpolated. A 24-hour window therefore contains 96 synchronized time steps per channel, and the 12-hour stride creates overlap so that abrupt changes are less likely to fall exactly on window boundaries. Windows are kept only when at least 60 percent of their resampled points correspond to active heating and at least 85 percent of the three-channel samples are complete. The goal is not simply to maximize the number of windows, but to preserve windows that are comparable enough for reconstruction-based modelling and later interpretation.",
        "The current architecture is a compact 1D convolutional autoencoder. The encoder contains two convolutional blocks with ReLU activations and max pooling, while the decoder reconstructs the signal using transposed convolutions. This architecture was chosen as a conservative baseline: it is expressive enough to learn daily temperature and flow patterns, but still simple enough that the later interpretation of its reconstruction errors remains manageable. The thesis does not claim that this is the optimal architecture; rather, it serves as a technically defensible first model for reconstruction-based anomaly detection in the available data setting.": "The current architecture is a compact 1D convolutional autoencoder. Each 24-hour input window is represented as a three-channel sequence of length 96. The encoder first applies a one-dimensional convolution with 16 output channels, kernel size 5, and padding 2, followed by a ReLU activation and max pooling by a factor of 2. A second convolution maps the signal to 16 latent channels with the same kernel size and padding, again followed by ReLU and max pooling. After the two pooling operations, the temporal resolution has been reduced from 96 to 24 time steps, so the latent representation is a compressed multichannel summary of the daily pattern. The decoder then uses two transposed convolutions with stride 2 to upsample the latent signal back to the original sequence length and reconstruct the three input channels. This architecture was chosen as a conservative baseline: it is expressive enough to learn daily temperature and flow patterns, but still simple enough that the later interpretation of its reconstruction errors remains manageable. The thesis does not claim that this is the optimal architecture; rather, it serves as a technically defensible first model for reconstruction-based anomaly detection in the available data setting.",
        "The model uses three synchronized channels per 24-hour window:": "The model uses three synchronized channels per 24-hour window:",
        "The flow channel is included because thermal anomalies are often easier to interpret when temperature behavior is viewed together with flow-related behavior. During method development, several formulations of the flow signal were explored in order to improve numerical robustness. In the final draft, the emphasis is therefore on the behavior of the input flow channel rather than on the intermediate engineering details of every tested formulation.": "The flow channel is included because thermal anomalies are often easier to interpret when temperature behavior is viewed together with flow-related behavior. The underlying engineering relation is m = P / (cp x (Ts - Tr)), where m is mass flow rate, P is power, cp is the specific heat capacity of water, and Ts - Tr is the temperature drop across the substation. In the implemented pipeline, power is treated as kilowatts for all sheets based on supervisor guidance, and cp is fixed at 4180 J/(kg deg C). This makes the physically scaled flow quantity derived_flow_kg_s available for inspection. During method development, several formulations of the flow signal were explored in order to improve numerical robustness when delta-T becomes very small. In the final draft, the emphasis is therefore on the behavior of the input flow channel rather than on the intermediate engineering details of every tested formulation.",
        "The latest main result pack uses the 3-sigma rule, following supervisor guidance. The thesis should discuss that neither threshold is uniformly stricter across all sheets; the difference depends on the shape of the training reconstruction-error distribution.": "The latest main result pack uses the 3-sigma rule, following supervisor guidance. Concretely, the windows are ordered chronologically and the first 80 percent are used for model fitting. After training, the model reconstructs all retained windows, the total reconstruction error is computed as the mean squared difference across all channels and time steps, and the anomaly threshold is estimated only from the training subset. Under the 3-sigma rule, a window is flagged when its total reconstruction error exceeds the training mean plus three training standard deviations. The same logic is also applied channel-wise so that supply, return, and flow-specific reconstruction errors can be compared afterward. The thesis should discuss that neither threshold is uniformly stricter across all sheets; the difference depends on the shape of the training reconstruction-error distribution.",
        "The engineering baseline is a low delta-T anomaly rule computed only on active-heating rows. It is not used by the autoencoder. Instead, it is used afterward to check whether detected anomaly windows overlap a simple, physically interpretable warning signal.": "The engineering baseline is a low delta-T anomaly rule computed only on active-heating rows. It is not used by the autoencoder. Instead, it is used afterward to check whether detected anomaly windows overlap a simple, physically interpretable warning signal. The implementation uses the active-heating delta-T distribution for each sheet, computes a robust modified z-score, and marks strongly negative deviations as low delta-T events. A reviewed anomaly window is then said to overlap the baseline if at least one low delta-T event occurs inside that same 24-hour window.",
        "Two clustering roles were explored:": "Two clustering roles were explored:",
        "The thesis should make clear that clustering is supportive rather than central in the final pipeline.": "The thesis should make clear that clustering is supportive rather than central in the final pipeline. Operating-regime clustering is applied to all retained windows in order to describe common daily behaviour patterns. Anomaly-only clustering is applied after detection and groups only the flagged windows according to their feature summaries or per-feature reconstruction-error structure. The point is not to replace the anomaly score with a cluster label, but to help the supervisor and reader see whether the flagged windows separate into recurring anomaly families such as mostly supply-driven, mostly return-driven, or mostly flow-driven behaviour.",
        "Because of these limitations, evaluation in this thesis is based on anomaly review, cross-method comparison, and supervisor or domain interpretation rather than standard supervised metrics such as accuracy, recall, or F1-score. This is an important methodological point: the thesis is primarily about finding interpretable anomaly candidates in a realistic low-label setting, not about optimizing a conventional labelled benchmark.": "Because of these limitations, evaluation in this thesis is based on anomaly review, cross-method comparison, and supervisor or domain interpretation rather than standard supervised metrics such as accuracy, recall, or F1-score. This is an important methodological point: the thesis is primarily about finding interpretable anomaly candidates in a realistic low-label setting, not about optimizing a conventional labelled benchmark. That makes the work closer in spirit to recent unsupervised district-heating studies and further motivates the need for richer visual inspection and later live-data validation [5, 7]. In effect, the thesis trades benchmark-style certainty for operational usefulness: the output is a reviewed set of anomaly candidates, dominant-feature labels, and comparative plots that can support expert interpretation and later live-data deployment.",
        "The current end-to-end result set used for the draft focuses on five heating-consumer sheets: Abat Cisneros, Abat Garriga, Abat Marcet, Abat Oliba, and Hostatgeria Underfloor. These five buildings were kept because they provided the most usable retained windows without the long faulty constant-value periods observed in two of the exploratory cases. The strongest anomaly case remains cons_hostatgeria_underfloor_hea, while the five-building set as a whole still shows substantial variation in anomaly count, dominant feature, and engineering-baseline overlap.": "The current end-to-end result set used for the draft covers all seven heating-consumer sheets modeled in the project: Abat Cisneros, Abat Garriga, Abat Marcet, Abat Oliba, Hostatgeria DHW Radiators, Hostatgeria Underfloor, and Nostra Senyora. The seven-building set gives the most complete picture of how the detector behaves across the available consumer substations. A narrower subset is used only for the reconstruction-error timeline comparison, where Abat Oliba and Hostatgeria Underfloor are omitted because long faulty constant-value stretches make that specific timeline view harder to interpret. The strongest anomaly case remains cons_hostatgeria_underfloor_hea, while the full seven-building set still shows substantial variation in anomaly count, dominant feature, and engineering-baseline overlap.",
        "The current end-to-end result set used for the draft focuses on five heating-consumer sheets: Abat Cisneros, Abat Garriga, Abat Marcet, Abat Oliba, and Hostatgeria Underfloor. These five buildings were kept because they provided the most usable retained windows without the long faulty constant-value periods observed in two of the exploratory cases. All five remain part of the main thesis result set. The only narrower view is the reconstruction-error timeline comparison, which is restricted to three buildings because Abat Oliba and Hostatgeria Underfloor contain long faulty constant-value stretches that would make that specific timeline figure visually misleading. The strongest anomaly case remains cons_hostatgeria_underfloor_hea, while the five-building set as a whole still shows substantial variation in anomaly count, dominant feature, and engineering-baseline overlap.": "The current end-to-end result set used for the draft covers all seven heating-consumer sheets modeled in the project: Abat Cisneros, Abat Garriga, Abat Marcet, Abat Oliba, Hostatgeria DHW Radiators, Hostatgeria Underfloor, and Nostra Senyora. The seven-building set gives the most complete picture of how the detector behaves across the available consumer substations. A narrower subset is used only for the reconstruction-error timeline comparison, where Abat Oliba and Hostatgeria Underfloor are omitted because long faulty constant-value stretches make that specific timeline view harder to interpret. The strongest anomaly case remains cons_hostatgeria_underfloor_hea, while the full seven-building set still shows substantial variation in anomaly count, dominant feature, and engineering-baseline overlap.",
    }
    for old, new in replacements.items():
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass


def insert_acronym_list(body: ET.Element) -> None:
    try:
        idx = find_para_index(body, "List of Acronyms and Abbreviations")
        existing = {paragraph_text(p) for p in paragraph_children(body)}
        if "HEAT - Hierarchical-constrained Encoder-Assisted Time-series clustering" not in existing:
            body.insert(idx + 4, make_paragraph("HEAT - Hierarchical-constrained Encoder-Assisted Time-series clustering", "BodyText"))
        return
    except ValueError:
        pass
    before = "1 Introduction"
    elements = [
        make_paragraph("List of Acronyms and Abbreviations", "Heading1"),
        make_paragraph("AE - Autoencoder", "BodyText"),
        make_paragraph("DH - District Heating", "BodyText"),
        make_paragraph("DHW - Domestic Hot Water", "BodyText"),
        make_paragraph("HEAT - Hierarchical-constrained Encoder-Assisted Time-series clustering", "BodyText"),
        make_paragraph("MSE - Mean Squared Error", "BodyText"),
        make_paragraph("Ts - Supply temperature", "BodyText"),
        make_paragraph("Tr - Return temperature", "BodyText"),
    ]
    insert_block(body, before, elements)


def insert_supervised_unsupervised_section(body: ET.Element) -> None:
    try:
        find_para_index(body, "2.3 Supervised and unsupervised fault detection")
        return
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "2.3 Reconstruction-based anomaly detection", "2.4 Reconstruction-based anomaly detection")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "2.4 Physics-informed feature construction", "2.5 Physics-informed feature construction")
    except ValueError:
        pass
    elements = [
        make_paragraph("2.3 Supervised and unsupervised fault detection", "Heading2"),
        make_paragraph(
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score.",
            "BodyText",
        ),
        make_paragraph(
            "The present project does not have that kind of labelled dataset. Most windows in the historical data are unlabeled, and even suspicious periods are usually not tied to a confirmed fault record. For that reason, the problem is better framed as unsupervised anomaly detection. In an unsupervised setting, the model is trained to capture the structure of historical normal-looking behaviour without being told explicit fault classes. A high anomaly score does not mean that a specific known fault has been diagnosed. It means that the operating pattern is sufficiently different from the learned historical structure that it deserves review. This distinction matters for the whole thesis: the contribution is not a supervised classifier of named faults, but a ranking and interpretation workflow for unusual operating windows.",
            "BodyText",
        ),
    ]
    insert_block(body, "2.4 Reconstruction-based anomaly detection", elements)


def insert_research_context(body: ET.Element) -> None:
    paragraphs = [paragraph_text(p) for p in paragraph_children(body)]

    if "District-heating-specific studies also span several different problem formulations." not in " ".join(paragraphs):
        block = [
            make_paragraph(
                "District-heating-specific studies also span several different problem formulations. Calikus et al. study data-driven heat-load patterns and show that operational behaviour can be meaningfully grouped even before explicit fault labels are introduced [6]. SHEDAD moves further toward anomaly detection by building neighborhood-aware comparisons between substations and isolating anomalous supply-temperature and performance behaviour in larger urban networks [5]. More recently, Roelofs et al. highlight the value of labelled service data and event-based evaluation for predictive maintenance, which is especially relevant for understanding what this thesis can and cannot validate with its current historical dataset [7].",
                "BodyText",
            )
        ]
        insert_block(body, "2.2 HEAT paper as reference", block)

    if "Broader time-series anomaly-detection research reaches a similar conclusion." not in " ".join(paragraphs):
        block = [
            make_paragraph(
                "Broader time-series anomaly-detection research reaches a similar conclusion. Classical anomaly-detection surveys and more recent time-series reviews emphasize that unsupervised methods remain especially important when anomaly labels are scarce, expensive, or operationally ambiguous, but they also note that method comparison becomes harder because results depend strongly on the dataset, anomaly type, and evaluation protocol [2, 8, 10]. This is directly relevant for district-heating data, where many suspicious periods can be recognized by operators as unusual without being linked to a single confirmed fault label.",
                "BodyText",
            )
        ]
        insert_block(body, "2.2 HEAT paper as reference", block)

    if "Explainability is also an active topic in the autoencoder literature." not in " ".join(paragraphs):
        block = [
            make_paragraph(
                "Explainability is also an active topic in the autoencoder literature. Recent work on robust and explainable unsupervised autoencoders argues that reconstruction-based detectors become more useful when the anomaly score can be decomposed into understandable temporal or feature-level contributions rather than being treated as a single opaque number [9]. That argument aligns closely with the design choice in this thesis to inspect per-feature reconstruction errors and dominant-feature labels after each window is flagged.",
                "BodyText",
            )
        ]
        insert_block(body, "2.5 Physics-informed feature construction", block)


def insert_related_work_positioning(body: ET.Element) -> None:
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "2.6 Related work positioning" in text:
        return

    elements = [
        make_paragraph("2.6 Related work positioning", "Heading2"),
        make_paragraph(
                "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12, 13]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9, 14, 15, 16, 17]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance [1, 5, 6, 7].",
                "BodyText",
            ),
        make_paragraph(
            "Compared with the broader anomaly-detection literature, the present thesis is deliberately conservative in model ambition. It does not attempt to claim a novel neural architecture or a state-of-the-art benchmark result. Instead, it focuses on a technically defensible end-to-end workflow for a real weak-label setting: daily window construction, reconstruction-based scoring, feature-level attribution, engineering comparison, and cross-building review. That positioning is appropriate because the central challenge in the available data is not model expressiveness alone, but how to convert imperfect historical measurements into anomaly evidence that remains understandable and reviewable.",
            "BodyText",
        ),
        make_paragraph(
            "Compared with the HEAT paper, the main methodological difference is scale. HEAT is strongest when a larger population of substations supports peer-based comparison and clustering. In the present project, the smaller number of usable buildings makes pure peer comparison less reliable as a primary detector. For that reason, the thesis gives reconstruction against each building's own historical behavior the central role, while still retaining clustering as a secondary interpretation layer. This keeps the work aligned with the spirit of HEAT while adapting it to the actual statistical structure of the available data.",
            "BodyText",
        ),
    ]
    insert_block(body, "3 Data", elements)


def restructure_introduction(body: ET.Element) -> None:
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "1.1 Problem setting" in text:
        return

    elements = [
        make_paragraph("1.1 Problem setting", "Heading2"),
        make_paragraph(
            "District-heating systems distribute thermal energy from centralized production to connected buildings through a shared network of pipes, heat exchangers, and local substations. At substation level, supply temperature, return temperature, flow, and power together provide a partial description of how efficiently heat is transferred from the network side to the building side. This makes district-heating monitoring an inherently multivariate problem: inefficient operation may appear as poor temperature separation, elevated return temperature, unstable flow behaviour, or some combination of these effects [5, 6, 7].",
            "BodyText",
        ),
        make_paragraph("1.2 Ethics and sustainability", "Heading2"),
        make_paragraph(
            "The sustainability motivation of this thesis is direct. District-heating systems are most effective when connected substations extract heat efficiently and return cooler water to the network. Poor control, hidden faults, or persistently inefficient operating periods can increase return temperature, reduce overall network efficiency, and make heat distribution less effective for the rest of the connected system [5, 6]. Better monitoring therefore has a practical sustainability role: it can help prioritize the building periods where wasted energy, poor control behaviour, or maintenance-relevant inefficiency are most likely to occur.",
            "BodyText",
        ),
        make_paragraph(
            "There is also an ethics dimension. Automated anomaly detection should support engineering review rather than replace it. In this thesis, anomaly flags are not treated as proof of fault. They are treated as review signals that help direct limited expert attention toward unusual operating windows. This is important because a weak-label industrial dataset can contain missing values, sensor artifacts, and building-specific operating patterns that a purely automatic system may misread if its outputs are interpreted without domain context [7, 11]. The ethical goal is therefore not blind automation, but responsible decision support: more transparent monitoring, better prioritization, and more accountable interpretation of abnormal behaviour.",
            "BodyText",
        ),
        make_paragraph("1.3 Quantitative and qualitative analysis", "Heading2"),
        make_paragraph(
            "The thesis combines quantitative and qualitative analysis. The quantitative part includes window counts, reconstruction errors, anomaly rates, threshold comparisons, dominant-feature summaries, and baseline-overlap statistics. These are needed to understand how the detector behaves across buildings and under different thresholding choices. The qualitative part consists of inspecting the highest-scoring anomaly windows, comparing supply, return, flow, and delta-T behaviour, and discussing those windows in engineering terms together with the supervisor. This combination is necessary because the available dataset does not support fully labelled benchmark evaluation. Quantitative results show where the detector reacts; qualitative review is needed to judge whether those reactions are meaningful.",
            "BodyText",
        ),
        make_paragraph("1.4 Thesis aim and research questions", "Heading2"),
    ]
    insert_block(body, "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer. In other words, the autoencoder answers the question 'does this daily operating pattern look unlike the historical normal behaviour of this building?', while clustering is used later to organize those detected anomalies into more interpretable groups. In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity. It can also indicate inefficient heat extraction, elevated return temperatures, and maintenance-relevant operating problems that reduce network performance [5, 7].", elements)
    remove_exact_paragraphs(
        body,
        [
            "In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity. It can also indicate inefficient heat extraction, elevated return temperatures, and maintenance-relevant operating problems that reduce network performance [5, 7]. The thesis is therefore motivated by both data-analysis and energy-system concerns: a useful detector should help prioritize the building periods that are most worth engineering attention.",
        ],
    )


def refresh_intro_and_future_work_text(body: ET.Element) -> None:
    try:
        set_paragraph_after(
            body,
            "1 Introduction",
            "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3]. The practical motivation is strong. Poor substation behaviour can increase return temperature and reduce network efficiency [19, 20]. District-heating performance also matters at system level because efficient substations support the broader energy and decarbonization role of heat networks [21]. A usable thesis method therefore has to do more than produce a score. It has to isolate windows that can be discussed in engineering terms and reviewed against the original signals.",
        )
    except ValueError:
        pass

    try:
        set_paragraph_after(
            body,
            "2.3 Supervised and unsupervised fault detection",
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score. In anomaly-detection practice, however, such clean labels are often unavailable, incomplete, or expensive to obtain, which is one reason classical anomaly and novelty-detection literature continues to treat unsupervised formulations as practically important rather than merely provisional [10, 12, 13, 22].",
        )
    except ValueError:
        pass

    try:
        idx = find_para_index(body, "The present project does not have that kind of labelled dataset. Most windows in the historical data are unlabeled, and even suspicious periods are usually not tied to a confirmed fault record. For that reason, the problem is better framed as unsupervised anomaly detection. In an unsupervised setting, the model is trained to capture the structure of historical normal-looking behaviour without being told explicit fault classes. A high anomaly score does not mean that a specific known fault has been diagnosed. It means that the operating pattern is sufficiently different from the learned historical structure that it deserves review. This distinction matters for the whole thesis: the contribution is not a supervised classifier of named faults, but a ranking and interpretation workflow for unusual operating windows.")
        p = list(body)[idx]
        texts = p.findall(".//w:t", NS)
        new = "The present project does not have that kind of labelled dataset. Most windows in the historical data are unlabeled, and even suspicious periods are usually not tied to a confirmed fault record. For that reason, the problem is better framed as unsupervised anomaly detection. In an unsupervised setting, the model is trained to capture the structure of historical normal-looking behaviour without being told explicit fault classes. A high anomaly score does not mean that a specific known fault has been diagnosed. It means that the operating pattern is sufficiently different from the learned historical structure that it deserves review. This distinction matters for the whole thesis: the contribution is not a supervised classifier of named faults, but a ranking and interpretation workflow for unusual operating windows. The evaluation consequence is equally important. Without stable labels, one must rely more heavily on score distributions, qualitative inspection, expert review, and careful discussion of what an anomaly flag actually means, which is fully consistent with the cautions raised in unsupervised outlier-evaluation research [11, 23]."
        if texts:
            texts[0].text = new
            for t in texts[1:]:
                t.text = ""
    except ValueError:
        pass

    try:
        idx = find_para_index(body, "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12, 13]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9, 14]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance [1, 5, 6, 7].")
        p = list(body)[idx]
        texts = p.findall(".//w:t", NS)
        new = "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12]. Older outlier-detection work provides the statistical framing behind that problem class [22]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9]. Later autoencoder-based and sequence-based studies show how this idea is implemented in practice [14, 15, 16, 17]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance. In this thesis, that line of work is represented by HEAT [1], by data-driven grouping of operational behavior [6], by neighborhood-based anomaly detection [5], and by more recent service-validated evaluation work [7]."
        if texts:
            texts[0].text = new
            for t in texts[1:]:
                t.text = ""
    except ValueError:
        pass

    try:
        set_paragraph_after(
            body,
            "1.1 Problem setting",
            "District-heating systems distribute thermal energy from centralized production to connected buildings through a shared network of pipes, heat exchangers, and local substations. At substation level, supply temperature, return temperature, flow, and power together provide a partial description of how efficiently heat is transferred from the network side to the building side. This makes district-heating monitoring an inherently multivariate problem: inefficient operation may appear as poor temperature separation, elevated return temperature, unstable flow behaviour, or some combination of these effects [19, 21].",
        )
    except ValueError:
        pass

    try:
        set_paragraph_after(
            body,
            "1.2 Ethics and sustainability",
            "The sustainability motivation of this thesis is direct. District-heating systems are most effective when connected substations extract heat efficiently and return cooler water to the network. Poor control, hidden faults, or persistently inefficient operating periods can increase return temperature, reduce overall network efficiency, and make heat distribution less effective for the rest of the connected system [19, 20]. Better monitoring therefore has a practical sustainability role: it can help prioritize the building periods where wasted energy, poor control behaviour, or maintenance-relevant inefficiency are most likely to occur.",
        )
    except ValueError:
        pass

    try:
        set_paragraph_after(
            body,
            "2.1 District-heating anomaly detection",
            "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations [19]. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour [5, 6]. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns. This is one reason recent district-heating research has increasingly combined physical intuition with data-driven modelling. Simple rules remain useful as references, but they are too narrow to represent the full range of possible substation faults or inefficient operating regimes [21].",
        )
    except ValueError:
        pass

    try:
        set_paragraph_after(
            body,
            "7.1 Future work",
            "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. A second priority is to refine threshold selection once live alert volume can be judged operationally rather than only historically. A third priority is to strengthen validation by collecting any maintenance, alarm, or manually reviewed event records that can be aligned with the flagged windows. Beyond deployment, a natural continuation of the thesis would be to broaden the building set as cleaner data become available, to compare the current joint autoencoder with alternative architectures or per-feature detectors under the same review workflow, and to incorporate contextual variables such as outdoor temperature, season, month, and day type [19, 20, 21]. Such context could reduce false positives by helping the detector separate genuinely abnormal behavior from expected seasonal regime shifts. If richer live measurements become available later, additional variables such as pressure, valve position, or occupancy-related proxies could also support more precise anomaly interpretation.",
        )
    except ValueError:
        pass


def restructure_dataset_section(body: ET.Element) -> None:
    try:
        set_paragraph_text(body, "3 Dataset and preprocessing", "3 Data")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "3.1 Available sources", "3.1 Dataset, source material, and variables")
    except ValueError:
        pass
    remove_exact_paragraphs(body, ["3.2 Main measured variables"])
    try:
        set_paragraph_text(body, "3.3 Preprocessing decisions", "3.2 Preprocessing decisions")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "3.4 Known limitations", "3.3 Known limitations")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "3.5 Result-set scope", "3.4 Result-set scope")
    except ValueError:
        pass


def move_acknowledgments_near_front(body: ET.Element) -> None:
    remove_exact_paragraphs(body, ["Acknowledgments"])
    remove_paragraphs_containing(
        body,
        [
            "Acknowledgments to be completed",
        ],
    )
    paragraphs = [paragraph_text(p) for p in paragraph_children(body)]
    if "Acknowledgments" in paragraphs:
        return
    try:
        insert_block(
            body,
            "List of Acronyms and Abbreviations",
            [
                make_paragraph("Acknowledgments", "Heading1"),
                make_paragraph("Acknowledgments to be completed.", "BodyText"),
            ],
        )
    except ValueError:
        pass


def expand_encoder_and_clustering_methodology(body: ET.Element) -> None:
    full_text = " ".join(paragraph_text(p) for p in paragraph_children(body))

    if "A compact mathematical summary of the autoencoder is helpful here." not in full_text:
        insert_block(
            body,
            "Figure 1 gives a compact schematic of the reconstruction-based detector used throughout the thesis.",
            [
                make_paragraph(
                    "A compact mathematical summary of the autoencoder is helpful here. Let x be one normalized input window with shape 3 x 96, where the three rows correspond to supply temperature, return temperature, and flow, and the 96 columns correspond to 15-minute steps over 24 hours. The encoder defines a mapping z = f_theta(x), where z has shape 16 x 24 after the two convolution-and-pooling stages. The decoder defines a reconstruction x_hat = g_phi(z), bringing the latent representation back to the original 3 x 96 shape.",
                    "BodyText",
                ),
                make_paragraph(
                    "Training minimizes reconstruction loss on the chronological training portion of the retained windows. In simplified form, the loss is the mean squared error L = (1 / (3 x 96)) sum_c sum_t (x_(c,t) - x_hat_(c,t))^2. This means the model is not trained to predict fault labels. It is trained to reproduce recurring normal-looking daily patterns. Windows that are reconstructed poorly after training therefore receive larger anomaly scores because they deviate from the temporal structure the model has learned.",
                    "BodyText",
                ),
                make_paragraph(
                    "This representation is useful because the two convolutional layers can learn short local motifs such as ramps, peaks, and short-term co-movement between supply, return, and flow, while the pooling layers compress those motifs into a lower-resolution latent summary of the day. The latent tensor is therefore not interpreted directly as an engineering variable. Its purpose is to retain enough structure that the decoder can reconstruct normal windows well and fail more visibly on unusual ones.",
                    "BodyText",
                ),
            ],
        )

    if "The clustering methodology can also be written more explicitly." not in full_text:
        elements = [
            make_paragraph(
                "The clustering methodology can also be written more explicitly. Two separate KMeans-based clustering paths are used in the project, both after feature standardization with StandardScaler and both using Euclidean distance in the standardized feature space. They differ in purpose and in the feature vectors being clustered.",
                "BodyText",
            )
        ]
        try:
            insert_block(body, "5 Results", elements)
        except ValueError:
            insert_block(body, "4 Results", elements)

    if "For operating-regime clustering, each retained daily window is summarized by descriptive statistics" not in full_text:
        elements = [
            make_paragraph(
                "For operating-regime clustering, each retained daily window is summarized by descriptive statistics rather than by the raw 3 x 96 sequence. The feature vector contains supply median and standard deviation, return median and standard deviation, flow median and standard deviation, delta-T median, delta-T 5th percentile, delta-T minimum, and mean active fraction over the window. After standardization, KMeans with k = 4 assigns each retained window to the nearest cluster center. In compact form, a window feature vector z_i is assigned to cluster argmin_j ||z_i - c_j||_2^2, where c_j is the j-th cluster centroid in standardized feature space.",
                "BodyText",
            ),
            make_paragraph(
                "For anomaly-only clustering, the input set is restricted to windows already flagged by the autoencoder. The summary vector again contains supply, return, flow, and delta-T statistics, but it also includes total reconstruction MSE and per-feature reconstruction MSE. This means the anomaly-only clustering is not grouping windows only by raw operating level; it is also grouping them by how the detector failed to reconstruct them. In the current implementation, KMeans with k = 3 is used for this second path.",
                "BodyText",
            ),
            make_paragraph(
                "This distinction is important for interpretation. Operating-regime clustering answers the question 'what kinds of daily operating patterns exist in the retained data?' Anomaly-only clustering answers a different question: 'among the windows already judged unusual, which anomaly families recur?' Because of that difference, the first clustering path is mainly descriptive at regime level, while the second clustering path is closer to anomaly typing and is more relevant when discussing whether flagged windows are mainly supply-related, return-related, or flow-related.",
                "BodyText",
            ),
        ]
        try:
            insert_block(body, "4.7 Evaluation strategy in a weak-label setting", elements)
        except ValueError:
            try:
                insert_block(body, "3.7 Evaluation strategy in a weak-label setting", elements)
            except ValueError:
                try:
                    insert_block(body, "5 Results", elements)
                except ValueError:
                    insert_block(body, "4 Results", elements)

def update_abstract_and_reference_framing(body: ET.Element) -> None:
    set_paragraph_after(
        body,
        "Abstract",
        "This thesis investigates anomaly detection in a small district-heating network using historical operational data from seven consumer substations. The work starts from the HEAT paper as a methodological reference, but adapts that approach to a setting with fewer substations, longer historical coverage, and limited fault labels. The main method is a reconstruction-based anomaly detector built on 24-hour windows of supply temperature, return temperature, and flow. Across the seven-building result set, the detector analyzed between 323 and 1113 retained windows per building. Under the final 3-sigma threshold, flagged anomaly rates ranged from 0.21 percent for Abat Oliba to 4.65 percent for Hostatgeria DHW Radiators. The clearest individual case was Hostatgeria Underfloor, where 5 of 323 windows were flagged and the strongest anomaly also overlapped the engineering low delta-T baseline. Dominant-feature analysis showed that anomaly behavior was not uniform: some buildings were mainly flow-dominant, others mainly return-dominant, while Underfloor and Nostra Senyora contributed the clearest supply-dominant cases. These results indicate that reconstruction-based anomaly detection can produce interpretable anomaly candidates in a realistic weak-label district-heating setting, while also showing that final validation still depends on domain review and future live-data evaluation.",
    )

    try:
        set_paragraph_text(
            body,
            "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3]. The practical motivation is strong: poor substation behaviour increases return temperature, degrades network efficiency, and can hide control or hydraulic problems long before a maintenance report is written. A usable thesis method therefore has to do more than produce a score. It has to isolate windows that can be discussed in engineering terms and reviewed against the original signals.",
            "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3]. The practical motivation is strong: poor substation behaviour increases return temperature, degrades network efficiency, and can hide control or hydraulic problems long before a maintenance report is written [19, 20, 21]. A usable thesis method therefore has to do more than produce a score. It has to isolate windows that can be discussed in engineering terms and reviewed against the original signals.",
        )
    except ValueError:
        pass

    try:
        set_paragraph_text(
            body,
            "District-heating systems distribute thermal energy from centralized production to connected buildings through a shared network of pipes, heat exchangers, and local substations. At substation level, supply temperature, return temperature, flow, and power together provide a partial description of how efficiently heat is transferred from the network side to the building side. This makes district-heating monitoring an inherently multivariate problem: inefficient operation may appear as poor temperature separation, elevated return temperature, unstable flow behaviour, or some combination of these effects [5, 6, 7].",
            "District-heating systems distribute thermal energy from centralized production to connected buildings through a shared network of pipes, heat exchangers, and local substations. At substation level, supply temperature, return temperature, flow, and power together provide a partial description of how efficiently heat is transferred from the network side to the building side. This makes district-heating monitoring an inherently multivariate problem: inefficient operation may appear as poor temperature separation, elevated return temperature, unstable flow behaviour, or some combination of these effects [5, 6, 7, 19, 21].",
        )
    except ValueError:
        pass

    try:
        set_paragraph_text(
            body,
            "The sustainability motivation of this thesis is direct. District-heating systems are most effective when connected substations extract heat efficiently and return cooler water to the network. Poor control, hidden faults, or persistently inefficient operating periods can increase return temperature, reduce overall network efficiency, and make heat distribution less effective for the rest of the connected system [5, 6]. Better monitoring therefore has a practical sustainability role: it can help prioritize the building periods where wasted energy, poor control behaviour, or maintenance-relevant inefficiency are most likely to occur.",
            "The sustainability motivation of this thesis is direct. District-heating systems are most effective when connected substations extract heat efficiently and return cooler water to the network. Poor control, hidden faults, or persistently inefficient operating periods can increase return temperature, reduce overall network efficiency, and make heat distribution less effective for the rest of the connected system [5, 6, 19, 20, 21]. Better monitoring therefore has a practical sustainability role: it can help prioritize the building periods where wasted energy, poor control behaviour, or maintenance-relevant inefficiency are most likely to occur.",
        )
    except ValueError:
        pass

    try:
        set_paragraph_text(
            body,
            "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns [5, 6]. This is one reason recent district-heating research has increasingly combined physical intuition with data-driven modelling: simple rules remain useful as references, but they are too narrow to represent the full range of possible substation faults or inefficient operating regimes.",
            "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns [5, 6, 19, 21]. This is one reason recent district-heating research has increasingly combined physical intuition with data-driven modelling: simple rules remain useful as references, but they are too narrow to represent the full range of possible substation faults or inefficient operating regimes.",
        )
    except ValueError:
        pass
    set_paragraph_after(
        body,
        "Sammanfattning",
        "Detta examensarbete undersöker anomalidetektion i ett litet fjärrvärmenät med hjälp av historiska driftsdata från sju kundcentraler. Arbetet utgår från HEAT-artikeln som metodologisk referens, men anpassar angreppssättet till en situation med färre undercentraler, längre historisk täckning och begränsad tillgång till felmärkta data. Huvudmetoden är en rekonstruktionsbaserad anomalidetektor byggd på 24-timmarsfönster av framledningstemperatur, returtemperatur och flöde. I resultatpaketet med sju byggnader analyserade modellen mellan 323 och 1113 behållna fönster per byggnad. Med den slutliga 3-sigma-tröskeln varierade andelen flaggade anomalier från 0,21 procent för Abat Oliba till 4,65 procent för Hostatgeria DHW Radiators. Det tydligaste enskilda fallet var Hostatgeria Underfloor, där 5 av 323 fönster flaggades och den starkaste anomalin också överlappade den ingenjörsmässiga låg-delta-T-baslinjen. Analysen av dominerande variabel visade att anomalibeteendet inte var enhetligt: vissa byggnader var främst flödesdominerade, andra främst returdominerade, medan Underfloor och Nostra Senyora gav de tydligaste framledningsdominerade fallen. Resultaten visar att rekonstruktionsbaserad anomalidetektion kan ge tolkbara anomalikandidater i en realistisk fjärrvärmesituation med svaga etiketter, men också att slutlig validering fortfarande kräver domängranskning och framtida utvärdering på live-data.",
    )
    try:
        set_paragraph_text(
            body,
            "Detta examensarbete undersöker anomalidetektion i ett litet fjärrvärmenät med hjälp av historiska driftsdata från flera kundcentraler. Arbetet utgår från HEAT-artikeln som metodologisk referens, men anpassar angreppssättet till en situation med färre undercentraler, längre historisk täckning och begränsad tillgång till felmärkta data. Huvudmetoden är en rekonstruktionsbaserad anomalidetektor som modellerar 24-timmarsfönster av framledningstemperatur, returtemperatur och härlett flöde. Studien jämför ingenjörsmässiga baslinjer, tröskelvärdesmetoder, dominant-funktionsattribuering och klusterbaserad tolkning för att identifiera anomalikandidater som kan granskas tillsammans med domänexperter och senare användas på live-data.",
            "Detta examensarbete undersöker anomalidetektion i ett litet fjärrvärmenät med hjälp av historiska driftsdata från sju kundcentraler. Arbetet utgår från HEAT-artikeln som metodologisk referens, men anpassar angreppssättet till en situation med färre undercentraler, längre historisk täckning och begränsad tillgång till felmärkta data. Huvudmetoden är en rekonstruktionsbaserad anomalidetektor byggd på 24-timmarsfönster av framledningstemperatur, returtemperatur och flöde. I resultatpaketet med sju byggnader analyserade modellen mellan 323 och 1113 behållna fönster per byggnad. Med den slutliga 3-sigma-tröskeln varierade andelen flaggade anomalier från 0,21 procent för Abat Oliba till 4,65 procent för Hostatgeria DHW Radiators. Det tydligaste enskilda fallet var Hostatgeria Underfloor, där 5 av 323 fönster flaggades och den starkaste anomalin också överlappade den ingenjörsmässiga låg-delta-T-baslinjen. Analysen av dominerande variabel visade att anomalibeteendet inte var enhetligt: vissa byggnader var främst flödesdominerade, andra främst returdominerade, medan Underfloor och Nostra Senyora gav de tydligaste framledningsdominerade fallen. Resultaten visar att rekonstruktionsbaserad anomalidetektion kan ge tolkbara anomalikandidater i en realistisk fjärrvärmesituation med svaga etiketter, men också att slutlig validering fortfarande kräver domängranskning och framtida utvärdering på live-data.",
        )
    except ValueError:
        pass

    try:
        set_paragraph_text(
            body,
            "Because of these limitations, evaluation in this thesis is based on anomaly review, cross-method comparison, and supervisor or domain interpretation rather than standard supervised metrics such as accuracy, recall, or F1-score. This is an important methodological point: the thesis is primarily about finding interpretable anomaly candidates in a realistic low-label setting, not about optimizing a conventional labelled benchmark. That makes the work closer in spirit to recent unsupervised district-heating studies and further motivates the need for richer visual inspection and later live-data validation [5, 7]. In effect, the thesis trades benchmark-style certainty for operational usefulness: the output is a reviewed set of anomaly candidates, dominant-feature labels, and comparative plots that can support expert interpretation and later live-data deployment.",
            "Because of these limitations, evaluation in this thesis is based on anomaly review, cross-method comparison, and supervisor or domain interpretation rather than standard supervised metrics such as accuracy, recall, or F1-score. This is an important methodological point: the thesis is primarily about finding interpretable anomaly candidates in a realistic low-label setting, not about optimizing a conventional labelled benchmark. That makes the work closer in spirit to recent unsupervised district-heating studies and further motivates the need for richer visual inspection and later live-data validation [5, 7, 10, 11]. In effect, the thesis trades benchmark-style certainty for operational usefulness: the output is a reviewed set of anomaly candidates, dominant-feature labels, and comparative plots that can support expert interpretation and later live-data deployment.",
        )
    except ValueError:
        pass


def strengthen_intro_and_conclusion(body: ET.Element) -> None:
    try:
        set_paragraph_text(
            body,
            "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer. In other words, the autoencoder answers the question 'does this daily operating pattern look unlike the historical normal behaviour of this building?', while clustering is used later to organize those detected anomalies into more interpretable groups.",
            "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer. In other words, the autoencoder answers the question 'does this daily operating pattern look unlike the historical normal behaviour of this building?', while clustering is used later to organize those detected anomalies into more interpretable groups. In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity. It can also indicate inefficient heat extraction, elevated return temperatures, and maintenance-relevant operating problems that reduce network performance [5, 7].",
        )
    except ValueError:
        pass

    try:
        set_paragraph_text(
            body,
            "From a thesis perspective, the contribution is therefore not the discovery of one universally validated fault class, but the construction of a defensible anomaly-detection and interpretation workflow for a realistic low-label district-heating dataset. That is an appropriate outcome for the available data setting and provides a solid basis for the transition from historical analysis to live operational use.",
            "From a thesis perspective, the contribution is therefore not the discovery of one universally validated fault class, but the construction of a defensible anomaly-detection and interpretation workflow for a realistic low-label district-heating dataset. That is an appropriate outcome for the available data setting and provides a solid basis for the transition from historical analysis to live operational use. A stronger post-thesis evaluation would require the kind of event-centered validation discussed in recent district-heating benchmark work, where accuracy, alert reliability, and earliness can be measured against service-validated fault records [7]. The present thesis does not yet have that evidence base, which is why its main contribution is methodological readiness and interpretable anomaly prioritization rather than benchmark-style fault-class performance.",
        )
    except ValueError:
        pass


def insert_gap_and_contribution_framing(body: ET.Element) -> None:
    paragraphs = [paragraph_text(p) for p in paragraph_children(body)]

    if "A clear research gap follows from this comparison." not in " ".join(paragraphs):
        block = [
            make_paragraph(
                "A clear research gap follows from this comparison. Much of the strongest recent work either assumes a larger peer population for comparison, access to cleaner labelled maintenance events, or an evaluation setup built around benchmark-style metrics [1, 5, 7, 8, 11]. The present thesis works in a different regime: a smaller set of consumer substations, long historical time-series coverage, and limited fault confirmation. The contribution is therefore not to outperform a labelled benchmark, but to show that a reconstruction-based workflow can still produce structured, feature-level anomaly evidence that is technically defensible and operationally reviewable in this weaker-data setting.",
                "BodyText",
            )
        ]
        insert_block(body, "The main research question is:", block)

    if "This difference from benchmark-style research should be stated explicitly." not in " ".join(paragraphs):
        block = [
            make_paragraph(
                "This difference from benchmark-style research should be stated explicitly. In a labelled benchmark study, the main question is usually whether one detector achieves better accuracy, recall, or F-score than another under a fixed protocol. In this thesis, the central question is different: whether the detector can convert weakly structured historical data into a manageable set of reviewable windows, each supported by signal plots, per-feature error attribution, and comparison against simple engineering references. That is a narrower but still meaningful research contribution because it addresses the decision conditions under which many industrial monitoring projects actually begin.",
                "BodyText",
            )
        ]
        insert_block(body, "6.3 Implications for live deployment", block)

    intro_has_new_structure = "1.1 Problem setting" in paragraphs and "1.2 Ethics and sustainability" in paragraphs
    if (
        not intro_has_new_structure
        and "In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity."
        not in " ".join(paragraphs)
    ):
        block = [
            make_paragraph(
                "In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity. It can also indicate inefficient heat extraction, elevated return temperatures, and maintenance-relevant operating problems that reduce network performance [5, 7]. The thesis is therefore motivated by both data-analysis and energy-system concerns: a useful detector should help prioritize the building periods that are most worth engineering attention.",
                "BodyText",
            )
        ]
        insert_block(body, "The main research question is:", block)


def insert_implementation_pipeline(body: ET.Element) -> None:
    paragraphs = [paragraph_text(p) for p in paragraph_children(body)]
    if "4.1.1 Implementation pipeline" in paragraphs or "3.1.1 Implementation pipeline" in paragraphs:
        return

    elements = [
        make_paragraph("4.1.1 Implementation pipeline", "Heading3"),
        make_paragraph(
            "The thesis workflow is implemented through a small set of scripts that correspond directly to the methodological stages of the pipeline. The purpose of this subsection is not to document every line of code, but to state clearly which computational step produces each intermediate result used later in the thesis.",
            "BodyText",
        ),
        make_paragraph(
            "prepare_autoencoder_windows.py prepares one building sheet for modeling. It loads the selected workbook and sheet, computes delta-T, constructs the three model channels, filters to active-heating periods, resamples the data to 15-minute intervals, forms overlapping 24-hour windows with 12-hour stride, applies completeness and activity thresholds, and stores the retained windows together with feature statistics used for normalization.",
            "BodyText",
        ),
        make_paragraph(
            "train_autoencoder.py loads the prepared windows, applies the chronological train-test split, fits the convolutional autoencoder on the training portion, and saves the trained model parameters together with the normalization terms needed for later reconstruction.",
            "BodyText",
        ),
        make_paragraph(
            "inspect_autoencoder_windows.py applies the trained model to all retained windows, computes total and per-feature reconstruction errors, applies the anomaly threshold, and writes the summary tables and inspection figures that support the result interpretation.",
            "BodyText",
        ),
        make_paragraph(
            "The comparison and visualization scripts then summarize the model outputs at building level. These scripts aggregate anomaly counts, dominant-feature assignments, baseline overlap, threshold comparisons, and clustering summaries into the figures used throughout Chapters 5 and 6. In this sense, the scripts are not separate from the method; they are the executable form of the methodological pipeline described in this thesis.",
            "BodyText",
        ),
    ]
    try:
        insert_block(body, "4.2 Autoencoder architecture", elements)
    except ValueError:
        insert_block(body, "3.2 Autoencoder architecture", elements)


def insert_method_and_discussion_expansion(body: ET.Element) -> None:
    full_text = " ".join(paragraph_text(p) for p in paragraph_children(body))

    if "A second important design choice is that the windows are split chronologically rather than randomly." not in full_text:
        insert_block(
            body,
            "Figure 2 shows the training reconstruction-error distributions used to compare the p99 and 3-sigma threshold rules.",
            [
                make_paragraph(
                    "A second important design choice is that the windows are split chronologically rather than randomly. This means the model is fitted on the earlier portion of the retained history and then evaluated on later periods. The purpose is not only statistical hygiene. It also reflects the intended operational use case, where a detector trained on historical data will later be applied to new incoming windows. A random split would mix early and late behaviour and make the evaluation less representative of prospective monitoring.",
                    "BodyText",
                )
            ],
        )

    if "The feature construction stage is where the thesis connects physical reasoning with statistical modeling." not in full_text:
        insert_block(
            body,
            "4.4 Thresholding",
            [
                make_paragraph(
                    "The feature construction stage is where the thesis connects physical reasoning with statistical modeling. Supply and return temperatures provide the direct thermal state of the substation, while the flow channel adds hydraulic context that helps distinguish between similar temperature patterns with different underlying operating behaviour. This is important because an unusual return-temperature pattern may have a different interpretation when it occurs together with steady flow than when it occurs together with abrupt flow changes.",
                    "BodyText",
                ),
                make_paragraph(
                    "In practice, the final three-channel representation is therefore a compromise between engineering meaning and model stability. The channels must remain interpretable enough for later anomaly review, but also regular enough that the autoencoder learns recurring daily structure rather than overfitting rare spikes or missing-data artifacts. That balance is one reason the thesis emphasizes channel-level interpretation after detection, instead of treating the latent representation as self-explanatory.",
                    "BodyText",
                ),
            ],
        )

    if "The thresholding stage should be understood as a calibration step rather than a separate detector." not in full_text:
        insert_block(
            body,
            "4.5 Engineering baseline",
            [
                make_paragraph(
                    "The thresholding stage should be understood as a calibration step rather than a separate detector. The autoencoder first produces a continuous reconstruction-error score for every retained window. The threshold then converts that score into a review decision. This distinction matters because the scientific question is not only whether the model can rank unusual windows, but also whether the chosen cutoff produces a manageable and interpretable alert set under realistic low-label conditions.",
                    "BodyText",
                ),
                make_paragraph(
                    "The comparison between p99 and 3-sigma is useful for precisely this reason. The p99 rule is distribution-free in the sense that it depends only on the empirical upper tail of the training errors, while the 3-sigma rule depends on the training mean and spread. If the error distribution is compact and roughly symmetric, the rules may behave similarly. If the error distribution is skewed or has a heavy right tail, the resulting anomaly counts can diverge substantially. The thesis therefore treats threshold choice as part of the method design, not as a cosmetic post-processing detail.",
                    "BodyText",
                ),
            ],
        )

    if "The baseline has two roles in the thesis." not in full_text:
        insert_block(
            body,
            "4.6 Clustering roles",
            [
                make_paragraph(
                    "The baseline has two roles in the thesis. First, it provides a familiar engineering reference that helps test whether at least some autoencoder anomalies correspond to a plausible and well-understood inefficiency signal. Second, it helps show what the learned detector contributes beyond a simple rule. When the autoencoder flags windows that do not overlap the low delta-T baseline, the interpretation challenge becomes whether those windows still display coherent abnormal thermal or hydraulic behaviour rather than just numerical noise.",
                    "BodyText",
                )
            ],
        )

    if "Operating-regime clustering and anomaly-only clustering should also be distinguished conceptually." not in full_text:
        insert_block(
            body,
            "5 Results",
            [
                make_paragraph(
                    "Operating-regime clustering and anomaly-only clustering should also be distinguished conceptually. The first summarizes common daily operating patterns across all retained windows and is useful for understanding how heterogeneous each building is under apparently normal or mixed conditions. The second starts only after anomaly detection and is used to organize the flagged windows into recurring anomaly families. In the final thesis framing, this makes clustering a supporting interpretation layer rather than the primary detection mechanism.",
                    "BodyText",
                )
            ],
        )

    if "One further reason the Underfloor case matters is methodological rather than only visual." not in full_text:
        insert_block(
            body,
            "6.2 What remains uncertain",
            [
                make_paragraph(
                    "One further reason the Underfloor case matters is methodological rather than only visual. It is the clearest example where several interpretation layers point in the same direction: a strong reconstruction anomaly, a stable dominant-feature assignment, a visibly abnormal signal window, and overlap with the low delta-T engineering reference. This makes it the strongest partial validation case in the thesis, even though it still does not replace formal labelled evaluation.",
                    "BodyText",
                )
            ],
        )

    if "A second uncertainty concerns transportability across buildings." not in full_text:
        insert_block(
            body,
            "6.3 Implications for live deployment",
            [
                make_paragraph(
                    "A second uncertainty concerns transportability across buildings. The results show that anomaly frequency, dominant feature, and baseline overlap differ markedly across the seven substations. This implies that one should be cautious about interpreting a high anomaly count in one building as equivalent in meaning to the same count in another. Part of the thesis contribution is therefore comparative rather than universal: it demonstrates that building-level context remains necessary even when the same modeling pipeline is applied across all sheets.",
                    "BodyText",
                )
            ],
        )

    if "A final discussion point concerns what successful evaluation should look like after the thesis." not in full_text:
        insert_block(
            body,
            "7 Conclusion",
            [
                make_paragraph(
                    "A final discussion point concerns what successful evaluation should look like after the thesis. In a fully labelled setting, one would expect event-level fault benchmarks, explicit alert reliability measures, and timing-based criteria such as earliness. Recent district-heating evaluation work shows the value of exactly those fault-centric metrics once service-validated labels become available [7]. The present thesis does not yet have that evidence base, which is why it focuses instead on interpretable anomaly ranking, cross-building comparison, and readiness for future live-data review.",
                    "BodyText",
                )
            ],
        )


def insert_data_and_results_expansion(body: ET.Element) -> None:
    full_text = " ".join(paragraph_text(p) for p in paragraph_children(body))

    try:
        set_paragraph_text(
            body,
            "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. The source data are split across two Excel workbooks. Abat Oliba and Hostatgeria Underfloor are read from District Heating_updated_16_07_2025_2.xlsx, while Abat Cisneros, Abat Garriga, and Abat Marcet are read from District Heating_updated_16_07_2025_1.xlsx. For the main thesis narrative, the analysis is narrowed to the five sheets with the most usable retained windows and without long faulty constant-value periods that would make anomaly interpretation ambiguous:",
            "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. The source data are split across two Excel workbooks. Abat Oliba and Hostatgeria Underfloor are read from District Heating_updated_16_07_2025_2.xlsx, while Abat Cisneros, Abat Garriga, and Abat Marcet are read from District Heating_updated_16_07_2025_1.xlsx. All seven reviewed heating-consumer sheets are retained in the main thesis result set:",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. The source data are split across two Excel workbooks. Abat Oliba and Hostatgeria Underfloor are read from District Heating_updated_16_07_2025_2.xlsx, while Abat Cisneros, Abat Garriga, and Abat Marcet are read from District Heating_updated_16_07_2025_1.xlsx. For the main thesis narrative, the analysis is narrowed to the five sheets with the most usable retained windows and without long faulty constant-value periods that would make anomaly interpretation ambiguous:",
            "The thesis uses historical data from a district-heating network associated with Montserrat / Abat Oliba. During the broader exploratory phase, seven heating-consumer sheets were reviewed in order to understand data quality, coverage, and modelling feasibility. The source data are split across two Excel workbooks. Abat Oliba and Hostatgeria Underfloor are read from District Heating_updated_16_07_2025_2.xlsx, while Abat Cisneros, Abat Garriga, and Abat Marcet are read from District Heating_updated_16_07_2025_1.xlsx. All seven reviewed heating-consumer sheets are retained in the main thesis result set:",
        )
    except ValueError:
        pass

    if "These seven sheets should not be understood as seven identical substations observed under identical conditions." not in full_text:
        elements = [
                make_paragraph(
                    "These seven sheets should not be understood as seven identical substations observed under identical conditions. They differ in coverage, missing-data behaviour, apparent heating intensity, and the frequency of clearly inactive periods. Some sheets contain long stretches that are visually flat or weakly informative for reconstruction-based modeling, while others show richer day-to-day variation. This heterogeneity is part of the practical challenge of the thesis and helps explain why a single shared detector can still produce building-specific anomaly behaviour.",
                    "BodyText",
                )
            ]
        for anchor in ["3.2 Main measured variables", "3.1 Overview", "4.1 Overview"]:
            try:
                insert_block(body, anchor, elements)
                break
            except ValueError:
                pass

    if "The unequal retained-window counts are therefore a data-quality result as well as a preprocessing result." not in full_text:
        elements = [
                make_paragraph(
                    "The unequal retained-window counts are therefore a data-quality result as well as a preprocessing result. A building contributes fewer windows not only when its original time span is shorter, but also when more of its resampled periods fail the active-heating requirement, contain long missing gaps, or are dominated by values that do not support meaningful daily reconstruction. For this reason, the retained-window count should not be read as a neutral sample-size statistic alone; it also summarizes how much of each sheet remains usable after applying the thesis quality criteria.",
                    "BodyText",
                )
            ]
        for anchor in ["3.4 Known limitations", "3.3 Known limitations", "3.1 Overview", "4.1 Overview"]:
            try:
                insert_block(body, anchor, elements)
                break
            except ValueError:
                pass

    if "Table 1 already shows that the seven buildings do not behave uniformly under the same pipeline." not in full_text:
        try:
            insert_block(
                body,
                "Figure 3 summarizes the retained-window counts, flagged anomalies, and anomaly rates across the seven selected buildings.",
                [
                make_paragraph(
                    "Table 1 already shows that the seven buildings do not behave uniformly under the same pipeline. Hostatgeria DHW Radiators accumulates by far the largest number of flagged windows and is strongly flow-dominant, which suggests a recurring hydraulic anomaly family rather than one isolated event. Hostatgeria Underfloor is different: its flagged count is modest, but the windows that are flagged are unusually strong and physically coherent, making it the clearest individual case study. Abat Garriga and Nostra Senyora occupy an intermediate position, with recurring anomalies that are substantial enough to study but not as extreme as the Underfloor case.",
                    "BodyText",
                )
                ],
            )
        except ValueError:
            pass

    if "The seven-building result set is useful precisely because it shows several different anomaly regimes at once." not in full_text:
        try:
            insert_block(
                body,
                "Figure 12 shows which feature dominates the anomaly score for each building.",
                [
                make_paragraph(
                    "The seven-building result set is useful precisely because it shows several different anomaly regimes at once. Flow-dominant behaviour appears most clearly in Abat Cisneros, Abat Marcet, and especially Hostatgeria DHW Radiators. Return-dominant behaviour is most visible in Abat Garriga and part of Abat Oliba. Supply-dominant behaviour is rarer but stronger where it occurs, with Hostatgeria Underfloor remaining the clearest case and Nostra Senyora contributing additional supply-heavy windows. This diversity is one of the strongest arguments that the detector is not simply reacting to one generic artifact.",
                    "BodyText",
                )
                ],
            )
        except ValueError:
            pass

    if "The low delta-T comparison should also be interpreted asymmetrically rather than as a pass-fail test." not in full_text:
        try:
            insert_block(
                body,
                "Figure 14 compares the number of autoencoder anomalies with the engineering low delta-T baseline.",
                [
                make_paragraph(
                    "The low delta-T comparison should also be interpreted asymmetrically rather than as a pass-fail test. Overlap with the baseline is useful when it occurs, because it links the learned anomaly score to a familiar engineering symptom. Lack of overlap, however, does not automatically weaken the detector. It may simply indicate that the flagged window belongs to another anomaly family, for example an unusual return-temperature pattern or unstable flow behaviour that does not appear as an extreme low delta-T event. This is why the baseline is a reference point rather than a ground-truth oracle in the thesis.",
                    "BodyText",
                )
                ],
            )
        except ValueError:
            pass

    if "The operating-regime view is most informative when it is used comparatively." not in full_text:
        try:
            insert_block(
                body,
                "Figure 16 summarizes the operating-regime cluster occupancy for the seven selected buildings.",
                [
                make_paragraph(
                    "The operating-regime view is most informative when it is used comparatively. A building whose retained windows concentrate heavily in one or two clusters is behaving more repetitively at the daily-pattern level than a building whose windows spread across many clusters. That does not by itself define anomaly severity, but it helps explain why some sheets produce sharper anomaly families while others produce a broader mix of flagged behaviour.",
                    "BodyText",
                )
                ],
            )
        except ValueError:
            pass


def insert_new_sections_for_structure(body: ET.Element) -> None:
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))

    if "4.7 Evaluation strategy in a weak-label setting" not in text and "3.7 Evaluation strategy in a weak-label setting" not in text:
        elements = [
            make_paragraph("4.7 Evaluation strategy in a weak-label setting", "Heading2"),
            make_paragraph(
                "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric. The first layer is internal model behavior: reconstruction-error distributions, threshold sensitivity, and the stability of dominant-feature assignments. The second layer is engineering comparison: overlap with the low delta-T baseline and inspection of supply, return, and flow behavior in the top anomaly windows. The third layer is cross-building consistency: whether different sheets produce qualitatively different but still interpretable anomaly families under the same pipeline. The fourth and final layer is expert interpretation, where the outputs are reviewed with the supervisor and later compared with live operational context.",
                "BodyText",
            ),
            make_paragraph(
                "This evaluation strategy is intentionally aligned with the data conditions of the thesis. In a fully labelled study, one would normally report fault-detection metrics against confirmed events. In the present work, the more defensible question is whether the method produces a manageable and physically interpretable anomaly set that is strong enough to justify later prospective testing. The thesis therefore treats interpretability, comparative consistency, and operational reviewability as primary evaluation targets at this stage.",
                "BodyText",
            ),
        ]
        try:
            insert_block(body, "5 Results", elements)
        except ValueError:
            insert_block(body, "4 Results", elements)

    if "6.4 Threats to validity" not in text and "5.4 Threats to validity" not in text:
        elements = [
            make_paragraph("6.4 Threats to validity", "Heading2"),
            make_paragraph(
                "Several threats to validity remain. Internal validity is limited by the fact that anomaly status is inferred from reconstruction error rather than confirmed by a comprehensive event log. Construct validity is affected by the need to derive and model a flow-related channel from the available measurements, which means that some anomaly behavior may still reflect feature construction choices rather than only physical system faults. External validity is limited because the network is small and the seven sheets are heterogeneous, so the present findings should not be generalized automatically to larger or structurally different district-heating systems.",
                "BodyText",
            ),
            make_paragraph(
                "These threats do not invalidate the thesis, but they do define the scope of its claims. The work demonstrates that reconstruction-based anomaly detection is viable and interpretable in the available historical setting. It does not yet demonstrate benchmark-grade fault identification under fully validated labels. That stronger claim must be reserved for later live-data evaluation and future access to richer service or maintenance records.",
                "BodyText",
            ),
        ]
        try:
            insert_block(body, "7 Conclusion", elements)
        except ValueError:
            insert_block(body, "6 Conclusion", elements)


def harmonize_data_scope(body: ET.Element) -> None:
    try:
        set_paragraph_text(
            body,
            "Two additional sheets, cons_hostatgeria_DHW_radiators and cons_nostra_senyora, were retained during the exploratory phase but are not used in the main thesis draft because they contain long periods of faulty constant-value behavior that make interpretation less reliable.",
            "Hostatgeria DHW Radiators and Nostra Senyora are also retained in the main thesis result set. They are interpreted mainly through summary statistics, anomaly inspections, and cross-building comparisons rather than through the reconstruction-error timeline figure.",
        )
    except ValueError:
        pass

    try:
        underfloor_idx = find_para_index(body, "cons_hostatgeria_underfloor_hea")
    except ValueError:
        return

    existing = {paragraph_text(p) for p in paragraph_children(body)}
    insert_idx = underfloor_idx + 1
    for stem in ["cons_hostatgeria_DHW_radiators", "cons_nostra_senyora"]:
        if stem not in existing:
            body.insert(insert_idx, make_paragraph(stem, "BodyText"))
            insert_idx += 1


def move_trita_block(body: ET.Element) -> None:
    trita_text = "TRITA – EECS-EX 2026:0000Stockholm, Sweden 2026www.kth.se"
    try:
        trita_idx = find_para_index(body, trita_text)
        body.remove(list(body)[trita_idx])
    except ValueError:
        pass

    end_marker = "Appendix A: Writing notes"
    elements = [
        make_paragraph("TRITA-EECS-EX-2026:0000", "BodyText", centered=True),
        make_paragraph("Stockholm, Sweden 2026", "BodyText", centered=True),
        make_paragraph("www.kth.se", "BodyText", centered=True),
    ]
    try:
        insert_block(body, end_marker, elements)
    except ValueError:
        for elem in elements:
            body.append(elem)


def cleanup_endmatter(body: ET.Element) -> None:
    safe_remove_between(body, "6.4 Writing priorities", "7 Conclusion")
    safe_remove_between(body, "Appendix A: Writing notes", "TRITA-EECS-EX-2026:0000")
    safe_remove_from(body, "Appendix A: Writing notes")
    try:
        set_paragraph_text(
            body,
            "The current architecture is a compact 1D convolutional autoencoder. Each 24-hour input window is represented as a three-channel sequence of length 96. The encoder first applies a one-dimensional convolution with 16 output channels, kernel size 5, and padding 2, followed by a ReLU activation and max pooling by a factor of 2. A second convolution maps the signal to 16 latent channels with the same kernel size and padding, again followed by ReLU and max pooling. After the two pooling operations, the temporal resolution has been reduced from 96 to 24 time steps, so the latent representation is a compressed multichannel summary of the daily pattern. The decoder then uses two transposed convolutions with stride 2 to upsample the latent signal back to the original sequence length and reconstruct the three input channels. This architecture was chosen as a conservative baseline: it is expressive enough to learn daily temperature and flow patterns, but still simple enough that the later interpretation of its reconstruction errors remains manageable. The thesis does not claim that this is the optimal architecture; rather, it serves as a technically defensible first model for reconstruction-based anomaly detection in the available data setting.",
            "The current architecture is a compact 1D convolutional autoencoder. Each 24-hour input window is represented as a three-channel sequence of length 96. The encoder first applies a one-dimensional convolution with 16 output channels, kernel size 5, and padding 2, followed by a ReLU activation and max pooling by a factor of 2. A second convolution maps the signal to 16 latent channels with the same kernel size and padding, again followed by ReLU and max pooling. After the two pooling operations, the temporal resolution has been reduced from 96 to 24 time steps, so the latent representation is a compressed multichannel summary of the daily pattern. The decoder then uses two transposed convolutions with stride 2 to upsample the latent signal back to the original sequence length and reconstruct the three input channels. This architecture was chosen as a conservative baseline: it is expressive enough to learn daily temperature and flow patterns, but still simple enough that the later interpretation of its reconstruction errors remains manageable. The thesis does not claim that this is the optimal architecture; rather, it serves as a technically defensible first model for reconstruction-based anomaly detection in the available data setting [4, 14, 15, 16, 17].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The current architecture is a compact 1D convolutional autoencoder.",
            "The current architecture is a compact 1D convolutional autoencoder. Each 24-hour input window is represented as a three-channel sequence of length 96. The encoder first applies a one-dimensional convolution with 16 output channels, kernel size 5, and padding 2, followed by a ReLU activation and max pooling by a factor of 2. A second convolution maps the signal to 16 latent channels with the same kernel size and padding, again followed by ReLU and max pooling. After the two pooling operations, the temporal resolution has been reduced from 96 to 24 time steps, so the latent representation is a compressed multichannel summary of the daily pattern. The decoder then uses two transposed convolutions with stride 2 to upsample the latent signal back to the original sequence length and reconstruct the three input channels. This architecture was chosen as a conservative baseline: it is expressive enough to learn daily temperature and flow patterns, but still simple enough that the later interpretation of its reconstruction errors remains manageable. The thesis does not claim that this is the optimal architecture; rather, it serves as a technically defensible first model for reconstruction-based anomaly detection in the available data setting [4, 14, 15, 16, 17].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The latest main result pack uses the 3-sigma rule, following supervisor guidance. Concretely, the windows are ordered chronologically and the first 80 percent are used for model fitting. After training, the model reconstructs all retained windows, the total reconstruction error is computed as the mean squared difference across all channels and time steps, and the anomaly threshold is estimated only from the training subset. Under the 3-sigma rule, a window is flagged when its total reconstruction error exceeds the training mean plus three training standard deviations. The same logic is also applied channel-wise so that supply, return, and flow-specific reconstruction errors can be compared afterward. The thesis should discuss that neither threshold is uniformly stricter across all sheets; the difference depends on the shape of the training reconstruction-error distribution.",
            "The latest main result pack uses the 3-sigma rule, following supervisor guidance. Concretely, the windows are ordered chronologically and the first 80 percent are used for model fitting. After training, the model reconstructs all retained windows, the total reconstruction error is computed as the mean squared difference across all channels and time steps, and the anomaly threshold is estimated only from the training subset. Under the 3-sigma rule, a window is flagged when its total reconstruction error exceeds the training mean plus three training standard deviations. The same logic is also applied channel-wise so that supply, return, and flow-specific reconstruction errors can be compared afterward. The thesis should discuss that neither threshold is uniformly stricter across all sheets; the difference depends on the shape of the training reconstruction-error distribution [11, 17, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The latest main result pack uses the 3-sigma rule, following supervisor guidance.",
            "The latest main result pack uses the 3-sigma rule, following supervisor guidance. Concretely, the windows are ordered chronologically and the first 80 percent are used for model fitting. After training, the model reconstructs all retained windows, the total reconstruction error is computed as the mean squared difference across all channels and time steps, and the anomaly threshold is estimated only from the training subset. Under the 3-sigma rule, a window is flagged when its total reconstruction error exceeds the training mean plus three training standard deviations. The same logic is also applied channel-wise so that supply, return, and flow-specific reconstruction errors can be compared afterward. The thesis should discuss that neither threshold is uniformly stricter across all sheets; the difference depends on the shape of the training reconstruction-error distribution [11, 17, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "A second important design choice is that the windows are split chronologically rather than randomly. This means the model is fitted on the earlier portion of the retained history and then evaluated on later periods. The purpose is not only statistical hygiene. It also reflects the intended operational use case, where a detector trained on historical data will later be applied to new incoming windows. A random split would mix early and late behaviour and make the evaluation less representative of prospective monitoring.",
            "A second important design choice is that the windows are split chronologically rather than randomly. This means the model is fitted on the earlier portion of the retained history and then evaluated on later periods. The purpose is not only statistical hygiene. It also reflects the intended operational use case, where a detector trained on historical data will later be applied to new incoming windows. A random split would mix early and late behaviour and make the evaluation less representative of prospective monitoring. This choice is also consistent with the broader concern in anomaly-detection evaluation that unrealistic sampling protocols can overstate performance or obscure deployment-relevant behavior [11, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "A second important design choice is that the windows are split chronologically rather than randomly.",
            "A second important design choice is that the windows are split chronologically rather than randomly. This means the model is fitted on the earlier portion of the retained history and then evaluated on later periods. The purpose is not only statistical hygiene. It also reflects the intended operational use case, where a detector trained on historical data will later be applied to new incoming windows. A random split would mix early and late behaviour and make the evaluation less representative of prospective monitoring. This choice is also consistent with the broader concern in anomaly-detection evaluation that unrealistic sampling protocols can overstate performance or obscure deployment-relevant behavior [11, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The thresholding stage should be understood as a calibration step rather than a separate detector. The autoencoder first produces a continuous reconstruction-error score for every retained window. The threshold then converts that score into a review decision. This distinction matters because the scientific question is not only whether the model can rank unusual windows, but also whether the chosen cutoff produces a manageable and interpretable alert set under realistic low-label conditions.",
            "The thresholding stage should be understood as a calibration step rather than a separate detector. The autoencoder first produces a continuous reconstruction-error score for every retained window. The threshold then converts that score into a review decision. This distinction matters because the scientific question is not only whether the model can rank unusual windows, but also whether the chosen cutoff produces a manageable and interpretable alert set under realistic low-label conditions [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The thresholding stage should be understood as a calibration step rather than a separate detector.",
            "The thresholding stage should be understood as a calibration step rather than a separate detector. The autoencoder first produces a continuous reconstruction-error score for every retained window. The threshold then converts that score into a review decision. This distinction matters because the scientific question is not only whether the model can rank unusual windows, but also whether the chosen cutoff produces a manageable and interpretable alert set under realistic low-label conditions [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The comparison between p99 and 3-sigma is useful for precisely this reason. The p99 rule is distribution-free in the sense that it depends only on the empirical upper tail of the training errors, while the 3-sigma rule depends on the training mean and spread. If the error distribution is compact and roughly symmetric, the rules may behave similarly. If the error distribution is skewed or has a heavy right tail, the resulting anomaly counts can diverge substantially. The thesis therefore treats threshold choice as part of the method design, not as a cosmetic post-processing detail.",
            "The comparison between p99 and 3-sigma is useful for precisely this reason. The p99 rule is distribution-free in the sense that it depends only on the empirical upper tail of the training errors, while the 3-sigma rule depends on the training mean and spread. If the error distribution is compact and roughly symmetric, the rules may behave similarly. If the error distribution is skewed or has a heavy right tail, the resulting anomaly counts can diverge substantially. The thesis therefore treats threshold choice as part of the method design, not as a cosmetic post-processing detail [11, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The comparison between p99 and 3-sigma is useful for precisely this reason.",
            "The comparison between p99 and 3-sigma is useful for precisely this reason. The p99 rule is distribution-free in the sense that it depends only on the empirical upper tail of the training errors, while the 3-sigma rule depends on the training mean and spread. If the error distribution is compact and roughly symmetric, the rules may behave similarly. If the error distribution is skewed or has a heavy right tail, the resulting anomaly counts can diverge substantially. The thesis therefore treats threshold choice as part of the method design, not as a cosmetic post-processing detail [11, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric. The first layer is internal model behavior: reconstruction-error distributions, threshold sensitivity, and the stability of dominant-feature assignments. The second layer is engineering comparison: overlap with the low delta-T baseline and inspection of supply, return, and flow behavior in the top anomaly windows. The third layer is cross-building consistency: whether different sheets produce qualitatively different but still interpretable anomaly families under the same pipeline. The fourth and final layer is expert interpretation, where the outputs are reviewed with the supervisor and later compared with live operational context.",
            "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric. The first layer is internal model behavior: reconstruction-error distributions, threshold sensitivity, and the stability of dominant-feature assignments. The second layer is engineering comparison: overlap with the low delta-T baseline and inspection of supply, return, and flow behavior in the top anomaly windows. The third layer is cross-building consistency: whether different sheets produce qualitatively different but still interpretable anomaly families under the same pipeline. The fourth and final layer is expert interpretation, where the outputs are reviewed with the supervisor and later compared with live operational context. This evaluation structure is intentionally aligned with established warnings that unsupervised anomaly detection cannot be judged responsibly by a single score when labels are weak or absent [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric.",
            "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric. The first layer is internal model behavior: reconstruction-error distributions, threshold sensitivity, and the stability of dominant-feature assignments. The second layer is engineering comparison: overlap with the low delta-T baseline and inspection of supply, return, and flow behavior in the top anomaly windows. The third layer is cross-building consistency: whether different sheets produce qualitatively different but still interpretable anomaly families under the same pipeline. The fourth and final layer is expert interpretation, where the outputs are reviewed with the supervisor and later compared with live operational context. This evaluation structure is intentionally aligned with established warnings that unsupervised anomaly detection cannot be judged responsibly by a single score when labels are weak or absent [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "This evaluation strategy is intentionally aligned with the data conditions of the thesis. In a fully labelled study, one would normally report fault-detection metrics against confirmed events. In the present work, the more defensible question is whether the method produces a manageable and physically interpretable anomaly set that is strong enough to justify later prospective testing. The thesis therefore treats interpretability, comparative consistency, and operational reviewability as primary evaluation targets at this stage.",
            "This evaluation strategy is intentionally aligned with the data conditions of the thesis. In a fully labelled study, one would normally report fault-detection metrics against confirmed events. In the present work, the more defensible question is whether the method produces a manageable and physically interpretable anomaly set that is strong enough to justify later prospective testing. The thesis therefore treats interpretability, comparative consistency, and operational reviewability as primary evaluation targets at this stage [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "This evaluation strategy is intentionally aligned with the data conditions of the thesis.",
            "This evaluation strategy is intentionally aligned with the data conditions of the thesis. In a fully labelled study, one would normally report fault-detection metrics against confirmed events. In the present work, the more defensible question is whether the method produces a manageable and physically interpretable anomaly set that is strong enough to justify later prospective testing. The thesis therefore treats interpretability, comparative consistency, and operational reviewability as primary evaluation targets at this stage [11, 12, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score.",
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score. In anomaly-detection practice, however, such clean labels are often unavailable, incomplete, or expensive to obtain, which is one reason classical anomaly and novelty-detection literature continues to treat unsupervised formulations as practically important rather than merely provisional [10, 12, 13, 22].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "This makes district-heating monitoring an inherently multivariate problem:",
            "District-heating systems distribute thermal energy from centralized production to connected buildings through a shared network of pipes, heat exchangers, and local substations. At substation level, supply temperature, return temperature, flow, and power together provide a partial description of how efficiently heat is transferred from the network side to the building side. This makes district-heating monitoring an inherently multivariate problem: inefficient operation may appear as poor temperature separation, elevated return temperature, unstable flow behaviour, or some combination of these effects [19, 21].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "In anomaly-detection practice, however, such clean labels are often unavailable, incomplete, or expensive to obtain",
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score. In anomaly-detection practice, however, such clean labels are often unavailable, incomplete, or expensive to obtain. Classical anomaly and novelty-detection surveys make clear why unsupervised formulations therefore remain practically important [10, 12]. Older outlier-detection work provides the statistical background for that same problem setting [22].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The sustainability motivation of this thesis is direct.",
            "The sustainability motivation of this thesis is direct. District-heating systems are most effective when connected substations extract heat efficiently and return cooler water to the network. Poor control, hidden faults, or persistently inefficient operating periods can increase return temperature, reduce overall network efficiency, and make heat distribution less effective for the rest of the connected system [19, 20]. Better monitoring therefore has a practical sustainability role: it can help prioritize the building periods where wasted energy, poor control behaviour, or maintenance-relevant inefficiency are most likely to occur.",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The practical motivation is strong:",
            "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3]. The practical motivation is strong. Poor substation behaviour can increase return temperature and reduce network efficiency [19, 20]. District-heating performance also matters at system level because efficient substations support the broader energy and decarbonization role of heat networks [21]. A usable thesis method therefore has to do more than produce a score. It has to isolate windows that can be discussed in engineering terms and reviewed against the original signals.",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "In practical monitoring, low supply-return temperature difference",
            "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations [19]. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour [5, 6]. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns. This is one reason recent district-heating research has increasingly combined physical intuition with data-driven modelling. Simple rules remain useful as references, but they are too narrow to represent the full range of possible substation faults or inefficient operating regimes [21].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "In anomaly-detection practice, however, such clean labels are often unavailable",
            "A useful distinction for this thesis is the difference between supervised and unsupervised fault detection. In a supervised setting, the training data contain reliable labels that state which observations correspond to known fault classes and which correspond to normal operation. A supervised model therefore learns a direct mapping from measured signals to predefined labels. This is attractive when labels are abundant and trustworthy, because the resulting performance can be evaluated with standard metrics such as accuracy, precision, recall, and F1-score. In anomaly-detection practice, however, such clean labels are often unavailable, incomplete, or expensive to obtain. Classical anomaly and novelty-detection surveys make clear why unsupervised formulations therefore remain practically important [10, 12]. Older outlier-detection work provides the statistical background for that same problem setting [22].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "The thesis sits at the intersection of three research lines.",
            "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12]. Older outlier-detection work provides the statistical framing behind that problem class [22]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9]. Later autoencoder-based and sequence-based studies show how this idea is implemented in practice [14, 15, 16, 17]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance. In this thesis, that line of work is represented by HEAT [1], by data-driven grouping of operational behavior [6], by neighborhood-based anomaly detection [5], and by more recent service-validated evaluation work [7].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "This architecture was chosen as a conservative baseline:",
            "The current architecture is a compact 1D convolutional autoencoder. Each 24-hour input window is represented as a three-channel sequence of length 96. The encoder first applies a one-dimensional convolution with 16 output channels, kernel size 5, and padding 2, followed by a ReLU activation and max pooling by a factor of 2. A second convolution maps the signal to 16 latent channels with the same kernel size and padding, again followed by ReLU and max pooling. After the two pooling operations, the temporal resolution has been reduced from 96 to 24 time steps, so the latent representation is a compressed multichannel summary of the daily pattern. The decoder then uses two transposed convolutions with stride 2 to upsample the latent signal back to the original sequence length and reconstruct the three input channels. This architecture was chosen as a conservative baseline. The basic autoencoder idea follows Hinton and Salakhutdinov [4]. Autoencoder-based anomaly detection has since been used by Sakurada and Yairi [15] and extended to richer multivariate settings by Zong et al. [16]. Sequence reconstruction for multivariate anomaly detection is also a standard design choice in Malhotra et al. [14]. A broader review of such detectors is given by Belay et al. [17].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "neither threshold is uniformly stricter across all sheets",
            "The latest main result pack uses the 3-sigma rule, following supervisor guidance. Concretely, the windows are ordered chronologically and the first 80 percent are used for model fitting. After training, the model reconstructs all retained windows, the total reconstruction error is computed as the mean squared difference across all channels and time steps, and the anomaly threshold is estimated only from the training subset. Under the 3-sigma rule, a window is flagged when its total reconstruction error exceeds the training mean plus three training standard deviations. The same logic is also applied channel-wise so that supply, return, and flow-specific reconstruction errors can be compared afterward. Neither threshold is uniformly stricter across all sheets. That depends on the shape of the training reconstruction-error distribution, which is consistent with the evaluation concerns discussed by Campos et al. [11] and by Zimek and Filzmoser [23]. Belay et al. also note that score behavior and thresholding are central practical issues in multivariate time-series anomaly detection [17].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "clustering is supportive rather than central in the final pipeline",
            "In the final pipeline, clustering is supportive rather than central. Operating-regime clustering is applied to all retained windows in order to describe common daily behaviour patterns. Anomaly-only clustering is applied after detection and groups only the flagged windows according to their feature summaries or per-feature reconstruction-error structure. The point is not to replace the anomaly score with a cluster label, but to help the supervisor and reader see whether the flagged windows separate into recurring anomaly families such as mostly supply-driven, mostly return-driven, or mostly flow-driven behaviour.",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "difference from benchmark-style research",
            "This difference from benchmark-style research is important. In a labelled benchmark study, the main question is usually whether one detector achieves better accuracy, recall, or F-score than another under a fixed protocol. In this thesis, the central question is different: whether the detector can convert weakly structured historical data into a manageable set of reviewable windows, each supported by signal plots, per-feature error attribution, and comparison against simple engineering references. That is a narrower but still meaningful research contribution because it addresses the decision conditions under which many industrial monitoring projects actually begin.",
        )
    except ValueError:
        pass
    remove_paragraphs_containing(
        body,
        [
            "A further methodological extension is to incorporate contextual variables that explain why expected operating behavior changes over time.",
        ],
    )
    try:
        set_paragraph_containing(
            body,
            "This evaluation structure is intentionally aligned with established warnings",
            "Because explicit fault labels are largely unavailable, the thesis uses a layered evaluation strategy rather than a single benchmark metric. The first layer is internal model behavior: reconstruction-error distributions, threshold sensitivity, and the stability of dominant-feature assignments. The second layer is engineering comparison: overlap with the low delta-T baseline and inspection of supply, return, and flow behavior in the top anomaly windows. The third layer is cross-building consistency: whether different sheets produce qualitatively different but still interpretable anomaly families under the same pipeline. The fourth and final layer is expert interpretation, where the outputs are reviewed with the supervisor and later compared with live operational context. This evaluation structure is intentionally aligned with established warnings that unsupervised anomaly detection cannot be judged responsibly by a single score when labels are weak or absent. That caution is emphasized in the outlier-evaluation study of Campos et al. [11] and in the novelty-detection review of Pimentel et al. [12]. Zimek and Filzmoser make the same point from an outlier-detection perspective [23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_containing(
            body,
            "to incorporate contextual variables such as outdoor temperature, season, month, and day type",
            "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. A second priority is to refine threshold selection once live alert volume can be judged operationally rather than only historically. A third priority is to strengthen validation by collecting any maintenance, alarm, or manually reviewed event records that can be aligned with the flagged windows. Beyond deployment, a natural continuation of the thesis would be to broaden the building set as cleaner data become available and to compare the current joint autoencoder with alternative architectures or per-feature detectors under the same review workflow. Another extension is to incorporate contextual variables such as outdoor temperature, season, month, and day type. Their relevance follows from the broader system role of district heating in seasonal energy supply [19, 21]. The efficiency perspective in Heat Roadmap Europe points in the same direction [20]. Such context could reduce false positives by helping the detector separate genuinely abnormal behavior from expected seasonal regime shifts. If richer live measurements become available later, additional variables such as pressure, valve position, or occupancy-related proxies could also support more precise anomaly interpretation.",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The present project does not have that kind of labelled dataset. Most windows in the historical data are unlabeled, and even suspicious periods are usually not tied to a confirmed fault record. For that reason, the problem is better framed as unsupervised anomaly detection. In an unsupervised setting, the model is trained to capture the structure of historical normal-looking behaviour without being told explicit fault classes. A high anomaly score does not mean that a specific known fault has been diagnosed. It means that the operating pattern is sufficiently different from the learned historical structure that it deserves review. This distinction matters for the whole thesis: the contribution is not a supervised classifier of named faults, but a ranking and interpretation workflow for unusual operating windows.",
            "The present project does not have that kind of labelled dataset. Most windows in the historical data are unlabeled, and even suspicious periods are usually not tied to a confirmed fault record. For that reason, the problem is better framed as unsupervised anomaly detection. In an unsupervised setting, the model is trained to capture the structure of historical normal-looking behaviour without being told explicit fault classes. A high anomaly score does not mean that a specific known fault has been diagnosed. It means that the operating pattern is sufficiently different from the learned historical structure that it deserves review. This distinction matters for the whole thesis: the contribution is not a supervised classifier of named faults, but a ranking and interpretation workflow for unusual operating windows. The evaluation consequence is equally important. Without stable labels, one must rely more heavily on score distributions, qualitative inspection, expert review, and careful discussion of what an anomaly flag actually means, which is fully consistent with the cautions raised in unsupervised outlier-evaluation research [11, 23].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12, 13]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9, 14]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance [1, 5, 6, 7].",
            "The thesis sits at the intersection of three research lines. The first is classical anomaly and novelty detection, where the main question is how to identify rare or abnormal observations without assuming that all possible fault classes are known in advance [10, 12, 13, 22]. The second is unsupervised time-series anomaly detection, where reconstruction models are used to learn normal temporal structure and assign anomaly scores from reconstruction failure [8, 9, 14, 15, 16, 17]. The third is district-heating-specific monitoring, where physical interpretation, efficiency loss, and operational validation matter as much as statistical detection performance [1, 5, 6, 7, 19, 20, 21].",
        )
    except ValueError:
        pass
    try:
        set_paragraph_text(
            body,
            "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. A second priority is to refine threshold selection once live alert volume can be judged operationally rather than only historically. A third priority is to strengthen validation by collecting any maintenance, alarm, or manually reviewed event records that can be aligned with the flagged windows. Beyond deployment, a natural continuation of the thesis would be to broaden the building set as cleaner data become available and to compare the current joint autoencoder with alternative architectures or per-feature detectors under the same review workflow.",
            "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. A second priority is to refine threshold selection once live alert volume can be judged operationally rather than only historically. A third priority is to strengthen validation by collecting any maintenance, alarm, or manually reviewed event records that can be aligned with the flagged windows. Beyond deployment, a natural continuation of the thesis would be to broaden the building set as cleaner data become available, to compare the current joint autoencoder with alternative architectures or per-feature detectors under the same review workflow, and to incorporate contextual variables such as outdoor temperature, season, month, and day type [19, 20, 21]. Such context could reduce false positives by helping the detector separate genuinely abnormal behavior from expected seasonal regime shifts. If richer live measurements become available later, additional variables such as pressure, valve position, or occupancy-related proxies could also support more precise anomaly interpretation.",
        )
    except ValueError:
        pass
    try:
        find_para_index(body, "7.1 Future work")
    except ValueError:
        try:
            insert_block(
                body,
                "Acknowledgments",
                [
                    make_paragraph("7.1 Future work", "Heading2"),
                    make_paragraph(
                        "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. A second priority is to refine threshold selection once live alert volume can be judged operationally rather than only historically. A third priority is to strengthen validation by collecting any maintenance, alarm, or manually reviewed event records that can be aligned with the flagged windows. Beyond deployment, a natural continuation of the thesis would be to broaden the building set as cleaner data become available and to compare the current joint autoencoder with alternative architectures or per-feature detectors under the same review workflow.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "A further methodological extension is to incorporate contextual variables that explain why expected operating behavior changes over time. Outdoor temperature, season, month, and day type are natural candidates because district-heating demand is strongly weather-dependent and because the same substation can behave differently in winter, shoulder-season, and milder operating periods [19, 20, 21]. Including such context could reduce false positives by helping the detector separate genuinely abnormal behavior from expected seasonal regime shifts. If richer live measurements become available later, additional variables such as pressure, valve position, or occupancy-related proxies could also support more precise anomaly interpretation.",
                        "BodyText",
                    ),
                ],
            )
        except ValueError:
            pass


def harmonize_building_scope(body: ET.Element) -> None:
    try:
        set_paragraph_text(body, "Table 1: Five-building result summary under the 3-sigma threshold.", "Table 1: Seven-building result summary under the 3-sigma threshold.")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "The clearest current anomaly-typing view is the dominant-feature analysis. Across the five-building set, the anomalies are mainly flow-dominant and return-dominant, with Hostatgeria Underfloor providing the clearest supply-dominant case. This indicates that the autoencoder is detecting multiple anomaly families rather than only one repeated signature.", "The clearest current anomaly-typing view is the dominant-feature analysis. Across the seven-building set, the anomalies are mainly flow-dominant and return-dominant, with Hostatgeria Underfloor providing the clearest supply-dominant case. This indicates that the autoencoder is detecting multiple anomaly families rather than only one repeated signature.")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "Only one sheet, cons_hostatgeria_underfloor_hea, shows strong overlap between top reviewed autoencoder anomalies and the low delta-T baseline. This should be interpreted carefully. It makes underfloor heating the strongest validated case, but the absence of overlap in the other four buildings does not invalidate the autoencoder. It instead suggests that many detected anomalies are not low delta-T events and therefore require interpretation through dominant feature, flow-channel behavior, and domain review.", "Only one sheet, cons_hostatgeria_underfloor_hea, shows strong overlap between top reviewed autoencoder anomalies and the low delta-T baseline. This should be interpreted carefully. It makes underfloor heating the strongest validated case, but the absence of overlap in the other six buildings does not invalidate the autoencoder. It instead suggests that many detected anomalies are not low delta-T events and therefore require interpretation through dominant feature, flow-channel behavior, and domain review.")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "Interpretation. This figure compares usable window count, flagged anomaly count, and flagged anomaly rate across the seven selected buildings. The retained-window count shows how much usable data each building contributes, the flagged-window count shows the absolute anomaly volume, and the flagged rate shows the relative density of anomalies after accounting for dataset size.", "Interpretation. This figure compares usable window count, flagged anomaly count, and flagged anomaly rate across the seven selected buildings. The retained-window count shows how much usable data each building contributes, the flagged-window count shows the absolute anomaly volume, and the flagged rate shows the relative density of anomalies after accounting for dataset size. The retained-window differences arise from unequal raw-data coverage, missing-data patterns, inactive-heating periods, and the fact that some windows fail the active-share or completeness thresholds during preprocessing.")
    except ValueError:
        pass

    try:
        safe_remove_between(body, "3.5 Five-building thesis scope", "4 Method")
        block = [
            make_paragraph("3.5 Result-set scope", "Heading2"),
            make_paragraph("The thesis result set now includes all seven modeled heating-consumer sheets:", "BodyText"),
            make_paragraph("Abat Cisneros", "BodyText"),
            make_paragraph("Abat Garriga", "BodyText"),
            make_paragraph("Abat Marcet", "BodyText"),
            make_paragraph("Abat Oliba", "BodyText"),
            make_paragraph("Hostatgeria DHW Radiators", "BodyText"),
            make_paragraph("Hostatgeria Underfloor", "BodyText"),
            make_paragraph("Nostra Senyora", "BodyText"),
            make_paragraph("For most result figures, all seven buildings are kept in order to preserve the full comparative picture. The only exception is the reconstruction-error timeline comparison, where Abat Oliba and Hostatgeria Underfloor are omitted because long faulty constant-value stretches make that specific plot harder to interpret. They are still retained everywhere else in the thesis result set.", "BodyText"),
        ]
        insert_block(body, "4 Method", block)
    except ValueError:
        pass


def deduplicate_results_block(body: ET.Element) -> None:
    def remove_extra_copies(start_text: str, end_text: str) -> None:
        while True:
            starts = find_all_para_indices(body, start_text)
            if len(starts) < 2:
                return
            try:
                end_idx = find_para_index(body, end_text)
            except ValueError:
                return
            second_start = starts[1]
            for child in list(body)[second_start:end_idx]:
                body.remove(child)

    remove_extra_copies(
        "Figure 3 summarizes the retained-window counts, flagged anomalies, and anomaly rates across the seven selected buildings.",
        "5.2 Dominant-feature interpretation",
    )
    remove_extra_copies(
        "Figure 12 shows which feature dominates the anomaly score for each building.",
        "5.3 Low delta-T overlap",
    )
    remove_extra_copies(
        "Figure 14 compares the number of autoencoder anomalies with the engineering low delta-T baseline.",
        "5.4 Operating regimes",
    )
    remove_extra_copies(
        "Figure 16 summarizes the operating-regime cluster occupancy for the seven selected buildings.",
        "5.5 Threshold comparison",
    )
    remove_extra_copies(
        "Figure 17 shows how anomalies are distributed between the training period and the later chronological period.",
        "6 Discussion",
    )


def deduplicate_scope_block(body: ET.Element) -> None:
    starts = find_all_para_indices(body, "3.5 Result-set scope")
    if len(starts) < 2:
        return
    try:
        end_idx = find_para_index(body, "4 Method")
    except ValueError:
        return
    second_start = starts[1]
    for child in list(body)[second_start:end_idx]:
        body.remove(child)
    try:
        set_paragraph_text(
            body,
            "The next stage of the work is to apply the current detector to live data and use that prospective period as an operational evaluation step. That stage will make it possible to compare flagged windows against ongoing system behaviour, operator observations, and any available maintenance or event context. Beyond deployment, a natural continuation of the thesis would be to refine threshold selection, broaden the building set as cleaner data become available, and investigate whether a stronger label base could support more formal validation in future work.",
            "The transition to live-data evaluation is discussed further in Section 7.1.",
        )
    except ValueError:
        pass


def update_results_table(doc_root: ET.Element) -> None:
    tables = doc_root.findall(".//w:tbl", NS)
    if not tables:
        return
    table = tables[0]
    rows = table.findall("./w:tr", NS)
    if len(rows) < 2:
        return
    template = rows[1]
    for row in rows[1:]:
        table.remove(row)

    summary = pd.read_csv(ROOT / "Results" / "tables" / "supervisor_results_sheet_2026-06-07.csv")
    feature_map = {
        "supply_temp_c": "Supply",
        "return_temp_c": "Return",
        "stabilized_flow_log_feature": "Flow",
    }
    for _, rec in summary.iterrows():
        row = copy.deepcopy(template)
        values = [
            str(rec["display_label"]),
            f"{int(rec['windows'])}",
            f"{int(rec['flagged_windows'])}",
            f"{100.0 * float(rec['flagged_rate']):.2f}",
            feature_map.get(str(rec["top_dominant_anomalous_feature"]), str(rec["top_dominant_anomalous_feature"])),
        ]
        cells = row.findall("./w:tc", NS)
        for cell, value in zip(cells, values, strict=False):
            texts = cell.findall(".//w:t", NS)
            if texts:
                texts[0].text = value
                for t in texts[1:]:
                    t.text = ""
        table.append(row)


def ensure_supplemental_result_figures(body: ET.Element, rels_root: ET.Element, files: dict[str, bytes]) -> None:
    docpr_id = 9000
    try:
        find_para_index(body, "Figure 3A summarizes the median daily retained-window profiles for all seven buildings.")
    except ValueError:
        docpr_id = add_image_block(
            body, rels_root, files, "Figure 4 shows the reconstruction-error timelines that underpin the anomaly counts reported in this section.",
            "Figure 3A summarizes the median daily retained-window profiles for all seven buildings.",
            FIGURE_FILES["profiles"],
            "Figure 3A. Median daily retained-window profiles for the seven selected buildings. Supply and return temperatures are shown with 10th-90th percentile bands, and flow is shown on the secondary axis with its own 10th-90th percentile band.",
            "Source: author-generated figure based on all retained 24-hour windows before anomaly filtering.",
            "Interpretation. This figure summarizes how the seven buildings typically behave across the day before focusing on anomalies. It is useful for understanding building-to-building differences in thermal level, return behaviour, and flow magnitude, and therefore helps explain why the retained-window counts and anomaly rates are not identical across sheets.",
            docpr_id,
        )
    try:
        find_para_index(body, "Figure 11A compares observed and reconstructed signals for the top Garriga anomaly window.")
    except ValueError:
        docpr_id = add_image_block(
            body, rels_root, files, "5.2 Dominant-feature interpretation",
            "Figure 11A compares observed and reconstructed signals for the top Garriga anomaly window.",
            FIGURE_FILES["overlay_garriga"],
            "Figure 11A. Observed versus reconstructed signals for the top Abat Garriga anomaly window.",
            "Source: author-generated figure from the trained joint autoencoder and the highest-scoring Garriga anomaly window.",
            "Interpretation. This figure explains why the Garriga example is classified as return-dominant even though the flow trace looks visually active. Dominance is assigned by reconstruction error, not by raw amplitude. The model reproduces the flow channel comparatively well, while the return channel shows the largest mismatch between observed and reconstructed behaviour.",
            docpr_id,
        )
        docpr_id = add_image_block(
            body, rels_root, files, "5.2 Dominant-feature interpretation",
            "Figure 11B compares observed and reconstructed signals for the strongest Underfloor anomaly window.",
            FIGURE_FILES["overlay_underfloor"],
            "Figure 11B. Observed versus reconstructed signals for the top Hostatgeria Underfloor anomaly window.",
            "Source: author-generated figure from the trained joint autoencoder and the highest-scoring Underfloor anomaly window.",
            "Interpretation. This figure shows the model failing much more strongly on the supply channel than on the other channels, which is why the Underfloor case remains the clearest supply-dominant thesis example. It also makes the reconstruction-based anomaly logic more concrete than the raw signal plot alone.",
            docpr_id,
        )
    try:
        find_para_index(body, "Figure 11C compares the joint Underfloor autoencoder with univariate alternatives trained on individual channels.")
    except ValueError:
        docpr_id = add_image_block(
            body, rels_root, files, "5.2 Dominant-feature interpretation",
            "Figure 11C compares the joint Underfloor autoencoder with univariate alternatives trained on individual channels.",
            FIGURE_FILES["joint_vs_univariate_underfloor"],
            "Figure 11C. Joint-versus-univariate comparison for Hostatgeria Underfloor, using flagged-window rate and median reconstruction MSE.",
            "Source: author-generated comparison between the joint three-channel autoencoder and single-channel autoencoders for the Underfloor sheet.",
            "Interpretation. This figure shows that the single-channel alternatives do not behave identically. Return-only reconstruction yields the highest flagged-window rate, while the flow-only model gives the lowest median reconstruction error. The joint model remains between those extremes and is kept as the main thesis detector because it preserves cross-channel context instead of forcing the anomaly decision to come from only one signal at a time.",
            docpr_id,
        )
    try:
        find_para_index(body, "Figure 16A visualizes the training-error distributions behind the 3-sigma thresholds across sheets.")
    except ValueError:
        add_image_block(
            body, rels_root, files, "5.6 Train-test split and anomaly timing",
            "Figure 16A visualizes the training-error distributions behind the 3-sigma thresholds across sheets.",
            FIGURE_FILES["threshold_dist"],
            "Figure 16A. Training reconstruction-error distribution by sheet with threshold markers.",
            "Source: author-generated figure based on training-window reconstruction errors under the 3-sigma evaluation pack.",
            "Interpretation. This figure complements Figure 2 by comparing the training-error distributions sheet by sheet. It helps explain why the same threshold rule does not behave uniformly across buildings: some sheets have compact error bands, while others have wider or more skewed tails.",
            docpr_id,
        )


def update_citations(body: ET.Element) -> None:
    replacements = {
        "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset.": "District-heating substations operate continuously and generate large amounts of operational time-series data, but confirmed fault labels are often sparse, incomplete, or entirely unavailable. This creates a practical monitoring problem. Operators still need to detect unusual or inefficient behaviour, yet a conventional supervised classification approach is difficult to justify when the ground truth is weak. In this setting, anomaly detection becomes a pragmatic alternative because it can identify windows that deviate from historically learned normal behaviour without requiring a fully labelled fault dataset [2, 3].",
            "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer.": "The thesis therefore aims to build and evaluate an anomaly-detection pipeline that can identify physically interpretable abnormal operating periods from historical district-heating data and later be transferred to live data as it becomes available. The work is motivated by the HEAT paper, which combines encoder-based representation learning and clustering for fault detection in district-heating substations [1]. However, the available KTH thesis dataset differs from that reference setting in two important ways. First, the network is much smaller, which reduces the statistical strength of pure peer-group comparison. Second, the historical coverage is longer, which makes per-substation temporal modelling more attractive than relying only on network-wide clustering. For this reason, the thesis treats reconstruction-based anomaly detection as the primary method and uses clustering mainly as a secondary interpretation layer.",
        "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns.": "District-heating systems transport thermal energy from a central production source to buildings through a pipe network and local substations. At the substation level, measurements such as supply temperature, return temperature, flow, and power provide indirect evidence about how effectively heat is being transferred to the building side. When the system behaves abnormally, that abnormality may appear as an unusual temperature profile, poor separation between supply and return, unstable flow behaviour, or some combination of these effects. In practical monitoring, low supply-return temperature difference, or low delta-T, is often used as an initial engineering warning sign because it can indicate poor heat extraction, inefficient operation, or high return-temperature behaviour. However, low delta-T only captures one narrow anomaly family and cannot explain all relevant abnormal operating patterns [5, 6].",
        "The HEAT paper proposes a hierarchical, encoder-assisted clustering approach for fault detection in district-heating substations. Its central idea is to transform time-series windows into a compact representation and then use clustering to construct local peer groups that can be compared against one another. This is a sensible design in a large network with many similar substations, because the method can exploit similarities and differences between multiple operating units instead of relying only on the history of a single site.": "The HEAT paper proposes a hierarchical, encoder-assisted clustering approach for fault detection in district-heating substations [1]. Its central idea is to transform time-series windows into a compact representation and then use clustering to construct local peer groups that can be compared against one another. This is a sensible design in a large network with many similar substations, because the method can exploit similarities and differences between multiple operating units instead of relying only on the history of a single site.",
        "An autoencoder is a neural network trained to reproduce its own input at the output layer. In the thesis pipeline, each input is a 24-hour multivariate window containing three synchronized channels: supply temperature, return temperature, and a flow-related channel. The encoder compresses the window into a latent representation that retains the most important structure, and the decoder uses that representation to reconstruct the original signal sequence. If a window follows patterns that are common in the historical training data, the model usually reconstructs it well and the reconstruction error remains low. If a window contains an unusual temporal pattern, one or more channels are reconstructed less accurately and the reconstruction error increases. This makes the reconstruction error a natural anomaly score in situations where explicit fault labels are not available.": "An autoencoder is a neural network trained to reproduce its own input at the output layer [4]. In the thesis pipeline, each input is a 24-hour multivariate window containing three synchronized channels: supply temperature, return temperature, and a flow-related channel. The encoder compresses the window into a latent representation that retains the most important structure, and the decoder uses that representation to reconstruct the original signal sequence. If a window follows patterns that are common in the historical training data, the model usually reconstructs it well and the reconstruction error remains low. If a window contains an unusual temporal pattern, one or more channels are reconstructed less accurately and the reconstruction error increases. This makes the reconstruction error a natural anomaly score in situations where explicit fault labels are not available.",
    }
    for old, new in replacements.items():
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass


def replace_references(body: ET.Element) -> None:
    appendix = "Appendix A: Writing notes"
    try:
        remove_between(body, "[1] HEAT: Hierarchical-constrained Encoder-Assisted Time series clustering for fault detection in district heating substations, Energy and AI, 2025.", appendix)
    except ValueError:
        safe_remove_from(body, "[1] HEAT: Hierarchical-constrained Encoder-Assisted Time series clustering for fault detection in district heating substations, Energy and AI, 2025.")
    refs = [
        "[1] HEAT: Hierarchical-constrained Encoder-Assisted Time series clustering for fault detection in district heating substations, Energy and AI, 2025.",
        "[2] R. Chalapathy and S. Chawla, Deep Learning for Anomaly Detection: A Survey, arXiv:1901.03407, 2019.",
        "[3] M. Jiang, C. Hou, A. Zheng, X. Hu, S. Han, H. Huang, X. He, P. S. Yu, and Y. Zhao, Weakly Supervised Anomaly Detection: A Survey, arXiv:2302.04549, 2023.",
        "[4] G. E. Hinton and R. R. Salakhutdinov, Reducing the Dimensionality of Data with Neural Networks, Science, vol. 313, no. 5786, pp. 504-507, 2006.",
        "[5] J. van Dreven, A. Cheddad, S. Alawadi, A. N. Ghazi, J. Al Koussa, and D. Vanhoudt, SHEDAD: SNN-Enhanced District Heating Anomaly Detection for Urban Substations, arXiv:2408.14499, 2024.",
        "[6] E. Calikus, S. Nowaczyk, A. Sant'Anna, H. Gadd, and S. Werner, A data-driven approach for discovering heat load patterns in district heating, arXiv:1901.04863, 2019.",
        "[7] C. M. A. Roelofs, E. Guevara Bastidas, T. Hugo, S. Faulstich, and A. Cadenbach, Enabling Predictive Maintenance in District Heating Substations: A Labelled Dataset and Fault Detection Evaluation Framework based on Service Data, arXiv:2511.14791, 2025.",
        "[8] N. Mejri, L. Lopez-Fuentes, K. Roy, P. Chernakov, E. Ghorbel, and D. Aouada, Unsupervised Anomaly Detection in Time-series: An Extensive Evaluation and Analysis of State-of-the-art Methods, arXiv:2212.03637, 2022.",
        "[9] T. Kieu, B. Yang, C. Guo, C. S. Jensen, Y. Zhao, F. Huang, and K. Zheng, Robust and Explainable Autoencoders for Unsupervised Time Series Outlier Detection, arXiv:2204.03341, 2022.",
        "[10] V. Chandola, A. Banerjee, and V. Kumar, Anomaly Detection: A Survey, ACM Computing Surveys, vol. 41, no. 3, article 15, 2009.",
        "[11] G. O. Campos, A. Zimek, J. Sander, R. J. G. B. Campello, and B. Micenkova, On the evaluation of unsupervised outlier detection: measures, datasets, and an empirical study, Data Mining and Knowledge Discovery, vol. 30, pp. 891-927, 2016.",
        "[12] M. A. F. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko, A review of novelty detection, Signal Processing, vol. 99, pp. 215-249, 2014.",
        "[13] M. Markou and S. Singh, Novelty detection: a review - part 1: statistical approaches, Signal Processing, vol. 83, no. 12, pp. 2481-2497, 2003.",
        "[14] P. Malhotra, L. Vig, G. Shroff, and P. Agarwal, LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection, Proceedings of the ICML 2016 Anomaly Detection Workshop, 2016.",
        "[15] M. Sakurada and T. Yairi, Anomaly Detection using Autoencoders with Nonlinear Dimensionality Reduction, Proceedings of the MLSDA 2014 2nd Workshop on Machine Learning for Sensory Data Analysis, 2014.",
        "[16] B. Zong, Q. Song, M. R. Min, W. Cheng, C. Lumezanu, D. Cho, and H. Chen, Deep Autoencoding Gaussian Mixture Model for Unsupervised Anomaly Detection, Proceedings of the 6th International Conference on Learning Representations Workshop Track, 2018.",
        "[17] M. A. Belay, S. S. Blakseth, A. Rasheed, and P. S. Rossi, Unsupervised Anomaly Detection for IoT-Based Multivariate Time Series: Existing Solutions, Performance Analysis and Future Directions, Sensors, vol. 23, no. 3, 2023.",
        "[18] All result figures in this thesis are author-generated from the historical district-heating dataset unless otherwise stated.",
        "[19] H. Lund, S. Werner, R. Wiltshire, S. Svendsen, J. E. Thorsen, F. Hvelplund, and B. V. Mathiesen, 4th Generation District Heating (4GDH): Integrating smart thermal grids into future sustainable energy systems, Energy, vol. 68, pp. 1-11, 2014.",
        "[20] D. Connolly, H. Lund, B. V. Mathiesen, S. Werner, B. Moller, U. Persson, T. Boermans, D. Trier, P. A. Ostergaard, and S. Nielsen, Heat Roadmap Europe: Combining district heating with heat savings to decarbonise the EU energy system, Energy Policy, vol. 65, pp. 475-489, 2014.",
        "[21] H. Lund, P. A. Ostergaard, D. Connolly, and B. V. Mathiesen, The status of 4th generation district heating: Research and results, Energy, vol. 164, pp. 147-159, 2018.",
        "[22] D. M. Hawkins, Identification of Outliers, London: Chapman and Hall, 1980.",
        "[23] A. Zimek and P. Filzmoser, There and back again: Outlier detection between statistical reasoning and data mining algorithms, WIREs Data Mining and Knowledge Discovery, vol. 8, no. 6, e1280, 2018.",
    ]
    try:
        insert_idx = find_para_index(body, appendix)
    except ValueError:
        insert_idx = len(list(body))
    for ref in refs:
        body.insert(insert_idx, make_paragraph(ref, "BodyText"))
        insert_idx += 1


def cleanup_known_intro_duplicates(body: ET.Element) -> None:
    paragraphs = [paragraph_text(p) for p in paragraph_children(body)]
    intro_has_new_structure = "1.1 Problem setting" in paragraphs and "1.2 Ethics and sustainability" in paragraphs
    if not intro_has_new_structure:
        return
    matches = []
    for child in list(body):
        if child.tag != qn("w", "p"):
            continue
        text = paragraph_text(child)
        if (
            "In district-heating terms, this matters because poor substation behaviour is not only a statistical irregularity."
            in text
            and "The thesis is therefore motivated by both data-analysis and energy-system concerns"
            in text
        ):
            matches.append(child)
    for child in matches:
        body.remove(child)


def finalize_supervisor_structure_updates(body: ET.Element) -> None:
    # Front matter
    remove_exact_paragraphs(body, ["Acknowledgments"])
    remove_paragraphs_containing(body, ["Acknowledgments to be completed"])
    try:
        insert_block(
            body,
            "List of Acronyms and Abbreviations",
            [
                make_paragraph("Acknowledgments", "Heading1"),
                make_paragraph("Acknowledgments to be completed.", "BodyText"),
            ],
        )
    except ValueError:
        pass
    remove_exact_paragraphs(body, ["Keywords"])
    remove_exact_paragraphs(
        body,
        [
            "district heating; anomaly detection; autoencoder; reconstruction error; time-series analysis",
            "fjärrvärme; anomalidetektion; autoencoder; rekonstruktionsfel; tidsserieanalys",
        ],
    )
    remove_paragraphs_containing(body, ["Keywords:", "Nyckelord:"])
    try:
        insert_block(
            body,
            "Acknowledgments",
            [
                make_paragraph("Keywords", "Heading1"),
                make_paragraph(
                    "district heating; anomaly detection; autoencoder; reconstruction error; time-series analysis",
                    "BodyText",
                ),
                make_paragraph(
                    "fjärrvärme; anomalidetektion; autoencoder; rekonstruktionsfel; tidsserieanalys",
                    "BodyText",
                ),
            ],
        )
    except ValueError:
        pass

    # Dataset section wording and numbering
    for old, new in [
        ("3 Dataset and preprocessing", "3 Data"),
        ("3.1 Available sources", "3.1 Dataset, source material, and variables"),
        ("3.3 Preprocessing decisions", "3.2 Preprocessing decisions"),
        ("3.4 Known limitations", "3.3 Known limitations"),
        ("3.5 Result-set scope", "3.4 Result-set scope"),
    ]:
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass
    remove_exact_paragraphs(body, ["3.2 Main measured variables"])
    remove_exact_paragraphs(
        body,
        [
            "The clustering methodology can also be written more explicitly. Two separate KMeans-based clustering paths are used in the project, both after feature standardization with StandardScaler and both using Euclidean distance in the standardized feature space. They differ in purpose and in the feature vectors being clustered."
        ],
    )
    while True:
        starts = find_all_para_indices(body, "3.4 Result-set scope")
        if len(starts) <= 1:
            break
        children = list(body)
        second_start = starts[1]
        end_idx = len(children)
        for idx in starts[2:]:
            if idx > second_start:
                end_idx = idx
                break
        else:
            try:
                method_idx = find_para_index(body, "4 Method")
                if method_idx > second_start:
                    end_idx = method_idx
            except ValueError:
                pass
        if end_idx <= second_start:
            break
        for child in children[second_start:end_idx]:
            body.remove(child)

    # Expand encoder methodology
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "A compact mathematical summary of the autoencoder is helpful here." not in text:
        try:
            insert_block(
                body,
                "Figure 1 gives a compact schematic of the reconstruction-based detector used throughout the thesis.",
                [
                    make_paragraph(
                        "A compact mathematical summary of the autoencoder is helpful here. Let x be one normalized input window with shape 3 x 96, where the rows correspond to supply temperature, return temperature, and flow, and the columns correspond to 15-minute samples across 24 hours. The encoder defines a mapping z = f_theta(x), where z has shape 16 x 24 after the two convolution-and-pooling stages. The decoder defines a reconstruction x_hat = g_phi(z), returning the latent representation to the original 3 x 96 shape.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "Training minimizes mean squared reconstruction loss on the chronological training subset. In simplified form, L = (1 / (3 x 96)) sum_c sum_t (x_(c,t) - x_hat_(c,t))^2. The model is therefore not trained to predict named faults. It is trained to reproduce recurrent normal-looking daily patterns. Windows that cannot be reconstructed well after training receive larger anomaly scores because they deviate from the temporal structure learned from the historical training windows.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "This representation is useful because the convolutional layers can learn short local motifs such as ramps, peaks, and short-lived co-movement between supply, return, and flow, while pooling compresses those motifs into a lower-resolution latent summary of the day. The latent tensor is therefore not interpreted directly as a physical variable. Its role is to retain enough information that the decoder reconstructs common operating behaviour accurately and fails more visibly on unusual windows.",
                        "BodyText",
                    ),
                ],
            )
        except ValueError:
            pass

    # Expand threshold theory
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "In mathematical terms, the 3-sigma threshold used in the final result pack is" not in text:
        try:
            insert_block(
                body,
                "Figure 2 shows the training reconstruction-error distributions used to compare the p99 and 3-sigma threshold rules.",
                [
                    make_paragraph(
                        "In mathematical terms, the 3-sigma threshold used in the final result pack is T = mu_train + 3 sigma_train, where mu_train is the mean reconstruction error on the training windows and sigma_train is the corresponding training standard deviation. A retained window i is flagged when its total reconstruction error e_i is greater than T. The rule is therefore fitted only from the historical training-error distribution and then applied consistently to both training and later windows.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "The 3-sigma rule is easy to explain and is commonly associated with outlier screening under approximately concentrated error distributions. It is not identical to the p99 threshold: p99 fixes the expected upper-tail fraction in the training set, while 3-sigma depends on both the mean and spread of the training errors. As a result, either rule can be stricter depending on whether the training-error distribution is compact, skewed, or contains a heavy tail.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "An interquartile-range threshold was also considered conceptually because it is a standard alternative when the error distribution is not close to normal. In that case, an upper threshold can be written as Q3 + k IQR, where IQR = Q3 - Q1. This thesis keeps the 3-sigma rule as the main reported threshold because it matches the supervisor's guidance and gives a transparent comparison across sheets, but the non-normal shape of some reconstruction-error distributions remains a limitation when interpreting alert volume.",
                        "BodyText",
                    ),
                ],
            )
        except ValueError:
            pass

    # Expand clustering methodology
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "For operating-regime clustering, each retained daily window is summarized by descriptive statistics" not in text:
        try:
            insert_block(
                body,
                "4.7 Evaluation strategy in a weak-label setting",
                [
                    make_paragraph(
                        "For operating-regime clustering, each retained daily window is summarized by descriptive statistics rather than by the raw 3 x 96 sequence. The feature vector contains supply median and standard deviation, return median and standard deviation, flow median and standard deviation, delta-T median, delta-T 5th percentile, delta-T minimum, and mean active fraction over the window. These features are standardized with StandardScaler before clustering so that no single variable dominates only because of its numerical scale.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "The operating-regime clustering then applies KMeans with k = 4 to the standardized daily summary vectors. A window feature vector z_i is assigned to the cluster whose centroid c_j minimizes squared Euclidean distance, that is, argmin_j ||z_i - c_j||_2^2. The resulting clusters are not interpreted as named physical fault classes. They are treated as recurring operating regimes that summarize how the retained windows populate the available feature space.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "The anomaly-only clustering follows the same KMeans logic but uses only windows already flagged by the autoencoder. Its feature vectors contain the same operating summaries plus total reconstruction MSE and per-feature reconstruction MSE. In the current implementation, KMeans with k = 3 is used for this second path. This means the anomaly-only clustering is influenced both by raw operating behavior and by how the reconstruction model failed. It is therefore better suited to anomaly-family interpretation than to generic operating-regime description.",
                        "BodyText",
                    ),
                ],
            )
        except ValueError:
            pass
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "The KMeans objective can be written as minimizing the within-cluster sum of squared distances" not in text:
        try:
            insert_block(
                body,
                "4.7 Evaluation strategy in a weak-label setting",
                [
                    make_paragraph(
                        "The KMeans objective can be written as minimizing the within-cluster sum of squared distances, J = sum_j sum_(z_i in C_j) ||z_i - c_j||_2^2, where z_i is a standardized window feature vector, C_j is the set of windows assigned to cluster j, and c_j is the centroid of that cluster. During fitting, assignment and centroid update steps are repeated until the cluster allocation stabilizes. This mathematical framing is useful because it clarifies that KMeans groups windows by geometric similarity in the selected feature space, not by a direct physical fault label.",
                        "BodyText",
                    ),
                    make_paragraph(
                        "This also explains why the dominant-feature analysis remains necessary. A KMeans cluster may contain mostly flow-dominant or return-dominant anomalies, but the cluster label itself is only an unsupervised grouping. The physical interpretation still comes from inspecting the original signals and from comparing per-feature reconstruction errors.",
                        "BodyText",
                    ),
                ],
            )
        except ValueError:
            pass

    # Expand weak-label evaluation framing
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "If confirmed fault labels were available, the natural evaluation would include precision, recall, and false-alarm rates" not in text:
        try:
            insert_block(
                body,
                "5 Results",
                [
                    make_paragraph(
                        "If confirmed fault labels were available, the natural evaluation would include precision, recall, and false-alarm rates against known events. That is not yet possible for this dataset because most historical windows do not have confirmed fault or normal labels. The evaluation therefore uses a weak-label protocol: anomaly counts and rates quantify detector output, dominant-feature summaries explain what part of the signal caused each flag, low delta-T overlap provides an engineering reference, and top-window inspection supports qualitative interpretation with the supervisor. This makes the current results suitable for review and thesis analysis, while leaving formal precision-based validation as future work once live data and event context are available.",
                        "BodyText",
                    )
                ],
            )
        except ValueError:
            pass


def add_training_history_figure(body: ET.Element, rels_root: ET.Element, files: dict[str, bytes]) -> None:
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "Figure 1A. Training history for the Hostatgeria Underfloor autoencoder" in text:
        return
    try:
        add_image_block(
            body,
            rels_root,
            files,
            "4.3 Feature construction",
            "Figure 1A shows an example training-history plot for the Hostatgeria Underfloor autoencoder.",
            FIGURE_FILES["training_history"],
            "Figure 1A. Training history for the Hostatgeria Underfloor autoencoder.",
            "Source: author-generated figure from the autoencoder training run.",
            "Interpretation. The training-history plot is used as a model-quality check. A decreasing and stabilizing training loss indicates that the autoencoder learned to reconstruct the retained windows rather than failing to train. This does not prove that every flagged window is a physical fault, but it supports the basic reconstruction premise used by the anomaly detector.",
            6500,
        )
    except ValueError:
        pass


def normalize_to_internal_numbering(body: ET.Element) -> None:
    """Use the script's older internal numbering while rebuilding generated blocks."""
    renames = [
        ("3 Method", "4 Method"),
        ("3.1 Overview", "4.1 Overview"),
        ("3.1.1 Implementation pipeline", "4.1.1 Implementation pipeline"),
        ("3.2 Autoencoder architecture", "4.2 Autoencoder architecture"),
        ("3.3 Feature construction", "4.3 Feature construction"),
        ("3.4 Thresholding", "4.4 Thresholding"),
        ("3.5 Engineering baseline", "4.5 Engineering baseline"),
        ("3.6 Clustering roles", "4.6 Clustering roles"),
        ("3.7 Evaluation strategy in a weak-label setting", "4.7 Evaluation strategy in a weak-label setting"),
        ("4 Results", "5 Results"),
        ("4.1 Current main result set", "5.1 Current main result set"),
        ("4.2 Dominant-feature interpretation", "5.2 Dominant-feature interpretation"),
        ("4.3 Low delta-T overlap", "5.3 Low delta-T overlap"),
        ("4.4 Operating regimes", "5.4 Operating regimes"),
        ("4.5 Threshold comparison", "5.5 Threshold comparison"),
        ("4.6 Train-test split and anomaly timing", "5.6 Train-test split and anomaly timing"),
        ("5 Discussion", "6 Discussion"),
        ("5.1 What is currently convincing", "6.1 What is currently convincing"),
        ("5.2 What remains uncertain", "6.2 What remains uncertain"),
        ("5.3 Implications for live deployment", "6.3 Implications for live deployment"),
        ("5.4 Threats to validity", "6.4 Threats to validity"),
        ("6 Conclusion", "7 Conclusion"),
        ("6.1 Future work", "7.1 Future work"),
    ]
    for old, new in renames:
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass


def renumber_no_data_chapters(body: ET.Element) -> None:
    renames = [
        ("4 Method", "3 Method"),
        ("4.1 Overview", "3.1 Overview"),
        ("4.1.1 Implementation pipeline", "3.1.1 Implementation pipeline"),
        ("4.2 Autoencoder architecture", "3.2 Autoencoder architecture"),
        ("4.3 Feature construction", "3.3 Feature construction"),
        ("4.4 Thresholding", "3.4 Thresholding"),
        ("4.5 Engineering baseline", "3.5 Engineering baseline"),
        ("4.6 Clustering roles", "3.6 Clustering roles"),
        ("4.7 Evaluation strategy in a weak-label setting", "3.7 Evaluation strategy in a weak-label setting"),
        ("5 Results", "4 Results"),
        ("5.1 Current main result set", "4.1 Current main result set"),
        ("5.2 Dominant-feature interpretation", "4.2 Dominant-feature interpretation"),
        ("5.3 Low delta-T overlap", "4.3 Low delta-T overlap"),
        ("5.4 Operating regimes", "4.4 Operating regimes"),
        ("5.5 Threshold comparison", "4.5 Threshold comparison"),
        ("5.6 Train-test split and anomaly timing", "4.6 Train-test split and anomaly timing"),
        ("6 Discussion", "5 Discussion"),
        ("6.1 What is currently convincing", "5.1 What is currently convincing"),
        ("6.2 What remains uncertain", "5.2 What remains uncertain"),
        ("6.3 Implications for live deployment", "5.3 Implications for live deployment"),
        ("6.4 Threats to validity", "5.4 Threats to validity"),
        ("7 Conclusion", "6 Conclusion"),
        ("7.1 Future work", "6.1 Future work"),
    ]
    for old, new in renames:
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass

    replacements = {
        "Chapters 5 and 6": "Chapters 4 and 5",
        "Chapter 5": "Chapter 4",
        "Chapter 6": "Chapter 5",
        "Section 7.1": "Section 6.1",
    }
    for child in paragraph_children(body):
        text = paragraph_text(child)
        new_text = text
        for old, new in replacements.items():
            new_text = new_text.replace(old, new)
        if new_text != text:
            set_paragraph_text_node(child, new_text)


def remove_orphan_scope_before_method(body: ET.Element) -> None:
    try:
        scope_idx = find_para_index(body, "3.4 Result-set scope")
        method_idx = find_para_index(body, "3 Method")
    except ValueError:
        return
    if scope_idx >= method_idx:
        return
    for child in list(body)[scope_idx:method_idx]:
        body.remove(child)


def insert_after_paragraph(body: ET.Element, marker_text: str, elements: list[ET.Element]) -> None:
    insert_idx = find_para_index(body, marker_text) + 1
    for elem in elements:
        body.insert(insert_idx, elem)
        insert_idx += 1


def add_interpretation_tables(body: ET.Element) -> None:
    safe_remove_between(body, "List of Figures", "1 Introduction")
    try:
        set_paragraph_text(body, "Table 3. Threshold comparison between p99 and 3-sigma.", "Table 4. Threshold comparison between p99 and 3-sigma.")
    except ValueError:
        pass
    try:
        set_paragraph_text(body, "Table 4. Operating-regime cluster anomaly rates.", "Table 3. Operating-regime cluster anomaly rates.")
    except ValueError:
        pass
    text = " ".join(paragraph_text(p) for p in paragraph_children(body))

    if "Table 2. Dominant-feature counts among flagged anomaly windows." not in text:
        summary = pd.read_csv(ROOT / "Results" / "tables" / "supervisor_results_sheet_2026-06-07.csv")
        rows = []
        for _, rec in summary.iterrows():
            rows.append(
                [
                    str(rec["display_label"]),
                    str(int(rec["supply_dominant_count"])),
                    str(int(rec["return_dominant_count"])),
                    str(int(rec["flow_dominant_count"])),
                    str(int(rec["flagged_windows"])),
                ]
            )
        insert_after_paragraph(
            body,
            "Figure 12. Dominant anomaly feature by sheet for the seven selected buildings.",
            [
                make_paragraph("Table 2. Dominant-feature counts among flagged anomaly windows.", "Caption"),
                make_simple_table(["Building", "Supply", "Return", "Flow", "Flagged"], rows),
                make_paragraph(
                    "Interpretation. This table gives the exact counts behind the dominant-feature figure. It is useful when a stacked bar is visually clear but the supervisor needs the numerical split between supply-, return-, and flow-dominant anomaly windows.",
                    "BodyText",
                ),
            ],
        )

    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "Table 4. Threshold comparison between p99 and 3-sigma." not in text:
        thresholds = pd.read_csv(ROOT / "Results" / "tables" / "threshold_method_comparison_2026-06-07.csv")
        rows = []
        for _, rec in thresholds.iterrows():
            rows.append(
                [
                    str(rec["display_label"]),
                    f"{float(rec['threshold_p99']):.3f}",
                    f"{float(rec['threshold_3sigma']):.3f}",
                    str(int(rec["flagged_p99"])),
                    str(int(rec["flagged_3sigma"])),
                    f"{int(rec['delta_flagged_windows']):+d}",
                ]
            )
        insert_after_paragraph(
            body,
            "Figure 16A. Training reconstruction-error distribution by sheet with threshold markers.",
                [
                make_paragraph("Table 4. Threshold comparison between p99 and 3-sigma.", "Caption"),
                make_simple_table(["Building", "p99 T", "3-sigma T", "p99 flags", "3-sigma flags", "Delta"], rows),
                make_paragraph(
                    "Interpretation. This table shows that the 3-sigma rule is not uniformly stricter than p99. The change in flagged windows depends on the shape and spread of each building's training-error distribution.",
                    "BodyText",
                ),
            ],
        )

    text = " ".join(paragraph_text(p) for p in paragraph_children(body))
    if "Table 3. Operating-regime cluster anomaly rates." not in text:
        clusters = pd.read_csv(ROOT / "Results" / "tables" / "cluster_sheet_summary_stabilized_log.csv")
        label_map = dict(
            pd.read_csv(ROOT / "Results" / "tables" / "supervisor_results_sheet_2026-06-07.csv")[["sheet", "display_label"]].values
        )
        rows = []
        for _, rec in clusters.iterrows():
            if int(rec["anomaly_windows"]) == 0:
                continue
            rows.append(
                [
                    label_map.get(str(rec["sheet"]), str(rec["sheet"])),
                    str(int(rec["cluster"])),
                    str(int(rec["windows"])),
                    str(int(rec["anomaly_windows"])),
                    f"{100.0 * float(rec['anomaly_rate']):.2f}",
                ]
            )
        insert_after_paragraph(
            body,
            "Figure 16. Operating-regime cluster distribution for the seven selected buildings.",
                [
                make_paragraph("Table 3. Operating-regime cluster anomaly rates.", "Caption"),
                make_simple_table(["Building", "Cluster", "Windows", "Anomaly windows", "Rate [%]"], rows),
                make_paragraph(
                    "Interpretation. This table adds the anomaly rate inside each occupied operating-regime cluster. It helps show whether anomalies are spread evenly across regimes or concentrated in specific daily-pattern clusters.",
                    "BodyText",
                ),
            ],
        )


def make_field_paragraph(instr: str) -> ET.Element:
    p = ET.Element(qn("w", "p"))
    ppr = ET.SubElement(p, qn("w", "pPr"))
    ET.SubElement(ppr, qn("w", "pStyle"), {qn("w", "val"): "BodyText"})
    r_begin = ET.SubElement(p, qn("w", "r"))
    ET.SubElement(r_begin, qn("w", "fldChar"), {qn("w", "fldCharType"): "begin"})
    r_instr = ET.SubElement(p, qn("w", "r"))
    instr_text = ET.SubElement(r_instr, qn("w", "instrText"))
    instr_text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr_text.text = instr
    r_sep = ET.SubElement(p, qn("w", "r"))
    ET.SubElement(r_sep, qn("w", "fldChar"), {qn("w", "fldCharType"): "separate"})
    p.append(make_run("Right-click and update field in Word."))
    r_end = ET.SubElement(p, qn("w", "r"))
    ET.SubElement(r_end, qn("w", "fldChar"), {qn("w", "fldCharType"): "end"})
    return p


def make_tc_runs(entry: str, category: str) -> list[ET.Element]:
    r_begin = ET.Element(qn("w", "r"))
    ET.SubElement(r_begin, qn("w", "fldChar"), {qn("w", "fldCharType"): "begin"})

    r_instr = ET.Element(qn("w", "r"))
    instr = ET.SubElement(r_instr, qn("w", "instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = f' TC "{entry}" \\f {category} '

    r_end = ET.Element(qn("w", "r"))
    ET.SubElement(r_end, qn("w", "fldChar"), {qn("w", "fldCharType"): "end"})
    return [r_begin, r_instr, r_end]


def remove_tc_fields_from_paragraph(paragraph: ET.Element) -> None:
    runs = list(paragraph.findall("./w:r", NS))
    remove_indices: set[int] = set()
    for idx, run in enumerate(runs):
        instr = " ".join(t.text or "" for t in run.findall(".//w:instrText", NS))
        if " TC " not in instr:
            continue
        remove_indices.add(idx)
        if idx > 0 and runs[idx - 1].find(".//w:fldChar", NS) is not None:
            remove_indices.add(idx - 1)
        if idx + 1 < len(runs) and runs[idx + 1].find(".//w:fldChar", NS) is not None:
            remove_indices.add(idx + 1)
    for idx in sorted(remove_indices, reverse=True):
        paragraph.remove(runs[idx])


def short_list_entry(caption: str) -> str:
    figure_title_map = {
        "Figure 1.": "Figure 1. Reconstruction-based anomaly detector",
        "Figure 1A.": "Figure 1A. Autoencoder training history",
        "Figure 2.": "Figure 2. Threshold distribution comparison",
        "Figure 3.": "Figure 3. Anomaly summary by building",
        "Figure 3A.": "Figure 3A. Median retained-window profiles",
        "Figure 4.": "Figure 4. Reconstruction-error timelines",
        "Figure 5.": "Figure 5. Abat Cisneros top anomaly window",
        "Figure 6.": "Figure 6. Abat Garriga top anomaly window",
        "Figure 7.": "Figure 7. Abat Marcet top anomaly window",
        "Figure 8.": "Figure 8. Abat Oliba top anomaly window",
        "Figure 9.": "Figure 9. Hostatgeria DHW Radiators top anomaly window",
        "Figure 10.": "Figure 10. Hostatgeria Underfloor top anomaly window",
        "Figure 11.": "Figure 11. Nostra Senyora top anomaly window",
        "Figure 11A.": "Figure 11A. Garriga observed versus reconstructed signals",
        "Figure 11B.": "Figure 11B. Underfloor observed versus reconstructed signals",
        "Figure 11C.": "Figure 11C. Joint versus univariate autoencoders",
        "Figure 12.": "Figure 12. Dominant anomaly feature by building",
        "Figure 13.": "Figure 13. Per-feature reconstruction-error space",
        "Figure 14.": "Figure 14. Autoencoder anomalies versus low delta-T baseline",
        "Figure 15.": "Figure 15. Low delta-T overlap in reviewed anomalies",
        "Figure 16.": "Figure 16. Operating-regime cluster distribution",
        "Figure 16A.": "Figure 16A. Sheet-level threshold distributions",
        "Figure 17.": "Figure 17. Train-versus-test anomaly split",
    }
    table_title_map = {
        "Table 1:": "Table 1. Seven-building result summary",
        "Table 2.": "Table 2. Dominant-feature anomaly counts",
        "Table 3.": "Table 3. Operating-regime cluster anomaly rates",
        "Table 4.": "Table 4. p99 versus 3-sigma threshold comparison",
    }
    figure_match = re.match(r"^(Figure\s+\d+[A-Z]?\.)", caption)
    if figure_match:
        return figure_title_map.get(figure_match.group(1), caption)
    table_match = re.match(r"^(Table\s+\d+[A-Z]?[:.])", caption)
    if table_match:
        return table_title_map.get(table_match.group(1), caption)
    return caption


def add_caption_tc_fields(body: ET.Element) -> None:
    for paragraph in paragraph_children(body):
        text = paragraph_text(paragraph)
        if not re.match(r"^(Figure\s+\d+[A-Z]?\.|Table\s+\d+[A-Z]?[:.]) ", text):
            continue
        remove_tc_fields_from_paragraph(paragraph)
        category = "F" if text.startswith("Figure") else "T"
        for run in make_tc_runs(short_list_entry(text), category):
            paragraph.append(run)


def rebuild_front_matter_lists(body: ET.Element) -> None:
    children = list(body)
    toc_blocks = []
    for child in children:
        if child.tag == qn("w", "sdt"):
            text = " ".join(t.text or "" for t in child.findall(".//w:t", NS))
            instr = " ".join(t.text or "" for t in child.findall(".//w:instrText", NS))
            if "Table of Contents" in text or " TOC " in instr:
                toc_blocks.append(child)
    if not toc_blocks:
        toc_blocks = [make_paragraph("Table of Contents", "Heading1"), make_field_paragraph('TOC \\o "1-3" \\h \\z \\u')]
    else:
        for block in toc_blocks:
            body.remove(block)

    safe_remove_between(body, "List of Figures", "1 Introduction")
    remove_exact_paragraphs(body, ["List of Figures", "List of Tables"])
    remove_paragraphs_containing(body, ["Right-click and update field in Word."])

    try:
        insert_idx = find_para_index(body, "1 Introduction")
    except ValueError:
        return

    list_blocks: list[ET.Element] = []
    list_blocks.extend(toc_blocks)
    captions = [paragraph_text(p) for p in paragraph_children(body)]
    figure_entries = [short_list_entry(c) for c in captions if re.match(r"^Figure\s+\d+[A-Z]?\. ", c)]
    table_entries = [short_list_entry(c) for c in captions if re.match(r"^Table\s+\d+[A-Z]?[:.] ", c)]

    list_blocks.append(make_paragraph("List of Figures", "Heading1"))
    for entry in figure_entries:
        list_blocks.append(make_paragraph(entry, "TOC1"))
    list_blocks.append(make_paragraph("List of Tables", "Heading1"))
    for entry in table_entries:
        list_blocks.append(make_paragraph(entry, "TOC1"))
    for offset, elem in enumerate(list_blocks):
        body.insert(insert_idx + offset, elem)


def fold_data_chapter_into_method(body: ET.Element) -> None:
    try:
        data_start = find_para_index(body, "3 Data")
        method_start = find_para_index(body, "4 Method")
    except ValueError:
        return
    if method_start <= data_start:
        return

    moved_paragraphs: list[ET.Element] = []
    for child in list(body)[data_start + 1 : method_start]:
        if child.tag != qn("w", "p"):
            continue
        text = paragraph_text(child)
        if text in {
            "3.1 Dataset, source material, and variables",
            "3.2 Preprocessing decisions",
            "3.3 Known limitations",
            "3.4 Result-set scope",
        }:
            continue
        moved_paragraphs.append(copy.deepcopy(child))

    for child in list(body)[data_start:method_start]:
        body.remove(child)

    try:
        overview_idx = find_para_index(body, "4.1 Overview")
    except ValueError:
        return

    insert_items = [
        make_paragraph(
            "The dataset and preprocessing choices are treated as part of the method because they define the input windows supplied to the detector. The historical data, retained variables, missing-data handling, and result-set scope are therefore summarized here before the modelling pipeline.",
            "BodyText",
        )
    ] + moved_paragraphs
    for offset, item in enumerate(insert_items, start=1):
        body.insert(overview_idx + offset, item)

    renames = [
        ("4 Method", "3 Method"),
        ("4.1 Overview", "3.1 Overview"),
        ("4.1.1 Implementation pipeline", "3.1.1 Implementation pipeline"),
        ("4.2 Autoencoder architecture", "3.2 Autoencoder architecture"),
        ("4.3 Feature construction", "3.3 Feature construction"),
        ("4.4 Thresholding", "3.4 Thresholding"),
        ("4.5 Engineering baseline", "3.5 Engineering baseline"),
        ("4.6 Clustering roles", "3.6 Clustering roles"),
        ("4.7 Evaluation strategy in a weak-label setting", "3.7 Evaluation strategy in a weak-label setting"),
        ("5 Results", "4 Results"),
        ("5.1 Current main result set", "4.1 Current main result set"),
        ("5.2 Dominant-feature interpretation", "4.2 Dominant-feature interpretation"),
        ("5.3 Low delta-T overlap", "4.3 Low delta-T overlap"),
        ("5.4 Operating regimes", "4.4 Operating regimes"),
        ("5.5 Threshold comparison", "4.5 Threshold comparison"),
        ("5.6 Train-test split and anomaly timing", "4.6 Train-test split and anomaly timing"),
        ("6 Discussion", "5 Discussion"),
        ("6.1 What is currently convincing", "5.1 What is currently convincing"),
        ("6.2 What remains uncertain", "5.2 What remains uncertain"),
        ("6.3 Implications for live deployment", "5.3 Implications for live deployment"),
        ("6.4 Threats to validity", "5.4 Threats to validity"),
        ("7 Conclusion", "6 Conclusion"),
        ("7.1 Future work", "6.1 Future work"),
    ]
    for old, new in renames:
        try:
            set_paragraph_text(body, old, new)
        except ValueError:
            pass

    replacements = {
        "Chapters 5 and 6": "Chapters 4 and 5",
        "Chapter 5": "Chapter 4",
        "Chapter 6": "Chapter 5",
        "Section 7.1": "Section 6.1",
    }
    for child in paragraph_children(body):
        text = paragraph_text(child)
        new_text = text
        for old, new in replacements.items():
            new_text = new_text.replace(old, new)
        if new_text != text:
            set_paragraph_text_node(child, new_text)


def rebuild_results(body: ET.Element, rels_root: ET.Element, files: dict[str, bytes]) -> None:
    # Rename section 5.7 to 5.6 after removing the raw-flow subsection.
    try:
        set_paragraph_text(body, "5.7 Train-test split and anomaly timing", "5.6 Train-test split and anomaly timing")
    except ValueError:
        pass

    # Remove existing figure/material blocks.
    safe_remove_between(body, "Figure 3 summarizes the retained-window counts, flagged anomalies, and anomaly rates across the five selected buildings.", "5.2 Dominant-feature interpretation")
    safe_remove_between(body, "Figure 6 shows which feature dominates the anomaly score for each building.", "5.3 Low delta-T overlap")
    safe_remove_between(body, "Figure 10 shows which feature dominates the anomaly score for each building.", "5.3 Low delta-T overlap")
    safe_remove_between(body, "Figure 8 compares the number of autoencoder anomalies with the engineering low delta-T baseline.", "5.4 Operating regimes")
    safe_remove_between(body, "Figure 12 compares the number of autoencoder anomalies with the engineering low delta-T baseline.", "5.4 Operating regimes")
    safe_remove_between(body, "Figure 10 summarizes the operating-regime cluster occupancy for the five selected buildings.", "5.5 Threshold comparison")
    safe_remove_between(body, "Figure 14 summarizes the operating-regime cluster occupancy for the five selected buildings.", "5.5 Threshold comparison")
    safe_remove_between(body, "5.6 Flow-channel sensitivity comparison", "5.6 Train-test split and anomaly timing")
    safe_remove_between(body, "Figure 14 shows how anomalies are distributed between the training period and the later chronological period.", "6 Discussion")
    safe_remove_between(body, "Figure 15 shows how anomalies are distributed between the training period and the later chronological period.", "6 Discussion")
    safe_remove_between(body, "Figure 3A summarizes the median daily retained-window profiles for all seven buildings.", "Figure 4 shows the reconstruction-error timelines that underpin the anomaly counts reported in this section.")
    safe_remove_between(body, "Figure 11A compares observed and reconstructed signals for the top Garriga anomaly window.", "5.2 Dominant-feature interpretation")
    safe_remove_between(body, "Figure 16A visualizes the training-error distributions behind the 3-sigma thresholds across sheets.", "5.6 Train-test split and anomaly timing")

    docpr_id = 3000
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 3 summarizes the retained-window counts, flagged anomalies, and anomaly rates across the seven selected buildings.",
        FIGURE_FILES["summary"],
        "Figure 3. Retained-window count, flagged-window count, and flagged-window rate for the seven selected buildings.",
        "Source: author-generated figure based on processed historical district-heating data.",
        "Interpretation. This figure compares usable window count, flagged anomaly count, and flagged anomaly rate across the seven selected buildings. The retained-window count shows how much usable data each building contributes, the flagged-window count shows the absolute anomaly volume, and the flagged rate shows the relative density of anomalies after accounting for dataset size.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 3A summarizes the median daily retained-window profiles for all seven buildings.",
        FIGURE_FILES["profiles"],
        "Figure 3A. Median daily retained-window profiles for the seven selected buildings. Supply and return temperatures are shown with 10th-90th percentile bands, and flow is shown on the secondary axis with its own 10th-90th percentile band.",
        "Source: author-generated figure based on all retained 24-hour windows before anomaly filtering.",
        "Interpretation. This figure summarizes how the seven buildings typically behave across the day before focusing on anomalies. It is useful for understanding building-to-building differences in thermal level, return behaviour, and flow magnitude, and therefore helps explain why the retained-window counts and anomaly rates are not identical across sheets.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 4 shows the reconstruction-error timelines that underpin the anomaly counts reported in this section.",
        FIGURE_FILES["fig4"],
        "Figure 4. Reconstruction-error timelines for the five selected buildings with clean timeline views. The dashed line is the anomaly threshold and the highlighted points are flagged windows.",
        "Source: author-generated figure based on autoencoder reconstruction error across retained windows.",
        "Interpretation. Each panel plots reconstruction error over chronological window start time for one building. The dashed line is the anomaly threshold learned from the training-error distribution, and the highlighted points are windows whose reconstruction error exceeds that threshold. This comparison is intentionally restricted to the five buildings whose retained-window timelines are not dominated by long faulty constant-value periods. Abat Oliba and Hostatgeria Underfloor remain part of the thesis result set, but they are interpreted mainly through their anomaly windows and summary statistics rather than through this timeline comparison.",
        docpr_id,
    )

    top_blocks = [
        ("Abat Cisneros", FIGURE_FILES["cisneros"], "Flow", "Figure 5 shows the top reviewed anomaly window for Abat Cisneros.", "Figure 5. Abat Cisneros top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is flow-dominant. The figure should be read from top to bottom. The first two panels show whether supply and return remain smooth or shift abruptly. The third panel shows the physically scaled flow behaviour in kg/s, which is the main panel of interest here. The fourth panel shows delta-T and highlights any overlap with the engineering low delta-T rule. Together the four traces indicate whether the abnormality is mainly hydraulic, mainly thermal, or coupled."),
        ("Abat Garriga", FIGURE_FILES["garriga"], "Return", "Figure 6 shows the top reviewed anomaly window for Abat Garriga.", "Figure 6. Abat Garriga top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is return-dominant. The main reading task is to compare the return-temperature trace against the supply trace and then check whether the flow profile changes in a way that supports a thermal explanation. The delta-T panel shows whether the abnormality also coincides with weak temperature separation."),
        ("Abat Marcet", FIGURE_FILES["marcet"], "Flow", "Figure 7 shows the top reviewed anomaly window for Abat Marcet.", "Figure 7. Abat Marcet top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is flow-dominant. The figure is useful for checking whether the main abnormality appears as unusual flow behaviour, weak thermal separation, or a coordinated change across all channels. Because the signals are synchronized, the reader can compare the timing of the abnormal flow behaviour with the temperature response."),
        ("Abat Oliba", FIGURE_FILES["oliba"], "Return", "Figure 8 shows the top reviewed anomaly window for Abat Oliba.", "Figure 8. Abat Oliba top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is return-dominant. The figure should be interpreted by comparing the return-temperature behaviour with the supply trace and then checking whether the flow panel remains plausible in physical scale. This is particularly important for Abat Oliba because the sheet was central in earlier flow-sensitivity analysis."),
        ("Hostatgeria DHW Radiators", FIGURE_FILES["dhw"], "Flow", "Figure 9 shows the top reviewed anomaly window for Hostatgeria DHW Radiators.", "Figure 9. Hostatgeria DHW Radiators top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is flow-dominant. The figure is useful for checking whether the detector is responding to a recurring hydraulic pattern rather than to a one-off temperature excursion. The relative stability of the temperature panels compared with the flow panel helps explain why this sheet tends to accumulate many flow-dominant anomalies."),
        ("Hostatgeria Underfloor", FIGURE_FILES["underfloor"], "Supply", "Figure 10 shows the top reviewed anomaly window for Hostatgeria Underfloor.", "Figure 10. Hostatgeria Underfloor top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This anomaly is supply-dominant and remains the strongest thesis case. The supply panel carries the main abnormality, the return and flow panels provide context, and the delta-T panel shows that the same window also overlaps the engineering baseline. This makes it the clearest example where the learned detector and the engineering reference point to the same abnormal operating period."),
        ("Nostra Senyora", FIGURE_FILES["nostra"], "Supply/Return", "Figure 11 shows the top reviewed anomaly window for Nostra Senyora.", "Figure 11. Nostra Senyora top reviewed anomaly window. The four traces show supply temperature [deg C], return temperature [deg C], flow [kg/s], and delta-T [deg C] over the 24-hour anomaly window.", "Interpretation. This sheet mixes supply-dominant and return-dominant behaviour in the broader result summary, so the top reviewed anomaly should be read by checking whether the strongest deviation is thermal on the supply side, thermal on the return side, or accompanied by a change in flow timing."),
    ]
    for label, path, _, intro, caption, interp in top_blocks:
        docpr_id = add_image_block(
            body,
            rels_root,
            files,
            "5.2 Dominant-feature interpretation",
            intro,
            path,
            caption,
            f"Source: author-generated anomaly inspection plot for {label}.",
            interp,
            docpr_id,
        )
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 11A compares observed and reconstructed signals for the top Garriga anomaly window.",
        FIGURE_FILES["overlay_garriga"],
        "Figure 11A. Observed versus reconstructed signals for the top Abat Garriga anomaly window.",
        "Source: author-generated figure from the trained joint autoencoder and the highest-scoring Garriga anomaly window.",
        "Interpretation. This figure explains why the Garriga example is classified as return-dominant even though the flow trace looks visually active. Dominance is assigned by reconstruction error, not by raw amplitude. The model reproduces the flow channel comparatively well, while the return channel shows the largest mismatch between observed and reconstructed behaviour.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 11B compares observed and reconstructed signals for the strongest Underfloor anomaly window.",
        FIGURE_FILES["overlay_underfloor"],
        "Figure 11B. Observed versus reconstructed signals for the top Hostatgeria Underfloor anomaly window.",
        "Source: author-generated figure from the trained joint autoencoder and the highest-scoring Underfloor anomaly window.",
        "Interpretation. This figure shows the model failing much more strongly on the supply channel than on the other channels, which is why the Underfloor case remains the clearest supply-dominant thesis example. It also makes the reconstruction-based anomaly logic more concrete than the raw signal plot alone.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.2 Dominant-feature interpretation",
        "Figure 11C compares the joint Underfloor autoencoder with univariate alternatives trained on individual channels.",
        FIGURE_FILES["joint_vs_univariate_underfloor"],
        "Figure 11C. Joint-versus-univariate comparison for Hostatgeria Underfloor, using flagged-window rate and median reconstruction MSE.",
        "Source: author-generated comparison between the joint three-channel autoencoder and single-channel autoencoders for the Underfloor sheet.",
        "Interpretation. This figure shows that the single-channel alternatives do not behave identically. Return-only reconstruction yields the highest flagged-window rate, while the flow-only model gives the lowest median reconstruction error. The joint model remains between those extremes and is kept as the main thesis detector because it preserves cross-channel context instead of forcing the anomaly decision to come from only one signal at a time.",
        docpr_id,
    )

    docpr_id = add_image_block(
        body, rels_root, files, "5.3 Low delta-T overlap",
        "Figure 12 shows which feature dominates the anomaly score for each building.",
        FIGURE_FILES["feature_type"],
        "Figure 12. Dominant anomaly feature by sheet for the seven selected buildings.",
        "Source: author-generated figure using per-feature reconstruction errors.",
        "Interpretation. This figure groups detected anomalies by the feature with the largest reconstruction-error contribution. It should be read as a feature-type summary across buildings: supply, return, and flow remain present in all analyses, but one channel contributes the largest share of the anomaly score more often in some buildings than in others.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.3 Low delta-T overlap",
        "Figure 13 visualizes anomalies in the actual per-feature reconstruction-error space.",
        FIGURE_FILES["feature_space"],
        "Figure 13. Anomaly feature space using actual per-feature reconstruction errors, with point color indicating the dominant anomaly feature.",
        "Source: author-generated figure based on anomaly windows and per-feature error attribution.",
        "Interpretation. Each point is one anomaly window, positioned using the actual per-feature reconstruction errors rather than a projected embedding. The axes therefore correspond to real model-error quantities, and the point color identifies the dominant anomalous feature for that window.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.4 Operating regimes",
        "Figure 14 compares the number of autoencoder anomalies with the engineering low delta-T baseline.",
        FIGURE_FILES["baseline"],
        "Figure 14. Autoencoder anomaly counts compared with the engineering low delta-T baseline for the seven selected buildings.",
        "Source: author-generated figure using autoencoder anomaly counts and baseline overlap checks.",
        "Interpretation. This figure compares the number of windows flagged by the learned detector with the number associated with the low delta-T engineering reference. Similar counts suggest partial agreement, while differences indicate that the autoencoder is also finding anomaly types outside the narrow low delta-T rule.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.4 Operating regimes",
        "Figure 15 shows the extent to which reviewed anomaly windows overlap low delta-T events.",
        FIGURE_FILES["low_delta"],
        "Figure 15. Reviewed anomaly windows with low delta-T overlap and the corresponding overlap rate.",
        "Source: author-generated figure based on reviewed anomaly windows and baseline overlap matching.",
        "Interpretation. The overlap count shows how many reviewed anomalies coincide with low delta-T events, and the overlap rate normalizes this by the number of reviewed anomalies. High overlap supports a familiar engineering reading, while low overlap suggests that the detected anomalies belong to other behavioural categories.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.5 Threshold comparison",
        "Figure 16 summarizes the operating-regime cluster occupancy for the seven selected buildings.",
        FIGURE_FILES["cluster"],
        "Figure 16. Operating-regime cluster distribution for the seven selected buildings.",
        "Source: author-generated figure based on operating-regime clustering across retained windows.",
        "Interpretation. The cluster labels are data-driven groups of similar daily behaviour rather than named physical modes. What matters is whether a building occupies many regimes or concentrates in a few, because that helps explain why anomaly behaviour is not uniform across the selected sheets.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "5.6 Train-test split and anomaly timing",
        "Figure 16A visualizes the training-error distributions behind the 3-sigma thresholds across sheets.",
        FIGURE_FILES["threshold_dist"],
        "Figure 16A. Training reconstruction-error distribution by sheet with threshold markers.",
        "Source: author-generated figure based on training-window reconstruction errors under the 3-sigma evaluation pack.",
        "Interpretation. This figure is the sheet-level detail view behind Figure 2 rather than a duplicate of it. Figure 2 introduces the thresholding idea at method level, while Figure 16A shows the actual training-error distributions building by building. It helps explain why the same threshold rule does not behave uniformly across buildings: some sheets have compact error bands, while others have wider or more skewed tails.",
        docpr_id,
    )
    docpr_id = add_image_block(
        body, rels_root, files, "6 Discussion",
        "Figure 17 shows how anomalies are distributed between the training period and the later chronological period.",
        FIGURE_FILES["train_test"],
        "Figure 17. Train-versus-test anomaly split for the seven selected buildings.",
        "Source: author-generated figure using the chronological train-test partition of the retained windows.",
        "Interpretation. This figure separates flagged anomalies by whether they occur in the earlier chronological portion or in the later period. It is useful for judging whether anomalies persist beyond the first historical segment and therefore remain relevant for later operational monitoring.",
        docpr_id,
    )

    # Adjust section wording after removal of the raw-flow subsection.
    try:
        set_paragraph_text(
            body,
            "The anomalies are not confined to the first chronological portion of the data. Some buildings show both training and later test-period anomalies, which is useful when thinking about eventual live deployment.",
            "The anomalies are not confined to the first chronological portion of the data. Some buildings show both training and later test-period anomalies, which is useful when thinking about eventual live deployment and about whether the detector can remain informative on later unseen periods.",
        )
    except ValueError:
        pass


def main() -> None:
    register_openxml_namespaces()
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)

    files = read_docx(DOCX)
    doc_root = ET.fromstring(files["word/document.xml"])
    styles_root = ET.fromstring(files["word/styles.xml"])
    settings_root = ET.fromstring(files["word/settings.xml"])
    rels_root = ET.fromstring(files["word/_rels/document.xml.rels"])
    body = get_body(doc_root)
    normalize_to_internal_numbering(body)

    update_styles(styles_root)
    disable_update_fields(settings_root)
    update_citations(body)
    expand_core_sections(body)
    insert_acronym_list(body)
    insert_supervised_unsupervised_section(body)
    insert_research_context(body)
    insert_related_work_positioning(body)
    update_abstract_and_reference_framing(body)
    strengthen_intro_and_conclusion(body)
    restructure_introduction(body)
    restructure_dataset_section(body)
    move_acknowledgments_near_front(body)
    refresh_intro_and_future_work_text(body)
    insert_gap_and_contribution_framing(body)
    insert_implementation_pipeline(body)
    insert_method_and_discussion_expansion(body)
    expand_encoder_and_clustering_methodology(body)
    insert_data_and_results_expansion(body)
    insert_new_sections_for_structure(body)
    harmonize_data_scope(body)
    move_trita_block(body)
    rebuild_results(body, rels_root, files)
    cleanup_endmatter(body)
    harmonize_building_scope(body)
    deduplicate_scope_block(body)
    deduplicate_results_block(body)
    update_results_table(doc_root)
    ensure_supplemental_result_figures(body, rels_root, files)
    add_interpretation_tables(body)
    replace_references(body)
    cleanup_known_intro_duplicates(body)
    finalize_supervisor_structure_updates(body)
    add_training_history_figure(body, rels_root, files)
    fold_data_chapter_into_method(body)
    renumber_no_data_chapters(body)
    remove_orphan_scope_before_method(body)
    rebuild_front_matter_lists(body)
    for paragraph in paragraph_children(body):
        remove_tc_fields_from_paragraph(paragraph)
    clean_mc_ignorable(doc_root)

    files["word/document.xml"] = ET.tostring(doc_root, encoding="utf-8", xml_declaration=True)
    files["word/styles.xml"] = ET.tostring(styles_root, encoding="utf-8", xml_declaration=True)
    files["word/settings.xml"] = ET.tostring(settings_root, encoding="utf-8", xml_declaration=True)
    files["word/_rels/document.xml.rels"] = ET.tostring(rels_root, encoding="utf-8", xml_declaration=True)
    write_docx(DOCX, files)
    print(f"Updated {DOCX}")


if __name__ == "__main__":
    main()
