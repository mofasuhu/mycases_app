import reportlab, rlbidi, pkg_resources, sys
print("ReportLab:", reportlab.Version)          # must be 4.4.0 or newer
print("rlbidi   :", pkg_resources.get_distribution("rlbidi").version)


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("NotoNaskh",  r"fonts/NotoNaskhArabic-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoNaskhBd",r"fonts/NotoNaskhArabic-Bold.ttf"))



from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums  import TA_RIGHT

rtl_style = ParagraphStyle(
    name      = "arabic_normal",
    fontName  = "NotoNaskh",
    fontSize  = 11,
    alignment = TA_RIGHT,   # right aligned
    leading   = 15,
    wordWrap  = "RTL",      # tells ReportLab to do bidi & RTL wrapping
)


import arabic_reshaper
def ar(text):                       # helper
    return arabic_reshaper.reshape(text)  # NO get_display() here


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4

doc = SimpleDocTemplate("rtl_test.pdf", pagesize=A4)
story = []

long_line = "مدى تقبل الأسرة للاضطراب واستعدادها للمشاركة في التأهيل"
story.append(Paragraph(ar(long_line), rtl_style))
story.append(Spacer(1,12))
story.append(Paragraph(ar("سطر قصير"), rtl_style))

doc.build(story)