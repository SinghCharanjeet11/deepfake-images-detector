"""
PDF report generator using ReportLab.
"""
import os
import tempfile
from datetime import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ImageAndFlowables
from reportlab.graphics.shapes import Drawing, Circle, Rect, String, Polygon, PolyLine
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from database.models import DetectionResult

BRAND_DARK = colors.HexColor("#0B1120")
BRAND_BLUE = colors.HexColor("#1D4ED8")
BRAND_BG = colors.HexColor("#f8fafc")
LABEL_REAL = colors.HexColor("#10B981")
LABEL_FAKE = colors.HexColor("#EF4444")

def draw_seal(label, is_real):
    d = Drawing(80, 80)
    col = LABEL_REAL if is_real else LABEL_FAKE
    # Outer circle
    d.add(Circle(40, 40, 36, fillColor=colors.white, strokeColor=col, strokeWidth=2))
    d.add(Circle(40, 40, 32, fillColor=None, strokeColor=col, strokeWidth=0.8))
    d.add(String(40, 52, "AUTHENTIC" if is_real else "FAKE", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8, fillColor=col))
    d.add(String(40, 24, "VERIFIED" if is_real else "MANIPULATED", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7, fillColor=col))
    if is_real:
        d.add(PolyLine([28, 40, 36, 32, 52, 48], strokeColor=col, strokeWidth=2.5))
    else:
        d.add(PolyLine([32, 48, 48, 32], strokeColor=col, strokeWidth=2.5))
        d.add(PolyLine([32, 32, 48, 48], strokeColor=col, strokeWidth=2.5))
    return d

def make_bg_rect(is_real):
    d = Drawing(80, 80)
    col = LABEL_REAL if is_real else LABEL_FAKE
    d.add(Circle(40, 40, 30, fillColor=col, strokeColor=None))
    if is_real:
        d.add(PolyLine([28, 40, 36, 30, 52, 50], strokeColor=colors.white, strokeWidth=3.5))
    else:
        d.add(PolyLine([30, 50, 50, 30], strokeColor=colors.white, strokeWidth=3.5))
        d.add(PolyLine([30, 30, 50, 50], strokeColor=colors.white, strokeWidth=3.5))
    return d

def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 35)
    canvas.setStrokeColorRGB(0.96, 0.96, 0.96)
    canvas.setFillColorRGB(0.96, 0.96, 0.96)
    canvas.translate(300, 400)
    canvas.rotate(30)
    canvas.drawCentredString(0, 0, "AI Generated Report - For Verification Purposes Only")
    canvas.restoreState()

