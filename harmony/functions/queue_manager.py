"""
Queue management: Creation, Deletion & Editing
"""

from random import shuffle
from termcolor import colored
from utils.core_utils import clear_screen, cleanup_files, format_duration, format_text, is_integer, check_integers_with_spaces, get_artist_names, extract_range_numbers
from functions.lyrics import create_lyrics_file
import subprocess
import integrations.lastfm as lastfm

class QueueManager:
    def __init__(self, queue: list, config_folder: str, 
                 synced_lyrics: bool, loop: bool, db,
                 persistent_queue: bool) -> None:
        
        self.queue = queue
        self.config_folder = config_folder
        self.synced_lyrics = synced_lyrics
        self.loop = loop
        self.playlist_db = db
        self.persistent_queue = persistent_queue

    def add_to_queue(self, track: dict) -> None:
        """Add track to queue"""
        if list(track):
            length = len(track)
        else:
            length = 1
            
        for i in range(length):
            title = format_text(track[i]['name'])
            artist = get_artist_names(track[i]['artists']['primary'])
            duration = format_duration(int(track[i]['duration']))
            url = track[i]['downloadUrl'][4]['url']  # Get the stream URL

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
            })

            print(colored(f"\nAdded: {title} - {artist}", 'green', attrs=['bold']))
            if self.persistent_queue:
                self.playlist_db.add_queue_to_db(self.queue)
        return
    
    def add_playlist_to_queue(self, track: dict) -> None:
        """Add a track from the playlist to queue"""

        self.queue.append({
            'title': track['title'],
            'artist': track['artist'],
            'duration': track['duration'],
            'url': track['url']
        })

        print(colored(f"\nAdded: {track['title']} - {track['artist']} to the queue!", 'green', attrs=['bold']))
        if self.persistent_queue:
            self.playlist_db.add_queue_to_db(self.queue)
        return
            
    def show_queue(self) -> None:
        """ Display current queue """
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        print(colored("\nCurrent Queue:", 'cyan', attrs=['bold']))

        for i, track in enumerate(self.queue, 1):
            print(f"{colored(str(i), 'green')}. {colored(track['title'], 'red')} - "
                  f"{colored(track['artist'], 'cyan')} ({track['duration']})")
        return

    def clear_queue(self) -> None:
        """ Clear the current queue """
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        self.queue.clear()
        print(colored("\nCleared the queue!", 'red', attrs=['bold']))
        if self.persistent_queue:
            self.playlist_db.add_queue_to_db(self.queue)
        return

    def edit_queue(self) -> None:
        """ Options to edit the current queue """
        while True:
            if not self.queue:
                print(colored("\nQueue is empty!", 'red', attrs=['bold']))
                return

            query = input(colored("\nEdit the queue ", 'cyan', attrs=['bold']) +
                            colored("[(R)emove, (M)ove, (S)huffle, (B)ack, L(oop), (D)isable Lyrics]: ", 'red'))

            if not query.strip():
                continue

            query = query.strip()

            if query.lower() == 'b':
                break
                    
            elif query.lower() == 'l':

                if self.loop == False: ## Provide option to enable the loop after entering interactive mode
                    self.loop = True
                    print(colored("\nEnabled the Queue/Track loop!",
                                  'green', attrs=['bold']))
                else:
                    self.loop = False
                    print(colored("\nDisabled the Queue/Track loop!", 'red', attrs=['bold']))

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
                        
                        if self.persistent_queue:
                            self.playlist_db.add_queue_to_db(self.queue)
                        return
                    
                    elif extract_range_numbers(index) is not None: ## If indexes are separated by ..
                        
                        for i in sorted(extract_range_numbers(index), key=int, reverse=True): ## If multiple inputs are entered
                            if i is None:
                                pass
                            print(colored(f"\nRemoved {self.queue[int(i) - 1]['title']} - {self.queue[int(i) - 1]['artist']}  ",
                                  'green', attrs=['bold']))
                            self.queue.pop(int(i) - 1)
                        
                        if self.persistent_queue:
                            self.playlist_db.add_queue_to_db(self.queue)
                        return
                        
                    else:
                        print(colored(f"\nRemoved {self.queue[int(index) - 1]['title']} - {self.queue[int(index) - 1]['artist']}  ",
                                  'green', attrs=['bold']))
                        self.queue.pop(int(index) - 1)
                        if self.persistent_queue:
                            self.playlist_db.add_queue_to_db(self.queue)

                except:
                    print(colored("\nIndex out of range!", 'red', attrs=['bold']))

            elif query.lower() == 's':

                shuffle(self.queue) ## Shuffle the queue
                print(colored("\nShuffled the queue!", 'green', attrs=['bold']))
                if self.persistent_queue:
                    self.playlist_db.add_queue_to_db(self.queue)

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
                    if self.persistent_queue:
                        self.playlist_db.add_queue_to_db(self.queue)
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
            return
                
    def play_media(self, url: str, lyrics: str, track_position: int,
                   queue: list) -> None: 
        
            # Play with mpv
        
            cmd = [
                'mpv',
                '--no-video',  
                '--term-osd-bar',
                '--no-resume-playback',
                f'--sub-file={self.config_folder}/lyrics.vtt',
                f"--term-status-msg=Track Number: {track_position + 1}/{len(queue)}",
                url
            ]

            try:
                subprocess.run(cmd, check=False)
                lastfm.scrobbleTrack(queue[track_position]['artist'], 
                                     queue[track_position]['title'])
            except KeyboardInterrupt:
                pass
            finally:
                cleanup_files(self.config_folder)

    def play_queue(self, queue_to_play: list = None, loop: bool = None) -> None:
        """Play all tracks in queue"""
        if queue_to_play is None:
            queue_to_play = self.queue
            
        if loop is not None:
            self.loop = loop

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        while True:  # Keep looping if loop is enabled
            i = 0
            queue_copy = queue_to_play.copy()

            while i < len(queue_copy):
                track = queue_copy[i]

                clear_screen()
                print(colored("Playing queue...", 'cyan', attrs=['bold']))
                print(colored("Controls: Next Track (Q), Exit (Ctrl + C), Seek with arrow keys", 'red'))
                
                if self.loop and len(queue_to_play) > 1:
                    print(colored("Queue Loop: Enabled", 'green', attrs=['bold']))
                elif self.loop and len(queue_to_play) == 1:
                    print(colored("Track Loop: Enabled", 'green', attrs=['bold']))
                
                # Show "Up Next" logic for all cases
                if len(queue_to_play) > 1:
                    if i < len(queue_copy) - 1:
                        # Not last track - show next track in queue
                        next_track = queue_copy[i + 1]
                        print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
                    elif self.loop:
                        # Last track and loop enabled - show first track
                        next_track = queue_copy[0]
                        print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
                    # If last track and no loop, don't show "Up Next"
                elif self.loop and len(queue_to_play) == 1:
                    # Single track with loop - "Up Next" is the same track
                    print(f"\nUp Next: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

                print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")
                
                create_lyrics_file(
                    f"{track['title']} - {track['artist'].split(",")[0]}", 
                    self.config_folder, 
                    self.synced_lyrics
                )

                try:
                    response = self.play_media(
                        track['url'],
                        f"{self.config_folder}/lyrics.vtt",
                        int(i),
                        queue_copy
                    )

                except KeyboardInterrupt:
                    return
                finally:
                    cleanup_files(self.config_folder)

                i += 1  # Only increment if not going back

            if not self.loop:
                break

            cleanup_files(self.config_folder)       

    def play_specific_index(self, index: int, queue_to_play: list = None, 
                            next_track_index=None) -> None:
        """Play a specific index in queue with loop functionality"""
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        try:
            track = queue_to_play[int(index) - 1]  # Index starts from 1 in the displayed list
        except IndexError:
            print(colored("\nIndex out of range!", 'red', attrs=['bold']))
            return

        while True:  # Keep looping if loop is enabled
            clear_screen()
            print(colored(f"Playing index: {index}", 'cyan', attrs=['bold']))
            print(colored("Controls: Next Track (Q), Exit (Ctrl + C), Seek with arrow keys", 'red'))
            if self.loop:
                print(colored("Track Loop: Enabled", 'green', attrs=['bold']))

            # Show next track info with proper loop handling
            if next_track_index is not None:
                try:
                    next_track = queue_to_play[int(next_track_index) - 1]
                    print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
                except IndexError:
                    pass
            elif self.loop:
                # If loop is enabled and no next_track_index, show the same track as "Up Next"
                print(f"\nUp Next: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

            print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

            # Create lyrics file
            create_lyrics_file(
                f"{track['title']} - {track['artist']}", 
                self.config_folder,
                self.synced_lyrics
            )

            try:
                response = self.play_media(
                    track['url'], 
                    f"{self.config_folder}/lyrics.vtt", 
                    int(index) - 1, 
                    queue_to_play
                )
                    
                # If user presses next track or song ends naturally, check loop setting
                if not self.loop:
                    break

            except KeyboardInterrupt:
                return
            finally:
                cleanup_files(self.config_folder)

    def play_indexes(self, indexes: str, queue_to_play: list = None,
                     loop: bool=None) -> None:
        """Play multiple indexes in the queue with Previous/Next support and loop functionality"""
        if queue_to_play is None:
            queue_to_play = self.queue
            
        if loop is not None:
            self.loop = loop

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        try:
            parts = [int(p) for p in indexes.split()]
        except ValueError: ## Integer is separated by ..
            parts = extract_range_numbers(indexes)
        
        while True:  # Keep looping if loop is enabled
            i = 0

            while i < len(parts):
                current_index = parts[i]

                try:
                    track = queue_to_play[current_index - 1]
                except IndexError:
                    print(colored(f"\nIndex {current_index} out of range!", 'red', attrs=['bold']))
                    i += 1
                    continue

                clear_screen()
                print(colored(f"Playing indexes: {", ".join(map(str, parts))}", 'cyan', attrs=['bold']))
                print(colored("Controls: Next Track (Q), Exit (Ctrl + C), Seek with arrow keys", 'red'))
                if self.loop:
                    print(colored("Queue Loop: Enabled", 'green', attrs=['bold']))

                # Show "Up Next" with proper loop handling
                if i + 1 < len(parts):
                    # Not the last index - show next index
                    next_index = parts[i + 1]
                    try:
                        next_track = queue_to_play[next_index - 1]
                        print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
                    except IndexError:
                        pass
                    
                elif self.loop and i == len(parts) - 1 and len(parts) > 1:
                    # Last index in list and loop is enabled - show first index as "Up Next"
                    first_index = parts[0]
                    try:
                        next_track = queue_to_play[first_index - 1]
                        print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
                    except IndexError:
                        pass

                print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

                # Create lyrics file
                create_lyrics_file(
                    f"{track['title']} - {track['artist']}", 
                    self.config_folder,
                    self.synced_lyrics
                )

                try:
                    response = self.play_media(
                        track['url'], 
                        f"{self.config_folder}/lyrics.vtt", 
                        current_index - 1, 
                        queue_to_play
                    )

                except KeyboardInterrupt:
                    return
                finally:
                    cleanup_files(self.config_folder)

                i += 1

            if not self.loop:
                break

            cleanup_files(self.config_folder)