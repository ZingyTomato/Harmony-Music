"""
Main MusicPlayer class handling core functionality
"""

import sys
import signal
import subprocess
from typing import List, Dict, Optional
import requests
from termcolor import colored
from utils.core_utils import clear_screen, format_text, format_duration, cleanup_files, create_config_folder, get_artist_names, is_range_format, create_config_file, get_config_value, extract_range_numbers
from functions.lyrics import create_lyrics_file
from integrations.spotify import SpotifyIntegration
from functions.database import DB
from utils.url_parser import URLParser
from functions.queue_manager import QueueManager
from functions.playlist_manager import PlaylistManager
from utils.track_utils import create_track 

class MusicPlayer:
    """Main music player class handling all functionality"""

    def __init__(self):
        self.__version__ = "0.6.3"
        self.playlist_queue = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.api_base = "https://jiosavan-api2.vercel.app/api"
        self.trending_api = "https://charts-spotify-com-service.spotify.com/public/v0/charts"
        self.spotify = SpotifyIntegration()

        self.config_folder = create_config_folder() ## Store config folder directory
        self.config_file = create_config_file(self.config_folder) ## Store config file directory
        self.synced_lyrics = get_config_value("SHOW_SYNCED_LYRICS", self.config_file) ## To figure out whether or not to display synced lyrics
        self.loop = get_config_value("LOOP_QUEUE", self.config_file) ## Looping the queue is disabled by default
        self.persistent_queue = get_config_value("PERSISTENT_QUEUE", self.config_file) ## Whether or not to save the queue in the db after exiting

        self.playlist_db = DB(self.config_folder)
        self.queue = self.playlist_db.get_queue_from_db()
        self.url_parser = URLParser() 
        self.queue_manager = QueueManager(self.queue, self.config_folder, self.synced_lyrics, self.loop,
                                          self.playlist_db, self.persistent_queue) 
        self.playlist_manager = PlaylistManager(self.playlist_db, self.playlist_queue, 
                                                self.queue_manager, self.loop) 

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
                print(colored(f"\nNo results found for '{query}'", 'red', attrs=['bold']))
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
                choice = input(colored(f"\nPick [1-{len(tracks)}, (B)ack, (Q)uit, (A)dd to Playlist]: ", 'red'))

                if choice.lower() == 'q':
                    cleanup_files(self.config_folder)
                    sys.exit(0)
                elif choice.lower() == 'b':
                    return None
                elif choice.lower() == 'a':
                    choice = input(colored(f"\nPick [1-{len(tracks)}, (B)ack] to add:  ", 'red'))

                    if choice.lower() == 'b':
                        continue

                    try:
                        # Handle multiple tracks for playlist
                        from utils.core_utils import check_integers_with_spaces # Moved import here to prevent circular dependency
                        if check_integers_with_spaces(choice) or extract_range_numbers(choice) is not None:
                            try:
                                track_indices = choice.split(" ")
                                test = choice.split("") ## TTo trigger ValueError
                                selected_tracks = []
                            except ValueError: ## If inputs were separated by ..
                                track_indices = extract_range_numbers(str(choice))
                                selected_tracks = []

                            for item in track_indices:
                                if str(item).strip():  # Skip empty strings
                                    try:
                                        idx = int(item) - 1
                                        if 0 <= idx < len(tracks):
                                            selected_tracks.append(tracks[idx])
                                        else:
                                            print(colored(f"\nInvalid track number: {item} (must be between 1 and {len(tracks)})", 'red', attrs=['bold']))
                                            break
                                    except ValueError:
                                        print(colored(f"\nInvalid track number: {item} (not a valid number)", 'red', attrs=['bold']))
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
                                print(colored(f"\nInvalid track number: {choice} (must be between 1 and {len(tracks)})", 'red', attrs=['bold']))

                    except ValueError:
                        print(colored("\nInvalid input!", 'red', attrs=['bold']))

                else:
                    # Original track selection logic for playing/queueing
                    try:
                        from utils.core_utils import check_integers_with_spaces # Moved import here to prevent circular dependency
                        if check_integers_with_spaces(choice) or extract_range_numbers(choice) is not None: ## Add multiple tracks to the queue
                            try:
                                track_indices = choice.split(" ")
                                test = choice.split("") ## TTo trigger ValueError
                                selected_tracks = []
                                
                                for item in track_indices:
                                    if str(item).strip():  # Skip empty strings
                                        try:
                                            idx = int(item) - 1
                                            if 0 <= idx < len(tracks):
                                                selected_tracks.append(tracks[idx])
                                            else:
                                                print(colored(f"\nInvalid track number: {item} (must be between 1 and {len(tracks)})", 'red', attrs=['bold']))
                                                return None
                                        except ValueError:
                                            print(colored(f"\nInvalid track number: {item} (not a valid number)", 'red', attrs=['bold']))
                                            return None
                                
                                return selected_tracks if selected_tracks else None
                                
                            except ValueError:
                                # Handle range-based input
                                track_indices = extract_range_numbers(choice)
                                selected_tracks = []
                                
                                for item in track_indices:
                                    try:
                                        idx = int(item) - 1
                                        if 0 <= idx < len(tracks):
                                            selected_tracks.append(tracks[idx])
                                        else:
                                            print(colored(f"\nInvalid track number: {item} (must be between 1 and {len(tracks)})", 'red', attrs=['bold']))
                                            return None
                                    except ValueError:
                                        print(colored(f"\nInvalid track number: {item} (not a valid number)", 'red', attrs=['bold']))
                                        return None
                                
                                return selected_tracks if selected_tracks else None
                        
                        # Handle single track selection
                        else:
                            try:
                                idx = int(choice) - 1
                                if 0 <= idx < len(tracks):
                                    return tracks[idx]
                                else:
                                    print(colored(f"\nInvalid track number: {choice} (must be between 1 and {len(tracks)})", 'red', attrs=['bold']))
                            except ValueError:
                                print(colored(f"\nInvalid input: {choice} (not a valid number)", 'red', attrs=['bold']))
                    
                    except Exception as e:
                        print(colored(f"\nError processing selection: {str(e)}", 'red', attrs=['bold']))

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
        if self.persistent_queue:
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
        if self.persistent_queue:
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
        if self.persistent_queue:
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
                            colored("[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear, (A)dd to playlist, (V)iew playlists]: ", 'red'))

                if not query.strip():
                    continue

                query = query.strip()

                # Handle commands
                from utils.core_utils import is_integer, check_integers_with_spaces # Moved import here to prevent circular dependency
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
                elif query.lower() == 'a': ## Add tracks from the queue to a playlist
                    self.queue_manager.show_queue()
                    name, data = self.playlist_manager.list_playlists()
                    
                    try:
                        choice = input(colored(f"\nPick [1-{len(self.queue)}, (B)ack] to add:  ", 'red'))
                        if choice.lower() == "b":
                            continue      
                                          
                        elif check_integers_with_spaces(choice):
                            for i in sorted(choice.split(" "), key=int): ## If multiple inputs are entered
                                if i is None:
                                    pass                                     
                                self.playlist_db.add_track_to_playlist(name, self.queue[int(i) - 1])
                                
                        elif extract_range_numbers(choice) is not None:
                            for i in sorted(extract_range_numbers(choice), key=int): ## If multiple inputs are entered
                                if i is None:
                                    pass   
                                self.playlist_db.add_track_to_playlist(name, self.queue[int(i) - 1])
                    except:
                        print(colored("\nInvalid input entered!", 'red', attrs=['bold']))

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
                elif is_range_format(query): ## If input is 2 intgers spearated by ..
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

    def playlist_info(self):
        """ Various options for playlists"""
        self.playlist_db.create_table()
        self.playlist_manager.playlist_info()