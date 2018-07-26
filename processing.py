from classes import Ranking, parseDecklist
from os import listdir, remove, makedirs
from os.path import isfile, join, exists
from tqdm import tqdm
from scraper import load_page
from optparse import OptionParser


def compute(collective, rankings, deck_size=60):
    if len(collective) < deck_size:
        return None, None
    removed = []
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
    print "Processing Decks..."
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

def call_this_function(name, format, n=2, mypath=None, onlyfiles=None):
    data = run(n, mypath, onlyfiles)
    if not exists("{}/collection/{}".format(format, name)):
        makedirs("{}/collection/{}".format(format,  name))
    for filename, cur_data in zip(['Maindeck', 'Maindeck_options', 'Sideboard', 'Sideboard_options'], data):
        if cur_data and type(cur_data[0]) != tuple:
            cur_data = [(x.name, x.position) for x in cur_data]
        with open("{}/collection/{}/{}.txt".format(format, name, filename), "w") as fp:
            for cardname, quantity in cur_data:
                fp.write("{} {}\n".format(quantity, cardname))

    
if __name__ == "__main__":
    option_parser = OptionParser()
    option_parser.add_option(
        "-n",
        "--number",
        dest="n",
        default=2,
        action="store",
        type="int",
        help="How many combinations of cards to look at. The higher the number, the longer the program will take to run. Default is 2.")
    option_parser.add_option(
        "-u",
        "--url",
        dest="url",
        action="store",
        type="string",
        help="mtgtop8 url to the archetype that you want to determine the best list for. Either this or -f must be specified. Example: 'http://mtgtop8.com/archetype?a=189&meta=51&f=MO'")
    option_parser.add_option(
        "-f",
        "--folder",
        dest="folder",
        action="store",
        type="string",
        help="Path to folder containing decklists. Either this or -u must be specified.")

    options, args = option_parser.parse_args()
    if not options.url and not options.folder:
        print "Need an input. Use -h for more information."
        exit()
    elif options.url and options.folder:
        print "Choose one of the input types."
        exit()
    if options.url:
        options.url = load_page(options.url)
    data = run(options.n, options.folder, options.url)
    
    for filename, cur_data in zip(['Maindeck', 'Maindeck_options', 'Sideboard', 'Sideboard_options'], data):
        print filename, cur_data
        print type(cur_data[0])
        if type(cur_data[0]) != tuple:
            cur_data = [(x.name, x.position) for x in cur_data]
        print filename, cur_data
        with open("{}.txt".format(filename), "w") as fp:
            for name, quantity in cur_data:
                fp.write("{} {}\n".format(quantity, name))

        
    
    
