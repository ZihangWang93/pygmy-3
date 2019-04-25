# Turning the Pygmy into an Amazon: Replication, Caching and Consistency


# Environment Setup

There  is  one  config  file sv_info.py that has server information in the comma-separated format:Type of Server, IP Address, Port. Modify the config files as required to setup the environment. There are four Python filescatalog.py, order.py, frontend.py and client.py- they represent the catalog server, order server, frontend server and the client respectively.

# src File Descriptions

catalog.py - Catalog server

order.py - Order server

frontend.py - Frontend server

client.py - Client

catalog.json - Book details for all books 

order_log.txt - Transaction logs for order server

sv_info.py - Config file for details of servers and their replicas

times - Directory with Response Time logs for search, lookup and buy

time_parser.py - Script to calculate ART (Average Response Time)

# docs File Descriptions

* CS677 Lab 3 Design Doc.pdf - Design document
* Output file showing sample output from runs is included in the Design Document. 
* Performance analysis is included in the Design Document.