def generate_pdf_report(record: DetectionResult) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", prefix=f"report_{record.id[:8]}_", delete=False)
    tmp.close()
    pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    logo_td = Paragraph("<font size=20 color='#1D4ED8'>🛡️</font>", styles["Normal"])
    
    title_td1 = Paragraph("<font size=24 color='#0B1120'><b>Deepfake Detection Report</b></font>", ParagraphStyle('CT1', parent=styles['Normal'], alignment=TA_CENTER, leading=28))
    title_td2 = Paragraph("<font size=10 color='gray'>AI &amp; Image Authenticity Platform</font>", ParagraphStyle('CT2', parent=styles['Normal'], alignment=TA_CENTER, leading=14))
    title_cell = [title_td1, Spacer(1, 0.2*cm), title_td2]
    
    vbadge = Paragraph("<font size=10 color='#1D4ED8'><b>DeepDetect<br/>v1.0</b></font>", ParagraphStyle('RT', parent=styles['Normal'], alignment=TA_RIGHT, leading=14))
    
    ht = Table([[logo_td, title_cell, vbadge]], colWidths=[2.5*cm, 11*cm, 3.5*cm])
    ht.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(ht)
    story.append(Spacer(1, 1*cm))

    # Verdict block
    is_real = record.label == "real"
    col = LABEL_REAL if is_real else LABEL_FAKE
    bg_col = colors.HexColor("#F8FAF9")
    
    verd_p1 = Paragraph(f"<font size=10 color='gray'>VERDICT</font>", ParagraphStyle('VC1', parent=styles['Normal'], alignment=TA_CENTER, leading=12))
    verd_p2 = Paragraph(f"<font size=42 color='{col.hexval()}'><b>{record.label.upper()}</b></font>", ParagraphStyle('VC2', parent=styles['Normal'], alignment=TA_CENTER, leading=50))
    verd_p3 = Paragraph(f"<font size=9 color='gray'>Confidence Score</font>", ParagraphStyle('VC3', parent=styles['Normal'], alignment=TA_CENTER, leading=12))
    verd_p4 = Paragraph(f"<font size=18 color='{col.hexval()}'><b>{(record.confidence or 0)*100:.2f}%</b></font>", ParagraphStyle('VC4', parent=styles['Normal'], alignment=TA_CENTER, leading=22))

    verd_cell = [verd_p1, Spacer(1, 0.3*cm), verd_p2, Spacer(1, 0.5*cm), verd_p3, Spacer(1, 0.2*cm), verd_p4]

    vtable = Table([[make_bg_rect(is_real), verd_cell, draw_seal(record.label, is_real)]], colWidths=[4.5*cm, 8.5*cm, 4.5*cm])
    vtable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_col),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, col),
        ('TOPPADDING', (0,0), (-1,-1), 25),
        ('BOTTOMPADDING', (0,0), (-1,-1), 25),
    ]))
    story.append(vtable)
    story.append(Spacer(1, 1*cm))

    # Summary
    stitle = Paragraph("<font size=10 color='#1D4ED8'><b>📊 ANALYSIS SUMMARY</b></font>", styles["Normal"])
    sdesc = Paragraph(f"<font size=9 color='gray'>Our AI model has analyzed the image and determined it to be <font color='{col.hexval()}'><b>{record.label.upper()}</b></font> with a high confidence score.</font>", styles["Normal"])
    story.append(stitle)
    story.append(Spacer(1, 0.3*cm))
    story.append(sdesc)
    story.append(Spacer(1, 0.5*cm))

    cc_style = ParagraphStyle('CC', parent=styles['Normal'], alignment=TA_CENTER, leading=14)
    c1 = Paragraph("<font color='gray' size=9>Face Detection</font><br/><br/><font color='#10B981' size=10><b>Detected</b></font>", cc_style)
    c2 = Paragraph("<font color='gray' size=9>AI Analysis</font><br/><br/><font color='#10B981' size=10><b>Completed</b></font>", cc_style)
    c3 = Paragraph(f"<font color='gray' size=9>Tamper Check</font><br/><br/><font color='{col.hexval()}' size=10><b>{'No Issues Found' if is_real else 'Suspicious Patterns'}</b></font>", cc_style)
    c4 = Paragraph(f"<font color='gray' size=9>Overall Assessment</font><br/><br/><font color='#F59E0B' size=10><b>{'Authentic' if is_real else 'Manipulated'}</b></font>", cc_style)
    
    ctable = Table([[c1, c2, c3, c4]], colWidths=[4.25*cm]*4)
    ctable.setStyle(TableStyle([
        ('BOX', (0,0), (0,0), 0.5, colors.lightgrey),
        ('BOX', (1,0), (1,0), 0.5, colors.lightgrey),
        ('BOX', (2,0), (2,0), 0.5, colors.lightgrey),
        ('BOX', (3,0), (3,0), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(ctable)
    story.append(Spacer(1, 1*cm))

    # Details Table
    dtitle = Paragraph("<font size=10 color='#1D4ED8'><b>📄 FILE &amp; ANALYSIS DETAILS</b></font>", styles["Normal"])
    story.append(dtitle)
    story.append(Spacer(1, 0.3*cm))

    completed = record.completed_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if record.completed_at else "—"
    
    tdata = [
        ["Field", "Value"],
        ["Job ID", record.id],
        ["Filename", record.filename],
        ["File size", f"{record.file_size / 1024:.1f} KB"],
        ["File type", record.mime_type],
        ["Analyzed at", completed],
        ["Label", Paragraph(f"<font color='{col.hexval()}'><b>{record.label.upper()}</b></font>", styles["Normal"])],
        ["Confidence", Paragraph(f"<font color='{col.hexval()}'><b>{(record.confidence or 0)*100:.2f}%</b></font>", styles["Normal"])],
    ]
    dtable = Table(tdata, colWidths=[4.5*cm, 12.5*cm])
    dtable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(dtable)
    story.append(Spacer(1, 1*cm))

    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    return pdf_path
