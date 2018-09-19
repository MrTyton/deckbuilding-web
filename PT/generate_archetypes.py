from processing import call_this_function
from time import time, sleep
from datetime import timedelta
from logger import log
import os
from os import listdir
from os.path import isfile, join

def get_archetype_names(d):

    return [[o, os.path.join(d, o)] for o in os.listdir(d) 
                    if os.path.isdir(os.path.join(d,o))]

def slugify(value):
    keepcharacters = ('<', '>', ':', '"', "/", "\\", "|", "?", "*")
    value = "".join(c for c in value if c not in keepcharacters).strip()
    return value    

def runer(format):
    failed = []
    log("Starting to scrape {}".format(format))
    archetypes = get_archetype_names("./{}/rawLists".format(format))
    log("There are {} archetypes present in {}".format(len(archetypes), format))
    for name, path in archetypes:
        name = slugify(name)
        log("\tStarting {}".format(name))
        i = 0
        while(i < 10):
            try:
                decklists = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
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
a = runer("PT25/Modern")
a.extend(runer("PT25/Legacy"))
#a.extend(runer("http://mtgtop8.com/format?f=MO", "Modern"))
#a.extend(runer("http://mtgtop8.com/format?f=ST", "Standard"))
log("Time for scraping decklists: {}".format(str(timedelta(seconds=time()-start))))    
if a:
    log("Didn't get the following: {}".format(a), 'error')