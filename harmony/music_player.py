"""
Main MusicPlayer class handling core functionality
"""

import sys
import signal
import subprocess
from typing import List, Dict, Optional
import requests
from termcolor import colored
from utils import clear_screen, format_text, format_duration, cleanup_files, create_config_folder, get_artist_names
from lyrics import create_lyrics_file
from spotify_integration import SpotifyIntegration
from database import PlaylistDB
from url_parser import URLParser
from queue_manager import QueueManager
from playlist_manager import PlaylistManager
from track_utils import create_track 

class MusicPlayer:
    """Main music player class handling all functionality"""

    def __init__(self):
        self.__version__ = "0.6.2"
        self.playlist_queue = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.api_base = "https://jiosavan-api2.vercel.app/api"
        self.trending_api = "https://charts-spotify-com-service.spotify.com/public/v0/charts"
        self.spotify = SpotifyIntegration()

        self.config_folder = create_config_folder() ## Store config folder directory
        self.synced_lyrics = True ## To figure out whether or not to display synced lyrics
        self.loop = False ## Looping the queue is disabled by default

        self.playlist_db = PlaylistDB(self.config_folder)
        self.queue = self.playlist_db.get_queue_from_db()
        self.url_parser = URLParser() 
        self.queue_manager = QueueManager(self.queue, self.config_folder, self.synced_lyrics, self.loop,
                                          self.playlist_db) 
        self.playlist_manager = PlaylistManager(self.playlist_db, self.playlist_queue, self.queue_manager) 

        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        """Handling Ctrl+C interrupt"""
        self.playlist_db.commit_db()
        print(colored("\nExiting...", 'red', attrs=['bold']))
        cleanup_files(self.config_folder)
        sys.exit(0)

    def search_songs(self, query: str) -> Optional[Dict]:
        """Search for songs using the API"""
        try:
            print(colored("Searching for songs...", 'cyan', attrs=['bold']))

            response = requests.get(
                f"{self.api_base}/search/songs",
                params={'query': query, 'page': 1, 'limit': 20},
                headers=self.headers,
                timeout=10
            )

            data = response.json()

            if not data.get('data', {}).get('results'):
                print(colored(f"No results found for '{query}'", 'red', attrs=['bold']))
                return None

            return data['data']

        except Exception as e:
            print(colored(f"Search failed: {e}", 'red', attrs=['bold']))
            return None

    def display_results(self, query: str, results: Dict) -> Optional[Dict]:
        """Display search results and let user pick"""
        clear_screen()

        print(colored(f"Results for: {query}\n", 'cyan', attrs=['bold']))

        tracks = results['results']
        for i, track in enumerate(tracks, 1):
            title = format_text(track['name'])
            artist = get_artist_names(track['artists']['primary'])
            duration = format_duration(int(track['duration']))
            explicit = colored("(E)", 'green') if track.get('explicitContent') else ""

            print(f"{colored(str(i), 'green')}. {colored(title, 'red', attrs=['bold'])} - "
                  f"{colored(artist, 'cyan', attrs=['bold'])} ({duration}) {explicit}")

        results = self._pick_track(tracks)
        return results

    def _pick_track(self, tracks: List[Dict]) -> Optional[Dict]:
        """Let user pick a track from results"""
        while True:
            choice = input(colored(f"\nPick [1-{len(tracks)}, (B)ack, (Q)uit, (A)dd to Playlist (space-separated for multiple)]: ", 'red'))

            if choice.lower() == 'q':
                cleanup_files(self.config_folder)
                sys.exit(0)
            elif choice.lower() == 'b':
                return None
            elif choice.lower() == 'a':
                choice = input(colored(f"\nPick [1-{len(tracks)}, (B)ack] to add (space-separated for multiple):  ", 'red'))

                if choice.lower() == 'b':
                    continue

                try:
                    # Handle multiple tracks for playlist
                    from utils import check_integers_with_spaces # Moved import here to prevent circular dependency
                    if check_integers_with_spaces(choice):
                        track_indices = choice.split(" ")
                        selected_tracks = []

                        for item in track_indices:
                            if item.strip():  # Skip empty strings
                                idx = int(item) - 1
                                if 0 <= idx < len(tracks):
                                    selected_tracks.append(tracks[idx])
                                else:
                                    print(colored(f"\nInvalid track number: {item}", 'red', attrs=['bold']))
                                    break
                        else:
                            # All indices were valid
                            name, data = self.playlist_manager.list_playlists()
                            if name:  # Check if user didn't cancel playlist selection
                                for track in selected_tracks:
                                    track_data = create_track(track)
                                    self.playlist_db.add_track_to_playlist(name, track_data)

                            return None

                    # Handle single track for playlist
                    else:
                        idx = int(choice) - 1
                        if 0 <= idx < len(tracks):
                            track_data = create_track(tracks[idx])
                            name, data = self.playlist_manager.list_playlists()
                            self.playlist_db.add_track_to_playlist(name, track_data)
                            return None
                        else:
                            print(colored("\nInvalid choice!", 'red', attrs=['bold']))

                except ValueError:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))

            else:
                # Original track selection logic for playing/queueing
                try:
                    from utils import check_integers_with_spaces # Moved import here to prevent circular dependency
                    if check_integers_with_spaces(choice): ## Add multiple tracks to the queue
                        track = choice.split(" ")
                        track = [tracks[int(item) - 1] for item in track if item is not None]
                        return track

                    idx = int(choice) - 1
                    if 0 <= idx < len(tracks):
                        track = tracks[idx]
                        return track
                    else:
                        print(colored("\nInvalid choice!", 'red', attrs=['bold']))
                except ValueError:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))

    def add_sp_track_to_queue(self):
        """ Add a track from Spotify to the queue """
        track_info = self.spotify.get_track_info(self.url_parser.track_id)
        title = track_info['name']
        artist = get_artist_names(track_info['artists'])
        duration = format_duration(track_info['duration_ms']/1000) ## Format in seconds, not ms.
        url = self.get_url(title, artist)

        self.queue.append({
            'title': title,
            'artist': artist,
            'duration': duration,
            'url': url
        })

        print(colored(f"\nAdded {title} - {artist}", 'green', attrs=['bold']))
        self.playlist_db.add_queue_to_db(self.queue)

    def add_sp_album_to_queue(self):
        """ Add an album from Spotify to the queue """

        tracks = self.spotify.get_album_tracks(self.url_parser.album_id)
        for track_info in tracks:

            title = track_info['name']
            artist = get_artist_names(track_info['artists'])
            duration = format_duration(track_info['duration_ms']/1000) ## Format in seconds, not ms.
            url = self.get_url(title, artist)

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
                })

        print(colored(f"\nAdded {len(tracks)} track(s) to the queue", 'green', attrs=['bold']))
        self.playlist_db.add_queue_to_db(self.queue)

    def add_sp_playlist_to_queue(self):
        """ Add a playlist from Spotify to the queue """

        tracks = self.spotify.get_playlist_tracks(self.url_parser.playlist_id)

        for track_info in tracks:

            title = track_info['track']['name']
            artist = get_artist_names(track_info['artists'])
            duration = format_duration(track_info['track']['duration_ms']/1000) ## Format in seconds, not ms.
            url = self.get_url(title, artist)

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
                })

        print(colored(f"\nAdded {len(tracks)} track(s) to the queue", 'green', attrs=['bold']))
        self.playlist_db.add_queue_to_db(self.queue)

    def get_url(self, title: str, artist: str):
        """ Get the track's stream URL """
        response = requests.get(
                f"{self.api_base}/search/songs",
                params={'query': f"{title} {artist}", 'page': 1, 'limit': 1},
                headers=self.headers,
                timeout=10
            )

        data = response.json()
        return data['data']['results'][0]['downloadUrl'][4]['url']

    def get_version(self):
        """ Get the program's current version """
        return self.__version__

    def get_trending(self):
        """Get trending tracks"""
        try:
            print(colored("Fetching trending tracks...", 'cyan', attrs=['bold']))

            response = requests.get(self.trending_api, headers=self.headers, timeout=10)
            data = response.json()

            clear_screen()
            print(colored("Trending Tracks:\n", 'cyan', attrs=['bold']))

            entries = data['chartEntryViewResponses'][0]['entries']
            for i, entry in enumerate(entries[:20], 1):
                track = entry['trackMetadata']
                title = format_text(track['trackName'])
                artist = format_text(track['artists'][0]['name'])
                print(f"{colored(str(i), 'green')}. {colored(title, 'red', attrs=['bold'])} - "
                      f"{colored(artist, 'cyan')}")

        except Exception as e:
            print(colored(f"\nFailed to fetch trending: {e}", 'red', attrs=['bold']))

    def interactive_mode(self):
        """ Main interactive loop """
        while True:
            try:
                query = input(colored("\nSearch/Add to queue ", 'cyan', attrs=['bold']) +
                            colored("[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear, (V)iew playlists]: ", 'red'))

                if not query.strip():
                    continue

                query = query.strip()

                # Handle commands
                from utils import is_integer, check_integers_with_spaces # Moved import here to prevent circular dependency
                if query.lower() == 'q':
                    break
                elif query.lower() == 'p':
                    self.queue_manager.play_queue()
                elif query.lower() == 'v':
                    self.playlist_manager.playlist_info()
                elif query.lower() == 's':
                    self.queue_manager.show_queue()
                elif query.lower() == 'c':
                    self.queue_manager.clear_queue()
                elif query.lower() == 'e':
                    self.queue_manager.edit_queue()

                elif self.url_parser.is_url(query):
                    if self.url_parser.is_track_url(query): ## If its a spotify track
                        self.add_sp_track_to_queue()
                    elif self.url_parser.is_album_url(query): ## If its a spotify album
                        self.add_sp_album_to_queue()
                    elif self.url_parser.is_playlist_url(query): ## If its a spotify playlist
                        self.add_sp_playlist_to_queue()

                elif is_integer(query): ## If input is an intger
                    self.queue_manager.play_specific_index(query)
                elif check_integers_with_spaces(query): ## If input is multiple intgers spearated by spaces
                    self.queue_manager.play_indexes(query)

                else:
                    # Search for songs
                    results = self.search_songs(query)
                    if results:
                        track = self.display_results(query, results)
                        if track is None:
                            continue
                        self.queue_manager.add_to_queue(track)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(colored(f"Error: {e}", 'red', attrs=['bold']))

        cleanup_files(self.config_folder)
        self.playlist_db.commit_db()

    def set_lyrics_mode(self, value: bool):
        if value:
            self.synced_lyrics = False ## If -dl was passed, synced should be false
            self.queue_manager.synced_lyrics = False
        return

    def playlist_info(self):
        """ Various options for playlists"""
        self.playlist_db.create_table()
        self.playlist_manager.playlist_info()