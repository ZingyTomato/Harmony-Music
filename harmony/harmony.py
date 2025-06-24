#!/usr/bin/env python3
"""
Harmony - An open souce CLI music streamer based on MPV.
"""

import argparse
import sys
from music_player import MusicPlayer


def main():
    """Entry Point"""
    
    parser = argparse.ArgumentParser(
        description="Harmony - An open souce TUI music streamer based on MPV. https://github.com/ZingyTomato/Harmony-Music",
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
        help="Displays the top 20 trending tracks worldwide."
    )

    parser.add_argument(
        '-p', '--playlist',
        action='store_true',
        help="View existing playlists or create new ones."
    )

    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help="Display the current version of the program."
    )

    parser.add_argument(
        '-dl', '--disable-lyrics',
        action='store_true',
        help="Disable synchronized lyrics display in MPV."
    )

    args = parser.parse_args()

    try:
        player = MusicPlayer()
        player.set_lyrics_mode(args.disable_lyrics) ## Set synced lyrics preference
        if args.trending:
            player.get_trending()
        elif args.version:
            print(player.get_version())
        elif args.playlist:
            player.playlist_info()
        elif args.query:
            query = ' '.join(args.query)

            if player.url_parser.is_url(query):
                if player.url_parser.is_track_url(query): ## If its a spotify track
                    player.add_sp_track_to_queue()
                    player.interactive_mode()
                elif player.url_parser.is_album_url(query): ## If its a spotify album
                    player.add_sp_album_to_queue()
                    player.interactive_mode()
                elif player.url_parser.is_playlist_url(query): ## If its a spotify playlist
                    player.add_sp_playlist_to_queue()
                    player.interactive_mode()
            else:
                results = player.search_songs(query)
                if results:
                    track = player.display_results(query, results)
                    if track:
                        player.queue_manager.add_to_queue(track)
                player.interactive_mode()
        else:
            player.interactive_mode()

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()