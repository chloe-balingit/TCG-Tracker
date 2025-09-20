import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
import requests
import json
np.set_printoptions(legacy='1.25')

card_id = "ST01-016"
url = "https://optcgapi.com/api/sets/card/" + card_id + "/"
response = requests.get(url)
data = response.json()
if 'error' in data:
    url = "https://optcgapi.com/api/decks/card/" + card_id + "/"
    response = requests.get(url)
    data = response.json()

print(data[0]['card_image'])