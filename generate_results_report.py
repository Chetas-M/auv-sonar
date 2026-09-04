"""
generate_results_report.py
Master Script to Generate:
AUV_Adaptive_Sonar_Complete_Results_and_Output_Interpretation_Report.docx
SIH Problem 26058: AUV Adaptive Sonar Digital Twin
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# Root directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DOCX = os.path.join(ROOT_DIR, "AUV_Adaptive_Sonar_Complete_Results_and_Output_Interpretation_Report.docx")
MATLAB_PLOTS_DIR = os.path.join(ROOT_DIR, "outputs_matlab", "plots")
PYTHON_PLOTS_DIR = os.path.join(ROOT_DIR, "outputs", "plots")

# Section builders
from results_sections_part1 import build_section_1, build_section_2, build_section_3, build_section_4
from results_sections_part2 import build_section_5
from results_sections_part3 import build_sections_6_to_12
from results_sections_part4 import build_sections_13_to_18

# Color Palette Constants
COLOR_PRIMARY_HEX = "1B365D"       # Deep Navy
COLOR_SECONDARY_HEX = "2B5B84"     # Slate Navy
COLOR_ACCENT_HEX = "008080"        # Deep Teal
COLOR_TEXT_HEX = "222222"          # Charcoal
COLOR_MUTED_HEX = "555555"         # Muted Grey
COLOR_LIGHT_BG_HEX = "F4F7FA"      # Very Light Blue-Grey
COLOR_BORDER_HEX = "D0D7DE"        # Subtle Grey Border

COLOR_ALERT_NOTE_HEX = "1B365D"      # Navy
COLOR_ALERT_NOTE_BG = "EBF2F8"
COLOR_ALERT_WARN_HEX = "B45309"      # Amber
COLOR_ALERT_WARN_BG = "FEF3C7"
COLOR_ALERT_CRIT_HEX = "B91C1C"      # Crimson
COLOR_ALERT_CRIT_BG = "FEE2E2"
COLOR_ALERT_ASSUMP_HEX = "0E7490"    # Cyan/Blue
COLOR_ALERT_ASSUMP_BG = "E0F2FE"


def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets internal padding (in twips) for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)


def set_cell_left_border(cell, hex_color="1B365D", sz="24"):
    """Sets a thick left border and clears other borders for callout style."""
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{hex_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)


def set_table_borders(table, border_color="D0D7DE"):
    """Sets clean horizontal and subtle vertical grid borders on a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)


def add_callout(doc, tag, title, body, callout_type="NOTE"):
    """Creates a professional callout box with a shaded background and colored left stripe."""
    type_map = {
        "NOTE": (COLOR_ALERT_NOTE_HEX, COLOR_ALERT_NOTE_BG),
        "WARNING": (COLOR_ALERT_WARN_HEX, COLOR_ALERT_WARN_BG),
        "CRITICAL": (COLOR_ALERT_CRIT_HEX, COLOR_ALERT_CRIT_BG),
        "IMPORTANT": (COLOR_ALERT_CRIT_HEX, COLOR_ALERT_CRIT_BG),
        "ASSUMPTION": (COLOR_ALERT_ASSUMP_HEX, COLOR_ALERT_ASSUMP_BG),
    }
    stroke_color, fill_color = type_map.get(callout_type.upper(), (COLOR_ALERT_NOTE_HEX, COLOR_ALERT_NOTE_BG))

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, fill_color)
    set_cell_left_border(cell, stroke_color, sz="28")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15

    r_tag = p.add_run(f"[{tag.upper()}] ")
    r_tag.bold = True
    r_tag.font.name = "Calibri"
    r_tag.font.size = Pt(10)
    r_tag.font.color.rgb = RGBColor.from_string(stroke_color)

    r_title = p.add_run(f"{title}\n")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(10)
    r_title.font.color.rgb = RGBColor.from_string(stroke_color)

    r_body = p.add_run(body)
    r_body.font.name = "Calibri"
    r_body.font.size = Pt(9.5)
    r_body.font.color.rgb = RGBColor.from_string(COLOR_TEXT_HEX)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)


