import sys
import os
import pickle
import fitz
import csv
from extract_textblock import TextBlock

if 'pdf_research' in os.getcwd():
    path = './Classifiers/'
else:
    path = 'pdf_research/Classifiers/'

with open(path+'data.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(TextBlock.headers())
    for i in os.listdir(path):
        if(i[-7:] == '.pickle'):
            with open(path+i, 'rb') as f:
                doc = pickle.load(f)
                for tb in doc:
                    writer.writerow(tb.properties())