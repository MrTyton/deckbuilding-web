from shutil import rmtree
from os.path import exists
import pickle

if exists("./Modern"):
    rmtree("./Modern")
if exists("./Legacy"):
    rmtree("./Legacy")
if exists("./Standard"):
    rmtree("./Standard")
if exists("cached_files.pkl"):
    with open("cached_decklists.pkl") as fp:
        cached_files = pickle.load(fp)
    cached_files = {k:v for k,v in cached_files.items() if exists(v)}
    with open("cached_decklists.pkl", "wb") as fp:
        pickle.dump(cached_files, fp)
    