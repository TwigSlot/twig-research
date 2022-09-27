from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar,LTLine,LAParams
from collections import defaultdict

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


d=defaultdict(int)
fonts = defaultdict(str)
path = "pdf_research/test_pdfs/371d526793649d12487cba5350aeda7888422af1428933d094ca8cbfb64209c3.pdf"
PDF_file = open(path, 'rb')

parser = PDFParser(PDF_file)
document = PDFDocument(parser)
try:
    print(list(document.get_outlines())) # TODO for caterpillar
    """
    for your ref,
    https://stackoverflow.com/questions/51436686/extract-text-from-pdf-table-of-contents-ignoring-page-and-indexing-numbers
    it is a list of tuples of (level, title, dest, a (href link like in html), se)
    use the level and title info 
    use a href info to get the content of that section
    to create a json "TREE" of the document
    i.e.
    everything_in_json = {
        'Short-term ...' : {
            'Abstract': {
                'content of abstract here'
            },
            'Introduction': {
                'introduction body here'
            }
        }
    }
    """
    exit()
except:
    print("no table of contents zzz, we are gonna have to analyse font size... ")

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
                    fonts[(size,font)] += text + " "

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


