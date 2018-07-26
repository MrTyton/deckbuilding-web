from bs4 import BeautifulSoup as BS
from requests import get
from tempfile import NamedTemporaryFile
from tqdm import tqdm
from time import sleep

"""
This module scrapes the first page of the linked mtgtop8 page and pulls all of the decklists into temporary files.
Does not yet scrape the second+ pages due to javascript shenanigans.
"""

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

def load_page(url):
    print "Loading page..."
    resp = get(url, headers=headers)
    if resp.status_code != 200:
        print "Error connecting to website."
        return
    bs = BS(resp.text, "html.parser")
    tables = bs.find_all("table")
    # this should be it always, unless it changes the format of the site
    decklist_tables = tables[4]
    decks = decklist_tables.find_all("tr", class_="hover_tr")
    urls = ["http://mtgtop8.com/{}".format(x.find("a")['href']) for x in decks]
    print "{} decks to download and process...".format(len(urls))
    decklists = []
    for cur in tqdm(urls):
        decklists.append(parse_deck_page(cur))#list(map(parse_deck_page, urls))
    return decklists


def parse_deck_page(url):
    resp = get(url, headers=headers)
    if resp.status_code != 200:
        print "Error connecting to website."
        return
    bs = BS(resp.text, "html.parser")
    try:
        link = "http://mtgtop8.com/{}".format(
            bs.find("a", text="MTGO")['href'].encode("utf-8"))
    except BaseException:
        print url
    try:
        resp = get(link)
    except:
        print "Error connecting to website"
        return
    if resp.status_code != 200:
        print "Error connecting to website."
        return
    with NamedTemporaryFile(delete=False) as fp:
        fp.write(resp.text)
        name = fp.name
    return name
