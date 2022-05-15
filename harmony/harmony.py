import argparse
import songs
import functions

parser = argparse.ArgumentParser(description="An open souce video/music streamer based on MPV and piped.")

parser.add_argument('SONG_NAME', help="Searches for songs based on the query. Example: harmony 2step Ed Sheeran", type=str, nargs="*")

args = parser.parse_args()

if args.SONG_NAME:
  songs.listTracks(" ".join(args.SONG_NAME))