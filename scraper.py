from bs4 import BeautifulSoup as BS
from requests import get, ConnectionError
from tempfile import NamedTemporaryFile
from time import sleep
from logger import log
import pickle
from os.path import exists
import re

"""
This module scrapes the first page of the linked mtgtop8 page and pulls all of the decklists into temporary files.
Does not yet scrape the second+ pages due to javascript shenanigans.
"""

mtgtop8compile = re.compile(r"d=(\d+)")
mtggoldfishcompile = re.compile(r"/(\d+)")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

if exists("./cached_decklists.pkl"):
    with open("./cached_decklists.pkl") as fp:
        cached_files = pickle.load(fp)
else:
    cached_files = {}

def load_page(url):
    log("\t\tLoading {}".format(url))
    resp = get(url, headers=headers)
    if resp.status_code != 200:
        log("\t\tError connecting to website, respone code {}".format(resp.status_code), 'error')
        return
    bs = BS(resp.text, "html.parser")
    if "mtgtop8" in url:
        mtgtop8 = True
        tables = bs.find_all("table")
        # this should be it always, unless it changes the format of the site
        decklist_tables = tables[4]
        decks = decklist_tables.find_all("tr", class_="hover_tr")
        urls = ["http://mtgtop8.com/{}".format(x.find("a")['href']) for x in decks]
    else:
        mtgtop8 = False
        decks = bs.find_all("a", href = lambda href: href and "/deck" in href and "#paper" in href)
        urls = ["https://mtggoldfish.com{}".format(x['href']) for x in decks]
    log("\t\t{} decks to download and process...".format(len(urls)))
    decklists = []
    for cur in urls:
        try:
            decklists.append(parse_deck_page(cur, mtgtop8))
        except Exception as e:
            log("\t\tError connecting to website: {}".format(e), 'error')
    log("\t\tFinished processing decks.")
    global cached_files
    with open("./cached_decklists.pkl", "wb") as fp:
        pickle.dump(cached_files, fp)
    return decklists


def parse_deck_page(url, mtgtop8=True):
    if mtgtop8:
        link = "http://mtgtop8.com/mtgo?{}".format(mtgtop8compile.search(url).group())
    else:
        link = "https://www.mtggoldfish.com/deck/download{}".format(mtggoldfishcompile.search(url).group())
    global cached_files
    if link in cached_files:
        if exists(cached_files[link]):
            return cached_files[link]
        else:
            del cached_files[link]
            
    try:
        resp = get(link)
    except:
        raise ConnectionError("Could not connect to website")
    if resp.status_code != 200:
        raise ConnectionError("Error code ".format(resp.status_code))
    with NamedTemporaryFile(delete=False, dir="./temp") as fp:
        fp.write(resp.text)
        name = fp.name
    cached_files[link] = name
    return name
