from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno
from collections import defaultdict

import fitz

class TextBlock:
    def __init__(self, font, text, text_lines, page):
        self.font_size = font[0]
        self.fontname = font[1]
        self.text = text
        self.text = self.text.replace('-\n', '')\
                .replace('\n', ' ')\
                .replace(u'\xa0', u' ')
        self.begins_with_number = (
            True if len(self.text) > 0 and self.text[0] in '1234567890IVXABCDEFabcdef'
            else False
        )
        self.has_fullstop = ('.' in self.text)
        self.text_length = len(self.text)
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
        self.height = self.y1 - self.y0
        self.size_diff_prev = None
        self.xdiff = None
        self.ydiff = None
        self.isHeader = None
        self.headerLevel  = None
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
    for page_layout in extract_pages(PDF_file):
        cur_text_block = ""
        cur_text_block_size_and_font = (None, None)
        cur_text_block_text_line = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
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
                    if(cur_text_block_size_and_font[0] is not None):
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
                    else:
                        cur_text_block_size_and_font = line_fonts[0][0]
                        cur_text_block = line_fonts[0][1]
                        cur_text_block_text_line = [text_line]
        doc.append(
            TextBlock(
                cur_text_block_size_and_font, 
                cur_text_block,
                cur_text_block_text_line,
                page = page_layout.pageid
            )
        ) 
    return doc