from mtgsdk import Card
#from processing import run
from itertools import groupby, zip_longest
from pprint import pprint
import pytablewriter
from io import StringIO
import os
import pickle
from os import makedirs
from os.path import exists
from time import time, sleep
import datetime


if exists("card_backup.pkl"):
    with open("card_backup.pkl", "rb") as fp:
        memoizer = pickle.load(fp)
else:
    memoizer = {}

def return_url_line_type(cardName):
    quantity, name = cardName.split(" ", 1)
    quantity = quantity.strip()
    name = name.strip()
    global memoizer
    if name in memoizer:
        url_string, card_type, name = memoizer[name]
        url_string = f"{quantity} {url_string}"
        return url_string, card_type, name
    cards = Card.where(name=name).iter()
    try:
        card = next(cards)
        while("Land" not in card.type and "Creature" not in card.type and "Sorcery" not in card.type and "Instant" not in card.type and "Enchantment" not in card.type and "Artifact" not in card.type and "Planeswalker" not in card.type):
            card = next(cards)
    except:
        return cardName, "Unknown", name
    url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={}".format(card.multiverse_id)
    if "Land" in card.type:
        card_type = "Land"
    elif "Creature" in card.type:
        card_type = "Creature"
    elif "Sorcery" in card.type:
        card_type = "Sorcery"
    elif "Instant" in card.type:
        card_type = "Instant"
    elif "Enchantment" in card.type:
        card_type = "Enchantment"
    elif "Artifact" in card.type:
        card_type = "Artifact"
    elif "Planeswalker" in card.type:
        card_type = "Planeswalker"
    else:
        card_type = "Unknown"
    memoizer[name] = "[{}]({})".format(name, url), card_type, name
    return "{} [{}]({})".format(quantity, name, url), card_type, name
    
def get_links_group_by_types(input):
    results = []
    for cur in input:
        results.append(return_url_line_type(cur))
    results = sorted(results, key = lambda x : (x[1], x[2]))
    results = {k: list([y[0] for y in v]) for k, v in groupby(results, key=lambda x: x[1])}
    return(results)
    
def generate_markdown_table_mainside(link_dictionary, title):
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name=title
    summation = {}
    for cur in link_dictionary:
        nums = [x.split(" ")[0] for x in link_dictionary[cur]]
        summation[cur] = sum(int(x) for x in nums)
    writer.header_list = list([f"{x} ({summation[x]})" for x in link_dictionary.keys()])
    writer.value_matrix = list(zip_longest(*list(link_dictionary.values())))
    writer.write_table()
    return res
    
def generate_markdown_table_options(input, title):
    maindeck, sideboard = input
    if not maindeck and not sideboard:
        return None
    nmd, md = [x[0] for x in maindeck], [x[1] for x in maindeck]
    nsb, sb= [x[0] for x in sideboard], [x[1] for x in sideboard]
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name=title
    writer.header_list = ["*n*<sup>th</sup> copy", "Maindeck Card", "*n*<sup>th</sup> copy", "Sideboard Card"]
    writer.value_matrix = list(zip_longest(nmd, md, nsb, sb))
    writer.write_table()
    return res
    
def merge_markdown_tables(input1, input2, title):
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name=title
    writer.header_list = ["Maindeck Options", "Sideboard Options"]
    writer.value_matrix = [[input1, input2]]
    writer.write_table()
    return res
    
def run(title, dir, format):
    everything = f"# {title}\n\n#### [Download MTGO](../collection/{title.replace(' ', '%20')}/{title.replace(' ', '%20')}.txt)"
    for cur in ["Maindeck", "Sideboard"]:
        with open(os.path.join(dir, f"{cur}.txt")) as fp:
            inputs = fp.readlines()
        inputs = [x.strip() for x in inputs]
        a = get_links_group_by_types(inputs)
        q = generate_markdown_table_mainside(a, f"{cur}\n")
        everything += "\n" + q.getvalue()
    
    temp = []
    for cur in ["Maindeck", "Sideboard"]:
        with open(os.path.join(dir, f"{cur}_options.txt")) as fp:
            inputs = fp.readlines()
        inputs = [x.strip() for x in inputs]
        temp.append([return_url_line_type(x)[0].split(" ", 1) for x in inputs])
    
    q = generate_markdown_table_options(temp, "Other Options\n")
    if q:
        everything += "\n" + q.getvalue()
    
    if not exists(f"./{format}/decks"):
        makedirs(f"./{format}/decks")
    with open(f"./{format}/decks/{title.replace(' ', '_')}.md", "w") as fp:
        fp.write(everything)

if __name__ == "__main__":
    start = time()
    for format in ["Standard", "Modern", "Legacy"]:
        d = f'./{format}/collection'
        archetypes = [(o, os.path.join(d, o)) for o in os.listdir(d) 
                        if os.path.isdir(os.path.join(d,o))]
        for title, dir in archetypes:
            print(f"Working on {title}")
            run(title, dir, format)
        
        with open("card_backup.pkl", "wb") as fp:
            pickle.dump(memoizer, fp)
    print("Time to completion:", str(datetime.timedelta(seconds=time()-start)))
    
    
