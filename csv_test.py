import sqlite3
import pandas as pd
import csv
from datetime import datetime
from datetime import date

# CONNECTING TO DATABASE
conn = sqlite3.connect("tcg_market.db")
cursor = conn.cursor()

# CREATING CSV WITH ALL DATA
cursor.execute(
    "SELECT * FROM card_prices_record"
)
rows = cursor.fetchall()
column_names = [description[0] for description in cursor.description]

with open('card_prices_record.csv', 'w', newline='', encoding="utf-8") as outfile:
    csv_writer = csv.writer(outfile)
    csv_writer.writerow(column_names)
    csv_writer.writerows(rows)

# ADDING NEW DATA INTO CSV
# data = []
# with open('card_prices_record.csv', 'r', newline='', encoding="utf-8") as outfile:
#     reader = csv.reader(outfile)
#     for row in reader:
#         data.append(row)
# # print(data)

# all_cards = pd.read_sql_query("SELECT * FROM card_prices_record", conn)
# today = str(date.today())
# new_cards = all_cards[all_cards['timestamp'].str.contains(today)]
# if(len(new_cards)) != 0:
#     for index, row in new_cards.iterrows():
#         data.append(row)
# else: print("no card data from today yet")

# with open('card_prices_record.csv', 'w', newline='', encoding="utf-8") as outfile:
#     csv_writer = csv.writer(outfile)
#     csv_writer.writerows(data)

# print("Data copied to CSV")