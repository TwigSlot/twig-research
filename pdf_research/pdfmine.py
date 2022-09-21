from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from collections import defaultdict
import urllib.request
from hashlib import sha256
# Open a PDF document.

pdf_link = ''
if pdf_link == '':
    pdf_link = input('gib me link or file path: ')
if('http' not in pdf_link):
    fp = open(pdf_link, 'rb')
else:
    response = urllib.request.urlopen(pdf_link)    
    filename = f'test_pdfs/{sha256(pdf_link.encode("utf-8")).hexdigest()}.pdf'
    fp = open(filename, 'wb')
    fp.write(response.read())
    fp.close()
    fp = open(filename, 'rb')

parser = PDFParser(fp)
document = PDFDocument(parser)
# Get the outlines of the document.
dictionary=defaultdict(list)
outlines = document.get_outlines()
for (level,title,dest,a,se) in outlines:
    title = title.replace(u'\xa0', u' ')
    print (" ==="*(level-1), title)
fp.close()
