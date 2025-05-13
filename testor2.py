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
from reportlab.lib.units import inch



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
    img = PILImage.open(image_path)
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


create_and_append_pdf_RTBCTB(
    text_file_path="L2_architecture/Report/output.txt",
    image_path="L2_architecture/Report/missing_values_dashboard.png",
    csv_file_path="L2_architecture/data/API.csv",
    output_pdf_path="random_output.pdf"
)