import datetime
import itertools as it
from time import time

import pandas as pd
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

DATETIME_FORMAT = '%m/%d %H:%M'


def format_now():
    return datetime.datetime.now().strftime(DATETIME_FORMAT)


# Initializing the book names as per the assignment
book_names = {'1': 'How to get a good grade in 677 in 20 minutes a day',
              '2': 'RPCs for Dummies',
              '3': 'Xen and the Art of Surviving Graduate School',
              '4': 'Cooking for the Impatient Graduate Student',
              '5': 'How to finish Project 3 on time',
              '6': 'Why theory classes are so hard',
              '7': 'Spring in the Pioneer Valley'}

# Initializing the available actions
actions = ['search', 'lookup', 'buy']
# Initializing the available topics
topics = ['ds', 'gs']

app = Flask(__name__)

c_state_heart = [False, False]
o_state_heart = [False, False]

c_state_global = it.cycle([0, 1])
o_state_global = it.cycle([0, 1])


@app.route('/getcatalog', methods=['GET'])
def get_catalog_server_id():
    server_id = next(c_state_global)
    if c_state_heart[server_id]:
        return server_id
    return get_catalog_server_id()


@app.route('/getorder', methods=['GET'])
def get_order_server_id():
    server_id = next(o_state_global)
    if o_state_heart[server_id]:
        return server_id
    return get_order_server_id()


# REST endpoint for search
@app.route('/search', methods=['GET'])
def search():
    topic = request.args.get('topic', type=str)

    if topic is not None:
        if dictionary.get(topic) is not None:
            print('Accessing cache')
            return dictionary.get(topic)
        else:
            print('Starting a search for topic', topic)
            frontend_search_start_time = time()
            c_state = get_catalog_server_id()
            r = requests.get(catalogs[c_state] + 'query?topic=' + topic)
            dictionary[topic] = r.text
            with open('times/frontend_search_time.txt', 'a') as f:
                f.write(str(time() - frontend_search_start_time) + '\n')
            if r.status_code != 200 and not c_state_heart[c_state]:
                r = requests.get(catalogs[get_catalog_server_id()] + 'query?topic=' + topic)
            assert r.status_code == 200, 'Search failed!'
            return r.text


# REST endpoint for lookup
@app.route('/lookup', methods=['GET'])
def lookup():
    item_number = request.args.get('item', type=int)
    if item_number is not None:
        if dictionary.get(item_number) is not None:
            print('Accessing cache')
            return dictionary.get(item_number)
        else:
            print('Starting a lookup for item', book_names[str(item_number)])
            frontend_lookup_start_time = time()
            c_state = get_catalog_server_id()
            r = requests.get(catalogs[c_state] + 'query?item=' + str(item_number))
            dictionary[item_number] = r.text
            with open('./times/frontend_lookup_time.txt', 'a') as f:
                f.write(str(time() - frontend_lookup_start_time) + '\n')
            if r.status_code != 200 and not c_state_heart[c_state]:
                r = requests.get(catalogs[get_catalog_server_id()] + 'query?item=' + str(item_number))
            return r.text


# REST endpoint for buy
@app.route('/buy', methods=['GET'])
def buy():
    item_number = request.args.get('item', type=int)
    if item_number is not None:
        print('Starting a buy request for item', book_names[str(item_number)])
        frontend_buy_start_time = time()
        o_state = get_order_server_id()
        r = requests.get(orders[o_state] + 'buy?item=' + str(item_number))
        with open('./times/frontend_buy_time.txt', 'a') as f:
            f.write(str(time() - frontend_buy_start_time) + '\n')
        if r.status_code != 200 and not o_state_heart[o_state]:
            r = requests.get(orders[get_order_server_id()] + 'buy?item=' + str(item_number))
        return r.text


# Invalidate cache (called from catalog/order)
@app.route('/invalidate', methods=['GET'])
def invalidate():
    topic = request.args.get('topic', type=str)
    if topic is not None:  # query by subject
        print('Invalidating ', topic)
        dictionary[topic] = None
        return 'Successfully invalidated topic'

    id = request.args.get('item', type=int)
    if id is not None:  # query by item
        print('Invalidating', book_names[str(id)])
        dictionary[id] = None
        return 'Successfully invalidated item'

    return 'Invalidation Error'


def heartbeat():
    print('Getting Heartbeats')
    global c_state_heart
    global o_state_heart
    o_state_heart = [(requests.get(ORDER_SERVER_1 + 'heartbeat').status_code == 200),
                     (requests.get(ORDER_SERVER_2 + 'heartbeat').status_code == 200)]
    c_state_heart = [(requests.get(CATALOG_SERVER_1 + 'heartbeat').status_code == 200),
                     (requests.get(CATALOG_SERVER_2 + 'heartbeat').status_code == 200)]


if __name__ == '__main__':
    dictionary = {}

    df = pd.read_csv('sv_info.csv')
    CATALOG_SERVER_1 = 'http://' + str(df['IP'][0]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_1 = 'http://' + str(df['IP'][1]) + ':' + str(df['Port'][1]) + '/'
    FRONTEND_SERVER = 'http://' + str(df['IP'][2]) + ':' + str(df['Port'][2]) + '/'
    CATALOG_SERVER_2 = 'http://' + str(df['IP'][3]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_2 = 'http://' + str(df['IP'][4]) + ':' + str(df['Port'][1]) + '/'

    catalogs = [CATALOG_SERVER_1, CATALOG_SERVER_2]
    orders = [ORDER_SERVER_1, ORDER_SERVER_2]

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(heartbeat, 'interval', seconds=5)
    scheduler.start()

    app.run(host='0.0.0.0', port=df['Port'][2], debug=True)
