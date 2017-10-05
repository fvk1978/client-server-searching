#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Very simple file indexer
To start:
    python3 cs_indexer.py path_to_directory_with_books
"""
import sys, os, re
import time
import pprint
from cs_sqlite import DB, statements


lines_per_page = 35


def book_parser(book_file, db):
    fp = open(book_file, 'r', encoding='utf-8', errors='ignore')
    page_no = 1
    line_no = 1
    page_text = ''
    for line in fp:
        line = line.strip()
        line = re.sub(' +', ' ', line)
        if line: 
            if '<a name=0>' in line and '<h2>' in line:
                book_title = re.sub('<.*?>', '', line)
                book_title_id = db.save_book_title(book_title)
            elif '<h2>' in line:
                chapter_title = re.sub('<.*?>', '', line)
                chapter_title_id = db.save_chapter_title(chapter_title, book_title_id)
                #print(chapter_title)
            else:
                page_text += line
                page_text += ' '
                #print(page_text)
        if line_no == lines_per_page:
            db.save_book_page(page_text, page_no, book_title_id, chapter_title_id)
            line_no = 0
            page_no += 1
            page_text = ''
        line_no += 1
        #print(page_no)
    fp.close()


if __name__ == '__main__':
    books_path = './books/'
    if len(sys.argv) == 2:
        books_path = sys.argv[1]

    db = DB('books.db', statements)
    for book_file in os.listdir(books_path):
        book_parser(books_path + book_file , db)

