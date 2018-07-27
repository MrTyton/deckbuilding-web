from bs4 import BeautifulSoup
from requests import get
from processing import call_this_function
from scraper import load_page
from time import time, sleep
from datetime import timedelta
from logger import log

def get_archetype_links(base):
    req = get(base)
    soup = BeautifulSoup(req.text, 'html.parser')
    a = soup.select("a[href*archetype]")
    return [[x.text, "http://mtgtop8.com/{}".format(x['href'])] for x in a]

def slugify(value):
    keepcharacters = ('<', '>', ':', '"', "/", "\\", "|", "?", "*")
    value = "".join(c for c in value if c not in keepcharacters).strip()
    return value    

def runer(base, format):
    failed = []
    log("Starting to scrape {}".format(format))
    archetypes = get_archetype_links(base)
    log("There are {} archetypes present in {}".format(len(archetypes), format))
    for name, link in archetypes:
        name = slugify(name)
        log("\tStarting {}".format(name))
        i = 0
        while(i < 10):
            try:
                decklists = load_page(link)
                call_this_function(name, format, onlyfiles=decklists)
                break
            except Exception as e:
                log("\t\tSomething broke with error {}.\n\t\tBreaking for 30 seconds.".format(e), 'warning')
                sleep(30)
                i += 1
        if i == 10:
            log("\tCould not scrape {} at {}".format(name, link), 'error')
            failed.append((name, link))
    return failed
    
start = time()
a = runer("http://mtgtop8.com/format?f=LE", "Legacy")
a.extend(runer("http://mtgtop8.com/format?f=MO", "Modern"))
a.extend(runer("http://mtgtop8.com/format?f=ST", "Standard"))
log("Time for scraping decklists: {}".format(str(timedelta(seconds=time()-start))))    
if a:
    log("Didn't get the following: {}".format(a), 'error')