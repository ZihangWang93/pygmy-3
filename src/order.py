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
import threading as t
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
ELECTION_TIMEOUT = 400
HEARTBEAT_TIMEOUT = 100

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

aereceived = False # Flag for appendingEntries call

# REST endpoint for buy
@app.route('/buy', methods=['GET'])
def buy_order():
    if NODE_STATE > 0:
        print("Got a request on order server which is not the follower")
        return

    file = open("log",'w')
    lines = file.readlines()
    term, votedFor = lines[0].split()
    logs = open("order_log.txt", 'a')
    id = request.args.get('item', type=int)
    print('Querying for', book_names[str(id)])
    lines.append("{} {}".format(TERM,id))

    if send_appendEntry():
        order_buy_start_time = time()
        c_state = int(requests.get(FRONTEND_SERVER + 'getcatalog').text)
        r = requests.get(catalogs[c_state] + 'query?item=' + str(id))

        if r.status_code != 200:
            c_state = int(requests.get(FRONTEND_SERVER + 'getcatalog').text)
            r = requests.get(catalogs[c_state] + 'query?item=' + str(id))

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

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return 'Heartbeat successful!'

@app.route('/vote', methods=['GET'])
def leader0_set():
    global TERM
    global commitIndex
    term = request.args.get('term', type=int)
    candidateId = request.args.get('candidateId', type=int)
    lastLogIndex = request.args.get('lastLogIndex', type=int)
    lastLogTerm = request.args.get('lastLogTerm', type=int)
    file = open("log", 'w')
    lines = file.readlines()
    _, votedFor = lines[0].split()
    global TERM
    if TERM > term:
        return False
    if (not votedFor or (votedFor == candidateId)) and lastLogIndex >= commitIndex:
        return True
    return False

def request_vote():
    global NODE_STATE
    global TERM
    for i in range(len(orders)):
        if i != server_id:
            t.Thread(target=request_vote_thread, args=()).start()

def request_vote_thread(i):
    global NODE_STATE
    global TERM
    file = open("log", 'w')
    lines = file.readlines()
    term, votedFor = lines[0].split()
    lastLogTerm = lines[-1].split()[0]
    r = requests.get(
        orders[i] + 'vote?term=' + term + '&candidateId=' + str(server_id) + '&lastLogIndex=' + str(
            len(lines)) + '&lastLogTerm=' + str(lastLogTerm))
    if 'True' in r.text:
        NODE_STATE = 2

def election_timeout_thread():
    global ELECTION_TIMEOUT
    global NODE_STATE
    global TERM
    TERM += 1
    request_vote()
    time.sleep((ELECTION_TIMEOUT + random.random(100)) * 1000)
    if NODE_STATE != 2:
        t.Thread(target=election_timeout_thread, args=()).start()

def follower_thread():
    global aereceived
    global NODE_STATE
    time.sleep((ELECTION_TIMEOUT + random.random(100)) * 1000)
    file = open("log", 'w')
    lines = file.readlines()
    term, votedFor = lines[0].split()
    if not aereceived or not votedFor:
        NODE_STATE = 1

def candidate_thread():
    t.Thread(target=election_timeout_thread, args=()).start()
    while True:
        global aereceived
        global NODE_STATE
        time.sleep(0.05)
        if aereceived:
            aereceived = False
            NODE_STATE = 0

@app.route('/appendentries', methods=['GET'])
def appendEntries_thread():
    global TERM
    global commitIndex
    term = request.args.get('term', type=int)
    leaderId = request.args.get('leaderId', type=int)
    prevLogIndex = request.args.get('prevLogIndex', type=int)
    prevLogTerm = request.args.get('prevLogTerm', type=int)
    logEntry = request.args.get('logEntry', type=int)
    leaderCommit = request.args.get('leaderCommit', type=int)
    file = open("log", 'w')
    lines = file.readlines()
    _, votedFor = lines[0].split()

    if term < TERM or prevLogIndex > len(lines) or lines[prevLogIndex].split()[0] != prevLogTerm:
        return False
    lines.append(logEntry)
    if leaderCommit > commitIndex:
        commitIndex = min(leaderCommit, len(lines))
    return True

def leader_thread():
    while True:
        time.sleep(HEARTBEAT_TIMEOUT/1000)
        send_appendEntry()

def send_appendEntry():
    for i in range(len(orders)):
        if i != server_id:
            t.Thread(target=request_vote_thread, args=(i)).start()
            global NODE_STATE
            global TERM
            f = open("log", 'w')
            lines = f.readlines()
            prevLogTerm = lines[-1].split()[0]
            logEntry = lines[-1].split()[1]
            r = requests.get(orders[i] + 'vote?term=' + TERM + '&leaderId=' + str(server_id) + '&prevLogIndex=' + str(
                len(lines)) + '&prevLogTerm=' + str(prevLogTerm) + '&logEntry=' + logEntry + '&leaderCommit=' + commitIndex)
            if True in r.text:
                return True
            return False

def raft_thread():
    # Start the leader election thread
    while True:
        if NODE_STATE == 0:
            t.Thread(target=follower_thread, args=()).start()
        elif NODE_STATE == 1:
            t.Thread(target=candidate_thread, args=()).start()
        else:
            t.Thread(target=leader_thread, args=()).start()

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

    # Initiating the log file
    file = open("log", 'w')
    file.write("0 False\n")
    file.close()

    app.run(host='0.0.0.0', port=df['Port'][1], debug=True)
    # Starting the RAFT thread
    t.Thread(target=raft_thread, args=()).start()
