#!flask/bin/python
import json
import sys
from time import time

import pandas as pd
import requests
from flask import Flask, jsonify, request

# Initializing the book names as per the assignment
book_names = {'1': 'How to get a good grade in 677 in 20 minutes a day',
              '2': 'RPCs for Dummies',
              '3': 'Xen and the Art of Surviving Graduate School',
              '4': 'Cooking for the Impatient Graduate Student',
              '5': 'How to finish Project 3 on time',
              '6': 'Why theory classes are so hard',
              '7': 'Spring in the Pioneer Valley'}

# Initializing the available topics
topic_names = ['ds', 'gs']

app = Flask(__name__)

# # Initializing the catalogs with the necessary details
books = [
    {
        'id': 1,
        'title': book_names['1'],
        'cost': 100,
        'topic': topic_names[0],
        'stock': 5
    },
    {
        'id': 2,
        'title': book_names['2'],
        'cost': 200,
        'topic': topic_names[0],
        'stock': 5
    },
    {
        'id': 3,
        'title': book_names['3'],
        'cost': 300,
        'topic': topic_names[1],
        'stock': 5
    },
    {
        'id': 4,
        'title': book_names['4'],
        'cost': 400,
        'topic': topic_names[1],
        'stock': 5
    },
    {
        'id': 5,
        'title': book_names['5'],
        'cost': 200,
        'topic': topic_names[0],
        'stock': 5
    },
    {
        'id': 6,
        'title': book_names['6'],
        'cost': 300,
        'topic': topic_names[1],
        'stock': 5
    },
    {
        'id': 7,
        'title': book_names['7'],
        'cost': 400,
        'topic': topic_names[1],
        'stock': 5
    }
]


# REST endpoint for query
@app.route('/query', methods=['GET'])
def get_books():
    books = json.load(open('catalog.json'))
    catalog_start_time = time()
    topic = request.args.get('topic', type=str)
    if topic is not None:  # query by subject
        print('Query in progress for', topic)
        ret = jsonify({'books': [b for b in books if b['topic'] == topic]})
        print('Query successful!')
        with open('./times/catalog_search_time.txt', 'a') as f:
            f.write(str(time() - catalog_start_time) + '\n')
        return ret

    id = request.args.get('item', type=int)
    if id is not None:  # query by item
        print('Query in progress for', book_names[str(id)])
        ret = jsonify({'books': [b for b in books if b['id'] == id]})
        print('Query successful!')
        with open('./times/catalog_lookup_time.txt', 'a') as f:
            f.write(str(time() - catalog_start_time) + '\n')
        return ret
    else:
        print('Invalid query')


# REST endpoint for update
@app.route('/update', methods=['POST'])
def update_books():
    books = json.load(open('catalog.json'))
    catalog_start_time = time()
    id = request.args.get('item', type=int)
    print('Update in progress for', book_names[str(id)])
    cost = request.json.get('cost')
    if cost is not None:  # query to update the cost of item
        for b in books:
            if b['id'] == id:
                b['cost'] = cost
                cur_topic = b['topic']

    delta = request.json.get('delta')
    if delta is not None:  # query to update number of item
        order = request.json.get('order')
        if order:
            for i in range(len(CATALOG_SERVERS)):
                if i != server_id:
                    b = requests.post(CATALOG_SERVERS[i] + 'update?item=' + str(id), json={'delta': -1, 'order': 0})
        for b in books:
            if b['id'] == id:
                b['stock'] += delta
                cur_topic = b['topic']

    json.dump(books, open('catalog.json', 'w'))
    ret = jsonify({'books': [b for b in books if b['id'] == id]})
    print('Update successful!')
    print('Invalidating', book_names[str(id)])
    invalidate_item = requests.get(FRONTEND_SERVER + 'invalidate?item=' + str(id))
    invalidate_topic = requests.get(FRONTEND_SERVER + 'invalidate?topic=' + cur_topic)
    assert invalidate_item.status_code == 200 and invalidate_topic.status_code == 200
    with open('./times/catalog_buy_time.txt', 'a') as f:
        f.write(str(time() - catalog_start_time) + '\n')
    return ret


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return 'Heartbeat successful!'

@app.route('/resync', methods=['GET'])
def resync():
    with open('catalog.json') as f:
        return f.readline()

if __name__ == '__main__':
    server_id = int(sys.argv[1])
    df = pd.read_csv('sv_info.csv')
    CATALOG_SERVER_1 = 'http://' + str(df['IP'][0]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_1 = 'http://' + str(df['IP'][1]) + ':' + str(df['Port'][1]) + '/'
    FRONTEND_SERVER = 'http://' + str(df['IP'][2]) + ':' + str(df['Port'][2]) + '/'
    CATALOG_SERVER_2 = 'http://' + str(df['IP'][3]) + ':' + str(df['Port'][0]) + '/'
    ORDER_SERVER_2 = 'http://' + str(df['IP'][4]) + ':' + str(df['Port'][1]) + '/'
    CATALOG_SERVERS = [CATALOG_SERVER_1, CATALOG_SERVER_2]

    resynced = False

    r = requests.get(FRONTEND_SERVER + 'crashed?id=' + str(server_id))
    if r.text is 'True':
        # re-sync process in case of a failure
        for i in range(len(CATALOG_SERVERS)):
            if i != server_id and requests.get(CATALOG_SERVERS[i] + 'heartbeat').status_code == 200:
                print('Trying to resync')
                json.dump(requests.get(CATALOG_SERVERS[i] + 'resync').json(), open('catalog.json', 'w'))
                print('Successfully Resynced with Catalog Server', i+1)
                resynced = True
    else:
        global books
        json.dump(books, open('catalog.json', 'w'))


app.run(host='0.0.0.0', port=df['Port'][0], debug=True)
