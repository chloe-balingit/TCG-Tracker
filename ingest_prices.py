import sqlite3
from datetime import datetime
import requests
import json

# CONNECTING TO DATABASE
conn = sqlite3.connect("tcg_market.db")
cursor = conn.cursor()

#   POKEMON
# SETTING UP API CONNECTION FOR INFO ON SETS
url = "https://api.pokemontcg.io/v2/sets"
headers = {
    "X-Api-Key": "8fd8acd5-6cbc-4e2f-bc2a-1b633aee675c"
}

response = requests.get(url, headers=headers)
while response.status_code != 200:
  response = requests.get(url, headers=headers)
data = response.json()

# CREATING TABLE THAT WILL HOLD CARD DATA
cursor.execute('''
  CREATE TABLE IF NOT EXISTS card_prices_record (
      timestamp DATETIME,
      tcg TEXT,
      set_id TEXT,
      card_id TEXT,
      card_name TEXT,
      card_version TEXT,
      price REAL,
      currency TEXT
    )
''')

# PROCESS OF INPUTTNG DATA INTO TABLES
if "data" in data:
  for set in data["data"]:
    # ACESSING CARDS IN SETS IN AND AFTER SWORD&SHIELD ERA
    if set['releaseDate'] >= '2020/01/01':
      url_name = set['name']
      data_tcg = "Pokemon"
      data_set_id = set['id']
      data_currency = "USD"

      # TWEAKING SET NAMES TO BE URL FRIENDLY
      if '&' in url_name:
        url_name = url_name.replace('&', '%26')
      if ' and' in url_name:
        url_name = url_name.replace(' and', ' %26')
    
      # ESTABLISHING CONNECTION WITH CARDS IN EACH INDIVIDUAL SET
      url = "https://api.pokemontcg.io/v2/cards?q=set.name:\"" + url_name + "\""
      headers = {
        "X-Api-Key": "8fd8acd5-6cbc-4e2f-bc2a-1b633aee675c"
      }
      response = requests.get(url, headers=headers)
      while response.status_code != 200:
        print(str(url_name) + ": Connection Error -- " + str(response))
        response = requests.get(url, headers=headers)

      print(str(url_name + ": Connection Successful! -- " + str(response)))
      data = response.json()
      
      # COLLECTING CARD DATA FROM SET
      if "data" in data:
        for card in data["data"]:
          data_card_id = card['id']
          data_card_name = card['name']
          if 'tcgplayer' not in card: # some cards will not have a 'tcgplayer' hush and therefore won't give us market price
            data_timestamp = datetime.now().isoformat()
            data_card_version = "NA (no tcg)"
            data_card_price = None
            cursor.execute(
              "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
              )
          elif 'prices' in card['tcgplayer']:
            card_prices = card['tcgplayer']['prices']
            if 'normal' in card_prices: # if there is a normal version of the card
              data_card_version = "Normal"
              if 'market' in card_prices['normal']: 
                data_timestamp = datetime.now().isoformat()
                data_price = card_prices['normal']['market']
              else: # sometimes card will not have a market price but may have other prices such as 'highest' or 'median'
                data_timestamp = datetime.now().isoformat()
                data_card_version = "Normal (no market price)"
                data_price = None                      
              cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
            if 'holofoil' in card_prices: # if there is a holofoil version of the card
              data_card_version = "Holofoil"
              if 'market' in card_prices['holofoil']: 
                data_timestamp = datetime.now().isoformat()
                data_price = card_prices['holofoil']['market']
              else:
                data_timestamp = datetime.now().isoformat()
                data_card_version = "Holofoil (no market price)"
                data_price = None                        
              cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
            if 'reverseHolofoil' in card_prices: # if there is a reverse holo version of the card
              data_card_version = "Reverse Holo"
              if 'market' in card_prices['reverseHolofoil']:
                data_timestamp = datetime.now().isoformat()
                data_price = card_prices['reverseHolofoil']['market']
              else:
                data_timestamp = datetime.now().isoformat()
                data_card_version = "Reverse Holo (no market price)"
                data_price = None
              cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
            if '1stEditionHolofoil' in card_prices: # if there is a 1st edition holo version of the card -- usually not present in these eras, mainly within early eras
              data_card_version = "1st Ed. Holo"
              if 'market' in card_prices['1stEditionHolofoil']:
                data_timestamp = datetime.now().isoformat()
                data_price = card_prices['1stEditionHolofoil']['market']
              else:
                data_timestamp = datetime.now().isoformat()
                data_card_version = "1st Ed. Holo (no market price)"
                data_price = None
              cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
            if '1stEditionNormal' in card_prices: # if there is a 1st edition normal version of the card -- usually not present in these eras, mainly within early eras
              data_card_version = "1st Ed. Normal"
              if 'market' in card_prices['1stEditionNormal']:
                data_timestamp = datetime.now().isoformat()
                data_price = card_prices['1stEditionNormal']['market']
              else:
                date_timestamp = datetime.now().isoformat()
                data_card_version = "1st Ed. Normal (no market price)"
                data_price = None                  
              cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
          else: # sometimes card will have 'tcgplayer' hush but no price info
            date_timestamp = datetime.now().isoformat()
            data_card_version = "NA (no prices)"
            data_card_price = None
                
            cursor.execute(
                "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
                )
      else: # this pretty much never happens but just in case a set just has no info on its cards
        print("No card data for " + url_name)
