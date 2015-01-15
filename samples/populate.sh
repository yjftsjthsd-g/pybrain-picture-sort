#!/bin/sh

# this script uses curl to download some cherry-picked sample images

set -e

mkdir ./whales
mkdir ./goats
mkdir ./unknown
mkdir ./probablyWhales
mkdir ./probablyGoats

#goats, from https://commons.wikimedia.org/wiki/Category:Goats
curl https://upload.wikimedia.org/wikipedia/commons/a/a6/A_goat_-_geograph.org.uk_-_1481583.jpg > ./goats/1.jpg &
curl https://upload.wikimedia.org/wikipedia/commons/5/56/A_Goat.JPG > ./goats/2.jpg &
curl https://upload.wikimedia.org/wikipedia/commons/5/5b/Chevraux.jpg > ./goats/3.jpg &

#whales, from https://commons.wikimedia.org/wiki/Category:Whales_in_art
curl https://upload.wikimedia.org/wikipedia/commons/3/3f/BH_Humpback_whale.jpg > ./whales/1.jpg &
curl https://upload.wikimedia.org/wikipedia/commons/6/6d/Orca_Health_Logo.jpeg > ./whales/2.jpg
curl https://upload.wikimedia.org/wikipedia/commons/e/ef/Wading-pool.jpg > ./whales/3.jpg


curl https://upload.wikimedia.org/wikipedia/commons/5/5d/Kitty_3.jpg > ./unknown/cat.jpg
curl http://www.photolib.noaa.gov/bigs/anim0833.jpg > ./unknown/whale.jpg

#note: yes, some of these are in parallel and some are in sequence. I don't like waiting, but if I do them all in parallel, then the script apparenly can finish before curl and the terminal gets messy. So yes, this is an ugly hack of a fix
