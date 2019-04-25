## Turning the Pygmy into an Amazon: Replication, Caching and Consistency


# Environment Setup

There  is  one  config  file sv_info.py that has server information in the comma-separated format:Type of Server, IP Address, Port. Modify the config files as required to setup the docker environment. There are four Python files catalog.py, order.py, frontend.py and client.py - they represent the catalog server, order server, frontend server and the client respectively.

# Docker Setup
1. Build the docker images for each of the components using 
`docker build -f dockerfile.server_name -t image_name`
, eg. `docker build . -f dockerfile.catalog -t catalog`.
Do this for catalog, frontend, order and client.
2. Create a subnet using `docker network create - -subnet=172.18.0.0/16 mynet123`
3. Run the docker containers using:

    `docker run - -net mynet123 --ip ip_here server_name server_id first_start` for catalog server
    
    `docker run - -net mynet123 --ip ip_here server_name server_id ` for order server
    
    `docker run - -net mynet123 --ip ip_here server_name` for frontend server and client
    
    server_id is zero-indexed (0/1 for the 2 replica case). first_start is 1 for a fresh boot of catalog, 0 for a boot after crash failure.
    
# Libraries used
Framework used - Flask is a micro web framework written in Python. The Flask version
used is 1.0.2


Additional Libraries used - requests (2.9.1), apscheduler (3.6.0)

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




