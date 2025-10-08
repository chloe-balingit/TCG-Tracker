import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
import requests
import json
import subprocess
np.set_printoptions(legacy='1.25')

url = "https://optcgapi.com/api/allSets"

response = requests.get(url)
# print(str(response))
while response.status_code != 200:
  print("One Piece API Decks: Connection Error -- " + str(response))
  response = requests.get(url)
data = response.json()
print("One Piece API Decks: Connection Successful! -- " + str(response))

# EDIT