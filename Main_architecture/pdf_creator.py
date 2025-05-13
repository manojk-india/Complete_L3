from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, PageBreak, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
import pandas as pd
from io import BytesIO
from PIL import Image as PILImage
import os
from PyPDF2 import PdfReader, PdfWriter,PdfMerger
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image, Table, TableStyle,
    PageBreak, KeepInFrame, Spacer
)
import tempfile
from reportlab.pdfgen import canvas


# creating pdf for L1 level here 
def create_pdf(pdf_path, image_path, text_path, csv_path):
    # Step 1: Generate a new PDF in memory or temp file
    temp_pdf_path = "outputs/temp_generated.pdf"
    doc = SimpleDocTemplate(temp_pdf_path, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    page_width, page_height = landscape(A4)

    # --- Page 1: Text + Image ---
    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.darkblue,
        alignment=TA_LEFT
    )
    
    with open(text_path, encoding="utf-8") as f:
        text_content = f.read()
    text_para = Paragraph(f"<b>Analysis Results:</b><br/><br/>{text_content.replace(chr(10), '<br/>')}", text_style)

    pil_img = PILImage.open(image_path)
    img_buffer = BytesIO()
    pil_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img = Image(img_buffer)

    max_img_width = (page_width - 100) / 2
    max_img_height = page_height - 180
    img._restrictSize(max_img_width, max_img_height)

    text_frame = KeepInFrame(max_img_width, max_img_height, [text_para], hAlign='LEFT', mode='shrink')
    img_frame = KeepInFrame(max_img_width, max_img_height, [img], hAlign='CENTER', mode='shrink')

    table = Table([[text_frame, img_frame]], colWidths=[max_img_width, max_img_width])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey)
    ]))
    story.append(table)
    story.append(PageBreak())

    # --- Page 2: CSV Table Summary ---
    df = pd.read_csv(csv_path)
    cols_to_remove = {'acceptance_crieteria', 'issue_type', 'parent_key', 
                      'project_key','description','components','reporter','labels','sprint_status','acceptance_result','acceptance_improvement','quality_check'}
    df = df.drop(columns=[c for c in df.columns if c in cols_to_remove], errors='ignore')

    data = [df.columns.tolist()] + df.values.tolist()
    num_cols = len(df.columns)
    col_width = (page_width - 100) / num_cols if num_cols else 100

    table = Table(data, 
                  colWidths=[col_width]*num_cols, 
                  repeatRows=1,
                  hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(Paragraph("<b>JIRA Data Summary:</b>", styles['Heading2']))
    story.append(table)

    doc.build(story)

    # Step 2: Merge temp PDF into existing one
    writer = PdfWriter()

    # If existing PDF exists, read and append its pages
    if os.path.exists(pdf_path):
        reader_existing = PdfReader(pdf_path)
        for page in reader_existing.pages:
            writer.add_page(page)

    # Add new pages from generated PDF
    reader_new = PdfReader(temp_pdf_path)
    for page in reader_new.pages:
        writer.add_page(page)

    # Save the final merged PDF
    with open(pdf_path, "wb") as f:
        writer.write(f)

    # Clean up temporary file
    os.remove(temp_pdf_path)



# common for everything 
def merge_pdfs(pdf_path1, pdf_path2, output_path):
    merger = PdfMerger()
    
    # Add the two PDFs
    merger.append(pdf_path1)
    merger.append(pdf_path2)

    
    # Write out the merged PDF
    with open(output_path, 'wb') as f_out:
        merger.write(f_out)
    merger.close()
    print(f"Merged PDF saved to: {output_path}")



def draw_separator_page(whats_next:str):
    from reportlab.pdfgen import canvas
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(420, 300, f"--- NEXT : {whats_next} ---")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def create_structured_pdf_feature(output_pdf_path, text_path, image1_path, image2_path, dataframe_csv_path, pdf1_path, pdf2_path):
    temp_pdf = "temp_main_content.pdf"
    doc = SimpleDocTemplate(temp_pdf, pagesize=landscape(A4), rightMargin=40, leftMargin=40, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    page_width, page_height = landscape(A4)

    # -------- Page 1: Text and Two Images -------- #
    with open(text_path, encoding="utf-8") as f:
        text_content = f.read()

    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=TA_LEFT
    )

    text_para = Paragraph(f"<b>Summary:</b><br/><br/>{text_content}", text_style)
    text_frame = KeepInFrame(page_width - 100, page_height - 150, [text_para], hAlign='LEFT')
    story.append(text_frame)

    def load_image_with_border(path, max_width, max_height):
        pil_img = PILImage.open(path)
        orig_width, orig_height = pil_img.size
        aspect_ratio = orig_width / orig_height

        # Calculate scaled dimensions preserving aspect ratio
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

    story.append(Spacer(1, 20))
    story.append(text_frame)
    story.append(Spacer(1, 20))
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

# # Example usage:
# create_structured_pdf("outputs/check.pdf","L2_architecture/Report/output.txt", "L2_architecture/Report/missing_values_dashboard.png", 
#                   "L2_architecture/Report/Bad_values_dashboard.png",
#                   "L2_architecture/data/Final_API.csv", "L2_architecture/Report/acceptance_report.pdf", 
#                   "L2_architecture/Report/summary_report.pdf")


# creating pdf cretor function for L2 level RTB/CTB classification
def create_and_append_pdf_RTBCTB(text_file_path, image_path, csv_file_path, output_pdf_path):
    # Use A4 in landscape orientation
    page_size = landscape(A4)
    width, height = page_size

    # Step 1: Create PDF for text + image
    temp_text_image_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    c = canvas.Canvas(temp_text_image_pdf, pagesize=page_size)

    # Draw text from file
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()

    text_object = c.beginText(40, height - 60)
    text_object.setFont("Helvetica", 11)
    for line in text_content.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Draw image below text
    img = Image.open(image_path)
    img_width, img_height = img.size
    aspect = img_height / img_width

    text_lines = len(text_content.splitlines())
    text_height = 12 * text_lines + 60

    max_width = width - 80
    max_height = height - text_height - 60
    img_width = min(max_width, img_width)
    img_height = img_width * aspect
    if img_height > max_height:
        img_height = max_height
        img_width = img_height / aspect

    x_img = (width - img_width) / 2
    y_img = 40
    c.drawImage(image_path, x_img, y_img, img_width, img_height)

    c.showPage()
    c.save()

    # Step 2: Create PDF for table
    temp_table_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    df = pd.read_csv(csv_file_path)
    df = df[['key', 'summary', 'Requested_by']]

    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1, colWidths=[2.5 * inch, 5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    doc = SimpleDocTemplate(temp_table_pdf, pagesize=page_size)
    doc.build([table])

    # Step 3: Merge text-image and table PDFs
    merged_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    writer = PdfWriter()
    for temp_pdf in [temp_text_image_pdf, temp_table_pdf]:
        reader = PdfReader(temp_pdf)
        for page in reader.pages:
            writer.add_page(page)
    with open(merged_pdf, "wb") as f:
        writer.write(f)

    # Step 4: Append to output PDF (if exists)
    final_writer = PdfWriter()
    if os.path.exists(output_pdf_path):
        with open(output_pdf_path, "rb") as existing:
            reader = PdfReader(existing)
            for page in reader.pages:
                final_writer.add_page(page)

    new_pages = PdfReader(merged_pdf)
    for page in new_pages.pages:
        final_writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        final_writer.write(f)

    # Cleanup
    os.remove(temp_text_image_pdf)
    os.remove(temp_table_pdf)
    os.remove(merged_pdf)

    print(f"✅ Appended landscape A4 pages to '{output_pdf_path}' successfully.")
