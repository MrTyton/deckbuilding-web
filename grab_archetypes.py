from bs4 import BeautifulSoup
from requests import get
from processing import call_this_function
from scraper import load_page
from time import time, sleep
from datetime import timedelta
from logger import log
from collections import defaultdict

def get_archetype_links(base, site):
    req = get(base)
    soup = BeautifulSoup(req.text, 'html.parser')
    if site == "mtgtop8":
        a = soup.select("a[href*archetype]")
        results = [[x.text, "http://mtgtop8.com/{}".format(x['href'])] for x in a]
    else:
        a = soup.find_all("a", href = lambda href: href and "archetype" in href and "paper" in href and "other" not in href)
        results = [[x.text, "https://www.mtggoldfish.com{}".format(x['href'])] for x in a]
    
    args = set(x[0] for x in results)
    ans = defaultdict(list)
    for cur in args:
        for temp in results:
            if temp[0] == cur:
                ans[cur].append(temp[1])
    return ans

def slugify(value):
    keepcharacters = ('<', '>', ':', '"', "/", "\\", "|", "?", "*")
    value = "".join(c for c in value if c not in keepcharacters).strip().encode('utf-8')
    return value    

def runer(base, format):
    if "mtgtop8" in base:
        site = "mtgtop8"
    else:
        site = "mtggoldfish"
    failed = []
    log("Starting to scrape {}".format(format))
    archetypes = get_archetype_links(base, site)
    log("There are {} archetypes present in {}".format(len(archetypes), format))
    for name, link in archetypes.items():
        name = slugify(name)
        log("\tStarting {}".format(name))
        i = 0
        while(i < 10):
            try:
                decklists = []
                for cur_link in link:
                    decklists.extend(load_page(cur_link))
                if decklists:
                    call_this_function(name, format, site, onlyfiles=decklists)
                    break
                else:
                    i += 1
                    log("\t\tSomething broke. Breaking for 30 seconds.", 'warning')
                    sleep(30)
            except Exception as e:
                log("\t\tSomething broke with error {}.\n\t\tBreaking for 30 seconds.".format(e), 'warning')
                sleep(30)
                i += 1
        if i == 10:
            log("\tCould not scrape {} at {}".format(name, link), 'error')
            failed.append((name, link))
    return failed
    
start = time()
a = []
a.extend(runer("https://www.mtggoldfish.com/metagame/standard/full#paper", "Standard"))
#a.extend(runer("http://mtgtop8.com/format?f=LE", "Legacy"))
a.extend(runer("https://www.mtggoldfish.com/metagame/modern/full#paper", "Modern"))
#a.extend(runer("http://mtgtop8.com/format?f=MO", "Modern"))
a.extend(runer("https://www.mtggoldfish.com/metagame/legacy/full#paper", "Legacy"))
#a.extend(runer("http://mtgtop8.com/format?f=ST", "Standard"))
a.extend(runer("https://www.mtggoldfish.com/metagame/pioneer/full#paper", "Pioneer"))
#a.extend(runer("http://mtgtop8.com/format?f=PI", "Pioneer"))
a.extend(runer("https://www.mtggoldfish.com/metagame/historic/full#paper", "Historic"))
#a.extend(runer("http://mtgtop8.com/format?f=HI", "Historic"))
log("Time for scraping decklists: {}".format(str(timedelta(seconds=time()-start))))    
if a:
    log("Didn't get the following: {}".format(a), 'error')