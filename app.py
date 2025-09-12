import gradio as gr
import analysis as analysis
import requests
import pandas as pd
import sqlite3
import json
import matplotlib as plt

# TO GENERATE DATAFRAMES FOR MOVERS
def movers(tcg, set_name):
    result = analysis.calculate_movers(tcg, set_name)
    if isinstance(result, str):
        raise gr.Error(result)
    return result

# SELECT CARD ID AND GET IMAGE OF CARD
def card_image(dataframe, select_data: gr.SelectData):
    card_id = select_data.value
    
    return analysis.generate_image(card_id)

# SELECT CARD ID AND GET GRAPH OF CARD
def card_graph(dataframe, select_data: gr.SelectData):
    row = select_data.row_value
    card_id = row[0]
    card_version = row[2]
    ago = row[6]

    return analysis.create_graph(card_id, card_version, ago)

# DROPDOWN MENUS
def update_dropdown(tcg):
    if tcg == "":
        return gr.Dropdown(label = "Choose Set", choices = [])
    if tcg == "Pokemon":
        url = "https://api.pokemontcg.io/v2/sets"
        headers = {
            "X-Api-Key": "8fd8acd5-6cbc-4e2f-bc2a-1b633aee675c"
        }

        response = requests.get(url, headers=headers)
        while response.status_code != 200:
            response = requests.get(url, headers=headers)
        data = response.json()
        sets = []
        for set in data['data']:
            if set['releaseDate'] >= '2020/01/01':
                sets.append(set['name'])
        return gr.Dropdown(label = "Choose Set", choices = sets)
    if tcg == "Lorcana":
        url = "https://api.lorcast.com/v0/sets"
        response = requests.get(url)
        data = response.json()
        sets = []
        for set in data['results']:
            sets.append(set['name'])
        return gr.Dropdown(label = "Choose Sets", choices = sets)
    if tcg == "One Piece":
        url = "https://optcgapi.com/api/allSets"
        response = requests.get(url)
        data = response.json()
        sets = []
        for set in data:
            sets.append(set['set_name'])
        url = "https://optcgapi.com/api/allDecks"
        response = requests.get(url)
        data = response.json()
        for set in data:
            sets.append(set['structure_deck_name'])
        return gr.Dropdown(label = "Choose Set", choices = sets)

# CREATING THE ACTUAL INTERFACE
with gr.Blocks() as demo:
    gr.Markdown("# TCG Market Movers")
    gr.Markdown("""
        ## Choose any available set from the following TCGs:
        - Pokemon -- Sword & Shield Era and beyond ONLY
        - Lorcana
        - One Piece
    """)

    tcg_name = gr.Dropdown(label = "Choose TCG", choices = ["", "Pokemon", "Lorcana", "One Piece"])
    set_name = gr.Dropdown(label = "Input Set Name", choices = [])

    tcg_name.change(fn = update_dropdown, inputs = tcg_name, outputs = set_name)

    market_movers = gr.Button("Generate Top 10 and Bottom 10 Market Movers")

    # with gr.Row():
    #     top_10 = gr.Dataframe(label = "Top 10 Market Movers", scale = 2)
    #     with gr.Column():  
    #         top_image = gr.Textbox(label = "image will be here")
    #         top_graph = gr.Textbox(label = "graph will be here")
    # with gr.Row():
    #     bottom_10 = gr.Dataframe(label = "Bottom 10 Market Movers", scale = 2)
    #     with gr.Column():  
    #         bottom_image = gr.Textbox(label = "image will be here")
    #         bottom_graph = gr.Textbox(label = "graph will be here")

    # with gr.Row():
    #     top_10 = gr.Dataframe(label = "Top 10 Market Movers")
    #     bottom_10 = gr.Dataframe(label = "Bottom 10 Market Movers")
    # with gr.Row():
    #     image = gr.Textbox(label = "image will be here")
    #     graph = gr.Textbox(label = "graph will be here")

    with gr.Row():
        with gr.Column(scale = 2):
            top_10 = gr.Dataframe(label = "Top 10 Market Movers")
            bottom_10 = gr.Dataframe(label = "Bottom 10 Market Movers")
        with gr.Column(scale = 1):
            graph = gr.Plot(label = "graph will be here", format = "png", scale = 2)
            image = gr.Image(label = "image will be here", scale = 1)
    
    output = [top_10, bottom_10]

    market_movers.click(fn = movers, inputs = [tcg_name, set_name], outputs = output)

    top_10.select(
        fn = card_image,
        inputs = [top_10],
        outputs = [image]
    )
    top_10.select(
        fn = card_graph,
        inputs = [top_10],
        outputs = [graph]
    )
    bottom_10.select(
        fn = card_image,
        inputs = [bottom_10],
        outputs = [image]
    )
    bottom_10.select(
        fn = card_graph,
        inputs = [bottom_10],
        outputs = [graph]
    )

demo.launch(share=True)