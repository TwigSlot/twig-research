from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar,LTLine,LAParams, LTAnno
from collections import defaultdict

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import fitz

import pickle

d=defaultdict(int)
fonts = defaultdict(str)
path = "pdf_research/test_pdfs/a16f4de62b51d42f71ace807b62ba31e6adbf5ef9719981f9178912cc6566477.pdf"
PDF_file = open(path, 'rb')

parser = PDFParser(PDF_file)
document = PDFDocument(parser)
try:
    # print(list(document.get_outlines())) # TODO for caterpillar
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

class TextBlock:
    def __init__(self, font, text, text_lines, page):
        self.font_size = font[0]
        self.fontname = font[1]
        self.text = text
        if(len(text_lines) > 0):
            self.page = page
            self.x0 = min([tl.x0 for tl in text_lines])
            self.x1 = max([tl.x1 for tl in text_lines])
            self.y0 = min([tl.y0 for tl in text_lines])
            self.y1 = max([tl.y1 for tl in text_lines])
        else:
            self.page = -1
            self.x0 = 0
            self.x1 = 0
            self.y0 = 0
            self.y1 = 0
    def drawRect(self, fitz_doc: fitz.Document):
        if(self.page == -1): return
        height = fitz_doc.load_page(self.page-1).rect[3]
        fitz_doc[self.page-1].draw_rect([self.x0, height-self.y1, self.x1, height-self.y0],
            color = (0,1,0), width = 2)

for page_layout in extract_pages(PDF_file):
    cur_text_block = ""
    cur_text_block_size_and_font = (None, None)
    cur_text_block_text_line = []
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
                # take the most common size and fontname
                line_fonts = sorted(list(line_fonts.items()), key = lambda x : len(x[1]))
                if(cur_text_block_size_and_font is not None):
                    # compare it with the previous line
                    # part of the same textblock if same as prev line
                    if(line_fonts[0][0] == cur_text_block_size_and_font):
                        cur_text_block += text_line.get_text()
                        cur_text_block_text_line.append(text_line)
                    # start a new textblock
                    else:
                        doc.append(
                            TextBlock(
                                cur_text_block_size_and_font, 
                                cur_text_block,
                                cur_text_block_text_line,
                                page = page_layout.pageid
                            )
                        )
                        cur_text_block_size_and_font = line_fonts[0][0]
                        cur_text_block = line_fonts[0][1]
                        cur_text_block_text_line = [text_line]
                for ((size, font), text) in line_fonts:
                    d[size] += len(text)
                    fonts[(size,font)] += text + " "
    doc.append(
        TextBlock(
            cur_text_block_size_and_font, 
            cur_text_block,
            cur_text_block_text_line,
            page = page_layout.pageid
        )
    ) 
fitz_doc = fitz.open(PDF_file)
for x in range(len(doc)):
    doc[x].text = doc[x].text.replace('-\n', '')\
                .replace('\n', ' ')\
                .replace(u'\xa0', u' ')
for x in range(len(doc)):
    doc[x].drawRect(fitz_doc)
fitz_doc.save(path.replace('.pdf', '_v2.pdf'))
with open(path.replace('.pdf', '.pickle'), 'wb') as save_file:
    pickle.dump(doc, save_file)

print(doc) # decent segmentation of content based on font sizes (no ML needed)
exit()

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

