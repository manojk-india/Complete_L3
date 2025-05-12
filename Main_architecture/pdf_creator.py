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
