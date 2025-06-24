from random import shuffle
from termcolor import colored
from utils import clear_screen, cleanup_files, format_duration, format_text, is_integer, check_integers_with_spaces, get_artist_names
from lyrics import create_lyrics_file
import mpv
import sys
import time

class QueueManager:
    def __init__(self, queue: list, config_folder: str, 
                 synced_lyrics: bool, loop: bool, db):
        self.queue = queue
        self.config_folder = config_folder
        self.synced_lyrics = synced_lyrics
        self.loop = loop
        self.playlist_db = db

    def add_to_queue(self, track: dict):
        """Add track to queue"""
        if list(track):
            length = len(track)
        else:
            length = 1
            
        for i in range(length):
            title = format_text(track[i]['name'])
            artist = get_artist_names(track[i]['artists']['primary'])
            duration = format_duration(int(track[i]['duration']))
            url = track[i]['downloadUrl'][4]['url']  # Get the streaming URL

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
            })

            print(colored(f"\nAdded: {title} - {artist}", 'green', attrs=['bold']))
            self.playlist_db.add_queue_to_db(self.queue)
            
    def show_queue(self):
        """ Display current queue """
        if not self.queue:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

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
        self.playlist_db.add_queue_to_db(self.queue)
        return

    def edit_queue(self):
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
                    print(colored("\nQueue loop enabled!",
                                  'green', attrs=['bold']))
                else:
                    self.loop = False
                    print(colored("\nQueue loop disabled!", 'red', attrs=['bold']))

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
                        
                        self.playlist_db.add_queue_to_db(self.queue)
                        return

                    print(colored(f"\nRemoved {self.queue[int(index) - 1]['title']} - {self.queue[int(index) - 1]['artist']}  ",
                                  'green', attrs=['bold']))
                    self.queue.pop(int(index) - 1)
                    self.playlist_db.add_queue_to_db(self.queue)

                except:
                    print(colored("\nIndex out of range!", 'red', attrs=['bold']))

            elif query.lower() == 's':

                shuffle(self.queue) ## Shuffle the queue
                print(colored("\nShuffled the queue!", 'green', attrs=['bold']))
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
                
    def play_media(self, url: str, lyrics: str, track_position: int,
                   queue: list): 
        
        player = mpv.MPV(terminal=True, input_terminal=True,
                         term_osd_bar=True) ## Disable the regular controls
        
        exit = False
        previous = False
        
        @player.on_key_press('l')
        def loop(): ## Handle queue loop logic
            
            if self.loop:
                self.loop = False
                player.term_status_msg = f"Queue Loop: Disabled"
                time.sleep(2)
                player.term_status_msg = player.term_status_msg = f"Track Number: {int(track_position) + 1}/{len(queue)}, (N)ext, (P)revious, (L)oop"

            else:
                self.loop = True
                player.term_status_msg = f"Queue Loop: Enabled"
                time.sleep(2)
                player.term_status_msg = player.term_status_msg = f"Track Number: {int(track_position) + 1}/{len(queue)}, (N)ext, (P)revious, (L)oop"
                  
        @player.on_key_press('c')
        def clear_queue():
            nonlocal exit
            queue = self.clear_queue()
            player.quit()
            exit = True
            
        @player.on_key_press('q')
        def exit_queue():
            nonlocal exit
            player.quit()
            exit = True
            
        @player.on_key_press('n')
        def next_track():
            player.quit()
            
        @player.on_key_press('p')
        def previous_track():
            nonlocal previous
            player.quit()
            previous = True
        
        if len(queue) > 0:
            player.loadfile(url, sub_file=lyrics)
            player.term_status_msg = f"Track Number: {int(track_position) + 1}/{len(queue)}, (N)ext, (P)revious, (L)oop"
            player.wait_for_playback()
        
        player.terminate()
        if exit:
            return "Exited"
        elif previous:
            return "Previous"

    def play_queue(self, queue_to_play: list = None):
        """Play all tracks in queue"""
        if queue_to_play is None:
            queue_to_play = self.queue

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
                print(colored("Controls: (Q)uit, (C)lear, Seek with arrow keys", 'red'))

                if i + 1 < len(queue_copy):
                    next_track = queue_copy[i + 1]
                    print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")

                print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

                create_lyrics_file(
                    f"{track['title']} - {track['artist']}", 
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

                    if response == "Exited":
                        return
                    if response == "Previous":
                        if i > 0:
                            i -= 1
                            continue

                except KeyboardInterrupt:
                    return
                finally:
                    cleanup_files(self.config_folder)

                i += 1  # Only increment if not going back

            if not self.loop:
                break

            cleanup_files(self.config_folder)

    def play_specific_index(self, index: int, queue_to_play: list = None, next_track_index=None):
        """Play a specific index in queue"""
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        clear_screen()
        print(colored(f"Playing track at index {index}...", 'cyan', attrs=['bold']))
        print(colored("Controls: (Q)uit, (C)lear, Seek with arrow keys", 'red'))

        try:
            track = queue_to_play[int(index) - 1] ## Index starts from 1 in the displayed list.
        except:
            print(colored("\nIndex out of range!", 'red', attrs=['bold'])) ## If an invalid index was entered.
            return

        if next_track_index is not None: ## Display next track in queue if present in input
            next_track = queue_to_play[int(next_track_index) - 1]
            print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")

        print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

        # Create lyrics file
        create_lyrics_file(f"{track['title']} - {track['artist']}", self.config_folder,
                           self.synced_lyrics)

        try:
            response = self.play_media(track['url'], f"{self.config_folder}/lyrics.vtt", int(index) - 1, queue_to_play)
        except KeyboardInterrupt:
            pass
        finally:
            cleanup_files(self.config_folder)

        cleanup_files(self.config_folder)
        return response

    def play_indexes(self, indexes: str, queue_to_play: list = None):
        """Play multiple indexes in the queue with Previous/Next support"""
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        parts = [int(p) for p in indexes.split()]
        i = 0

        while i < len(parts):
            current_index = parts[i]
            next_index = parts[i + 1] if i + 1 < len(parts) else None

            response = self.play_specific_index(current_index, queue_to_play, next_index)

            if response == "Exited":
                break
            elif response == "Previous":
                if i > 0:
                    i -= 1
                    continue

            i += 1