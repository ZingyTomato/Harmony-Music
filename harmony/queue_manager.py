import subprocess
import sys
from random import shuffle
from termcolor import colored
from utils import clear_screen, cleanup_files, format_duration, format_text, is_integer, check_integers_with_spaces
from lyrics import create_lyrics_file

class QueueManager:
    def __init__(self, queue: list, persist: bool, config_folder: str, synced_lyrics: bool):
        self.queue = queue
        self.persist = persist
        self.config_folder = config_folder
        self.synced_lyrics = synced_lyrics

    def add_to_queue(self, track: dict):
        """Add track to queue"""
        if list(track):
            length = len(track)
        else:
            length = 1
            
        for i in range(length):
            title = format_text(track[i]['name'])
            artist = format_text(track[i]['artists']['primary'][0]['name'])
            duration = format_duration(int(track[i]['duration']))
            url = track[i]['downloadUrl'][4]['url']  # Get the streaming URL

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
            })

            print(colored(f"\nAdded: {title} - {artist}", 'green', attrs=['bold']))

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

    def play_queue(self, queue_to_play: list = None):
        """Play all tracks in queue"""
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        clear_screen()
        print(colored("Playing queue...", 'cyan', attrs=['bold']))
        print(colored("Controls: (Q)uit, (L)oop", 'red'))

        for i, track in enumerate(queue_to_play.copy()):

            if i + 1 < len(queue_to_play): ## Display up next if there's more than 1 track in the queue
                next_track = queue_to_play[i + 1]
                print(f"\nUp Next: {colored(next_track['title'], 'red')} - {colored(next_track['artist'], 'cyan')}")
            else:
                pass

            print(f"\nNow Playing: {colored(track['title'], 'red')} - {colored(track['artist'], 'cyan')}")

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
            if queue_to_play and queue_to_play[0] == track and self.persist == False:
                queue_to_play.pop(0)

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
        print(colored("Controls: (Q)uit, (L)oop", 'red'))

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
        if queue_to_play and queue_to_play[int(index) - 1] == track and self.persist == False:
            queue_to_play.pop(int(index) - 1)

        cleanup_files(self.config_folder)

    def play_indexes(self, indexes: str, queue_to_play: list = None):
        """Play multiple indexes in the queue"""
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            print(colored("\nQueue is empty!", 'red', attrs=['bold']))
            return

        parts = indexes.split()
        for i, index in enumerate(parts):

            if i + 1 < len(parts):
                next_track = parts[i + 1]
                self.play_specific_index(int(index), queue_to_play, next_track) ## If multiple indexes were entered
            else:
                self.play_specific_index(int(index), queue_to_play, None)  ## If only 1 index was entered

        return