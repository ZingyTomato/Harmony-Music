import argparse
import songs
import functions
from termcolor import colored
import videos

parser = argparse.ArgumentParser(description="An open souce CLI music/video streamer based on MPV.", prog="harmony")

parser.add_argument('SEARCH_QUERY', help="Name of the song/video to search for. Example: harmony 2step Ed Sheeran", type=str, nargs="*")

parser.add_argument('-v', '--video', help="Allows to search for videos instead of music. Example harmony -v 2step Ed Sheeran", action="store_true")

args = parser.parse_args()

if args.video:
  videos.listVideos(" ".join(args.SEARCH_QUERY))
elif " ".join(args.SEARCH_QUERY) == "":
  print(colored("Please enter the name of a song/video! Type -h for help.", 'red', attrs=['bold']))
else:
  songs.listTracks(" ".join(args.SEARCH_QUERY))