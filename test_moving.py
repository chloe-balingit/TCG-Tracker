import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.25')

# CONNECTING TO DATABASE RECORD
conn = sqlite3.connect("tcg_market.db")
cursor = conn.cursor()

# INPUT FOR THE COMMAND
set_id = 'swsh1'

# GETTING CARD DATA FROM TODAY
today = str(date.today())
all_cards = pd.read_sql_query("SELECT * FROM card_prices_record", conn)
set_cards = all_cards[all_cards['set_id'] == set_id]
set_cards_today = set_cards[set_cards['timestamp'].str.contains(today)]

# GETTING CARD DATA FROM BEFORE
ago = 7
before = str(date.today() - timedelta(days = ago))
set_cards_before = set_cards[set_cards['timestamp'].str.contains(before)]
if (len(set_cards_before) == 0):
    i = 1
    j = 0
    while len(set_cards_before) == 0:
        ago = 7
        ago += ( (-1)**j ) * (i)
        j += 1
        if j % 2 == 0: i += 1
        before = str(date.today() - timedelta(days = ago))
        set_cards_before = set_cards[set_cards['timestamp'].str.contains(before)]
# ago will go up to 14 days ago before just setting rate to 0 -- when ago = 0, len(set_cards_before) = len(set_cards_today)
#  -> since the set_cards has all the cards in a set, length of zero implies that 
#     NO CARDS IN THE SET HAVE HAD MARKET PRICES IN THE LAST 14 DAYS, which in my head just means the set is off the market
#  -> dealing with a singular card that does not have market prices will be done in future steps

if(ago == 0): print("No market price data from the last 14 days")

# CREATING DATA WITH DIFFERENCES
card_ids = []
card_names = []
card_versions = []
current_price = []
past_price = []
price_change = []
i = 0
if len(set_cards_today) == len(set_cards_before): # length might actually always be the same cause I add a row even if there's no price or info
    while i != len(set_cards_today):
        if ((set_cards_today.iloc[i].loc['card_id'] == set_cards_before.iloc[i].loc['card_id']) and 
            (set_cards_today.iloc[i].loc['card_version'] == set_cards_before.iloc[i].loc['card_version'])):
            card_ids.append(set_cards_today.iloc[i].loc['card_id'])
            card_names.append(set_cards_today.iloc[i].loc['card_name'])
            card_versions.append(set_cards_today.iloc[i].loc['card_version'])

            # CALCULATING MOVEMENT EQUATION
            price_today = set_cards_today.iloc[i].loc['price']
            price_before = set_cards_before.iloc[i].loc['price']
            # when a price shows as None, that implies that it wasn't on the market for that day
            #   for price_today, I'm just gonna set the price to zero since it isn't being sold
            #   for price_before, I'll do the same check as I did before, checking from all the way back to 2 weeks ago
            #   if price_before is still None considering the past 14 days, I'd consider the card off the market
            if price_today == None and price_before == None:
                price_today = 0
                price_before = 0
                ppc = 0
            elif price_before == None:
                i = 1
                j = 0
                while price_before == None:
                    ago = 7
                    ago += ( (-1)**j ) * (i)
                    if ago == 0: price_before == 0
                    else: 
                        j += 1
                        if j % 2 == 0: i += 1
                        before = str(date.today() - timedelta(days = ago))
                        card = set_cards[set_cards['card_id'] == set_cards_today.iloc[i].loc['card_id']]
                        card = card[card['card_version'] == set_cards_today.iloc[i].loc['card_version']]
                        card_before = card[card['timestamp'].str.contains(before)]
                        price_before = card_before.iloc[i].loc['price']
                if price_before == 0: ppc = '?' # figure this out later
                else: ppc = ( (price_today - price_before) / price_before ) * 100
            elif price_today == None:
                price_today == 0 # the card is now off the market --> its free
                ppc = ( (price_today - price_before) / price_before ) * 100
            else:
                ppc = ( (price_today - price_before) / price_before ) * 100
            
            current_price.append(price_today)
            past_price.append(price_before)
            price_change.append(ppc)
            
            i += 1
        else:
            print("card order doesn't match") # will change to something else later -- theoretically, order should always match

# CREATING DATAFRAME
data = {
    'card_id' : card_ids,
    'card_name' : card_names,
    'card_version' : card_versions,
    'current_price' : current_price,
    'past_price' : past_price,
    'price_change': price_change
}

difference_data = pd.DataFrame(data)
difference_data = difference_data.sort_values(by= "price_change", ascending = False)

# PRINTING TOP 10 MOVING CARDS AND BOTTOM 10 MOVING CARDS
print("Top 10 Moving Cards:")
print(difference_data.head(10))
print("Bottom 10 Moving Cards:")
print(difference_data.tail(10))

# CLOSING OUT OF DATABASE (can put earlier in code if I want)
conn.close()