from mtgsdk import Card, Set
from itertools import groupby, zip_longest
import pytablewriter
from io import StringIO
import os
import pickle
from os import makedirs
from os.path import exists
from time import time, sleep
import datetime
from logger import log

def return_url_line_type(cardName, memoizer):
    quantity, name = cardName.split(" ", 1)
    quantity = quantity.strip()
    name = name.strip()
    if name in memoizer:
        url_string, card_type, name, _, _ = memoizer[name]
        url_string = f"{quantity} {url_string}"
        return url_string, card_type, name
    cards = Card.where(name=name.split("/")[0]).iter()
    try:
        card = next(cards)
        while(("Land" not in card.type and "Creature" not in card.type and "Sorcery" not in card.type and "Instant" not in card.type and "Enchantment" not in card.type and "Artifact" not in card.type and "Planeswalker" not in card.type) or (not card.multiverse_id) or (not card.name.lower().strip() == name.split("/")[0].lower().strip())):
            card = next(cards)
    except:
        return cardName, "Unknown", name
    url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={}".format(
        card.multiverse_id)
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
    try:
        last_set = sorted([x for x in card.printings if Set.find(x).type in ['expansion', 'core', 'draft_innovation', 'masters', 'commander', 'archenemy', 'starter', 'planechase']], key = lambda x : Set.find(x).release_date, reverse=True)[0]
    except:
        print(name)
        #print([Set.find(x).type for x in card.printings])
        last_set = None
    try:
        number = [x for x in Card.where(name=name.split("/")[0], set=last_set).all() if x.name == name.split("/")[0]][0].number
    except:
        number = 0
    if last_set == "DOM":
        last_set = "DAR"
        
    memoizer[name] = ("[{}]({})".format(name, url), card_type, name, last_set, number)
    return "{} [{}]({})".format(quantity, name, url), card_type, name


def get_links_group_by_types(input, memoizer):
    results = []
    for cur in input:
        results.append(return_url_line_type(cur, memoizer))
    results = sorted(results, key=lambda x: (x[1], x[2]))
    results = {k: list([y[0] for y in v])
               for k, v in groupby(results, key=lambda x: x[1])}
    return(results)


def generate_markdown_table_mainside(link_dictionary, title):
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name = title
    summation = {}
    for cur in link_dictionary:
        nums = [x.split(" ")[0] for x in link_dictionary[cur]]
        summation[cur] = sum(int(x) for x in nums)
    writer.header_list = list(
        [f"{x} ({summation[x]})" for x in link_dictionary.keys()])
    writer.value_matrix = list(zip_longest(*list(link_dictionary.values())))
    writer.write_table()
    return res


def generate_markdown_table_options(input, title):
    maindeck, sideboard = input
    if not maindeck and not sideboard:
        return None
    nmd, md = [x[0] for x in maindeck], [x[1] for x in maindeck]
    nsb, sb = [x[0] for x in sideboard], [x[1] for x in sideboard]
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name = title
    writer.header_list = ["*n*<sup>th</sup> copy",
                          "Maindeck Card", "*n*<sup>th</sup> copy", "Sideboard Card"]
    writer.value_matrix = list(zip_longest(nmd, md, nsb, sb))
    writer.write_table()
    return res


def merge_markdown_tables(input1, input2, title):
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name = title
    writer.header_list = ["Maindeck Options", "Sideboard Options"]
    writer.value_matrix = [[input1, input2]]
    writer.write_table()
    return res
    
def create_arena_export(title, site, format, memoizer):
    with open(f"./{site}/{format}/collection/{title}/{title}.txt", "r") as fp:
        data = fp.readlines()
    results = []
    for line in data:
        line = line.strip()
        if line == "Sideboard":
            results.append("\n")
            continue
        name = line.split(" ", 1)[1].strip()
        if name in memoizer:
            res = memoizer[name]
            results.append(f"{line.replace('/', ' // ')}\n")
        else:
            continue
    with open(f"./{site}/{format}/collection/{title}/{title}_arena.txt", "w", newline="\r\n") as fp:
        fp.writelines(results)
    return

