"""
Main MusicPlayer class handling core functionality
"""

import sys
import re
import signal
import subprocess
from typing import List, Dict, Optional
import requests
from termcolor import colored
from utils import clear_screen, format_text, format_duration, cleanup_files, is_integer, create_config_folder, check_integers_with_spaces
from lyrics import create_lyrics_file
import spotipy
from spotipy import SpotifyClientCredentials
from random import shuffle

class MusicPlayer:
    """Main music player class handling all functionality"""
    
    def __init__(self):
        self.__version__ = "0.5.3"
        self.queue = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.api_base = "https://jiosavan-api2.vercel.app/api"
        self.trending_api = "https://charts-spotify-com-service.spotify.com/public/v0/charts"
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id="804e387d07ba4ce9b86e10a2acde9804", 
        client_secret="83e9384758c341c0bc96296d8d233145" ## Not sure of a better way to implement this.
            ))
        
        self.track_id = ""
        self.album_id = ""
        self.playlist_id = ""
        self.persist = False ## To figure out whether or not to keep the queue persistent
        self.config_folder = create_config_folder() ## Store config folder directory
        self.synced_lyrics = True ## To figure out whether or not to display synced lyrics
        
        # URL patterns

        self.spotify_track_pattern = re.compile(
            r'track/([a-zA-Z0-9]+)'
        )
        
        self.spotify_album_pattern = re.compile(
            r'(spotify:album:[a-zA-Z0-9]{22}|https://open\.spotify\.com/album/[a-zA-Z0-9]{22})'
        )
        
        self.spotify_playlist_pattern = re.compile(
            r'(spotify:playlist:[a-zA-Z0-9]{22}|https://open\.spotify\.com/playlist/[a-zA-Z0-9]{22})'
        )
        
        self.url_pattern = re.compile(
            r'https?://[^\s"]+'
        )
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """Handling Ctrl+C interrupt"""
        print(colored("\nExiting...", 'red', attrs=['bold']))
        cleanup_files(self.config_folder)
        sys.exit(0)
        
    def is_url(self, url: str) -> bool:
        """Check if text is a valid URL"""
        track_id_match = re.search(self.url_pattern, url)
        
        if not track_id_match:
            return False
        else:
            return True
    
    def is_track_url(self, url: str) -> bool:
        """Check if text is a Spoify track URL"""
        track_id_match = re.search(self.spotify_track_pattern, url)
        
        if not track_id_match:
            return False
        else:
            self.track_id = track_id_match.group(1)
            return True
        
    def is_album_url(self, url: str) -> bool:
        """Check if text is a Spoify album URL"""
        album_id_match = re.search(self.spotify_album_pattern, url)
        
        if not album_id_match:
            return False
        else:
            self.album_id = album_id_match.group(1)
            return True
        
    def is_playlist_url(self, url: str) -> bool:
        """Check if text is a Spoify playlist URL"""
        playlist_id_match = re.search(self.spotify_playlist_pattern, url)
        
        if not playlist_id_match:
            return False
        else:
            self.playlist_id = playlist_id_match.group(1)
            return True
    
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
            artist = format_text(track['artists']['primary'][0]['name'])
            duration = format_duration(int(track['duration']))
            explicit = colored("(E)", 'green') if track.get('explicitContent') else ""
            
            print(f"{colored(str(i), 'green')}. {colored(title, 'red', attrs=['bold'])} - "
                  f"{colored(artist, 'cyan', attrs=['bold'])} ({duration}) {explicit}")
        
        return self._pick_track(tracks)
    
    def _pick_track(self, tracks: List[Dict]) -> Optional[Dict]:
        """Let user pick a track from results"""
        while True:
            choice = input(colored(f"\nPick [1-{len(tracks)}, (B)ack, (Q)uit]: ", 'red'))
            
            if choice.lower() == 'q':
                cleanup_files(self.config_folder)
                sys.exit(0)
            elif choice.lower() == 'b':
                return None
            
            try:
                if check_integers_with_spaces(choice): ## Add multiple tracks to the queue
                    track = choice.split(" ")
                    track = [tracks[int(item) - 1] for item in track if item is not None]
                    return track
                
                idx = int(choice) - 1
                if 0 <= idx < len(tracks):
                    track = tracks[idx]
                    return track
                else:
                    print(colored("Invalid choice!", 'red', attrs=['bold']))
            except ValueError:
                print(colored("Invalid input!", 'red', attrs=['bold']))
    
    def add_to_queue(self, track: dict):
        """Add track to queue"""
        title = format_text(track['name'])
        artist = format_text(track['artists']['primary'][0]['name'])
        duration = format_duration(int(track['duration']))
        url = track['downloadUrl'][4]['url']  # Get the streaming URL
        
        self.queue.append({
            'title': title,
            'artist': artist,
            'duration': duration,
            'url': url
        })
        
        print(colored(f"\nAdded: {title} - {artist}", 'green', attrs=['bold']))
        
    def add_sp_track_to_queue(self):
        """ Add a track from Spotify to the queue """
        track_info = self.sp.track(self.track_id)
        title = track_info['name']
        artist = track_info['artists'][0]['name']
        duration = format_duration(track_info['duration_ms']/1000) ## Format in seconds, not ms.
        url = self.get_url(title, artist)
        
        self.queue.append({
            'title': title,
            'artist': artist,
            'duration': duration,
            'url': url
        })
        
        print(colored(f"\nAdded {title} - {artist}", 'green', attrs=['bold']))
        
    def add_sp_album_to_queue(self):
        """ Add an album from Spotify to the queue """
        
        album = self.sp.album(self.album_id)
        tracks = album['tracks']['items']
        for track_info in tracks:
            
            title = track_info['name']
            artist = track_info['artists'][0]['name']
            duration = format_duration(track_info['duration_ms']/1000) ## Format in seconds, not ms.
            url = self.get_url(title, artist)
        
            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
                })
        
        print(colored(f"\nAdded {len(tracks)} tracks to the queue", 'green', attrs=['bold']))

    def add_sp_playlist_to_queue(self):
        """ Add a playlist from Spotify to the queue """
        
        playlist_id = self.playlist_id
        results = self.sp.playlist_items(playlist_id)
        tracks = results['items']

        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
            
        for track_info in tracks:
            
            title = track_info['track']['name']
            artist = track_info['track']['artists'][0]['name']
            duration = format_duration(track_info['track']['duration_ms']/1000) ## Format in seconds, not ms.
            url = self.get_url(title, artist)
        
            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
                })
        
        print(colored(f"\nAdded {len(tracks)} tracks to the queue", 'green', attrs=['bold']))
    
    def show_queue(self):
        """ Display current queue """
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return
        
        if self.persist:
            print(colored("\nCurrent Queue (Persistent):", 'cyan', attrs=['bold'])) ## Let the user know
        else:
            print(colored("\nCurrent Queue:", 'cyan', attrs=['bold']))
        
        for i, track in enumerate(self.queue, 1):
            print(f"{colored(str(i), 'green')}. {colored(track['title'], 'red')} - "
                  f"{colored(track['artist'], 'cyan')} ({track['duration']})")
            
    def clear_queue(self):
        """ Clear the current queue """
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return
        
        self.queue.clear()
        print(colored("\nCleared the queue!", 'red', attrs=['bold']))
        return
            
    def edit_queue(self):
        """ Options to edit the current queue """
        while True:
            if not self.queue:
                print(colored("\nQueue is empty!", 'red', attrs=['bold']))
                return
                    
            query = input(colored("\nEdit the queue ", 'cyan', attrs=['bold']) + 
                            colored("[(R)emove, (M)ove, (S)huffle, (B)ack, (P)ersist, (D)isable Lyrics]: ", 'red'))

            if not query.strip():
                continue
                
            query = query.strip()
        
            if query.lower() == 'b':
                break
            elif query.lower() == 'p':
                
                if self.persist == False: ## Provide option to make queue persistent after entering interactive mode
                    self.persist = True 
                    print(colored("\nQueue is now persistent", 
                                  'green', attrs=['bold']))
                else:
                    self.persist = False 
                    print(colored("\nQueue is no longer persistent!", 'red', attrs=['bold']))
                    
            elif query.lower() == 'r': ## Remove a track from the queue
                
                index = input(colored(f"\nPick [1-{len(self.queue)}, (B)ack] to remove: ", 'red'))
                
                if index.lower() == "b": ## Allow exiting the remove sequence
                    return self.edit_queue()
                
                try:
                    if check_integers_with_spaces(index):
                        
                        for i in sorted(index.split(" "), key=int, reverse=True): ## If multiple inputs are entered
                            if i is None:
                                pass
                            print(colored(f"\nRemoved {self.queue[int(i) - 1]['title']} - {self.queue[int(i) - 1]['artist']}  ", 
                                  'green', attrs=['bold']))
                            self.queue.pop(int(i) - 1)
                        
                        return
                            
                    print(colored(f"\nRemoved {self.queue[int(index) - 1]['title']} - {self.queue[int(index) - 1]['artist']}  ", 
                                  'green', attrs=['bold']))
                    self.queue.pop(int(index) - 1)
                    
                except:
                    print(colored("\nIndex out of range!", 'red', attrs=['bold']))
                
            elif query.lower() == 's':
                
                shuffle(self.queue) ## Shuffle the queue                    
                print(colored("\nShuffled the queue!", 'green', attrs=['bold']))
                 
            elif query.lower() == 'm': ## Move tracks within the queue
                
                curent_index = input(colored(f"\nPick [1-{len(self.queue)}, (B)ack] to move: ", 'red'))               
                if curent_index.lower() == "b": ## Allow exiting the remove sequence
                    return self.edit_queue()
                
                final_index = input(colored(f"\nPick [1-{len(self.queue)}, (B)ack] to move to: ", 'red'))
                if final_index.lower() == "b": ## Allow exiting the remove sequence
                    return self.edit_queue()
                
                try:
                    self.queue.insert(int(final_index) - 1, self.queue.pop(int(curent_index) - 1))
                    print(colored(f"\nMoved track to position {final_index} ", 'green', attrs=['bold']))
                except:
                    print(colored("\nTrack index out of range!", 'red', attrs=['bold']))

            elif query.lower() == 'd': ## Option to enable/disable synced lyrics
                
                if self.synced_lyrics:
                    self.synced_lyrics = False 
                    print(colored("\nDisabled Synced lyrics!", 'red', attrs=['bold'])) 
                else:
                    self.synced_lyrics = True
                    print(colored("\nEnabled Synced lyrics!", 'green', attrs=['bold']))   
                
            else:
                print(colored("\nInvalid option entered!", 'red', attrs=['bold']))

    def play_queue(self):
        """Play all tracks in queue"""
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return
        
        clear_screen()
        print(colored("Playing queue...", 'cyan', attrs=['bold']))
        print(colored("Controls: (Q)uit, (L)oop, (J) Disable Lyrics", 'red'))
        
        for i, track in enumerate(self.queue.copy()):
            
            if i + 1 < len(self.queue): ## Display up next if there's more than 1 track in the queue
                next_track = self.queue[i + 1]
                print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
            else:
                pass
        
            print(f"\nNow playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")
            
            # Create lyrics file
            create_lyrics_file(f"{track['title']} - {track['artist']}", self.config_folder,
                               self.synced_lyrics)
            
            # Play with mpv
            cmd = [
                'mpv', 
                '--no-video',
                '--term-osd-bar',
                '--no-resume-playback',
                f'--sub-file={self.config_folder}/lyrics.vtt',
                f"--term-playing-msg={track['title']} - {track['artist']}",
                track['url']
            ]
            
            try:
                subprocess.run(cmd, check=False)
            except KeyboardInterrupt:
                break
            finally:
                cleanup_files(self.config_folder)
            
            # Remove played track from queue
            if self.queue and self.queue[0] == track and self.persist == False:
                self.queue.pop(0)
        
        cleanup_files(self.config_folder)
        
    def play_specific_index(self, index: int, next_track_index=None):
        """Play a specific index in queue"""
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return
        
        clear_screen()
        print(colored(f"Playing track at index {index}...", 'cyan', attrs=['bold']))
        print(colored("Controls: (Q)uit, (L)oop, (J) Disable Lyrics", 'red'))
        
        try:
            track = self.queue[int(index) - 1] ## Index starts from 1 in the displayed list.
        except:
            print(colored("\nIndex out of range!", 'red', attrs=['bold'])) ## If an invalid index was entered.
            return
            
        if next_track_index is not None: ## Display next track in queue if present in input
            next_track = self.queue[int(next_track_index) - 1]
            print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
            
        print(f"\nNow playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")
            
        # Create lyrics file
        create_lyrics_file(f"{track['title']} - {track['artist']}", self.config_folder,
                           self.synced_lyrics)
                    
        # Play with mpv
        cmd = [
            'mpv', 
            '--no-video',
            '--term-osd-bar',
            '--no-resume-playback',
            f'--sub-file={self.config_folder}/lyrics.vtt',
            f"--term-playing-msg={track['title']} - {track['artist']}",
            track['url']
        ]
            
        try:
            subprocess.run(cmd, check=False)
        except KeyboardInterrupt:
            pass
        finally:
            cleanup_files(self.config_folder)
            
        # Remove played track from queue
        if self.queue and self.queue[int(index) - 1] == track and self.persist == False:
            self.queue.pop(int(index) - 1)
        
        cleanup_files(self.config_folder)
        
    def play_indexes(self, indexes: str):
        """Play a indexes in queue"""
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return
        
        parts = indexes.split()
        for i, index in enumerate(parts):
            
            if i + 1 < len(parts):
                next_track = parts[i + 1]
                self.play_specific_index(int(index), next_track) ## If multiple indexes were entered
            else:
                self.play_specific_index(int(index), None)  ## If only 1 index was entered
                
        return
        
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
            print(colored("Top Trending Tracks:\n", 'cyan', attrs=['bold']))
            
            entries = data['chartEntryViewResponses'][0]['entries']
            for i, entry in enumerate(entries[:20], 1):
                track = entry['trackMetadata']
                title = format_text(track['trackName'])
                artist = format_text(track['artists'][0]['name'])
                print(f"{colored(str(i), 'green')}. {colored(title, 'red', attrs=['bold'])} - "
                      f"{colored(artist, 'cyan')}")
                      
        except Exception as e:
            print(colored(f"Failed to fetch trending: {e}", 'red', attrs=['bold']))
    
    def interactive_mode(self):
        """ Main interactive loop """
        while True:
            try:
                query = input(colored("\nSearch/Add to queue ", 'cyan', attrs=['bold']) + 
                            colored("[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear]: ", 'red'))
                
                if not query.strip():
                    continue
                
                query = query.strip()
                
                # Handle commands
                if query.lower() == 'q':
                    break
                elif query.lower() == 'p':
                    self.play_queue()
                elif query.lower() == 's':
                    self.show_queue()
                elif query.lower() == 'c':
                    self.clear_queue()
                elif query.lower() == 'e':
                    self.edit_queue()
                    
                elif self.is_url(query):
                    if self.is_track_url(query): ## If its a spotify track
                        self.add_sp_track_to_queue()
                    elif self.is_album_url(query): ## If its a spotify album
                        self.add_sp_album_to_queue()
                    elif self.is_playlist_url(query): ## If its a spotify playlist
                        self.add_sp_playlist_to_queue() 
                        
                elif is_integer(query): ## If input is an intger
                    self.play_specific_index(query)
                elif check_integers_with_spaces(query): ## If input is multiple intgers spearated by spaces
                    self.play_indexes(query)
                    
                else:
                    # Search for songs
                    results = self.search_songs(query)
                    if results:
                        track = self.display_results(query, results)
                        
                        if track is None:
                            continue
                        
                        if list(track): ## If multiple inputs
                            for i in track:
                                self.add_to_queue(i)
                        else: ## If a single input
                            self.add_to_queue(track)
                            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(colored(f"Error: {e}", 'red', attrs=['bold']))
        
        cleanup_files(self.config_folder)
        print(colored("Goodbye!", 'green', attrs=['bold']))
        
    def set_lyrics_mode(self, value: bool):
        if value:
            self.synced_lyrics = False ## If -dl was passed, synced should be false
        return
    
    def set_queue_persist(self, persist: bool):
        if persist:
            self.persist = True
        return