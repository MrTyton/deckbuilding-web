from os import listdir
from os.path import isfile, join
import pytablewriter
from io import StringIO
from itertools import zip_longest
from math import ceil
import datetime
from logger import log

def format_paths(format):
    mypath = f"./PT25/{format}/decks/"
    onlyfiles = sorted(
        [f"[{f[:-3].replace('_', ' ')}]({mypath}{f})" for f in listdir(mypath) if isfile(join(mypath, f))])
    return onlyfiles


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_table(title, files):
    res = StringIO()
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = res
    writer.table_name = title
    # writer.header_list = #list(link_dictionary.keys())
    val = 1
    while (ceil(len(files) / val) != 5):
        val += 1
    writer.value_matrix = list(zip_longest(*list(chunks(files, val))))
    writer.write_table()
    return res


def create(format):
    files = format_paths(format)
    q = generate_table(f"{format}\n", files)
    return q.getvalue()


def output():
    everything = "# Stock Decklists for PT 25\n\n"
    for format in ["Modern", "Legacy"]:
        everything += "\n" + create(format)

    everything += f"\n\n#### Last Updated at {datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')}"
    with open("PT25.md", "w") as fp:
        fp.write(everything)


if __name__ == "__main__":
    log("Generating readme.")
    output()
