#!/usr/bin/env python3
"""
Harmony - An open source CLI music streamer based on MPV.
"""

import argparse
import sys
from typing import List, Optional
from rich.traceback import install 
from functions.core import MusicPlayer


class HarmonyArgumentParser:
    """Handles command line argument parsing and validation."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Harmony - An open source TUI music streamer based on MPV. https://github.com/ZingyTomato/Harmony-Music",
            prog="harmony"
        )
        
        self._add_arguments(parser)
        return parser
    
    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add all command line arguments to the parser."""
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
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.parser.parse_args(args)


class HarmonyCommandHandler:
    """Handles the execution of different Harmony commands."""
    
    def __init__(self, player: MusicPlayer):
        self.player = player
        self._command_map = {
            'trending': self._handle_trending,
            'version': self._handle_version,
            'playlist': self._handle_playlist,
            'query': self._handle_query,
            'default': self._handle_default
        }
    
    def execute_command(self, args: argparse.Namespace) -> None:
        """Execute the appropriate command based on parsed arguments."""
        if args.trending:
            self._command_map['trending']()
        elif args.version:
            self._command_map['version']()
        elif args.playlist:
            self._command_map['playlist']()
        elif args.query:
            self._command_map['query'](args.query)
        else:
            self._command_map['default']()
    
    def _handle_trending(self) -> None:
        """Handle trending tracks command."""
        self.player.get_trending()
    
    def _handle_version(self) -> None:
        """Handle version display command."""
        self.player.get_version()
    
    def _handle_playlist(self) -> None:
        """Handle playlist management command."""
        self.player.playlist_info()
    
    def _handle_query(self, query_parts: List[str]) -> None:
        """Handle search query or URL processing."""
        query = ' '.join(query_parts)
        
        if self.player.url_parser.is_url(query):
            self._handle_url_query(query)
        else:
            self._handle_search_query(query)
        
        self.player.interactive_mode()
    
    def _handle_url_query(self, query: str) -> None:
        """Handle URL-based queries (Spotify tracks, albums, playlists)."""
        url_handlers = {
            'track': (self.player.url_parser.is_track_url, self.player.add_sp_track_to_queue),
            'album': (self.player.url_parser.is_album_url, self.player.add_sp_album_to_queue),
            'playlist': (self.player.url_parser.is_playlist_url, self.player.add_sp_playlist_to_queue)
        }
        
        for url_type, (checker, handler) in url_handlers.items():
            if checker(query):
                handler()
                return
    
    def _handle_search_query(self, query: str) -> None:
        """Handle text-based search queries."""
        results = self.player.search_songs(query)
        if results:
            track = self.player.display_results(query, results)
            if track:
                self.player.queue_manager.add_to_queue(track)
    
    def _handle_default(self) -> None:
        """Handle default case (no specific command entered)."""
        self.player.interactive_mode()


class HarmonyApplication:
    """Main application class that orchestrates the Harmony music player."""
    
    def __init__(self):
        self.arg_parser = HarmonyArgumentParser()
        self.player = None
        self.command_handler = None
    
    def initialize(self) -> None:
        """Initialize the music player and command handler."""
        self.player = MusicPlayer()
        self.command_handler = HarmonyCommandHandler(self.player)
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the application with the given arguments."""
        install(show_locals=True) 
        try:
            parsed_args = self.arg_parser.parse_args(args)
            self.initialize()
            self.command_handler.execute_command(parsed_args)
            return 0
        
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0
        except Exception:
            return 1


def main():
    """Entry Point"""
    app = HarmonyApplication()
    sys.exit(app.run())


if __name__ == '__main__':
    main()