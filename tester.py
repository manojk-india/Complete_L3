# Have to still research about a good way of presentation of the output

from reportlab.lib.pagesizes import landscape, A4,portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, PageBreak, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
import pandas as pd
from io import BytesIO
from PIL import Image as PILImage

def create_pdf(pdf_path, image_path, text_path, csv_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    page_width, page_height = landscape(A4)

    # --- Page 1: Text Content ---
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
    story.append(Paragraph(f"<b>Analysis Results:</b><br/><br/>{text_content.replace(chr(10), '<br/>')}", text_style))
    story.append(PageBreak())

    # --- Page 2: Image (Guaranteed Fit) ---
    pil_img = PILImage.open(image_path)
    img_buffer = BytesIO()
    pil_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Load into ReportLab Image
    img = Image(img_buffer)
    # Restrict image size to fit within page margins and allow for heading
    img._restrictSize(page_width - 100, page_height - 150)  # leave room for heading and margins

    story.append(Paragraph("<b>JIRA Hygiene Dashboard</b>", styles['Heading2']))
    story.append(KeepInFrame(page_width - 100, page_height - 150, [img], hAlign='CENTER'))
    story.append(PageBreak())

    # --- Page 3: Data Table ---
    df = pd.read_csv(csv_path)
    cols_to_remove = {'acceptance_crieteria', 'issue_type', 'parent_key', 
                     'project_key','description','components','reporter','labels'}
    df = df.drop(columns=[c for c in df.columns if c in cols_to_remove], errors='ignore')

    data = [df.columns.tolist()] + df.values.tolist()
    num_cols = len(df.columns)
    col_width = (page_width - 100) / num_cols if num_cols else 100

    table = Table(data, 
                colWidths=[col_width]*num_cols, 
                repeatRows=1,
                hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(Paragraph("<b>JIRA Data Summary:</b>", styles['Heading2']))
    story.append(table)

    doc.build(story)

# Example call
create_pdf(
    "output.pdf",
    "L1_architecture/outputs/jira_hygiene_dashboard.png",
    "L1_architecture/outputs/output.txt",
    "L1_architecture/generated_files/current.csv"
)

# hello