def add_equation_box(doc, eq_text, eq_label=""):
    """Adds a formatted mathematical equation block with shaded background and label."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, COLOR_LIGHT_BG_HEX)
    set_cell_left_border(cell, COLOR_SECONDARY_HEX, sz="16")
    set_cell_margins(cell, top=100, bottom=100, left=160, right=160)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.2
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    r_eq = p.add_run(eq_text)
    r_eq.bold = True
    r_eq.font.name = "Cambria Math"
    r_eq.font.size = Pt(10.5)
    r_eq.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    if eq_label:
        r_lbl = p.add_run(f"\n{eq_label}")
        r_lbl.font.name = "Calibri"
        r_lbl.font.size = Pt(8.5)
        r_lbl.font.italic = True
        r_lbl.font.color.rgb = RGBColor.from_string(COLOR_MUTED_HEX)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)


def add_styled_table(doc, headers, data, col_widths=None, alignments=None):
    """Creates a beautifully styled table with Navy header, alternating row shading, and cell margins."""
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)

    # Format Header Row
    hdr_row = tbl.rows[0]
    hdr_tr = hdr_row._tr.get_or_add_trPr()
    hdr_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_tr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        if col_widths and i < len(col_widths):
            cell.width = col_widths[i]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if alignments and i < len(alignments):
            p.alignment = alignments[i]
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Format Data Rows
    for r_idx, row_data in enumerate(data):
        row = tbl.rows[r_idx + 1]
        tr = row._tr.get_or_add_trPr()
        tr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        is_even = (r_idx % 2 == 1)
        bg_color = COLOR_LIGHT_BG_HEX if is_even else "FFFFFF"

        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if alignments and c_idx < len(alignments):
                p.alignment = alignments[c_idx]
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            run = p.add_run(str(val))
            run.font.name = "Calibri"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor.from_string(COLOR_TEXT_HEX)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)


def add_figure(doc, img_filename, fig_num, title, description, width_in=5.8, subfolder="matlab"):
    """Inserts a figure image, centers it, and adds a bold caption."""
    # Check in preferred subfolder first, then fallback to other
    if subfolder == "matlab":
        primary = os.path.join(MATLAB_PLOTS_DIR, img_filename)
        fallback = os.path.join(PYTHON_PLOTS_DIR, img_filename)
    else:
        primary = os.path.join(PYTHON_PLOTS_DIR, img_filename)
        fallback = os.path.join(MATLAB_PLOTS_DIR, img_filename)

    img_path = primary if os.path.exists(primary) else fallback

    if not os.path.exists(img_path):
        p_err = doc.add_paragraph(f"[Image file not found: {img_filename}]")
        p_err.runs[0].font.color.rgb = RGBColor(200, 0, 0)
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)

    r_num = p_cap.add_run(f"Figure {fig_num}: ")
    r_num.bold = True
    r_num.font.name = "Calibri"
    r_num.font.size = Pt(9.5)
    r_num.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    r_title = p_cap.add_run(f"{title}. ")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = RGBColor.from_string(COLOR_SECONDARY_HEX)

    r_desc = p_cap.add_run(description)
    r_desc.font.name = "Calibri"
    r_desc.font.size = Pt(9)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor.from_string(COLOR_MUTED_HEX)


def add_h1(doc, text):
    """Adds a Chapter heading (Heading 1)."""
    h = doc.add_heading(text, level=1)
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(8)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)
    return h


def add_h2(doc, text):
    """Adds a Section heading (Heading 2)."""
    h = doc.add_heading(text, level=2)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(COLOR_SECONDARY_HEX)
    return h


def add_h3(doc, text):
    """Adds a Sub-section heading (Heading 3)."""
    h = doc.add_heading(text, level=3)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(COLOR_ACCENT_HEX)
    return h


def add_body(doc, text):
    """Adds standard body text paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string(COLOR_TEXT_HEX)
    return p


def add_bullet(doc, bold_prefix, text):
    """Adds a formatted bullet item with bold prefix."""
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15

    r_bold = p.add_run(bold_prefix)
    r_bold.bold = True
    r_bold.font.name = "Calibri"
    r_bold.font.size = Pt(10)
    r_bold.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = RGBColor.from_string(COLOR_TEXT_HEX)
    return p


