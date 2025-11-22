"""Export rebuttal to various formats"""
import markdown
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def export_as_markdown(rebuttal):
    """
    Export rebuttal as Markdown.

    Args:
        rebuttal: Rebuttal instance

    Returns:
        HttpResponse with Markdown content
    """
    content = f"# {rebuttal.title}\n\n"
    content += f"**Version:** {rebuttal.version}\n\n"
    content += f"**Published:** {rebuttal.published_at.strftime('%Y-%m-%d %H:%M') if rebuttal.published_at else 'Draft'}\n\n"
    content += "---\n\n"

    for section in rebuttal.sections.all():
        content += f"## {section.title}\n\n"
        content += f"{section.content}\n\n"

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="{rebuttal.title.replace(" ", "_")}.md"'
    return response


def export_as_html(rebuttal):
    """
    Export rebuttal as HTML.

    Args:
        rebuttal: Rebuttal instance

    Returns:
        HttpResponse with HTML content
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{rebuttal.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .meta {{
            color: #777;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>{rebuttal.title}</h1>
    <p class="meta">Version: {rebuttal.version}</p>
    <p class="meta">Published: {rebuttal.published_at.strftime('%Y-%m-%d %H:%M') if rebuttal.published_at else 'Draft'}</p>
    <hr>
"""

    for section in rebuttal.sections.all():
        # Convert markdown to HTML
        section_html = markdown.markdown(section.content)
        html += f"<h2>{section.title}</h2>\n{section_html}\n"

    html += """
</body>
</html>
"""

    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="{rebuttal.title.replace(" ", "_")}.html"'
    return response


def export_as_pdf(rebuttal):
    """
    Export rebuttal as PDF.

    Args:
        rebuttal: Rebuttal instance

    Returns:
        HttpResponse with PDF content
    """
    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)

    # Container for PDF elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#333333',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#555555',
        spaceAfter=12,
        spaceBefore=12
    )
    body_style = styles['BodyText']

    # Title
    elements.append(Paragraph(rebuttal.title, title_style))
    elements.append(Spacer(1, 12))

    # Metadata
    meta_text = f"<i>Version: {rebuttal.version} | Published: {rebuttal.published_at.strftime('%Y-%m-%d') if rebuttal.published_at else 'Draft'}</i>"
    elements.append(Paragraph(meta_text, body_style))
    elements.append(Spacer(1, 20))

    # Sections
    for section in rebuttal.sections.all():
        elements.append(Paragraph(section.title, heading_style))

        # Split content into paragraphs
        for para in section.content.split('\n\n'):
            if para.strip():
                elements.append(Paragraph(para.strip(), body_style))
                elements.append(Spacer(1, 12))

        elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)

    # Get PDF data
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{rebuttal.title.replace(" ", "_")}.pdf"'
    return response
