from shutil import rmtree
from os.path import exists
import os
import pickle
from time import time

if exists("./Modern"):
    rmtree("./Modern")
if exists("./Legacy"):
    rmtree("./Legacy")
if exists("./Standard"):
    rmtree("./Standard")
if exists("./mtggoldfish"):
    rmtree("./mtggoldfish")
if exists("./mtgtop8"):
    rmtree("./mtgtop8")
if not exists("./data"):
    os.makedirs("./data")
if not exists("./data/temp"):
    os.makedirs("./data/temp")
if exists("./data/temp"):
    now = time()
    for f in os.listdir("./data/temp"):
        if os.stat(os.path.join("./data/temp",f)).st_mtime < now - 14 * 86400:
            os.remove(os.path.join("./data/temp", f))
if exists("./data/cached_files.pkl"):
    with open("./data/cached_decklists.pkl") as fp:
        cached_files = pickle.load(fp)
    cached_files = {k:v for k,v in cached_files.items() if exists(v)}
    with open("./data/cached_decklists.pkl", "wb") as fp:
        pickle.dump(cached_files, fp)
    