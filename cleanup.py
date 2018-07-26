from shutil import rmtree
from os.path import exists

if exists("./Modern"):
    rmtree("./Modern")
if exists("./Legacy"):
    rmtree("./Legacy")
if exists("./Standard"):
    rmtree("./Standard")