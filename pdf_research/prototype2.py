from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.request
from hashlib import sha256
from os.path import exists
from pathlib import Path

def convert_pdf_to_html(fp):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0 #is for all
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

pdf_link = 'https://arxiv.org/pdf/1901.06573.pdf'
if pdf_link == '':
    pdf_link = input('gib me link or file path: ')
if('http' not in pdf_link):
    fp = open(pdf_link, 'rb')
else:
    filename = f'pdf_research/test_pdfs/{sha256(pdf_link.encode("utf-8")).hexdigest()}.pdf'
    if(not exists(Path(filename))):
        print('getting file from the web')
        response = urllib.request.urlopen(pdf_link)    
        fp = open(filename, 'wb')
        fp.write(response.read())
        fp.close()
        print('gotten file')
    fp = open(filename, 'rb')
    print('opened pdf file')
test = convert_pdf_to_html(fp)
f = open("pdf_research/html.html", "w")
f.write(str(test))
f.close()


htmlData = open('pdf_research/html.html', 'r')
soup = BeautifulSoup(htmlData,features="html.parser")

font_spans = [ data for data in soup.select('span') if 'font-size' in str(data) ]
output = []
d=defaultdict(list)
for i in font_spans:
    fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
    d[fonts_size.strip()].append(str(i.text).strip())   
print(d)
mostcommonfontsize=-1
count=0

for key in d.keys():
    values=d[key]
    for text in values:
        total=0
        total+=len(text)
    if total>count:
        count=total
        mostcommonfontsize=key
print(mostcommonfontsize)
array=sorted([int(keys) for keys in d.keys()])[::-1]
for i in font_spans:
    fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
    i=i.text
    i=i.replace(u'\\n', u' ')
    if int(fonts_size.strip())>int(mostcommonfontsize):
        print ("=== "*(array.index(int(fonts_size.strip()))),str(i).strip())

    


