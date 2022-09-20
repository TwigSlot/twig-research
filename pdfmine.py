from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from collections import defaultdict
# Open a PDF document.
fp = open('example.pdf', 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser)
# Get the outlines of the document.
dictionary=defaultdict(list)
outlines = document.get_outlines()
for (level,title,dest,a,se) in outlines:
    title = title.replace(u'\xa0', u' ')
    print (" ==="*(level-1), title)