else:
  print("No set data")


#       GETTING LORCANA TCG INFO
url = "https://api.lorcast.com/v0/sets"

response = requests.get(url)
data = response.json()

for set in data['results']:
    # set_release.append(set['']
    set_code = set['code']
    url = "https://api.lorcast.com/v0/cards/search?q=set:\"" + set_code + "\""

    response = requests.get(url)
    data = response.json()

    data_tcg = "Lorcana"
    data_set_id = set['id']
    data_currency = "USD"

    for card in data['results']:
      # normal card
      if 'usd' in card['prices']:
        data_timestamp = datetime.now().isoformat()
        data_card_id = card['id']
        data_card_name = card['name']
        data_card_version = "Normal"
        data_price = float(card['prices']['usd'])
        cursor.execute(
           "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
        )
      # foil card
      if 'usd_foil' in card['prices']:
        data_timestamp = datetime.now().isoformat()
        data_card_id = card['id']
        data_card_name = card['name']
        data_card_version = "Foil"
        data_price = float(card['prices']['usd_foil'])
        cursor.execute(
           "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
        )

#       GETTING ONE PIECE TCG INFO
url = "https://optcgapi.com/api/allSets"

response = requests.get(url)
# print(str(response))
data = response.json()
# print(data)

data_tcg = "One Piece"
data_currency = "USD"
# i = 0
for set in data:
    data_set_id = set['set_id']

    url = "https://optcgapi.com/api/sets/" + data_set_id + "/"
    response = requests.get(url)
    data = response.json()

    if len(data) > 1:
      for card in data:
        data_timestamp = datetime.now().isoformat()
        data_card_id = card['card_set_id']
        data_card_name = card['card_name']
        data_card_version = card['rarity']
        data_price = card['market_price']

        cursor.execute(
           "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data_timestamp, data_tcg, data_set_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
        )


# GETTING CARDS FROM DECKS
url = "https://optcgapi.com/api/allDecks"

response = requests.get(url)
# print(str(response))
data = response.json()
# print(data)

# i = 0
for deck in data:
    data_deck_id = deck['structure_deck_id']

    url = "https://optcgapi.com/api/decks/" + data_deck_id + "/"
    response = requests.get(url)
    data = response.json()

    if len(data) > 1:
      for card in data:
        data_timestamp = datetime.now().isoformat()
        data_card_id = card['card_set_id']
        data_card_name = card['card_name']
        data_card_version = card['rarity']
        data_price = card['market_price']

        cursor.execute(
           "INSERT OR IGNORE INTO card_prices_record(timestamp, tcg, set_id, card_id, card_name, card_version, price, currency)" \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data_timestamp, data_tcg, data_deck_id, data_card_id, data_card_name, data_card_version, data_price, data_currency)
        )

# CONFIRMING INFO AND COMMITING IT TO DATABASE
cursor.execute(
  "SELECT * FROM card_prices_record"
)
rows = cursor.fetchall()
for row in rows:
  print(row)
    
conn.commit()
conn.close()