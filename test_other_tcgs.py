import sqlite3
from datetime import datetime
import requests
import json
import requests

url = "https://api.lorcast.com/v0/sets"

response = requests.get(url)
data = response.json()

for set in data['results']:
    set_code = set['code']
    set_id = set['id']
    set_name = set['name']
    url = "https://api.lorcast.com/v0/cards/search?q=set:\"" + set_code + "\""

    response = requests.get(url)
    data = response.json()
    
    i = 0
    for card in data['results']:
        i += 1
    
    print(set_name + " has " + str(i) + " cards!")

# set_code = "1"
# url = "https://api.lorcast.com/v0/cards/search?q=set:\"" + set_code + "\""

# response = requests.get(url)
# data = response.json()

# print(data['results'][0]['prices'])