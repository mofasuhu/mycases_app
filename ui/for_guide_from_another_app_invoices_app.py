import pandas as pd
import re
from bidi.algorithm import get_display
import arabic_reshaper
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from warnings import filterwarnings
filterwarnings("ignore", category=DeprecationWarning)

def normalize_space(string):
    return str(re.sub(r'\s+', ' ', string)).strip(' ').strip('\n').replace(" - - - - - - - "," - ").replace(" - - - - - - "," - ").replace(" - - - - - "," - ").replace(" - - - - "," - ").replace(" - - - "," - ").replace(" - - "," - ").strip(' - ')
    
def pdf_ar_fix(text):
    return get_display(arabic_reshaper.reshape(text))

# Define a function to check if a grade is in Arabic
def is_arabic_grade(grade):
    return any(char.isalnum() and not char.isdigit() for char in grade) and grade not in ["Compensation", "CRM", "Content Task"]


# Function to calculate column widths
def calculate_column_widths(data, font_name, font_size):
    widths = []
    for i in range(len(data[0])):
        col_width = max([pdfmetrics.stringWidth(str(row[i]), font_name, font_size) for row in data])
        widths.append(col_width + 10)  # Add padding
    total_width = sum(widths)
    return widths, total_width

    
file_path = 'consolidated_tutor_data.xlsx'
consolidated_df = pd.read_excel(file_path, dtype=str).fillna("")

for col in consolidated_df.columns:
    consolidated_df[col]=consolidated_df[col].astype(str).apply(normalize_space)
    

