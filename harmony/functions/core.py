"""
Main MusicPlayer class handling core functionality
"""

import sys
import signal
import subprocess
from typing import List, Dict, Optional, Union, Any
from abc import ABC, abstractmethod
import requests
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from utils.core_utils import (
    clear_screen, format_text, format_duration, cleanup_files, 
    create_config_folder, get_artist_names, is_range_format, 
    create_config_file, get_config_value, extract_range_numbers,
    is_integer, check_integers_with_spaces
)
from functions.lyrics import create_lyrics_file
from integrations.spotify import SpotifyIntegration
from functions.database import DB
from utils.url_parser import URLParser
from functions.queue_manager import QueueManager
from functions.playlist_manager import PlaylistManager
from utils.track_utils import create_track

# Initialize rich console
console = Console()


class CommandHandler(ABC):
    """Abstract base class for command handlers."""
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this handler can process the given command."""
        pass
    
    @abstractmethod
    def handle(self, command: str, player: 'MusicPlayer') -> bool:
        """Handle the command. Return True if command was processed."""
        pass


class SystemCommandHandler(CommandHandler):
    """Handles system commands like quit, play, show queue, etc."""
    
    COMMANDS = {
        'q': 'quit',
        'p': 'play',
        's': 'show_queue',
        'c': 'clear_queue',
        'e': 'edit_queue',
        'v': 'view_playlists',
        'a': 'add_to_playlist'
    }
    
    def can_handle(self, command: str) -> bool:
        return command.lower() in self.COMMANDS
    
    def handle(self, command: str, player: 'MusicPlayer') -> bool:
        command_key = command.lower()
        action = self.COMMANDS.get(command_key)
        
        if action == 'quit':
            return False  # Signal to exit
        elif action == 'play':
            player.queue_manager.play_queue()
        elif action == 'show_queue':
            player.queue_manager.show_queue()
        elif action == 'clear_queue':
            player.queue_manager.clear_queue()
        elif action == 'edit_queue':
            player.queue_manager.edit_queue()
        elif action == 'view_playlists':
            player.playlist_manager.playlist_info()
        elif action == 'add_to_playlist':
            player._handle_add_to_playlist()
        elif action == "help":
            return True
        
        return True


class URLCommandHandler(CommandHandler):
    """Handles URL-based commands (Spotify URLs)."""
    
    def can_handle(self, command: str) -> bool:
        # Check if command is a URL - we'll get the url_parser from player in handle()
        return ('spotify.com' in command or 
                'open.spotify.com' in command or
                command.startswith('https://'))
    
    def handle(self, command: str, player: 'MusicPlayer') -> bool:
        # Parse the URL first
        player.url_parser.parse_url(command)
        
        if player.url_parser.is_track_url(command):
            player.add_sp_track_to_queue()
        elif player.url_parser.is_album_url(command):
            player.add_sp_album_to_queue()
        elif player.url_parser.is_playlist_url(command):
            player.add_sp_playlist_to_queue()
        else:
            error_panel = Panel(
                "[red]Unsupported Spotify URL format![/red]",
                title="Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)
            return True
        
        return True


class IndexCommandHandler(CommandHandler):
    """Handles index-based commands for playing specific tracks."""
    
    def can_handle(self, command: str) -> bool:
        return (is_integer(command) or 
                check_integers_with_spaces(command) or 
                is_range_format(command))
    
    def handle(self, command: str, player: 'MusicPlayer') -> bool:
        if is_integer(command):
            player.queue_manager.play_specific_index(command)
        elif check_integers_with_spaces(command) or is_range_format(command):
            player.queue_manager.play_indexes(command)
        
        return True


class SearchCommandHandler(CommandHandler):
    """Handles search queries."""
    
    def can_handle(self, command: str) -> bool:
        # This is the fallback handler - it can handle anything
        return True
    
    def handle(self, command: str, player: 'MusicPlayer') -> bool:
        results = player.search_songs(command)
        if results:
            track = player.display_results(command, results)
            if track is not None:
                player.queue_manager.add_to_queue(track)
        return True


class TrackSelector:
    """Handles track selection logic from search results."""
    
    def __init__(self, tracks: List[Dict], player: 'MusicPlayer'):
        self.tracks = tracks
        self.player = player
    
    def select_track(self) -> Optional[Union[Dict, List[Dict]]]:
        """Main selection loop."""
        while True:
            choice = Prompt.ask(
                "[bold red]Pick[/bold red]",
                show_choices=False
            )
            
            if choice.lower() == 'q':
                cleanup_files(self.player.config_folder)
                sys.exit(0)
            elif choice.lower() == 'b':
                return None
            elif choice.lower() == 'a':
                return self._handle_playlist_addition()
            else:
                return self._handle_track_selection(choice)
    
    def _handle_playlist_addition(self) -> None:
        """Handle adding tracks to playlist."""
        choice = Prompt.ask(
            f"[bold yellow]Pick [1-{len(self.tracks)}, (B)ack] to add[/bold yellow]",
        )
        
        if choice.lower() == 'b':
            return None
        
        try:
            selected_tracks = self._parse_track_selection(choice)
            if selected_tracks:
                name, _ = self.player.playlist_manager.list_playlists()
                if name:
                    for track in selected_tracks:
                        track_data = create_track(track)
                        self.player.playlist_db.add_track_to_playlist(name, track_data)
                    
                    success_panel = Panel(
                        f"[green]✓ Added {len(selected_tracks) if isinstance(selected_tracks, list) else 1} track(s) to {name}[/green]",
                        title="Success",
                        border_style="green",
                        padding=(0, 1)
                    )
                    console.print(success_panel)
        except ValueError as e:
            error_panel = Panel(
                f"[red]✗ {str(e)}[/red]",
                title="Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)
        
        return None
    
    def _handle_track_selection(self, choice: str) -> Optional[Union[Dict, List[Dict]]]:
        """Handle track selection for playing/queueing."""
        try:
            return self._parse_track_selection(choice)
        except ValueError as e:
            error_panel = Panel(
                f"[red]✗ {str(e)}[/red]",
                title="Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)
            return None
    
    def _parse_track_selection(self, choice: str) -> Union[Dict, List[Dict]]:
        """Parse user input and return selected track(s)."""
        # Handle range input (e.g., "1..5")
        range_numbers = extract_range_numbers(choice)
        if range_numbers is not None:
            return self._get_tracks_by_indices(range_numbers)
        
        # Handle space-separated numbers (e.g., "1 3 5")
        if check_integers_with_spaces(choice):
            indices = [item.strip() for item in choice.split(" ") if item.strip()]
            return self._get_tracks_by_indices(indices)
        
        # Handle single track selection
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.tracks):
                return self.tracks[idx]
            else:
                raise ValueError(f"Invalid track number: {choice} (must be between 1 and {len(self.tracks)})")
        except ValueError:
            raise ValueError(f"Invalid input: {choice} (not a valid number)")
    
    def _get_tracks_by_indices(self, indices: List[str]) -> List[Dict]:
        """Get tracks by list of string indices."""
        selected_tracks = []
        
        for item in indices:
            try:
                idx = int(item) - 1
                if 0 <= idx < len(self.tracks):
                    selected_tracks.append(self.tracks[idx])
                else:
                    raise ValueError(f"Invalid track number: {item} (must be between 1 and {len(self.tracks)})")
            except ValueError:
                raise ValueError(f"Invalid track number: {item} (not a valid number)")
        
        return selected_tracks


class SpotifyTrackProcessor:
    """Handles processing of Spotify tracks/albums/playlists."""
    
    def __init__(self, player: 'MusicPlayer'):
        self.player = player
    
    def add_track_to_queue(self) -> None:
        """Add a track from Spotify to the queue."""
        with console.status("[bold blue]Adding Spotify track...", spinner="dots"):
            track_info = self.player.spotify.get_track_info(self.player.url_parser.track_id)
            track_data = self._create_track_data(track_info)
            
            self.player.queue.append(track_data)
        
        success_panel = Panel(
            f"[green]✓ Added[/green] [bold]{track_data['title']}[/bold] [dim]by[/dim] [cyan]{track_data['artist']}[/cyan]",
            title="Track Added",
            border_style="green",
            padding=(0, 1)
        )
        console.print(success_panel)
        
        if self.player.persistent_queue:
            self.player.playlist_db.add_queue_to_db(self.player.queue)
    
    def add_album_to_queue(self) -> None:
        """Add an album from Spotify to the queue."""
        with console.status("[bold blue]Adding Spotify album...", spinner="dots"):
            tracks = self.player.spotify.get_album_tracks(self.player.url_parser.album_id)
            
            for track_info in tracks:
                track_data = self._create_track_data(track_info)
                self.player.queue.append(track_data)
        
        success_panel = Panel(
            f"[green]✓ Added[/green] [bold yellow]{len(tracks)}[/bold yellow] track(s) to the queue",
            title="Album Added",
            border_style="green",
            padding=(0, 1)
        )
        console.print(success_panel)
        
        if self.player.persistent_queue:
            self.player.playlist_db.add_queue_to_db(self.player.queue)
    
    def add_playlist_to_queue(self) -> None:
        """Add a playlist from Spotify to the queue."""
        with console.status("[bold blue]Adding Spotify playlist...", spinner="dots"):
            tracks = self.player.spotify.get_playlist_tracks(self.player.url_parser.playlist_id)
            
            for track_info in tracks:
                # Playlist tracks have nested structure
                track_data = self._create_track_data(track_info['track'], track_info.get('artists'))
                self.player.queue.append(track_data)
        
        success_panel = Panel(
            f"[green]✓ Added[/green] [bold yellow]{len(tracks)}[/bold yellow] track(s) to the queue",
            title="Playlist Added",
            border_style="green",
            padding=(0, 1)
        )
        console.print(success_panel)
        
        if self.player.persistent_queue:
            self.player.playlist_db.add_queue_to_db(self.player.queue)
    
    def _create_track_data(self, track_info: Dict, artists: Optional[List] = None) -> Dict:
        """Create standardized track data structure."""
        title = track_info['name']
        artist_list = artists if artists else track_info['artists']
        artist = get_artist_names(artist_list)
        duration = format_duration(track_info['duration_ms'] / 1000)
        url = self.player.get_url(title, artist)
        
        return {
            'title': title,
            'artist': artist,
            'duration': duration,
            'url': url
        }


class MusicPlayer:
    """Main music player class handling all functionality"""

    def __init__(self):
        self.__version__ = "0.7.0"
        self.playlist_queue = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.api_base = "https://jiosavan-api2.vercel.app/api"
        self.trending_api = "https://charts-spotify-com-service.spotify.com/public/v0/charts"
        
        self._initialize_components()
        self._setup_command_handlers()
        self._setup_signal_handler()
    
    def _show_version(self) -> None:
        """Display program version."""
        version_panel = Panel.fit(
            f"[bold cyan]Harmony Music[/bold cyan]\n[dim]Version {self.__version__}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(version_panel)
    
    def _initialize_components(self) -> None:
        """Initialize all player components."""
        self.spotify = SpotifyIntegration()
        
        self.config_folder = create_config_folder()
        self.config_file = create_config_file(self.config_folder)
        self.synced_lyrics = get_config_value("SHOW_SYNCED_LYRICS", self.config_file)
        self.loop = get_config_value("LOOP_QUEUE", self.config_file)
        self.persistent_queue = get_config_value("PERSISTENT_QUEUE", self.config_file)
        
        self.playlist_db = DB(self.config_folder)
        self.queue = self.playlist_db.get_queue_from_db()
        self.url_parser = URLParser()
        self.queue_manager = QueueManager(
            self.queue, self.config_folder, self.synced_lyrics, 
            self.loop, self.playlist_db, self.persistent_queue
        )
        self.playlist_manager = PlaylistManager(
            self.playlist_db, self.playlist_queue, 
            self.queue_manager, self.loop
        )
        
        self.spotify_processor = SpotifyTrackProcessor(self)
    
    def _setup_command_handlers(self) -> None:
        """Set up command handlers in order of priority."""
        self.command_handlers = [
            SystemCommandHandler(),
            URLCommandHandler(),
            IndexCommandHandler(),
            SearchCommandHandler()  # Fallback handler
        ]
    
    def _setup_signal_handler(self) -> None:
        """Set up signal handling for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """Handling Ctrl+C interrupt"""
        self.playlist_db.commit_db()
        
        exit_panel = Panel(
            "[red]Exiting...[/red]",
            title="Goodbye",
            border_style="red",
            padding=(0, 1)
        )
        console.print(exit_panel)
        
        cleanup_files(self.config_folder)
        sys.exit(0)

    def search_songs(self, query: str) -> Optional[Dict]:
        """Search for songs using the API"""
        try:
            with console.status(f"[bold blue]Searching for '[cyan]{query}[/cyan]'...", spinner="dots"):
                response = requests.get(
                    f"{self.api_base}/search/songs",
                    params={'query': query, 'page': 1, 'limit': 20},
                    headers=self.headers,
                    timeout=10
                )

                data = response.json()

            if not data.get('data', {}).get('results'):
                no_results_panel = Panel(
                    f"[red]No results found for '[bold]{query}[/bold]'[/red]",
                    title="Search Results",
                    border_style="red",
                    padding=(0, 1)
                )
                console.print(no_results_panel)
                return None

            return data['data']

        except Exception as e:
            error_panel = Panel(
                f"[red]Search failed: {e}[/red]",
                title="Search Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)
            return None

    def display_results(self, query: str, results: Dict) -> Optional[Union[Dict, List[Dict]]]:
        """Display search results and let user pick"""
        console.clear()

        # Create results table
        table = Table(
            title=f"Results for: [bold cyan]{query}[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )
        
        table.add_column("#", style="green", width=3, justify="right")
        table.add_column("Title", style="red", min_width=20)
        table.add_column("Artist", style="cyan", min_width=15)
        table.add_column("Duration", style="yellow", width=8, justify="center")
        table.add_column("", width=3, justify="center")  # For explicit marker

        tracks = results['results']
        for i, track in enumerate(tracks, 1):
            title = format_text(track['name'])
            artist = get_artist_names(track['artists']['primary'])
            duration = format_duration(int(track['duration']))
            explicit = "(E)" if track.get('explicitContent') else ""

            table.add_row(str(i), title, artist, duration, explicit)

        console.print(table)
        
        # Show options panel
        options_panel = Panel(
            "[bold red]Pick[/bold red] [dim]1-{}[/dim] • [bold cyan](A)dd to Playlist • (B)ack • (Q)uit[/bold cyan]".format(len(tracks)),
            border_style="dim",
            padding=(0,2)
        )
        console.print(options_panel, justify="center")

        selector = TrackSelector(tracks, self)
        return selector.select_track()

    def add_sp_track_to_queue(self):
        """Add a track from Spotify to the queue"""
        self.spotify_processor.add_track_to_queue()

    def add_sp_album_to_queue(self):
        """Add an album from Spotify to the queue"""
        self.spotify_processor.add_album_to_queue()

    def add_sp_playlist_to_queue(self):
        """Add a playlist from Spotify to the queue"""
        self.spotify_processor.add_playlist_to_queue()

    def get_url(self, title: str, artist: str) -> str:
        """Get the track's stream URL"""
        response = requests.get(
            f"{self.api_base}/search/songs",
            params={'query': f"{title} {artist}", 'page': 1, 'limit': 1},
            headers=self.headers,
            timeout=10
        )

        data = response.json()
        return data['data']['results'][0]['downloadUrl'][4]['url']

    def get_version(self) -> str:
        """Get the program's current version"""
        return self._show_version()

    def get_trending(self):
        """Get trending tracks"""
        try:
            with console.status("[bold blue]Fetching trending tracks...", spinner="dots"):
                response = requests.get(self.trending_api, headers=self.headers, timeout=10)
                data = response.json()

            console.clear()
            
            # Create trending table
            table = Table(
                title="Trending Tracks Worldwide",
                show_header=True,
                header_style="bold red",
                border_style="red",
                box=box.HEAVY
            )
            
            table.add_column("Rank", style="gold1 bold", width=4, justify="right")
            table.add_column("Track", style="white bold", min_width=25)
            table.add_column("Artist", style="cyan", min_width=20)

            entries = data['chartEntryViewResponses'][0]['entries']
            for i, entry in enumerate(entries[:20], 1):
                track = entry['trackMetadata']
                title = format_text(track['trackName'])
                artist = format_text(track['artists'][0]['name'])
                
                # Add special styling for top 3
                rank_style = "gold1 bold" if i <= 3 else "yellow"
                table.add_row(f"#{i}", title, artist, style=rank_style if i <= 3 else None)

            console.print(table, justify="center")

        except Exception as e:
            error_panel = Panel(
                f"[red]Failed to fetch trending: {e}[/red]",
                title="Trending Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)

    def _handle_add_to_playlist(self) -> None:
        """Handle adding tracks from queue to playlist."""
        name, _ = self.playlist_manager.list_playlists()
        self.queue_manager.show_queue()
        
        if not name:
            return
        
        try:
            
            controls_panel = Panel(
            "[bold red]Pick[/bold red] [dim]1-{}[/dim] • [bold cyan](B)ack[/bold cyan]".format(len(self.queue)),
            title="Options",
            border_style="dim",
            padding=(0,2)
            )

            console.print(controls_panel)
            
            choice = Prompt.ask(
                f"[bold red]Track(s) to add[/bold red]"
            )
            
            if choice.lower() == "b":
                return
            
            indices = []
            if check_integers_with_spaces(choice):
                indices = [int(i) - 1 for i in choice.split(" ") if i.strip()]
            elif extract_range_numbers(choice) is not None:
                indices = [int(i) - 1 for i in extract_range_numbers(choice)]
            else:
                indices = [int(choice) - 1]
            
            added_count = 0
            for idx in sorted(indices):
                if 0 <= idx < len(self.queue):
                    self.playlist_db.add_track_to_playlist(name, self.queue[idx])
                    added_count += 1
            
        except (ValueError, IndexError):
            error_panel = Panel(
                "[red]Invalid input entered![/red]",
                title="Input Error",
                border_style="red",
                padding=(0, 1)
            )
            console.print(error_panel)

    def interactive_mode(self):
        """Main interactive loop"""
        
        if len(self.queue) == 0: ## Show only if the queue is empty
            help_panel = Panel(
                "[bold cyan]Commands:[/bold cyan]\n"
                "[dim]•[/dim] [bold](P)lay[/bold] - Start playback\n"
                "[dim]•[/dim] [bold](S)how queue[/bold] - View current queue\n"
                "[dim]•[/dim] [bold](E)dit[/bold] - Edit queue\n"
                "[dim]•[/dim] [bold](C)lear[/bold] - Clear queue\n"
                "[dim]•[/dim] [bold](A)dd to playlist[/bold] - Add from queue\n"
                "[dim]•[/dim] [bold](V)iew playlists[/bold] - Playlist management\n"
                "[dim]•[/dim] [bold](Q)uit[/bold] - Exit application\n"
                "[dim]Or enter a search query, number, or Spotify URL[/dim]",
                title="Controls",
                border_style="dim",
                padding=(1, 2)
            )
            console.print(help_panel)
        
        while True:
            try:
                if len(self.queue) > 0: ## If the queue is not empty
                    self.queue_manager.show_queue()
                    options_panel = Panel(
                        "[bold red]Pick[/bold red] [dim]1-{}[/dim] • [bold cyan](P)lay all • (E)dit • (S)how Queue • (Q)uit • (V)iew Playlists • (A)dd to playlist • (C)lear[/bold cyan]".format(len(self.queue)),
                        title="Options",
                        border_style="dim",
                        padding=(0,2)
                    )
                    console.print(options_panel, justify="center")
        
                query = Prompt.ask(
                    "\n[bold red]Search/Command[/bold red]"
                ).strip()

                if not query:
                    continue

                # Process command through handlers
                should_continue = self._process_command(query)
                if not should_continue:
                    break

            except KeyboardInterrupt:
                break
            except Exception as e:
                error_panel = Panel(
                    f"[red]Error: {e}[/red]",
                    title="System Error",
                    border_style="red",
                    padding=(0, 1)
                )
                console.print(error_panel)

        cleanup_files(self.config_folder)
        self.playlist_db.commit_db()
        
        exit_panel = Panel(
            "[green]Exiting...[/green]",
            border_style="green",
            padding=(0, 1)
        )
        console.print(exit_panel)
    
    def _process_command(self, command: str) -> bool:
        """Process command through appropriate handler."""
        for handler in self.command_handlers:
            if handler.can_handle(command):
                return handler.handle(command, self)
        
        return True  # Should never reach here due to fallback handler

    def playlist_info(self):
        """Various options for playlists"""
        self.playlist_db.create_table()
        self.playlist_manager.playlist_info()