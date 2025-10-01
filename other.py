import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
import requests
import json
np.set_printoptions(legacy='1.25')

conn = sqlite3.connect("tcg_market.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS auto_test (
        timestamp DATETIME,
        done TEXT
    )
''')

cursor.execute(
    "INSERT INTO auto_test(timestamp, done) VALUES (?, ?)", (datetime.now(), "Auto Test")
)

conn.commit()
conn.close()