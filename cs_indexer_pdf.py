#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Very simple file indexer
To start:
    python3 cs_indexer.py path_to_directory_with_pdf_files
"""
import sys, os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from io import StringIO, BytesIO
import time
import pprint


def parse(filename, maxlevel):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    metadata = doc.info[0]
    title = metadata['Title']
    author = metadata['Author']

    outlines = doc.get_outlines()
    for (level, title, dest, a, se) in outlines:
        print(level, title, dest, a, se)
        if level <= maxlevel:
            title_words = title \
                          .replace('\n', '') \
                          .split()
            title = ' '.join(title_words)
            print(' ' * level, title)

def pdf_parser(pdf_file):
    rsrcmgr = PDFResourceManager()
    out_str = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, out_str, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Extract text
    fp = open(pdf_file, 'rb')
    # Process each page contained in the document.
    for (pageno, page) in enumerate(PDFPage.get_pages(fp)):
        interpreter.process_page(page)
        results = out_str.getvalue()
        pprint.pprint(page.annots)
        print(results)
        if pageno == 8: break
    print("Page = %d" % pageno)
    fp.close()
    out_str.close()


if __name__ == '__main__':
    pdf_path = './pdf/'
    if len(sys.argv) == 2:
        pdf_path = sys.argv[1]

    for pdf_file in os.listdir(pdf_path):
        if '.pdf' in pdf_file:
            pdf_parser(pdf_path + pdf_file)
            parse(pdf_path + pdf_file, 10)

