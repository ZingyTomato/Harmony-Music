import argparse
import songs
import functions
import termcolor

parser = argparse.ArgumentParser(description="An open souce CLI music streamer based on MPV.", prog="harmony")

parser.add_argument('SONG_NAME', help="Name of the song to search for. Example: harmony 2step Ed Sheeran", type=str, nargs="*")

args = parser.parse_args()

if args.SONG_NAME:
  songs.listTracks(" ".join(args.SONG_NAME))
