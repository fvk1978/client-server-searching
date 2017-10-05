#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3


# let's create tables and indexies
statements = [
"""
CREATE TABLE if not exists books_titles (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  book_title TEXT NOT NULL
);""",
"""
CREATE TABLE if not exists chapters_titles (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  chapter_title TEXT NOT NULL,
  book_title_id integer NOT NULL,
  FOREIGN KEY (book_title_id) REFERENCES books_titles (id)
);""",
"""
CREATE TABLE if not exists books_pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  page_text TEXT NOT NULL,
  page_no INTEGER NOT NULL,
  book_title_id integer NOT NULL,
  chapter_title_id integer NOT NULL,
  FOREIGN KEY (book_title_id) REFERENCES books_titles (id)
  FOREIGN KEY (chapter_title_id) REFERENCES chapters_titles (id)
);""",
"""
CREATE VIRTUAL TABLE if not exists books_pages_index USING fts4(page_text, tokenize=simple);
""",
"""
CREATE TRIGGER after_books_pages_insert AFTER INSERT ON books_pages BEGIN
  INSERT INTO books_pages_index (
    rowid,
    page_text
  )
  VALUES(
    new.id,
    new.page_text
  );
END;""",
"""
-- Trigger on UPDATE
CREATE TRIGGER after_books_pages_update UPDATE OF page_text ON books_pages BEGIN
  UPDATE books_pages_index SET page_text = new.page_text WHERE rowid = old.id;
END;""",
"""
-- Trigger on DELETE
CREATE TRIGGER after_books_pages_delete AFTER DELETE ON books_pages BEGIN
    DELETE FROM books_pages_index WHERE rowid = old.id;
END;"""]


class DB(object):    
    """DB initializes and manipulates SQLite3 databases."""

    def __init__(self, database='books.db', statements=[]):
        """Initialize a new or connect to an existing database.

        Accept setup statements to be executed.
        """

        #the database filename
        self.database = database
        #holds incomplete statements
        self.statement = ''
        #indicates if selected data is to be returned or printed
        self.display = False

        self.connect()

        #execute setup satements
        for statement in statements:
            try:
                self.cursor.executescript(statement)
            except sqlite3.OperationalError as error:
                print('Warning:', error.args[0])

        self.close()            

    def connect(self):
        """Connect to the SQLite3 database."""

        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.connected = True
        self.statement = ''

    def close(self): 
        """Close the SQLite3 database."""

        self.connection.commit()
        self.connection.close()
        self.connected = False

    def create_tables(self):
        self.connect()
        for statement in statements:
            try:
                self.cursor.executescript(statement)
            except sqlite3.OperationalError as error:
                print('An error occurred:', error.args[0])
        self.close()

    def save_book_title(self, title):
        self.connect()
        self.cursor.execute(
            "INSERT INTO books_titles (book_title) values (?);", (title,))
        self.close()
        return self.cursor.lastrowid

    def save_chapter_title(self, title, book_title_id):
        self.connect()
        self.cursor.execute(
            "INSERT INTO chapters_titles (chapter_title, book_title_id)"\
            "values (?, ?);", (title, book_title_id))
        self.close()
        return self.cursor.lastrowid

    def save_book_page(self, page_text, page_no, book_title_id, chapter_title_id):
        self.connect()
        self.cursor.execute(
            "INSERT INTO books_pages (page_text, page_no, book_title_id, chapter_title_id) "\
                "values (?, ?, ?, ?);", (page_text, page_no, book_title_id, chapter_title_id))
        self.close()
        return self.cursor.lastrowid

    def get_page_attrs(self, page_id):
        self.connect()
        self.cursor.execute(
            "SELECT page_no, book_title_id, chapter_title_id FROM books_pages "\
            "WHERE id = %d " % page_id)
        page_no, book_title_id, chapter_title_id = self.cursor.fetchone()
        self.cursor.execute(
            "SELECT book_title FROM books_titles "\
            "WHERE id = %d " % book_title_id)
        book_title = self.cursor.fetchone()[0]
        self.cursor.execute(
            "SELECT chapter_title FROM chapters_titles "\
            "WHERE id = %d " % chapter_title_id)
        chapter_title = self.cursor.fetchone()[0]
        self.close()
        return book_title, chapter_title, page_no
        
    def search(self, search_text):
        self.connect()
        self.cursor.execute(
            "SELECT rowid FROM books_pages_index WHERE books_pages_index "\
            "MATCH 'page_text:%s';" % search_text)
        result = [i[0] for i in self.cursor.fetchall()]
        self.close()
        return result


if __name__ == '__main__':     
    database = 'books.db'
    db = DB(database, statements)

    print(db.search('could see that bit'))
    print(db.get_page_attrs(4))
    for page_no in db.search('could see that bit'):
        print(db.get_page_attrs(page_no))

