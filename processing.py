from classes import Ranking, parseDecklist
from os import listdir, remove, makedirs
from os.path import isfile, join, exists
from logger import log


def compute(collective, rankings, deck_size=60):
    removed = []
    if len(collective) >= deck_size:
        for _ in range(len(collective) - deck_size):
            for cards, rank in rankings.getNext():
                updater = rank * (1. / (2 ** len(cards)))
                for card in cards:
                    card.updateRank(updater)
            collective = sorted(
                collective, key=lambda x: (
                    x.uprank, 100 - x.position))
            removed.append(collective[0])
            rankings.remove(collective[0])
            collective = collective[1:]
            [x.resetRank() for x in collective]
    names = set(x.name for x in collective)
    namelist = [x.name for x in collective]
    finallist = sorted([(x, namelist.count(x)) for x in names])
    removed = removed[::-1]
    return finallist, removed


def run(n=2, mypath=None, onlyfiles=None):
    if mypath:
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        onlyfiles = ["{}/{}".format(mypath, x) for x in onlyfiles]
    decklists = [parseDecklist(x) for x in onlyfiles]
    
    ranks = Ranking()
    for deck in decklists:
        ranks.addDeck(deck, n)
    sbranks = Ranking()
    sideboards = [parseDecklist(x, sideboard=True) for x in onlyfiles]
    for sideboard in sideboards:
        sbranks.addDeck(sideboard, n)
    mainDeck, removed_mainDeck = compute(ranks.getCollective(), ranks, 60)
    sideBoard, removed_sideBoard = compute(sbranks.getCollective(), sbranks, 15)

    return mainDeck, removed_mainDeck, sideBoard, removed_sideBoard

def call_this_function(name, format, site, n=2, mypath=None, onlyfiles=None):
    log("\t\tComputing final and sideboard")
    data = run(n, mypath, onlyfiles)
    log("\t\tFinished Computation")
    if not exists("{}/{}/collection/{}".format(site, format, name)):
        makedirs("{}/{}/collection/{}".format(site, format,  name))
    log("\t\tSaving decklists")
    for filename, cur_data in zip(['Maindeck', 'Maindeck_options', 'Sideboard', 'Sideboard_options'], data):
        if cur_data and type(cur_data[0]) != tuple:
            cur_data = [(x.name, x.position) for x in cur_data]
        with open("{}/{}/collection/{}/{}.txt".format(site, format, name, filename), "w") as fp:
            for cardname, quantity in cur_data:
                fp.write("{} {}\n".format(quantity, cardname))
    with open("{}/{}/collection/{}/{}.txt".format(site, format, name, name), "w") as fp:
        for cardname, quantity in data[0]:
            fp.write("{} {}\n".format(quantity, cardname))
        fp.write("Sideboard\n")
        for cardname, quantity in data[2]:
            fp.write("{} {}\n".format(quantity, cardname))
    log("\t\tDone Saving Decklists")


        
    
    
