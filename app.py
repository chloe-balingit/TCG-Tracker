import gradio as gr
import analysis
import requests
import json

def movers(tcg, set_name):
    result = analysis.calculate_movers(tcg, set_name)
    if isinstance(result, str):
        raise gr.Error(result)
    return result

with gr.Blocks() as demo:
    gr.Markdown("# TCG Market Movers")
    gr.Markdown("""
        ## Input the name of any set from the following TCGs:
        - Pokemon -- Sword & Shield Era and beyond ONLY
        - Lorcana
        - One Piece -- both expansion packs and starter decks; does not include: Premium Booster Pack, Starter Deck 22 Ace and Newgate
    """)

    tcg_name = gr.Text(label = "Input TCG")
    set_name = gr.Text(label = "Input Set Name")
    market_movers = gr.Button("Generate Top 10 and Bottom 10 Market Movers")
    output = [gr.Dataframe(label = "Top 10 Market Movers"), gr.Dataframe(label = "Bottom 10 Market Movers")]

    market_movers.click(fn = movers, inputs = [tcg_name, set_name], outputs = output)

demo.launch(share=True)