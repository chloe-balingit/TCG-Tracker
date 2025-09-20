import sqlite3
from datetime import datetime, date, timedelta
import requests
import json
import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
np.set_printoptions(legacy='1.25')

def calculate_movers(tcg, set_name):
    # CONNECTING TO DATABASE RECORD
    conn = sqlite3.connect("tcg_market.db")
    cursor = conn.cursor()

    set_id = ''

    # POKEMON
    if tcg.lower() == "pokemon" or tcg.lower() == "pokémon":
        # CHANGING set_name to set_id
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
        if len(data['data']) == 0:
            return("Set not found -- Check spelling of input or whether set available in data")
        set_id = data['data'][0]['id']
    
    # LORCANA
    if tcg.lower() == "lorcana":
        # CHANGING set_name to set_id
        url = "https://api.lorcast.com/v0/sets"

        response = requests.get(url)
        data = response.json()
        found = False

        for set in data['results']:
            if set['name'].lower() == set_name.lower():
                set_id = set['id']
                found = True
        
        if found == False: return("Set not found -- Check spelling of input or whether set available in data")
    
    # ONE PIECE
    if tcg.lower() == "one piece":
        url = "https://optcgapi.com/api/allSets"
        response = requests.get(url)
        data = response.json()
        found = False

        for set in data:
            if set['set_name'].lower() == set_name.lower(): 
                set_id = set['set_id']
                found = True

        if found == False:
            url = "https://optcgapi.com/api/allDecks"

            response = requests.get(url)
            data = response.json()

            for set in data:
                if set_name.lower() in set['structure_deck_name'].lower():
                    set_id = set['structure_deck_id']
                    found = True
        
        if found == False: return("Set not found -- Check spelling of input or whether set available in data")

    if set_id == '':
        return ("No data found related to TCG -- Check spelling of input or whether TCG available in data")
    # GETTING CARD DATA FROM TODAY
    today = str(date.today())
    all_cards = pd.read_sql_query("SELECT * FROM card_prices_record", conn)
    tcg_cards = all_cards[all_cards['tcg'].str.lower() == tcg.lower()]
    set_cards = tcg_cards[tcg_cards['set_id'] == set_id]
    set_cards_today = set_cards[set_cards['timestamp'].str.contains(today)]
    if(len(set_cards_today) <= 1): return ("No card data found -- There is no data for today yet")

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
    
    if(ago == 0): return("No market price data from the last 14 days")
    else:
        # CREATING DATA WITH DIFFERENCES
        card_ids = []
        card_names = []
        card_versions = []
        current_price = []
        past_price = []
        price_change = []
        days_apart = []
        i = 0
        if len(set_cards_today) == len(set_cards_before):
            while i != len(set_cards_today):
                j = i
                not_found = False
                while ((set_cards_today.iloc[i].loc['card_id'] != set_cards_before.iloc[j].loc['card_id']) or
                       (set_cards_today.iloc[i].loc['card_version'] != set_cards_before.iloc[j].loc['card_version'])) and not_found == False:
                    if j < len(set_cards_before):
                        j += 1
                    if j >= len(set_cards_before):
                        j = 0
                    if j == i-1:
                        not_found = True
                
                card_ids.append(set_cards_today.iloc[i].loc['card_id'])
                card_names.append(set_cards_today.iloc[i].loc['card_name'])
                card_versions.append(set_cards_today.iloc[i].loc['card_version'])
                price_today = set_cards_today.iloc[i].loc['price']
                if not_found == True:
                    price_before = None
                else: price_before = set_cards_before.iloc[j].loc['price']

                ago2 = ago
                if (price_today == None or price_today == "null") and (price_before == None or price_before == "null"):
                    price_today = 0
                    price_before = 0
                    ppc = 0
                elif price_before == None or price_before == "null":
                    m = 1
                    n = 0
                    while price_before == None:
                        # ago is how many days ago the original set_cards_before is from -- I wanna keep this ago as it is
                        # ago2 is how many days ago this specific card data is from -- this variable may change as we look for cards
                        # if there is no need to go searching for cards, ago2 = ago -- if there is a need, ago2 = data of other card BUT has to reset to ago2 = ago after ago2 is recorded
                        ago2 = 7
                        ago2 += ( (-1)**n ) * (m)
                        if ago2 == 0: price_before == 0
                        else:
                            n += 1
                            if n%2 == 0: m += 1
                            before = str(date.today() - timedelta(days = ago2))
                            card = set_cards[set_cards['card_id'] == set_cards_today.iloc[i].loc['card_id']]
                            card = card[card['card_version'] == set_cards_today.iloc[i].loc['card_version']]
                            card_before = card[card['timestamp'].str.contains(before)]
                            if len(card_before) == 0: 
                                price_before = None
                            else: price_before = card_before.iloc[0].loc['price']
                    if price_before == 0: 
                        ppc = float('inf')
                        ago2 = ago
                    else: 
                        ppc = ( (price_today - price_before) / price_before ) * 100
                elif price_today == None or price_today == "null":
                    price_today = 0
                    ppc = ( (price_today - price_before) / price_before ) * 100
                else:
                    ppc = ( (price_today - price_before) / price_before ) * 100
                
                current_price.append(price_today)
                past_price.append(price_before)
                price_change.append(ppc)
                days_apart.append(ago2)
                ago2 = ago

                i += 1
        elif len(set_cards_today) > len(set_cards_before):
            # print("before less than today")
            while i != len(set_cards_today):
                if i < len(set_cards_before):
                    j = 0
                    not_found = False
                    while ((set_cards_today.iloc[i].loc['card_id'] != set_cards_before.iloc[j].loc['card_id']) or
                        (set_cards_today.iloc[i].loc['card_version'] != set_cards_before.iloc[j].loc['card_version'])) and not_found == False:
                        if j < len(set_cards_before):
                            j += 1
                        if j >= len(set_cards_before)-1:
                            # print(set_cards_today.iloc[i].loc['card_id'] + " " + set_cards_today.iloc[i].loc['card_version'] +
                            #       " -- " + set_cards_before.iloc[j].loc['card_id'] + " " + set_cards_before.iloc[j].loc['card_version'])
                            not_found = True
                    
                    card_ids.append(set_cards_today.iloc[i].loc['card_id'])
                    card_names.append(set_cards_today.iloc[i].loc['card_name'])
                    card_versions.append(set_cards_today.iloc[i].loc['card_version'])
                    price_today = set_cards_today.iloc[i].loc['price']
                    if not_found == True:
                        price_before = None
                    else: price_before = set_cards_before.iloc[j].loc['price']

                    ago2 = ago
                    if (price_today == None or price_today == "null") and (price_before == None or price_before == "null"):
                        price_today = 0
                        price_before = 0
                        ppc = 0
                    elif price_before == None or price_before == "null":
                        m = 1
                        n = 0
                        while price_before == None:
                            # ago is how many days ago the original set_cards_before is from -- I wanna keep this ago as it is
                            # ago2 is how many days ago this specific card data is from -- this variable may change as we look for cards
                            # if there is no need to go searching for cards, ago2 = ago -- if there is a need, ago2 = data of other card BUT has to reset to ago2 = ago after ago2 is recorded
                            ago2 = 7
                            ago2 += ( (-1)**n ) * (m)
                            if ago2 == 0: price_before == 0
                            else:
                                n += 1
                                if n%2 == 0: m += 1
                                before = str(date.today() - timedelta(days = ago2))
                                card = set_cards[set_cards['card_id'] == set_cards_today.iloc[i].loc['card_id']]
                                card = card[card['card_version'] == set_cards_today.iloc[i].loc['card_version']]
                                card_before = card[card['timestamp'].str.contains(before)]
                                if len(card_before) == 0: 
                                    price_before = None
                                else: price_before = card_before.iloc[0].loc['price']
                        if price_before == 0: 
                            ppc = float('inf')
                            ago2 = ago
                        else: 
                            ppc = ( (price_today - price_before) / price_before ) * 100
                    elif price_today == None or price_today == "null":
                        price_today = 0 
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    else:
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    
                    current_price.append(price_today)
                    past_price.append(price_before)
                    price_change.append(ppc)
                    days_apart.append(ago2)
                    ago2 = ago

                    i += 1
                else:
                    j = 0
                    not_found = False
                    while ((set_cards_today.iloc[i].loc['card_id'] != set_cards_before.iloc[j].loc['card_id']) or
                        (set_cards_today.iloc[i].loc['card_version'] != set_cards_before.iloc[j].loc['card_version'])) and not_found == False:
                        if j < len(set_cards_before)-1:
                            j += 1
                        if j >= len(set_cards_before)-1:
                            # print(set_cards_before.iloc[i].loc['card_id'] + " " + set_cards_before.iloc[i].loc['card_version'] +
                            #       " -- " + set_cards_today.iloc[j].loc['card_id'] + " " + set_cards_today.iloc[j].loc['card_version'])
                            not_found = True
                    
                    card_ids.append(set_cards_today.iloc[i].loc['card_id'])
                    card_names.append(set_cards_today.iloc[i].loc['card_name'])
                    card_versions.append(set_cards_today.iloc[i].loc['card_version'])
                    price_today = set_cards_today.iloc[i].loc['price']
                    if not_found == True:
                        price_before = None
                    else: price_before = set_cards_before.iloc[j].loc['price']

                    ago2 = ago
                    if (price_today == None or price_today == "null") and (price_before == None or price_before == "null"):
                        price_today = 0
                        price_before = 0
                        ppc = 0
                    elif price_before == None or price_before == "null":
                        m = 1
                        n = 0
                        while price_before == None:
                            # ago is how many days ago the original set_cards_before is from -- I wanna keep this ago as it is
                            # ago2 is how many days ago this specific card data is from -- this variable may change as we look for cards
                            # if there is no need to go searching for cards, ago2 = ago -- if there is a need, ago2 = data of other card BUT has to reset to ago2 = ago after ago2 is recorded
                            ago2 = 7
                            ago2 += ( (-1)**n ) * (m)
                            if ago2 == 0: price_before == 0
                            else:
                                n += 1
                                if n%2 == 0: m += 1
                                before = str(date.today() - timedelta(days = ago2))
                                card = set_cards[set_cards['card_id'] == set_cards_today.iloc[i].loc['card_id']]
                                card = card[card['card_version'] == set_cards_today.iloc[i].loc['card_version']]
                                card_before = card[card['timestamp'].str.contains(before)]
                                if len(card_before) == 0: 
                                    price_before = None
                                else: price_before = card_before.iloc[0].loc['price']
                        if price_before == 0: 
                            ppc = float('inf')
                            ago2 = ago
                        else: 
                            ppc = ( (price_today - price_before) / price_before ) * 100
                    elif price_today == None or price_today == "null":
                        price_today = 0
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    else:
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    
                    current_price.append(price_today)
                    past_price.append(price_before)
                    price_change.append(ppc)
                    days_apart.append(ago2)
                    ago2 = ago

                    i += 1
        elif len(set_cards_today) < len(set_cards_before):
            # print("today less than before")
            while i != len(set_cards_before):
                if i < len(set_cards_today):
                    j = 0
                    not_found = False
                    while ((set_cards_before.iloc[i].loc['card_id'] != set_cards_today.iloc[j].loc['card_id']) or
                        (set_cards_before.iloc[i].loc['card_version'] != set_cards_today.iloc[j].loc['card_version'])) and not_found == False:
                        if j < len(set_cards_today):
                            j += 1
                        if j >= len(set_cards_today)-1:
                            # print(set_cards_before.iloc[i].loc['card_id'] + " " + set_cards_before.iloc[i].loc['card_version'] +
                            #       " -- " + set_cards_today.iloc[j].loc['card_id'] + " " + set_cards_today.iloc[j].loc['card_version'])
                            not_found = True
                    
                    card_ids.append(set_cards_before.iloc[i].loc['card_id'])
                    card_names.append(set_cards_before.iloc[i].loc['card_name'])
                    card_versions.append(set_cards_before.iloc[i].loc['card_version'])
                    price_before = set_cards_before.iloc[i].loc['price']
                    if not_found == True:
                        price_today = None
                    else: price_today = set_cards_today.iloc[j].loc['price']

                    ago2 = ago
                    if price_today == None and price_before == None:
                        price_today = 0
                        price_before = 0
                        ppc = 0
                    elif price_before == None:
                        m = 1
                        n = 0
                        while price_before == None:
                            # ago is how many days ago the original set_cards_before is from -- I wanna keep this ago as it is
                            # ago2 is how many days ago this specific card data is from -- this variable may change as we look for cards
                            # if there is no need to go searching for cards, ago2 = ago -- if there is a need, ago2 = data of other card BUT has to reset to ago2 = ago after ago2 is recorded
                            ago2 = 7
                            ago2 += ( (-1)**n ) * (m)
                            if ago2 == 0: price_before == 0
                            else:
                                n += 1
                                if n%2 == 0: m += 1
                                before = str(date.today() - timedelta(days = ago2))
                                card = set_cards[set_cards['card_id'] == set_cards_before.iloc[i].loc['card_id']]
                                card = card[card['card_version'] == set_cards_before.iloc[i].loc['card_version']]
                                card_before = card[card['timestamp'].str.contains(before)]
                                if len(card_before) == 0: 
                                    price_before = None
                                else: price_before = card_before.iloc[0].loc['price']
                        if price_before == 0: 
                            ppc = float('inf')
                            ago2 = ago
                        else: 
                            ppc = ( (price_today - price_before) / price_before ) * 100
                    elif price_today == None:
                        price_today = 0
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    else:
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    
                    current_price.append(price_today)
                    past_price.append(price_before)
                    price_change.append(ppc)
                    days_apart.append(ago2)
                    ago2 = ago

                    i += 1
                else:
                    j = 0
                    not_found = False
                    while ((set_cards_before.iloc[i].loc['card_id'] != set_cards_today.iloc[j].loc['card_id']) or
                        (set_cards_before.iloc[i].loc['card_version'] != set_cards_today.iloc[j].loc['card_version'])) and not_found == False:
                        if j < len(set_cards_today):
                            j += 1
                        if j >= len(set_cards_today):
                            # print(set_cards_before.iloc[i].loc['card_id'] + " " + set_cards_before.iloc[i].loc['card_version'] +
                            #       " -- " + set_cards_today.iloc[j].loc['card_id'] + " " + set_cards_today.iloc[j].loc['card_version'])
                            not_found = True
                    
                    card_ids.append(set_cards_before.iloc[i].loc['card_id'])
                    card_names.append(set_cards_before.iloc[i].loc['card_name'])
                    card_versions.append(set_cards_before.iloc[i].loc['card_version'])
                    price_before = set_cards_before.iloc[i].loc['price']
                    if not_found == True:
                        price_today = None
                    else: price_today = set_cards_today.iloc[j].loc['price']

                    ago2 = ago
                    if price_today == None and price_before == None:
                        price_today = 0
                        price_before = 0
                        ppc = 0
                    elif price_before == None:
                        m = 1
                        n = 0
                        while price_before == None:
                            # ago is how many days ago the original set_cards_before is from -- I wanna keep this ago as it is
                            # ago2 is how many days ago this specific card data is from -- this variable may change as we look for cards
                            # if there is no need to go searching for cards, ago2 = ago -- if there is a need, ago2 = data of other card BUT has to reset to ago2 = ago after ago2 is recorded
                            ago2 = 7
                            ago2 += ( (-1)**n ) * (m)
                            if ago2 == 0: price_before == 0
                            else:
                                n += 1
                                if n%2 == 0: m += 1
                                before = str(date.today() - timedelta(days = ago2))
                                card = set_cards[set_cards['card_id'] == set_cards_before.iloc[i].loc['card_id']]
                                card = card[card['card_version'] == set_cards_before.iloc[i].loc['card_version']]
                                card_before = card[card['timestamp'].str.contains(before)]
                                if len(card_before) == 0: 
                                    price_before = None
                                else: price_before = card_before.iloc[0].loc['price']
                        if price_before == 0: 
                            ppc = float('inf')
                            ago2 = ago
                        else: 
                            ppc = ( (price_today - price_before) / price_before ) * 100
                    elif price_today == None:
                        price_today = 0
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    else:
                        ppc = ( (price_today - price_before) / price_before ) * 100
                    
                    current_price.append(price_today)
                    past_price.append(price_before)
                    price_change.append(ppc)
                    days_apart.append(ago2)
                    ago2 = ago

                    i += 1


        
        # CREATING DATAFRAME
        data = {
            'Card ID' : card_ids,
            'Card Name' : card_names,
            'Card Version' : card_versions,
            'Current Price' : current_price,
            'Past Price' : past_price,
            'Price Percentage Change (PPC)' : price_change,
            'Days Apart' : days_apart
        }

        difference_data = pd.DataFrame(data)
        difference_data = difference_data.sort_values(by= "Price Percentage Change (PPC)", ascending = False)

        # RETURN TOP 10 MOVING CARDS AND BOTTOM 10 MOVING CARDS
        # print("Top 10 Moving Cards:")
        # print(difference_data.head(10))
        # print("Bottom 10 Moving Cards:")
        # print(difference_data.tail(10))
        return difference_data.head(10), difference_data.tail(10).sort_values(by= "Price Percentage Change (PPC)")

    # CLOSING OUT OF DATABASE (can put earlier in code if I want)
    conn.close()

