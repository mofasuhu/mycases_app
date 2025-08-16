import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Frame, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

# Try to import Arabic text support libraries
try:
    from bidi.algorithm import get_display
    import arabic_reshaper
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False



# Register fonts for Arabic support
def register_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    pdfmetrics.registerFont(TTFont('MyNoto', os.path.join(font_dir, "NotoNaskhArabic-Regular.ttf")))
    pdfmetrics.registerFont(TTFont('MyNotoBold', os.path.join(font_dir, "NotoNaskhArabic-Bold.ttf")))

    pdfmetrics.registerFont(TTFont('NotoSerif', os.path.join(font_dir, "NotoSerif-Regular.ttf")))
    pdfmetrics.registerFont(TTFont('NotoSerifBold', os.path.join(font_dir, "NotoSerif-Bold.ttf")))
    pdfmetrics.registerFont(TTFont('NotoSerifItalic', os.path.join(font_dir, "NotoSerif-Italic.ttf")))




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




        header_style = ParagraphStyle(
            name='Header',
            fontName=ar_font_name_bold,
            fontSize=18,
            alignment=TA_RIGHT,
            spaceAfter=10,
            wordWrap='RTL'
        )

        subheader_style = ParagraphStyle(
            name='SubHeader',
            fontName=ar_font_name,
            fontSize=10,
            alignment=TA_RIGHT,
            spaceAfter=12,
            wordWrap='RTL'
        )

        sectiontitle_style = ParagraphStyle(
            name='SectionTitle',
            fontName=ar_font_name_bold,
            fontSize=14,
            alignment=TA_RIGHT,
            spaceAfter=12,
            wordWrap='RTL'
        )


        # Prepare doc
        doc = SimpleDocTemplate(custom_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
        story = []

        # Header
        story.append(Paragraph(pdf_ar_fix(f"<b>تقرير استبيان:</b> {survey_data.get('survey_type', '')}"), header_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(pdf_ar_fix(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), subheader_style))
        story.append(Spacer(1, 12))

        # Case data
        if case_data_for_context:
            story.append(Paragraph(pdf_ar_fix("معلومات الحالة"), sectiontitle_style))
            story.append(Spacer(1, 12))
            case_data = [
                [Paragraph(pdf_ar_fix(case_data_for_context.get("case_id", "-")), cell_style), Paragraph(pdf_ar_fix("رقم الحالة"), cell_style_bold)],
                [Paragraph(pdf_ar_fix(case_data_for_context.get("child_name", {}).get("value", "-")), cell_style), Paragraph(pdf_ar_fix("اسم الحالة"), cell_style_bold)],
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
            story.append(Spacer(1, 20))

        # Survey data
        story.append(Paragraph(pdf_ar_fix("بيانات الاستبيان"), sectiontitle_style))
        story.append(Spacer(1, 12))

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
        story.append(Spacer(1, 30))
        story.append(Paragraph(pdf_ar_fix("تم إنشاؤه بواسطة تطبيق MyCases"), ParagraphStyle(name='Footer', fontName=ar_font_name, fontSize=8, alignment=1)))

        # Build PDF (handles automatic page breaks)
        doc.build(story)
        return True, custom_path

    except Exception as e:
        return False, f"Error exporting survey to PDF: {str(e)}"


# Legacy functions for backward compatibility
def export_case_to_pdf(case_folder_name, case_data, surveys_data):
    """Legacy function for backward compatibility."""
    try:
        # Create a default path
        from utils.file_manager import DATA_DIR # type: ignore
        pdf_dir = os.path.join(DATA_DIR, case_folder_name, "exports")
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
            
        pdf_filename = f"Case_Report_{case_folder_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # Use the new function
        success, message = export_survey_to_pdf_with_custom_path(case_folder_name, case_data, pdf_path, None)
        return success, message
    except Exception as e:
        return False, f"Error exporting case to PDF: {str(e)}"

def export_survey_to_pdf(case_folder_name, survey_data, case_data_for_context=None):
    """Legacy function for backward compatibility."""
    try:
        # Create a default path
        from utils.file_manager import DATA_DIR # type: ignore
        pdf_dir = os.path.join(DATA_DIR, case_folder_name, "exports", "surveys")
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        survey_date_str = survey_data.get("survey_date", "nodate").replace("-","")
        survey_type_sanitized = survey_data.get("survey_type", "Survey").split("(")[0].strip().replace(" ", "_")
        pdf_filename = f"Survey_{survey_type_sanitized}_{survey_date_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # Use the new function
        success, message = export_survey_to_pdf_with_custom_path(case_folder_name, survey_data, pdf_path, case_data_for_context)
        return success, message
    except Exception as e:
        return False, f"Error exporting survey to PDF: {str(e)}"






# if __name__ == "__main__":
#     # --- Sample data for testing ---
#     case_data_for_context = {
#         "child_name": {
#             "ar_key": "اسم الحالة",
#             "value": "منار محمد عبد الحفيظ"
#         },
#         "dob": {
#             "ar_key": "تاريخ الميلاد",
#             "value": "2018-09-03"
#         },
#         "age": {
#             "ar_key": "العمر",
#             "value": "6 سنة، 11 شهر، 11 يوم"
#         },
#         "gender": {
#             "ar_key": "الجنس",
#             "value": "أنثى"
#         },
#         "first_language": {
#             "ar_key": "اللغة الأولى",
#             "value": "اللغة العربية - مصر"
#         },
#         "first_language_notes": {
#             "ar_key": "ملاحظات اللغة الأولى",
#             "value": ""
#         },
#         "second_language": {
#             "ar_key": "اللغة الثانية",
#             "value": "لا يوجد"
#         },
#         "second_language_notes": {
#             "ar_key": "ملاحظات اللغة الثانية",
#             "value": ""
#         },
#         "diagnosis": {
#             "ar_key": "التشخيص",
#             "value": "حركي"
#         }
#     }

#     survey_data = {
#         "survey_type": "استبيان التقييم الأول",
#         "survey_date": "2025-07-10",
#         "case_id": "8",
#         "child_name": "منار محمد عبد الحفيظ",
#         "dob": "2018-09-03",
#         "gender": "أنثى",
#         "submission_timestamp": "2025-08-14T12:13:30.611892",
#         "school_attendance": {
#             "ar_key": "هل يذهب الى (المدرسة \\ الحضانة)",
#             "value": "نعم"
#         },
#         "school_year": {
#             "ar_key": "العام الدراسى",
#             "value": ""
#         },
#         "school_duration": {
#             "ar_key": "المدى التى قضاها",
#             "value": ""
#         },
#         "school_type": {
#             "ar_key": "نوعها",
#             "value": ""
#         },
#         "school_discontinue": {
#             "ar_key": "سبب عدم الاستمرار",
#             "value": ""
#         }
#     }

#     # --- Output path ---
#     test_output_path = os.path.abspath("test_survey_export.pdf")

#     # --- Run export ---
#     success, result = export_survey_to_pdf_with_custom_path(
#         case_folder_name="test_case",
#         survey_data=survey_data,
#         custom_path=test_output_path,
#         case_data_for_context=case_data_for_context
#     )

#     if success:
#         print(f"✅ PDF generated successfully: {test_output_path}")
#     else:
#         print(f"❌ Failed to generate PDF: {result}")


