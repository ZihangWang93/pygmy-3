from time import time

import pandas as pd
import requests
from flask import Flask, request

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


# REST endpoint for search
@app.route('/search', methods=['GET'])
def search():
    topic = request.args.get('topic', type=str)

    if topic is not None:
        if dictionary.get(topic) is not None:
            return dictionary.get(topic)
        else:
            print('Starting a search for topic', topic)
            frontend_search_start_time = time()
            r = requests.get(CATALOG_SERVER_1 + 'query?topic=' + topic)
            dictionary[topic] = r
            with open('times/frontend_search_time.txt', 'a') as f:
                f.write(str(time() - frontend_search_start_time) + '\n')
            assert r.status_code == 200, 'Search failed!'

            return r.text


# REST endpoint for lookup
@app.route('/lookup', methods=['GET'])
def lookup():
    item_number = request.args.get('item', type=int)
    if item_number is not None:
        if dictionary.get(item_number) is not None:
            return dictionary.get(item_number)
        else:
            print('Starting a lookup for item', book_names[str(item_number)])
            frontend_lookup_start_time = time()
            r = requests.get(CATALOG_SERVER_1 + 'query?item=' + str(item_number))
            dictionary[item_number] = r
            with open('./times/frontend_lookup_time.txt', 'a') as f:
                f.write(str(time() - frontend_lookup_start_time) + '\n')
            return r.text


# REST endpoint for buy
@app.route('/buy', methods=['GET'])
def buy():
    item_number = request.args.get('item', type=int)
    if item_number is not None:
        print('Starting a buy request for item', book_names[str(item_number)])
        frontend_buy_start_time = time()
        r = requests.get(ORDER_SERVER_1 + 'buy?item=' + str(item_number))
        with open('./times/frontend_buy_time.txt', 'a') as f:
            f.write(str(time() - frontend_buy_start_time) + '\n')
        return r.text


# Invalidate cache (called from catalog/order)
@app.route('/invalidate', methods=['GET'])
def invalidate():
    topic = request.args.get('topic', type=str)
    if topic is not None:  # query by subject
        print('Invalidating ', topic)
        dictionary[topic] = None

    id = request.args.get('item', type=int)
    if id is not None:  # query by item
        print('Invalidating', book_names[str(id)])
        dictionary[id] = None


if __name__ == '__main__':
    dictionary = {}

    df = pd.read_csv('sv_info.csv')
    CATALOG_SERVER_1 = 'http://' + str(df['IP'][0]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_1 = 'http://' + str(df['IP'][1]) + ':' + str(df['Port'][1]) + '/'
    FRONTEND_SERVER = 'http://' + str(df['IP'][2]) + ':' + str(df['Port'][2]) + '/'
    # CATALOG_SERVER_2 = 'http://' + str(df['IP'][3]) + ':' + str(df['Port'][0]) + '/'
    # ORDER_SERVER_2 = 'http://' + str(df['IP'][4]) + ':' + str(df['Port'][1]) + '/'

app.run(host='0.0.0.0', port=df['Port'][2], debug=True)