def generate_image(tcg, card_id):
    if tcg.lower() == "pokemon":
        url = "https://api.pokemontcg.io/v2/cards/" + card_id
        headers = {
            "X-Api-Key": "8fd8acd5-6cbc-4e2f-bc2a-1b633aee675c"
        }

        response = requests.get(url, headers=headers)
        while response.status_code != 200:
            response = requests.get(url, headers=headers)
        data = response.json()

        return(data['data']['images']['large'])
    
    if tcg.lower() == "lorcana":
        url = "https://api.lorcast.com/v0/cards/" + card_id

        response = requests.get(url)
        while response.status_code != 200:
            response = requests.get(url)
        data = response.json()

        return(data['image_uris']['digital']['large'])
    
    if tcg.lower() == "one piece":
        url = "https://optcgapi.com/api/sets/card/" + card_id + "/"

        response = requests.get(url)
        data = response.json()
        if 'error' in data:
            url = "https://optcgapi.com/api/decks/card/" + card_id + "/"
            response = requests.get(url)
            data = response.json()

        return(data[0]['card_image'])

def create_graph(id, version, days):
    # CONNECTING TO DATABASE RECORD
    conn = sqlite3.connect("tcg_market.db")
    cursor = conn.cursor()

    # GETTING INFO FOR CARD
    card_id = id
    card_version = version
    ago = days

    # GET ALL ROWS WITH THIS INFO FROM card_prices_record IN tcg_market.db
    today = str(date.today())
    all_cards = pd.read_sql_query("SELECT * FROM card_prices_record", conn)
    cards = all_cards[all_cards['card_id'] == card_id]
    cards = cards[cards['card_version'] == card_version]

    # COLLECT DATA FOR GRAPH
    #   x-axis = days ago, y-axis = market price
    x_axis = []
    y_axis = []

    while ago >= 0:
        timestamp = str(date.today() - timedelta(days = ago))
        card_info = cards[cards['timestamp'].str.contains(timestamp)]
        if len(card_info) == 0: card_price = 0
        else: card_price = card_info.iloc[0].loc['price']

        y_axis.append(card_price)
        x_axis.append((ago*-1))
        ago -= 1

    x_axis = np.array(x_axis)
    y_axis = np.array(y_axis)

    # GENERATE GRAPH
    fig, ax = plt.subplots()
    ax.plot(x_axis, y_axis)
    ax.set_xlabel("Days Ago")
    ax.set_ylabel("Market Price (USD)")
    ax.set_title("Market Price Overtime")
    ax.grid()
    return fig


# print(calculate_movers("Lorcana", "Challenge Promo"))
# print(generate_image("One Piece", "ST01-016"))
# print(create_graph("swsh2-3", "Holofoil"))