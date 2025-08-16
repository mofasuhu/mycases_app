import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import cm
from utils.file_manager import register_fonts


# Try to import Arabic text support libraries
try:
    from bidi.algorithm import get_display
    import arabic_reshaper
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False


# Function to fix Arabic text for PDF rendering
def pdf_ar_fix(text):
    if not ARABIC_SUPPORT:
        return text
    
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return text


# Function to normalize whitespace in text
def normalize_space(string):
    return str(re.sub(r'\s+', ' ', str(string))).strip()


def export_survey_to_pdf_with_custom_path(survey_data, custom_path, case_data_for_context=None):
    try:
        register_fonts()

        ar_font_name = 'MyNoto'
        ar_font_name_bold = 'MyNotoBold'




        cell_style = ParagraphStyle(
            name='CellStyle',
            fontName=ar_font_name,
            fontSize=10,
            alignment=TA_RIGHT,
            leading=14,
            wordWrap='RTL'
        )

        cell_style_bold = ParagraphStyle(
            name='CellStyleBold',
            fontName=ar_font_name_bold,
            fontSize=10,
            alignment=TA_RIGHT,
            leading=14,
            wordWrap='RTL'
        )


        header_name_style = ParagraphStyle(
            name='HeaderName',
            fontName=ar_font_name_bold,
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.white, # Set text color to white
            wordWrap='RTL'
        )

        header_style = ParagraphStyle(
            name='Header',
            fontName=ar_font_name_bold,
            fontSize=18,
            alignment=TA_RIGHT,
            spaceAfter=25,
            wordWrap='RTL'
        )

        subheader_style = ParagraphStyle(
            name='SubHeader',
            fontName=ar_font_name,
            fontSize=10,
            alignment=TA_RIGHT,
            spaceAfter=15,
            wordWrap='RTL'
        )

        sectiontitle_style = ParagraphStyle(
            name='SectionTitle',
            fontName=ar_font_name_bold,
            fontSize=14,
            alignment=TA_RIGHT,
            spaceAfter=15,
            wordWrap='RTL'
        )


        # Prepare doc
        doc = SimpleDocTemplate(custom_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
        story = []

        # Header with Logo and Centered White Text ---
        logo_path = os.path.join(os.path.dirname(__file__), "..", "icons", "app_icon.png")
        if os.path.exists(logo_path):
            im = Image(logo_path, width=1.5*cm, height=1.5*cm)
            
            if case_data_for_context:
                # Create the Paragraph for the child's name using the new white style
                child_name_paragraph = Paragraph(
                    pdf_ar_fix(case_data_for_context.get("child_name", {}).get("value", "-")),
                    header_name_style
                )

            # Create a table with two cells: one for the logo, one for the name
            header_table_data = [[im, child_name_paragraph]]
            header_table = Table(header_table_data, colWidths=[2*cm, doc.width - 2*cm])
            
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#175606")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertically align content
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),   # Center the logo cell
                ('SPAN', (1, 0), (1, 0)),              # The name cell spans as before
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(header_table)
        
        story.append(Spacer(1, 5)) # Add space after the logo header


        # Header
        story.append(Paragraph(pdf_ar_fix(f"<b>تقرير استبيان:</b> {survey_data.get('survey_type', '')}"), header_style))
        story.append(Paragraph(pdf_ar_fix(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), subheader_style))

        # Case data
        if case_data_for_context:
            story.append(Paragraph(pdf_ar_fix("معلومات الحالة"), sectiontitle_style))
            case_data = [
                [Paragraph(pdf_ar_fix(case_data_for_context.get("case_id", "-")), cell_style), Paragraph(pdf_ar_fix("رقم الحالة"), cell_style_bold)],
                # [Paragraph(pdf_ar_fix(case_data_for_context.get("child_name", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("اسم الحالة"), cell_style_bold)],
                [Paragraph(pdf_ar_fix(case_data_for_context.get("dob", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("تاريخ الميلاد"), cell_style_bold)],
                [Paragraph(pdf_ar_fix(case_data_for_context.get("age", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("العمر"), cell_style_bold)],          
                [Paragraph(pdf_ar_fix(case_data_for_context.get("gender", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("الجنس"), cell_style_bold)],           
                [Paragraph(pdf_ar_fix(case_data_for_context.get("diagnosis", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("التشخيص"), cell_style_bold)],
            ]
            table = Table(case_data, colWidths=[doc.width*0.35, doc.width*0.65])
            table.setStyle(TableStyle([
                ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (1, 0), (1, -1), ar_font_name_bold),
                ('FONTNAME', (0, 0), (0, -1), ar_font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),                
            ]))


            story.append(table)
            story.append(Spacer(1, 10))

        # Survey data
        story.append(Paragraph(pdf_ar_fix("بيانات الاستبيان"), sectiontitle_style))

        survey_table_data = [
            [pdf_ar_fix(survey_data.get("survey_type", "-")), pdf_ar_fix("نوع الاستبيان")],
            [pdf_ar_fix(survey_data.get("survey_date", "-")), pdf_ar_fix("تاريخ الاستبيان")]
        ]

        skip_fields = ['survey_type', 'survey_date', 'submission_timestamp', 'case_id', 'child_name', 'dob', 'gender', '_filename']
        for key, value in survey_data.items():
            if key not in skip_fields and value:
                survey_table_data.append([
                    Paragraph(pdf_ar_fix(value['value']), cell_style) if isinstance(value, dict) else Paragraph(pdf_ar_fix(value), cell_style),
                    Paragraph(pdf_ar_fix(value['ar_key']), cell_style_bold) if isinstance(value, dict) else Paragraph(pdf_ar_fix(key), cell_style_bold)
                ])

        survey_table = Table(survey_table_data, colWidths=[doc.width*0.35, doc.width*0.65])
        survey_table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, -1), ar_font_name_bold),
            ('FONTNAME', (0, 0), (0, -1), ar_font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),            
        ]))
        story.append(survey_table)

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(pdf_ar_fix("تم إنشاؤه بواسطة تطبيق MyCases"), ParagraphStyle(name='Footer', fontName=ar_font_name, fontSize=8, alignment=1)))

        # Build PDF (handles automatic page breaks)
        doc.build(story)
        return True, custom_path

    except Exception as e:
        return False, f"Error exporting survey to PDF: {str(e)}"

