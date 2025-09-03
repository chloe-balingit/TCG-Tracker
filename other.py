import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
import requests
import json
np.set_printoptions(legacy='1.25')

set_name = "Sword & Sheld"
url_name = set_name
if '&' in set_name:
    url_name = set_name.replace('&', '%26')
if 'and' in set_name:
    url_name = set_name.replace('and', '%26')

url = "https://api.pokemontcg.io/v2/sets?q=name:\"" + url_name + "\""
headers = {
    "X-Api-Key": "8fd8acd5-6cbc-4e2f-bc2a-1b633aee675c"
}
response = requests.get(url, headers=headers)
while response.status_code != 200:
    response = requests.get(url, headers=headers)
data = response.json()

print(len(data['data']))