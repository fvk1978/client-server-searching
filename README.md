Small client-server example.

Used instruments:
    python3
    sqlite
    
At first we have to index some files to fill database:
    python3 cs_indexer.py 
    
Then let's start server:
    python3 cs_server.py -p 9090

That's it, test server is available at http://127.0.0.1:9090