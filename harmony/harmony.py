import argparse
import songs
import functions
from termcolor import colored

parser = argparse.ArgumentParser(description="An open souce CLI music streamer based on MPV.", prog="harmony")

parser.add_argument('SEARCH_QUERY', help="Name of the song/video to search for. Example: harmony 2step Ed Sheeran", type=str, nargs="*")

args = parser.parse_args()

if " ".join(args.SEARCH_QUERY) == "":
  print(colored("Please enter the name of a song! Type -h for help.", 'red', attrs=['bold']))
else:
  songs.listTracks(" ".join(args.SEARCH_QUERY))