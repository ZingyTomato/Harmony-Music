#!/usr/bin/env python3
"""
Harmony - An open souce CLI music streamer based on MPV.
"""

import argparse
import sys
from player import MusicPlayer


def main():
    """Entry Point"""
    parser = argparse.ArgumentParser(
        description="Harmony - An open souce TUI music streamer based on MPV.",
        prog="harmony"
    )
    
    parser.add_argument(
        'query', 
        nargs='*', 
        help="""Search for a song (e.g., 'harmony Never Gonna Give You Up',)
                Use a valid Spotify track/album/playlist URL (e.g, 'harmony https://open.spotify.com/xxxx)'"""
    )
    
    parser.add_argument(
        '-t', '--trending',
        action='store_true',
        help="Displays the top 20 trending tracks around the world."
    )
    
    parser.add_argument(
        '-p', '--persist',
        action='store_true',
        help="Ensures the queue's content is persistent and that tracks aren't deleted after being played."
    )
    
    args = parser.parse_args()
    
    try:
        player = MusicPlayer()
        
        if args.trending:
            player.get_trending()
        elif args.query:
            query = ' '.join(args.query)
            
            if player.is_url(query):
              if player.is_track_url(query): ## If its a spotify track
                  player.add_sp_track_to_queue(args.persist) 
                  player.interactive_mode(args.persist)
              elif player.is_album_url(query): ## If its a spotify album
                  player.add_sp_album_to_queue(args.persist) 
                  player.interactive_mode(args.persist)
              elif player.is_playlist_url(query): ## If its a spotify playlist
                  player.add_sp_playlist_to_queue(args.persist) 
                  player.interactive_mode(args.persist)
            else:
                results = player.search_songs(query)
                if results:
                    track = player.display_results(query, results)
                    if track:
                        player.add_to_queue(track, args.persist)
                        player.interactive_mode(args.persist)
        else:
            player.interactive_mode(args.persist)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()