import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.platypus.flowables import KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib import colors
from PIL import Image as PILImage
import pandas as pd

# Dummy separator generator if not already defined
def draw_separator_page(title):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height / 2, title)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
def create_structured_pdf_feature(output_pdf_path, text_path, image1_path, image2_path, dataframe_csv_path, pdf1_path, pdf2_path):
    temp_pdf = "temp_main_content.pdf"
    doc = SimpleDocTemplate(temp_pdf, pagesize=landscape(A4), rightMargin=40, leftMargin=40, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    page_width, page_height = landscape(A4)

    # -------- Page 1: Text and Two Images -------- #
    with open(text_path, encoding="utf-8") as f:
        text_content = f.read()
        print(text_content)

    # Create header style
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.darkblue,
        alignment=TA_LEFT,
        spaceAfter=12
    )

    # Create content style
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=TA_LEFT
    )

    # Add bold header
    # header_para = Paragraph("<b>ANALYSIS SUMMARY</b>", header_style)
    
    # Add content with proper formatting
    content_para = Paragraph(text_content.replace('\n', '<br/>'), header_style)
    
    # Create frame for content
    content_frame = KeepInFrame(
        page_width - 100, 
        page_height - 200, 
        [content_para], 
        hAlign='LEFT'
    )

    # Add elements to story
    # story.append(header_para)
    story.append(content_frame)
    story.append(Spacer(1, 20))

    # -------- Load Image with Border -------- #
    def load_image_with_border(path, max_width, max_height):
        pil_img = PILImage.open(path)
        orig_width, orig_height = pil_img.size
        aspect_ratio = orig_width / orig_height

        if orig_width > orig_height:
            scaled_width = min(max_width, orig_width)
            scaled_height = scaled_width / aspect_ratio
        else:
            scaled_height = min(max_height, orig_height)
            scaled_width = scaled_height * aspect_ratio

        scaled_width = min(scaled_width, max_width)
        scaled_height = min(scaled_height, max_height)

        buffer = BytesIO()
        pil_img.save(buffer, format='PNG')
        buffer.seek(0)

        img = Image(buffer, width=scaled_width, height=scaled_height)

        img_table = Table([[img]], colWidths=[max_width], rowHeights=[max_height])
        img_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        return img_table

    max_img_width = (page_width - 120) / 2
    max_img_height = page_height * 0.6

    img1_table = load_image_with_border(image1_path, max_img_width, max_img_height)
    img2_table = load_image_with_border(image2_path, max_img_width, max_img_height)

    combined_table = Table([[img1_table, img2_table]], colWidths=[max_img_width] * 2)
    combined_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(combined_table)
    story.append(PageBreak())

    # -------- Page 2: CSV Table -------- #
    df = pd.read_csv(dataframe_csv_path)
    df = df[["key", "summary", "Missing_Columns"]]
    data = [df.columns.tolist()] + df.values.tolist()

    column_widths = [80, (page_width - 180) / 2, (page_width - 180) / 2]
    table = Table(data, colWidths=column_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.95, 1)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(Paragraph("<b>JIRA Issue Summary:</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(table)
    story.append(PageBreak())

    doc.build(story)

    # -------- Merge All PDFs -------- #
    writer = PdfWriter()

    def append_pdf(reader):
        for page in reader.pages:
            writer.add_page(page)

    # Step 1: Append existing output if it exists
    if os.path.exists(output_pdf_path):
        existing_reader = PdfReader(output_pdf_path)
        append_pdf(existing_reader)

    # Step 2: Append new content
    append_pdf(PdfReader(temp_pdf))
    append_pdf(PdfReader(BytesIO(draw_separator_page("Acceptance Criteria suggestion Report"))))
    append_pdf(PdfReader(pdf1_path))
    append_pdf(PdfReader(BytesIO(draw_separator_page(" Summary suggestion Report"))))
    append_pdf(PdfReader(pdf2_path))

    # Step 3: Write final output
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    os.remove(temp_pdf)











create_structured_pdf_feature("outputs/temp.pdf","L2_architecture/Report/output.txt", "L2_architecture/Report/missing_values_dashboard.png", 
                  "L2_architecture/Report/Bad_values_dashboard.png",
                  "L2_architecture/data/Final_API.csv", "L2_architecture/Report/acceptance_report.pdf", 
                  "L2_architecture/Report/summary_report.pdf")