pdfmetrics.registerFont(TTFont('NotoSerif', 'fonts/NotoSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('MyNoto', 'fonts/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('MyNotoBold', 'fonts/NotoNaskhArabic-Bold.ttf'))
    

counter=0
for idx, row in consolidated_df.iterrows():
    counter+=1
    print(f'\r{counter}',end=' ')
    pdf_file_path = f"PDFs/{normalize_space(row['Full Name'])}_{row['ID']}.pdf"
    c = canvas.Canvas(pdf_file_path, pagesize=(A4[0]+20, A4[1]+20))
    c.translate(10,10)  
    width, height = A4
    # header
    c.setFont('MyNotoBold', 12)
    c.drawString(25, height - 25, 'Invoice')

    # Box
    c.setLineJoin(1) # round
    c.setLineWidth(1.5)
    box_x,box_y,box_width,box_height=25,height-70,(width/2-30),20

    y_factor=0*0
    c.setFont('MyNotoBold', 10)
    c.drawString(30, height - 45 - y_factor, 'Name:')
    c.rect(box_x, box_y - y_factor, box_width, box_height, stroke=1, fill=0)
    c.setFont('MyNoto', 9)
    c.drawString(box_x + 5, box_y - y_factor + 6.25, pdf_ar_fix(row['Full Name']))

    y_factor=45*1
    c.rect(box_x, box_y - y_factor - 10, box_width, box_height + 10, stroke=1, fill=0)    
    styles = ParagraphStyle(name='', fontName='MyNoto', fontSize=9, textColor='black')
    text = pdf_ar_fix(row['Address'])
    paragraph = Paragraph(text, styles, encoding='utf-8')
    frame = Frame(box_x, box_y - y_factor - 10 - 5, box_width - 5, box_height + 18, showBoundary=0)
    frame.addFromList([paragraph], c)
    c.setFont('MyNotoBold', 10)    
    c.drawString(30, height - 45 -y_factor, 'Address:') 
    
    y_factor=10+45*2
    c.setFont('MyNotoBold', 10)    
    c.drawString(30, height - 45 -y_factor, 'Mobile Number:')
    c.rect(box_x, box_y - y_factor, box_width, box_height, stroke=1, fill=0)
    c.setFont('MyNoto', 9)    
    c.drawString(box_x + 5, box_y - y_factor + 6.25, pdf_ar_fix(row['Mobile']))    

    y_factor=10+45*3
    c.setFont('MyNotoBold', 10)    
    c.drawString(30, height - 45 -y_factor, 'Email Address:')
    c.rect(box_x, box_y - y_factor, box_width, box_height, stroke=1, fill=0)
    c.setFont('MyNoto', 9)    
    c.drawString(box_x + 5, box_y - y_factor + 6.25, pdf_ar_fix(row['Email Address']))    
    
    y_factor=10+45*4
    c.setFont('MyNotoBold', 10)    
    c.drawString(30, height - 45 -y_factor, 'To:')
    c.rect(box_x, box_y - y_factor-30, box_width, box_height+30, stroke=1, fill=0)
    c.setFont('MyNoto', 9)    
    # Create a text object for multiline text
    text = c.beginText()
    text.setTextOrigin(box_x + 5, box_y - y_factor + 6.25)
    text.setFont('MyNoto', 9)
    text.setLeading(15)  # Adjust leading (line spacing) value here
    text.textLines("Nagwa Limited\nYork House, 41 Sheet Street, Windsor, SL4 1DD\nUNITED KINGDOM")
    c.drawText(text)    
    

    y_factor=10+45*4
    c.rect(width - box_x, box_y - y_factor-30, -box_width, box_height+30, stroke=1, fill=0)    
    styles = ParagraphStyle(name='', fontName='MyNoto', fontSize=9, textColor='black', leading=14)
    text = f"{pdf_ar_fix(row['Subjects'])}<br />{pdf_ar_fix(row['Accrual Month'])}"
    paragraph = Paragraph(text, styles, encoding='utf-8')
    frame = Frame(width - box_x - box_width, 104, box_width - 5, 500, showBoundary=0)
    frame.addFromList([paragraph], c)
    c.setFont('MyNotoBold', 10)    
    c.drawString((width/2)+10, height - 45 -y_factor, 'For:')     
    
    
    c.setFont('MyNotoBold', 7)
    c.drawRightString(width - box_x - 125, height - 45, 'Unique Invoice Number:')
    c.rect(width - box_x - 5, height - 50, -115, 15, stroke=1, fill=0)
    c.setFont('MyNoto', 9)
    c.drawCentredString(width - box_x - 5 - 115/2, height - 45.5, row['Invoice Number'])

    c.setFont('MyNotoBold', 7)
    c.drawRightString(width - box_x - 125, height - 45 - 15, 'Invoice Date:')
    c.rect(width - box_x - 5, height - 50 - 15, -115, 15, stroke=1, fill=0)
    c.setFont('MyNoto', 9)
    c.drawCentredString(width - box_x - 5 - 115/2, height - 45.5 - 15, row['Invoice Date'])
    c.setFont('MyNoto', 7)
    c.drawCentredString(width - box_x - 5 - 115/2, height - 45.5 - 30, '(Last day of the month being invoiced)') 
    
    # Define table data
    table_data = [
        ['Description', 'Amount (EGP)'],
    ]

    # Add constant rows
    constant_rows = [
        ['Current Month Amount', f"{float(row['Current Month Amount']):.2f}"],
        ['Previous Months Amount', f"{float(row['Previous Months Amount']):.2f}"],
        ['Free Sessions', f"{float(row['Free Sessions']):.2f}"],
        ['Rehearsals', f"{float(row['Rehearsals']):.2f}"],
        ['Additions', f"{float(row['Additions']):.2f}"],
        ['Deductions', f"-{float(row['Deductions']):.2f}"],
        ['Total', f"{float(row['Total']):.2f}"]
    ]
    table_data.extend(constant_rows)

       
    
    table_data=[list(map(pdf_ar_fix,table)) for table in table_data]
    
    # Calculate column widths
    column_widths, total_width = calculate_column_widths(table_data, 'MyNoto', 10)

    # Calculate scaling factor to fit table within page margins
    page_width = width - 50  # Subtracting 25 units from both sides for margins
    scaling_factor = page_width / total_width
    # Adjust column widths based on scaling factor
    adjusted_column_widths = [w * scaling_factor for w in column_widths]
    # Create table
    table = Table(table_data, colWidths=adjusted_column_widths)

    # Apply table style
    # (col 0-index, row 0-index) for starting cell and end cell (indexing is from top left to bottom right) 
    # and -1 is last index like python list indexing    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'MyNotoBold'),
        ('FONTNAME', (0, 1), (-1, -1), 'MyNoto'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertically align text to the middle
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black), # Add black grid lines
    ]))  

    # Draw the table below the existing content
    table_y = height - (45 * 5 + 240 + 5)  # Adjust this value based on your layout needs
    table.wrapOn(c, width - 50, table_y)  # Ensure table is wrapped before drawing
    table.drawOn(c, 25, table_y)

    
    c.setFont('MyNotoBold', 10)    
    c.drawString(30, 245, 'Payment Details:')   
    
    

    # Define the additional table data
    additional_table_data = [
        ['Account Name', row["Bank Account Name"]],
        ['Bank Name', row["Bank Name"]],
        ['Bank Address', row["Bank Address"]],
        ['□ Account Number\n□ IBAN\n(Tick which it is)', f'{row["Account Number"]}\n{row["Bank Account Number (IBAN)"]}\n'],
        ['□ Swift\n□ BIC\n□ Routing Number\n□ Sort Code\n(Tick which it is)', f'{row["Swift"]}\n\n\n\n'],
        ['Account Type', 'EGP'],
        ['Payment Method', 'Transfer']
    ]
    additional_table_data=[list(map(pdf_ar_fix,table)) for table in additional_table_data]
    
    # Create the additional table
    additional_table = Table(additional_table_data, colWidths=[page_width * 0.2, page_width * 0.8])

    # Apply style to the additional table
    additional_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'NotoSerif'),  
        ('FONTNAME', (-1, 0), (-1, -1), 'MyNoto'),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('FONTSIZE', (1, 0), (1, -1), 9),        
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black), # Add black grid lines
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertically align text to the middle
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))    
    
    # Draw the additional table below the first table
    additional_table_y = table_y - (len(table_data) * 30)  # Adjust this value based on your layout needs
    additional_table.wrapOn(c, width - 50, additional_table_y)
    additional_table.drawOn(c, 25, additional_table_y)
    
    
    c.showPage()
    c.save()    