def run(title, dir, format, site, memoizer):
    everything = f"# {title}\n\n#### [Export MTGO List](../collection/{title.replace(' ', '%20')}/{title.replace(' ', '%20')}.txt)"
    maindeckString = ""
    sideboardString = ""
    other = ""
    for cur in ["Maindeck", "Sideboard"]:
        with open(os.path.join(dir, f"{cur}.txt")) as fp:
            inputs = fp.readlines()
        inputs = [x.strip() for x in inputs]
        w = [x.split(" ", 1) for x in inputs]
        w = [f"{x[0]}%09{x[1].replace(' ', '%20')}" for x in w]
        if cur == "Maindeck":
            maindeckString += "%0A".join(w)
        else:
            sideboardString += "%0A".join(w)
            
        a = get_links_group_by_types(inputs, memoizer)
        q = generate_markdown_table_mainside(a, f"{cur}\n")
        other += "\n" + q.getvalue()
    
    if format == "Standard" or format == "Historic":
        create_arena_export(title, site, format, memoizer)
        everything += f"\n#### [Export Arena List](../collection/{title.replace(' ', '%20')}/{title.replace(' ', '%20')}_arena.txt)"

    everything += f"\n#### [Print on decklist.org](http://decklist.org/?deckmain={maindeckString}&deckside={sideboardString})"
    
    everything += other
    
    temp = []

    for cur in ["Maindeck", "Sideboard"]:
        with open(os.path.join(dir, f"{cur}_options.txt")) as fp:
            inputs = fp.readlines()
        inputs = [x.strip() for x in inputs]
        temp.append([return_url_line_type(x, memoizer)[0].split(" ", 1) for x in inputs])
    
    q = generate_markdown_table_options(temp, "Other Options\n")
    if q:
        everything += "\n" + q.getvalue()
    else:
        log("\t\tNo other options for maindeck or sideboard", 'warning')

    if not exists(f"./{site}/{format}/decks"):
        makedirs(f"./{site}/{format}/decks")
    with open(f"./{site}/{format}/decks/{title.replace(' ', '_')}.md", "w") as fp:
        fp.write(everything)


if __name__ == "__main__":
    start = time()
    if exists("./data/card_backup.pkl"):
        with open("./data/card_backup.pkl", "rb") as fp:
            memoizer = pickle.load(fp)
    else:
        log("Creating memoizer")
        memoizer = {"Mountain":("[{}]({})".format("Mountain", "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=439859"), "Land", "Mountain", "RIX", 195),
        "Swamp":("[{}]({})".format("Swamp", "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=439858"), "Land", "Swamp", "RIX", 194),
        "Island":("[{}]({})".format("Island", "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=439857"), "Land", "Island", "RIX", 193),
        "Plains":("[{}]({})".format("Plains", "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=439856"), "Land", "Plains", "RIX", 192),
        "Forest":("[{}]({})".format("Forest", "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=439860"), "Land", "Forest", "RIX", 196)}
    
    for site in ["mtggoldfish"]:#, "mtgtop8"]:
        for format in ["Modern", "Standard", "Legacy", "Pioneer", "Historic"]:
            d = f'./{site}/{format}/collection'
            archetypes = [(o, os.path.join(d, o)) for o in os.listdir(d)
                          if os.path.isdir(os.path.join(d, o))]
            print(archetypes)
            for title, dir in archetypes:
                log(f"\tGenerating Page for {title}")
                try:
                    run(title, dir, format, site, memoizer)
                except Exception as e:
                    print(e)
                    continue
                with open("./data/card_backup.pkl", "wb") as fp:
                    pickle.dump(memoizer, fp)
    log(f"Time for generating decklists: {str(datetime.timedelta(seconds=time()-start))}")