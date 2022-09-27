from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar,LTLine,LAParams, LTAnno
from collections import defaultdict

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


d=defaultdict(int)
fonts = defaultdict(str)
path = "pdf_research/test_pdfs/example.pdf"
PDF_file = open(path, 'rb')

parser = PDFParser(PDF_file)
document = PDFDocument(parser)
try:
    print(list(document.get_outlines())) # TODO for caterpillar
    """
    for your ref,
    https://stackoverflow.com/questions/51436686/extract-text-from-pdf-table-of-contents-ignoring-page-and-indexing-numbers
    it is a list of tuples of (level, title, dest, a (href link like in html), se)
    1) use the level and title info 
    2) use a href info to get the content of that section
            --> see "print(doc)" line of code
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
    raise "bypass"
    exit()
except:
    print("no table of contents zzz, we are gonna have to analyse font size... ")

doc = []

cur_text_block = ""
cur_text_block_size_and_font = (None, None)
for page_layout in extract_pages(PDF_file):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            prev_line = None
            for text_line in element:
                line_fonts = defaultdict(str)
                try:
                    prev_char = None
                    for character in text_line:
                        if isinstance(character, LTChar):
                            Font_size=character.size
                            Font_size = round(character.size)
                            line_fonts[(Font_size, character.fontname)] += character._text
                        elif isinstance(character, LTAnno):
                            line_fonts[(round(prev_char.size), prev_char.fontname)] += character._text
                        prev_char = character
                except:
                    continue
                line_fonts = sorted(list(line_fonts.items()), key = lambda x : len(x[1]))
                if(cur_text_block_size_and_font is not None):
                    if(line_fonts[0][0] == cur_text_block_size_and_font):
                        cur_text_block += line_fonts[0][1]
                    else:
                        doc.append([cur_text_block_size_and_font, cur_text_block])
                        cur_text_block_size_and_font = line_fonts[0][0]
                        cur_text_block = line_fonts[0][1]
                for ((size, font), text) in line_fonts:
                    d[size] += len(text)
                    fonts[(size,font)] += text + " "
for x in range(len(doc)):
    doc[x][1] = doc[x][1].replace('-\n', '')\
                .replace('\n', ' ')\
                .replace(u'\xa0', u' ')
print(doc) # decent segmentation of content based on font sizes (no ML needed)

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


