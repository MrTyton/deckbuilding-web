from bs4 import BeautifulSoup
from requests import get
from processing import call_this_function
from scraper import load_page
from time import time, sleep
import datetime

def get_archetype_links(base):
    req = get(base)
    soup = BeautifulSoup(req.text, 'html.parser')
    a = soup.select("a[href*archetype]")
    return [[x.text, "http://mtgtop8.com/{}".format(x['href'])] for x in a]
    

def runer(base, format):
    failed = []
    archetypes = get_archetype_links(base)
    for name, link in archetypes:
        name = name.replace("/", "").replace("\\", "").strip()
        print "Working on ", name
        i = 0
        while(i < 10):
            try:
                decklists = load_page(link)
                call_this_function(name, format, onlyfiles=decklists)
                break
            except Exception as e:
                print "Taking a break...", e
                sleep(30)
                i += 1
            failed.append((name, link))
    return failed
start = time()

a = runer("http://mtgtop8.com/format?f=LE", "Legacy")
a.extend(runer("http://mtgtop8.com/format?f=MO", "Modern"))
a.extend(runer("http://mtgtop8.com/format?f=ST", "Standard"))
print "Time to completion:", str(datetime.timedelta(seconds=time()-start))    
print "Didn't get the following: ", a
