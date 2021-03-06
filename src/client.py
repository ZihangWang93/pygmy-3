import json
import os
import random
from time import sleep, time

import requests

import sv_info as S

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

# Creating the time file along with starting the server
if not os.path.isfile('./times/client_lookup_time.txt'):
    os.makedirs('./times')
    file = open("./times/client_lookup_time.txt", "x")
    file.close()


# Pretty printing for json
def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


# Method to update the book stock randomly
def update_stock():
    id = random.randint(1, 4)
    b = requests.post(CATALOG_SERVER_1 + 'update?item=' + str(id), json={'delta': 2})
    c = requests.post(CATALOG_SERVER_2 + 'update?item=' + str(id), json={'delta': 2})
    assert b.status_code == 200 and c.status_code == 200, 'Periodic update failed!'
    print('Periodic updates successful for', book_names[str(id)])


# Method for getting the performance stats for search, lookup and buy
def test_response_times(num_req=10, mode='search'):
    for i in range(num_req):
        print(i)
        if mode == 'search':
            topic = random.choice(topics)
            client_search_start_time = time()
            r = requests.get(FRONTEND_SERVER + 'search?topic=' + topic)
            with open('./times/client_search_time.txt', 'a') as f:
                f.write(str(time() - client_search_start_time) + '\n')
            assert r.status_code == 200, 'Search request failed!'
        if mode == 'lookup':
            item = random.randint(1, 4)
            client_lookup_start_time = time()
            r = requests.get(FRONTEND_SERVER + 'lookup?item=' + str(item))
            with open('./times/client_lookup_time.txt', 'a') as f:
                f.write(str(time() - client_lookup_start_time) + '\n')
            assert r.status_code == 200, 'Search request failed!'
        if mode == 'buy':
            item = random.randint(1, 4)
            client_buy_start_time = time()
            r = requests.get(FRONTEND_SERVER + 'buy?item=' + str(item))
            with open('./times/client_buy_time.txt', 'a') as f:
                f.write(str(time() - client_buy_start_time) + '\n')
            assert r.status_code == 200, 'Search request failed!'
        sleep(0.1)


if __name__ == '__main__':

    CATALOG_SERVER_1 = 'http://' + S.ips['catalog1'][0] + ':' + str(S.ips['catalog1'][1]) + '/'
    ORDER_SERVER_1 = 'http://' + S.ips['order1'][0] + ':' + str(S.ips['order1'][1]) + '/'
    FRONTEND_SERVER = 'http://' + S.ips['frontend'][0] + ':' + str(S.ips['frontend'][1]) + '/'
    CATALOG_SERVER_2 = 'http://' + S.ips['catalog2'][0] + ':' + str(S.ips['catalog2'][1]) + '/'
    ORDER_SERVER_2 = 'http://' + S.ips['order2'][0] + ':' + str(S.ips['order2'][1]) + '/'

    # test_response_times(mode='search')  # Uncomment to run ART per-tier for this search()
    # test_response_times(mode='lookup') # Uncomment to run ART per-tier for this search()
    # test_response_times(mode='buy') # Uncomment to run ART per-tier for this search()
    while True:

        action = random.choice(actions)
        print(action)
        if action == 'search':
            topic = random.choice(topics)
            print('Starting a search for', topic)
            r = requests.get(FRONTEND_SERVER + 'search?topic=' + topic)
            print(r.status_code)
            # assert r.status_code == 200, 'Search request failed!'
            pp_json(r.json())

        elif action == 'lookup':
            item = random.randint(1, 4)
            print('Starting a lookup for', book_names[str(item)])
            r = requests.get(FRONTEND_SERVER + 'lookup?item=' + str(item))
            print(r.status_code)
            # assert r.status_code == 200, 'Lookup request failed!'
            pp_json(r.json())

        else:
            item = random.randint(1, 4)
            print('Trying to buy', book_names[str(item)])
            r = requests.get(FRONTEND_SERVER + 'buy?item=' + str(item))
            print(r.status_code)
            # assert r.status_code == 200, 'Buy request failed!'
            print('Successfully bought', book_names[str(item)])

        # update_stock()

        sleep(10)
