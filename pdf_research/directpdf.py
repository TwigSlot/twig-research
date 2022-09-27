from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar,LTLine,LAParams
from collections import defaultdict
d=defaultdict(int)
fonts = defaultdict(str)
PDF_file = open('./pdf_research/test_pdfs/example.pdf', 'rb')

for page_layout in extract_pages(PDF_file):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                line_fonts = defaultdict(str)
                try:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            Font_size=character.size
                            Font_size = round(character.size)
                            line_fonts[(Font_size, character.fontname)] += character._text
                except:
                    continue
                for ((size, font), text) in line_fonts.items():
                    d[size] += len(text)
                    fonts[(size,font)] += text + "\n"
mostcommonfontsize=-1
localMax=0
#this dict stores the value of the font and number of chars with font 
for key in d.keys():
    if d[key]>localMax:
        localMax=d[key]
        mostcommonfontsize=key
sortedkeys=sorted([key for key in d.keys()])
sortedkeys=sortedkeys[::-1]
print(d)
print(fonts)
for page_layout in extract_pages(PDF_file):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                try:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            Font_size=character.size
                except:continue
                text_line=text_line.get_text()
                text_line=text_line.replace(u'\n', u' ')
                if round(Font_size)>mostcommonfontsize:
                    print("=== "*(sortedkeys.index(round(Font_size))),text_line)


