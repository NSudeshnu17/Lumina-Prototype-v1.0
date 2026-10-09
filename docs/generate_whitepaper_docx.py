"""
Compiles docs/TECHNICAL_WHITEPAPER.md into a formal, beautifully formatted
Microsoft Word document (docs/Lumina_RFID_Technical_Whitepaper.docx) complete
with meta tables, code blocks, callouts, and embedded high-resolution diagrams.
"""
import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

DOC_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(DOC_DIR, 'TECHNICAL_WHITEPAPER.md')
OUTPUT_PATH = os.path.join(DOC_DIR, 'Lumina_RFID_Technical_Whitepaper.docx')

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def add_diagram_image(doc, img_name, caption):
    img_path = os.path.join(DOC_DIR, img_name)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(6.2))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(f"Technical Diagram: {caption}")
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(8.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(100, 116, 139)

def generate_whitepaper_docx():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    NAVY = RGBColor(15, 35, 75)
    SLATE = RGBColor(70, 80, 95)
    CHARCOAL = RGBColor(30, 41, 59)
    BLUE_ACCENT = RGBColor(37, 99, 235)

    # Document Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("Lumina RFID — Technical Architecture & Specification")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    run_sub = sub_p.add_run("In-Depth Technical Whitepaper: Tech Stack, Dependencies, Component Interfaces & Relational Architecture")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = SLATE

    # Metadata Summary Box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Document Classification", "Technical Architecture Whitepaper & Dependency Specification"),
        ("System Release", "Lumina RFID — Phase-1 Production Prototype"),
        ("Date of Publication", "October 8, 2026"),
        ("Target Reviewers", "CTO, Software Architects, Full-Stack Developers, Security Evaluators")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.3)
        c1.width = Inches(4.4)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 50, 50, 100, 100)
        set_cell_margins(c1, 50, 50, 100, 100)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = "Arial"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = CHARCOAL

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = "Arial"
        r1.font.size = Pt(9)
        r1.font.color.rgb = CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    lines = md_text.split('\n')
    in_code_block = False
    code_buffer = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        
        data_rows = [r for r in table_rows if not re.match(r'^\s*\|?\s*:?-+:?\s*\|', r)]
        if not data_rows:
            in_table = False
            table_rows = []
            return

        cols_count = len([c.strip() for c in data_rows[0].strip('|').split('|')])
        t = doc.add_table(rows=len(data_rows), cols=cols_count)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        for r_idx, raw_row in enumerate(data_rows):
            cols = [c.strip() for c in raw_row.strip('|').split('|')]
            for c_idx in range(min(len(cols), cols_count)):
                cell = t.rows[r_idx].cells[c_idx]
                set_cell_margins(cell, 70, 70, 90, 90)
                cp = cell.paragraphs[0]
                cp.paragraph_format.space_after = Pt(0)
                
                txt = cols[c_idx]
                c_run = cp.add_run(txt.replace('**', '').replace('`', ''))
                c_run.font.name = "Arial"
                c_run.font.size = Pt(8.5)
                
                if r_idx == 0:
                    set_cell_background(cell, "1E3A8A")
                    c_run.font.bold = True
                    c_run.font.color.rgb = RGBColor(255, 255, 255)
                else:
                    bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                    set_cell_background(cell, bg)
                    c_run.font.color.rgb = CHARCOAL
                    if '**' in txt:
                        c_run.font.bold = True

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(4)
        in_table = False
        table_rows = []

    def flush_code():
        nonlocal in_code_block, code_buffer
        if not code_buffer:
            in_code_block = False
            return
        
        code_text = "\n".join(code_buffer)
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(code_text)
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(30, 41, 59)
        
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(4)
        in_code_block = False
        code_buffer = []

    i = 0
    while i < len(lines) and not lines[i].startswith('## 1.'):
        i += 1

    while i < len(lines):
        line = lines[i]

        # Strategic Placement of Architectural Diagrams
        if line.startswith('## 3. Detailed Component Architecture'):
            add_diagram_image(doc, 'system_architecture_diagram.jpg', 'System Architecture & Tier-by-Tier Technology Integration')
        elif line.startswith('### 4.2 Reusable Context-Aware RFID Hardware Input'):
            add_diagram_image(doc, 'rfid_modes_diagram.jpg', 'Hardware Context Engine: Single USB RFID Reader across 6 Operational Modes')
        elif line.startswith('## 5. Backend Layer Architecture'):
            add_diagram_image(doc, 'user_flow_diagram.jpg', 'Frontend-to-Backend Operational Workflow across Admin, Salesperson, and Manager Roles')
        elif line.startswith('### 5.3 Mandatory Product Lifecycle State Machine'):
            add_diagram_image(doc, 'workflow_lifecycle_diagram.jpg', 'Mandatory Product State Machine & Tag Reusability Lifecycle')

        if line.startswith('```'):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_buffer = []
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        if '|' in line and not line.startswith('#'):
            in_table = True
            table_rows.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()

        if line.startswith('## '):
            h_text = line.replace('## ', '').strip()
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(h_text)
            r.font.name = "Arial"
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = NAVY
        elif line.startswith('### '):
            h_text = line.replace('### ', '').strip()
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(h_text)
            r.font.name = "Arial"
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = BLUE_ACCENT
        elif line.startswith('#### '):
            h_text = line.replace('#### ', '').strip()
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
            h.paragraph_format.keep_with_next = True
            r = h.add_run(h_text)
            r.font.name = "Arial"
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = CHARCOAL
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            
            parts = re.split(r'(\*\*.*?\*\*)', bullet_text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    r = bp.add_run(part[2:-2])
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    r.font.bold = True
                else:
                    r = bp.add_run(part.replace('`', ''))
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = CHARCOAL
        elif line.strip() == '---':
            pass
        elif line.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    r = p.add_run(part[2:-2])
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    r.font.bold = True
                else:
                    r = p.add_run(part.replace('`', ''))
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = CHARCOAL

        i += 1

    if in_code_block:
        flush_code()
    if in_table:
        flush_table()

    doc.save(OUTPUT_PATH)
    print(f"[SUCCESS] Formal Technical Whitepaper Word Document generated at: {OUTPUT_PATH}")

if __name__ == '__main__':
    generate_whitepaper_docx()