def add_ascii_diagram(doc, diagram_text):
    """Adds a centered, fixed-width ASCII architecture diagram in a shaded box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_left_border(cell, COLOR_ACCENT_HEX, sz="20")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05

    run = p.add_run(diagram_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)


def setup_header_footer(doc):
    """Configures professional headers and footers with page numbers."""
    for s_idx, section in enumerate(doc.sections):
        section.different_first_page_header_footer = True

        # Header (pages > 1)
        hdr = section.header
        p_hdr = hdr.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.paragraph_format.space_after = Pt(0)
        r_hdr = p_hdr.add_run("SIH Problem 26058 — AUV Adaptive Sonar Digital Twin: Complete Results Report")
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = RGBColor.from_string(COLOR_MUTED_HEX)

        # Footer (pages > 1)
        ftr = section.footer
        p_ftr = ftr.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_ftr.paragraph_format.space_before = Pt(0)
        r_ftr = p_ftr.add_run("Engineering Report & Results Interpretation | Confidential — SIH Evaluation")
        r_ftr.font.name = "Calibri"
        r_ftr.font.size = Pt(8.5)
        r_ftr.font.color.rgb = RGBColor.from_string(COLOR_MUTED_HEX)


def build_cover_page(doc):
    """Builds a striking, highly professional engineering report cover page."""
    # Top spacing
    p_top = doc.add_paragraph()
    p_top.paragraph_format.space_before = Pt(36)

    # Super-title badge
    p_badge = doc.add_paragraph()
    p_badge.paragraph_format.space_before = Pt(0)
    p_badge.paragraph_format.space_after = Pt(6)
    r_badge = p_badge.add_run("SMART INDIA HACKATHON (SIH) — PROBLEM STATEMENT 26058")
    r_badge.bold = True
    r_badge.font.name = "Calibri"
    r_badge.font.size = Pt(11)
    r_badge.font.color.rgb = RGBColor.from_string(COLOR_ACCENT_HEX)

    # Main Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.1
    r_title = p_title.add_run("AUV Adaptive Sonar Digital Twin\nTransmitter Payload")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(28)
    r_title.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    # Horizontal Accent Line
    tbl_line = doc.add_table(rows=1, cols=1)
    tbl_line.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_line.autofit = False
    c_line = tbl_line.cell(0, 0)
    c_line.width = Inches(6.5)
    set_cell_background(c_line, COLOR_ACCENT_HEX)
    set_cell_margins(c_line, top=15, bottom=15, left=0, right=0)
    p_l = c_line.paragraphs[0]
    p_l.paragraph_format.space_before = Pt(0)
    p_l.paragraph_format.space_after = Pt(0)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(14)
    p_sub.paragraph_format.space_after = Pt(18)
    p_sub.paragraph_format.line_spacing = 1.2
    r_sub = p_sub.add_run(
        "Complete Results, Outputs, and Engineering Interpretation Report\n"
        "Exhaustive Analysis of All Priority 1 Experiments, Sweep Metrics, Dual Confidence Indicators, "
        "Controller Protection Mechanisms, and Automated Verification Suites"
    )
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor.from_string(COLOR_SECONDARY_HEX)

    # Key takeaway card
    takeaway_box = (
        "CORE ENGINEERING RESULT & PHYSICAL JUSTIFICATION:\n"
        "• LOW_FREQUENCY (100-220k): Lowest attenuation (64.5 dB/km) -> Propagation-Resilience Fallback\n"
        "• BALANCED (200-400k): Widest sweep bandwidth (200 kHz) -> Optimal 3.75 mm Range Resolution\n"
        "• HIGH_FREQUENCY (350-500k): Highest center frequency (425 kHz) -> 1.417x Relative Directivity\n"
        "• Profile selection is strictly governed by: (1) Propagation Viability, (2) Mission Objective, \n"
        "  (3) Dual Confidence Metrics, and (4) Existing Hysteresis, Debounce, and PRI Protections."
    )
    add_ascii_diagram(doc, takeaway_box)

    # Metadata Table
    p_meta_lbl = doc.add_paragraph()
    p_meta_lbl.paragraph_format.space_before = Pt(16)
    p_meta_lbl.paragraph_format.space_after = Pt(4)
    r_ml = p_meta_lbl.add_run("SYSTEM SPECIFICATIONS & ARTIFACT METADATA")
    r_ml.bold = True
    r_ml.font.name = "Calibri"
    r_ml.font.size = Pt(9.5)
    r_ml.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    meta_headers = ["Parameter", "Engineering Specification", "Verification Status"]
    meta_data = [
        ["Problem Statement", "SIH Problem 26058: Low-Power Adaptive Sonar Transmitter Payload", "Official Hackathon Problem"],
        ["Target Microcontroller", "STM32G474 (128 KB SRAM, 512 KB Flash, 12-Bit DAC)", "Hardware Feasibility Confirmed"],
        ["Digital Sampling Rate", "4.0 MSPS (0.25 us clock period, 8000 samples / 2 ms pulse)", "Phase Monotonicity Verified"],
        ["Pulse Repetition Interval", "PRI = 20.0 ms (50 Hz PRF, 10.0% Nominal Duty Cycle)", "Atomic Latching Verified"],
        ["Automated Test Coverage", "56 Unit Tests across Python & MATLAB (100% Passing)", "Bit-Exact Cross-Parity Verified"],
        ["Document Classification", "Results Interpretation & Experimental Engineering Report", "Current Implementation State"],
    ]
    add_styled_table(doc, meta_headers, meta_data, col_widths=[Inches(2.0), Inches(3.0), Inches(1.5)])

    # Page break after cover
    doc.add_page_break()


def build_table_of_contents(doc):
    """Builds a structured Table of Contents."""
    add_h1(doc, "Table of Contents")
    add_body(doc, "This document contains eighteen comprehensive sections detailing every result produced by the digital twin:")

    toc_items = [
        ("Section 1", "Executive Summary of Results & Core Trade-offs"),
        ("Section 2", "Output Taxonomy & Module Classification Table"),
        ("Section 3", "Complete Profile Output Explanation (LOW, BALANCED, HIGH)"),
        ("Section 4", "Complete Output Metric Reference (Ainslie-McColm, Margin, Confidence)"),
        ("Section 5", "Complete Graph-by-Graph Analysis (14-Point Engineering Review)"),
        ("Section 5.1 - 5.7", "Figures 1 to 7: Attenuation, Margin, Resolution, Directivity, Winner, Confidence, Sensitivity"),
        ("Section 5.8 - 5.10", "Companion Figures 8 to 10: Single Pulse, Quantization Analysis, Dynamic 150-Ping Timeline"),
        ("Section 6", "Range Sweep Outputs & Narrative of Regime Transitions"),
        ("Section 7", "Noise Sensitivity Outputs & Receiver Model Distinctions"),
        ("Section 8", "Environmental Sweep Outputs & Physical Hierarchy of Effects"),
        ("Section 9", "Signal Generation Outputs & Physical Transmitter Mapping"),
        ("Section 10", "DAC Quantization Outputs & Analog Hardware Distinctions"),
        ("Section 11", "Memory Footprint and DMA Buffer Allocation"),
        ("Section 12", "Controller Outputs: Hysteresis, Debounce, and Atomic PRI Latching"),
        ("Section 13", "Automated Test Suite Outputs (56 Tests across 5 Functional Groups)"),
        ("Section 14", "Output Interpretation Summary Master Table"),
        ("Section 15", "Verified Implementation Results vs Theoretical Assumptions"),
        ("Section 16", "What the Outputs Legitimately Prove"),
        ("Section 17", "What the Outputs Do NOT Prove (Physical Limitations)"),
        ("Section 18", "Final Engineering Story: The Transformation of SIH Problem 26058"),
    ]

    toc_headers = ["Section Identifier", "Section Title & Content Overview"]
    add_styled_table(doc, toc_headers, toc_items, col_widths=[Inches(1.8), Inches(4.7)])
    doc.add_page_break()


def generate_complete_results_report():
    print("=" * 80)
    print("  GENERATING COMPLETE RESULTS, OUTPUTS & GRAPH INTERPRETATION ENGINEERING REPORT")
    print(f"  Target File: {OUTPUT_DOCX}")
    print("=" * 80)

    doc = docx.Document()

    # Configure 1.0 inch page margins
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Setup headers and footers
    setup_header_footer(doc)

    # Dictionary of helper functions passed to builders
    helpers = {
        'add_h1': add_h1,
        'add_h2': add_h2,
        'add_h3': add_h3,
        'add_body': add_body,
        'add_bullet': add_bullet,
        'add_callout': add_callout,
        'add_equation_box': add_equation_box,
        'add_styled_table': add_styled_table,
        'add_figure': add_figure,
        'add_ascii_diagram': add_ascii_diagram,
    }

    print("[*] Building Cover Page...")
    build_cover_page(doc)

    print("[*] Building Table of Contents...")
    build_table_of_contents(doc)

    print("[*] Building Section 1: Executive Summary...")
    build_section_1(doc, helpers)

    print("[*] Building Section 2: Output Taxonomy...")
    build_section_2(doc, helpers)

    print("[*] Building Section 3: Complete Profile Outputs...")
    build_section_3(doc, helpers)

    print("[*] Building Section 4: Complete Output Metric Reference...")
    build_section_4(doc, helpers)

    print("[*] Building Section 5: Complete Graph-by-Graph Analysis (14 points per figure)...")
    build_section_5(doc, helpers)

    print("[*] Building Sections 6 to 12: Range, Noise, Env, Signal, DAC, Memory, Controller...")
    build_sections_6_to_12(doc, helpers)

    print("[*] Building Sections 13 to 18: Tests, Summary Table, Scope, Engineering Story...")
    build_sections_13_to_18(doc, helpers)

    print(f"[*] Saving Document to: {OUTPUT_DOCX}...")
    doc.save(OUTPUT_DOCX)

    size_bytes = os.path.getsize(OUTPUT_DOCX)
    size_mb = size_bytes / (1024 * 1024)
    print("=" * 80)
    print(f"  SUCCESSFULLY GENERATED REPORT: {OUTPUT_DOCX}")
    print(f"  Document File Size: {size_bytes:,} bytes ({size_mb:.2f} MB)")
    print("=" * 80)


if __name__ == "__main__":
    generate_complete_results_report()
