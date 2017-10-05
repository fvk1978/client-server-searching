#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Very simple server
To start:
    python3 cs_server.py -p 9090
    then "(lynx|opera|whatever) http://127.0.0.1:9090"
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Manager
import smtplib
from email.mime.text import MIMEText
import getopt
import sys
import time
import cgi
import logging
from cs_sqlite import DB


logger = logging.getLogger('cs_server')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('cs.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class SimpleServer(BaseHTTPRequestHandler):

    def __init__(self, *args):
        self.db = DB()
        self.search_result = Manager().list()
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        template_file = open('cs_index.tmpl', encoding='utf-8')
        html = template_file.read()
        template_file.close()
        # Write content as utf-8 data
        self.wfile.write(bytes(html, "utf8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        postvars = cgi.parse_qs(post_data, keep_blank_values=1)
        email = postvars[b'email'][0].decode("utf-8") 
        search_text = postvars[b'search_text'][0].decode("utf-8") 
        
        started = time.time()
        found_pages = self.db.search(search_text)
        logger.info("Searched for '%s', elapsed time = %d ms" % (search_text, (time.time()-started)*1000))
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        resp_list = [
            '<html>',
            '  <head>',
            '    <title>Test Form Response</title>',
            '  </head>',
            '  <body>',
            '  <h1>Test Form Response</h1>',
            '    <p>You searched for "%s".</p>' % search_text,
            '    <p>The results will be sent to %s.</p>' % email,
            '  </body>',
            '</html>',
        ]
        for resp in resp_list:
            self.wfile.write(resp.encode('utf-8'))
            
        #self.get_results(found_pages, email)
        p = Process(target=self.get_results, name="get_results", args=(found_pages, self.search_result, ))
        p.start()
        # Wait a maximum of 2 seconds for get_results
        p.join(2)
        # If thread is active
        if p.is_alive():
            logger.info("get_results is running... let's stop it...")

            # Terminate get_results
            p.terminate()
            p.join()
        
        self.send_email(email)

    def get_results(self, found_pages, search_result):
        started = time.time()
        # Test if process terminating works
        #time.sleep(10)
        for page in found_pages:
            search_result.append(self.db.get_page_attrs(page))
        logger.info("Receiving data, elapsed time = %d ms" % ((time.time()-started)*1000))

    def send_email(self, email):
        msg = 'Your books set:\n'
        for book_title, chapter_title, page_no in self.search_result[:]:
            msg += "Book: {0}, chapter: {1}, on page {2}\n".format(book_title, chapter_title, page_no)
        msg = MIMEText(msg)
        msg['Subject'] = 'Your search results are ready'
        msg['From'] = 'user@localhost'
        msg['To'] = email
        
        # Send the message via local SMTP server
        s = smtplib.SMTP('localhost')
        s.sendmail('user@localhost', [email], msg.as_string())
        s.quit()


def usage():
    sys.stderr.write("""
Usage: python3 cs_server.py -p port

Examples:
    cs_server.py -p 9090
""")
    sys.exit(1)


def main():
    try:
        (opts, files) = getopt.getopt(sys.argv[1:], "p:")
    except getopt.GetoptError as msg:
        usage()

    if len(opts) == 0 or sys.argv[1] == '--help':
        usage()

    # let's init some variables
    port = 9090
    for opt in opts:
        if opt[0] in ['-p']:
            port = int(opt[1])

    try:
        server = HTTPServer(('', port), SimpleServer)
        print('Started httpserver on port ', port)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        server.socket.close()
        sys.exit(1)


if __name__ == '__main__':
    main()
