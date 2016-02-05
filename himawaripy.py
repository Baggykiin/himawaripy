#!/usr/bin/env python3

from io import BytesIO
from json import loads
from time import strptime, strftime
from subprocess import call
from os import makedirs
from os.path import expanduser, split
from urllib.request import urlopen

from PIL import Image

<<<<<<< HEAD
=======
from multiprocessing import Pool, cpu_count, Value
from itertools import product
>>>>>>> 60b75f8a59a6b2b7786187acca26ac4c41da7670

# Configuration
# =============

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4
width = 550
height = 550

# Path to the output file
output_file = expanduser("~/.himawari/himawari-latest.png")

# ==============================================================================
counter = None


def download_chunk(args):
    global counter

    x, y, latest = args
    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    with urlopen(url_format.format(level, width, strftime("%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
        tiledata = tile_w.read()

    with counter.get_lock():
        counter.value += 1
        print("Downloading tiles: {}/{} completed".format(counter.value, level*level), end="\r", flush=True)
    return (x, y,tiledata)


def main():
    global counter

    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")

    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    png = Image.new('RGB', (width*level, height*level))

    counter = Value("i", 0)
    p = Pool(cpu_count() * level)
    res = p.map(download_chunk, product(range(level), range(level), (latest,)))

    for (x, y, tiledata) in res:
            tile = Image.open(BytesIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

    makedirs(split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")
    
    print(output_file)
    
if __name__ == "__main__":
    main()

