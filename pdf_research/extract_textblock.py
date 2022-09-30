from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno
from collections import defaultdict

import fitz

class TextBlock:
    @classmethod
    def sanitize_text(cls, x):
        return x.replace('-\n', '')\
                .replace('\n', ' ')\
                .replace(u'\xa0', u' ')

    def __init__(self, font, element, page):
        self.font_size = font[0]
        self.fontname = font[1]
        self.text = TextBlock.sanitize_text(element.get_text())
        self.begins_with_number = (
            True if len(self.text) > 0 and self.text[0] in '1234567890IVXABCDEFabcdef'
            else False
        )
        self.has_fullstop = ('.' in self.text)
        self.text_length = len(self.text)
        self.page = page
        self.x0 = element.x0
        self.x1 = element.x1
        self.y0 = element.y0
        self.y1 = element.y1
        self.height = self.y1 - self.y0
        self.size_diff_prev = None
        self.xdiff = None
        self.ydiff = None
        self.isHeader = None
        self.headerLevel  = None

    def append_text(self, new_text):
        self.text += TextBlock.sanitize_text(new_text)
        self.text_length = len(self.text)

    def compare_prev(self, prev):
        self.size_diff_prev = self.font_size - prev.font_size
        self.xdiff = self.x0 - prev.x0 # basically indentation
        self.ydiff = self.height - prev.height
    def properties(self):
        return [
            self.font_size,
            self.fontname,
            self.text,
            self.has_fullstop,
            self.text_length,
            self.x0,
            self.x1,
            self.y0,
            self.y1,
            self.height,
            self.size_diff_prev,
            self.xdiff,
            self.ydiff,
            self.isHeader,
            self.headerLevel
        ]
    def drawRect(self, fitz_doc: fitz.Document):
        if(self.page == -1): return
        height = fitz_doc.load_page(self.page-1).rect[3]
        fitz_doc[self.page-1].draw_rect([self.x0, height-self.y1, self.x1, height-self.y0],
            color = (0,1,0), width = 2)

def extract(PDF_file):
    doc = []
    fitz_doc = fitz.open(PDF_file)
    for page_layout in extract_pages(PDF_file):
        for element in page_layout:
            fitz_doc[page_layout.pageid-1].draw_rect([element.x0, page_layout.height - element.y1, element.x1, page_layout.height - element.y0])
            if isinstance(element, LTTextContainer):
                element_fonts = defaultdict(str)
                for text_line in element:
                    try:
                        prev_char = None
                        for character in text_line:
                            if isinstance(character, LTChar):
                                Font_size=character.size
                                Font_size = round(character.size)
                                element_fonts[(Font_size, character.fontname)] += character._text
                            elif isinstance(character, LTAnno):
                                element_fonts[(round(prev_char.size), prev_char.fontname)] += character._text
                            prev_char = character
                    except:
                        continue
                # take the most common size and fontname
                element_fonts_list = sorted(list(element_fonts.items()), key = lambda x : len(x[1]))
                print(element.get_text())
                for x in list(list(element)[0]):
                    if(isinstance(x,LTChar)):
                        print(x.fontname, x._text)
                    else:
                        print(x._text)
                print("===")
                doc.append(
                    TextBlock(
                        element_fonts_list[0],
                        element,
                        page = page_layout.pageid
                    )
                )
    # fitz_doc.save('pdf_research/test_pdfs/test.pdf')
    return doc

if __name__ == "__main__":
    path = "pdf_research/test_pdfs/0a215e5530b55260a1c1ef3196c3c66b85f87b89549a86e51b009d6c3a9466cc.pdf"
    with open(path, 'rb') as f:
        extract(f)