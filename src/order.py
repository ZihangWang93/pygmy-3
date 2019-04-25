#!flask/bin/python
import datetime
import os
import sys
from time import time

import pandas as pd
import requests
from flask import Flask, request
import random
import time

# Initializing the book names as per the assignment
book_names = {'1': 'How to get a good grade in 677 in 20 minutes a day',
              '2': 'RPCs for Dummies',
              '3': 'Xen and the Art of Surviving Graduate School',
              '4': 'Cooking for the Impatient Graduate Student',
              '5': 'How to finish Project 3 on time',
              '6': 'Why theory classes are so hard',
              '7': 'Spring in the Pioneer Valley'}

# How to finish Project 3 on time
# Why theory classes are so hard.
# Spring in the Pioneer Valley

# Initializing the available topics
topic_names = ['ds', 'gs']

app = Flask(__name__)

# Creating the log file along with starting the server
if not os.path.isfile('order_log.txt'):
    logs = open("order_log.txt", "x")
    logs.close()

# Randomizing with adding a random amount of time between 0 - 100 ms
ELECTION_TIMEOUT = 200
HEARTBEAT_TIMEOUT = 50

# RAFT STATES
# 0 : Follower (Default)
# 1 : Candidate
# 2 : Leader
NODE_STATE = 0
TERM = 0

commitIndex = None # initialized to 0, increases monotonically
lastApplied = None # initialized to 0, increases monotonically

nextIndex = None # List: initialized to leader last log index + 1
matchIndex = None # initialized to 0, increases monotonically


# REST endpoint for buy
@app.route('/buy', methods=['GET'])
def buy_order():
    if NODE_STATE != 2:
        print("Got a request on order server which is not the leader")
    file = open("log",'w')
    lines = file.readlines()
    term, votedFor = lines[0].split()

    if append_entries():
        logs = open("order_log.txt", 'a')
        id = request.args.get('item', type=int)
        print('Querying for', book_names[str(id)])
        order_buy_start_time = time()
        c_state = int(requests.get(FRONTEND_SERVER + 'getcatalog').text)
        r = requests.get(catalogs[c_state] + 'query?item=' + str(id))
        if r.status_code != 200:
            c_state = int(requests.get(FRONTEND_SERVER + 'getcatalog').text)
            r = requests.get(catalogs[c_state] + 'query?item=' + str(id))
        print(r.json())
        if r.json()['books'][0]['stock'] > 0:  # Checking for item to be in stock
            b = requests.post(catalogs[c_state] + 'update?item=' + str(id), json={'delta': -1, 'order': 1})
            with open('./times/order_buy_time.txt', 'a') as f:
                f.write(str(time() - order_buy_start_time) + '\n')
            logs.write(str(datetime.datetime.now()) + ':Bought - ' + book_names[str(id)] + '\n')
            print('Bought ' + book_names[str(id)])
            return 'Bought ' + book_names[str(id)]
        else:
            with open('./times/order_buy_time.txt', 'a') as f:
                f.write(str(time() - order_buy_start_time) + '\n')
            logs.write(str(datetime.datetime.now()) + ':Out of Stock - ' + book_names[str(id)] + '\n')
            print('Out of Stock')
            return 'Out of Stock'

def append_entries():


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return 'Heartbeat successful!'

@app.route('/vote', methods=['GET'])
def leader0_set():
    term = request.args.get('term', type=int)
    candidateId = request.args.get('candidateId', type=int)
    lastLogIndex = request.args.get('lastLogIndex', type=int)
    lastLogTerm = request.args.get('lastLogTerm', type=int)
    file = open("raft_log", 'w')
    lines = file.readlines()
    term, votedFor = lines[0].split()
    global TERM
    if TERM > term:
        return False
    if (not votedFor or (votedFor == candidateId)) and lastLogIndex >= commitIndex:
        return True
    return False


def heartbeat_timeout_thread():
    while True:
        next_timeout_heartbeat = (time()*1000) + HEARTBEAT_TIMEOUT
        time.sleep((next_timeout_heartbeat/1000) - time())
        if NODE_STATE != 2:
            break


def append_entries_thread():
    hearbeat_timeout_thread()


def request_vote():
    global NODE_STATE
    global TERM
    for i in range(len(orders)):
        if i != server_id and "True" in requests.get(orders[i] + 'vote?term='+ str(TERM)).text:
            NODE_STATE = 2


def election_timeout_thread():
    global ELECTION_TIMEOUT
    global NODE_STATE
    time.sleep((ELECTION_TIMEOUT + random.random(100)) * 1000)
    if NODE_STATE != 2:
        election_timeout_thread()


def leader_election_thread():
    election_timeout_thread()
    request_vote()
    if NODE_STATE != 2:
        leader_election_thread()
    else:
        append_entries_thread()


if __name__ == '__main__':
    server_id = int(sys.argv[1])
    df = pd.read_csv('sv_info.csv')
    CATALOG_SERVER_1 = 'http://' + str(df['IP'][0]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_1 = 'http://' + str(df['IP'][1]) + ':' + str(df['Port'][1]) + '/'
    FRONTEND_SERVER = 'http://' + str(df['IP'][2]) + ':' + str(df['Port'][2]) + '/'
    CATALOG_SERVER_2 = 'http://' + str(df['IP'][3]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_2 = 'http://' + str(df['IP'][4]) + ':' + str(df['Port'][1]) + '/'
    ORDER_SERVER_3 = 'http://' + str(df['IP'][5]) + ':' + str(df['Port'][1]) + '/'
    catalogs = [CATALOG_SERVER_1, CATALOG_SERVER_2]
    orders = [ORDER_SERVER_1, ORDER_SERVER_2, ORDER_SERVER_3]

    # Start the leader election thread
    leader_election_thread()


app.run(host='0.0.0.0', port=df['Port'][1], debug=True)
