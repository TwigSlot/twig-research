import sys
import os
import pickle
import fitz
import csv
from extract_textblock import TextBlock

if 'pdf_research' in os.getcwd():
    write_path = './Classifiers/'
    read_path = './test_pdfs/'
else:
    write_path = 'pdf_research/Classifiers/'
    read_path = './pdf_research/test_pdfs/'

with open(write_path+'data.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(TextBlock.headers())
    for i in os.listdir(read_path):
        if(i[-7:] == '.pickle'):
            with open(read_path+i, 'rb') as f:
                doc = pickle.load(f)
                for tb in doc:
                    writer.writerow(tb.properties())