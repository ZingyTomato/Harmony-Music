import argparse
import songs
import videos
import albums
import playlists
import functions

parser = argparse.ArgumentParser(description="An open souce video/music streamer based on MPV and piped.")

group = parser.add_mutually_exclusive_group()

group.add_argument('--song', '-s', '--s', action='store_true', help="""Searches for songs based on query. Example: harmony --song "Never gonna give you up" """)

group.add_argument('--video', '-v', '--v', action='store_true', help="""Searches for videos based on the query. Example: harmony --video "Never gonna give you up" """)

group.add_argument('--album', '-a', '--a', action='store_true', help="""Searches for albums based on the query. Example: harmony --album "All Over The Place" """)

group.add_argument('--playlist', '-p', '--p', action='store_true', help="""Searches for playlists based on the query. Example: harmony --playlist "All Over The Place" """)

parser.add_argument('query', type=str)

args = parser.parse_args()

if args.song:
  songs.listTracks(args.query)
  
elif args.video:
  videos.listVideos(args.query)
  
elif args.album:
  albums.listAlbums(args.query)
  
elif args.playlist:
  playlists.listPlaylists(args.query)