import json
from termcolor import colored
from utils import check_integers_with_spaces
from track_utils import create_track
from random import shuffle

class PlaylistManager:
    def __init__(self, playlist_db, playlist_queue: list, queue_manager):
        self.playlist_db = playlist_db
        self.playlist_queue = playlist_queue
        self.queue_manager = queue_manager # To use play_queue, play_specific_index, play_indexes

    def playlist_info(self):
        """ Various options for playlists"""
        self.playlist_db.create_table()

        while True:
            choice = input(colored(f"\nPick [(L)ist Playlists, (C)reate Playlist, (R)emove Playlist, (Q)uit]: ", 'red'))

            if choice.lower() == "c":

                name = input(colored(f"\nEnter playlist name [(B)ack]: ", 'red'))

                if not name or name.lower() == "b":
                    continue

                else:
                    self.playlist_db.create_playlist(name)
                    continue

            elif choice.lower() == "l":
                name, data = self.list_playlists()
                if name is False and data is False:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))
                elif name is not None and data is not None:
                    self.list_playlist_content(name, data)
                continue

            elif choice.lower() == "r":
                try:
                    name, data = self.list_playlists()
                except Exception:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))
                    continue

                if name is None or name is False:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))
                    continue

                self.playlist_db.delete_playlist(name)
                print(colored(f"\nDeleted playlist {name}!", 'red', attrs=['bold']))
                continue

            elif choice.lower() == "q":
                self.playlist_db.commit_db()
                return

            else:
                print(colored("\nInvalid input!", 'red', attrs=['bold']))

    def list_playlists(self):
        """ List all playlists in the db """
        self.playlist_db.create_table()

        results = self.playlist_db.get_all_playlists()

        if not results:
            print(colored(f"\nNo playlists!", 'red', attrs=['bold']))
            return None, None

        print(colored(f"\nCurrent Playlists: \n", 'cyan', attrs=['bold']))
        for i, row in enumerate(results, 1):
            name, metadata = row
            print(f"{colored(str(i), 'green')}. {colored(name, 'red', attrs=['bold'])} - {colored(len(json.loads((metadata))), 'green', attrs=['bold'])} tracks")

        count = self.playlist_db.get_playlist_count()
        choice = input(colored(f"\nPick [1-{count}, (B)ack]: ", 'red'))
        if choice == "b":
            return None, None

        try:
            result = self.playlist_db.get_playlist_by_index(int(choice) - 1) ## Identify the playlist at the index specified
            if result is None:
                return False, False
            return result
        except ValueError:
            return False, False


    def list_playlist_content(self, name: str, data: dict):
        """ List contents of a playlist in the db """
        print(colored(f"\nContents of: {name}\n", 'cyan', attrs=['bold']))
        for i, track in enumerate(json.loads(data), 1):
            print(f"{colored(str(i), 'green')}. {colored(track['title'], 'red', attrs=['bold'])} - "
                      f"{colored(track['artist'], 'cyan')}")

        self.playlist_queue.clear() # Clear existing playlist queue before loading new one
        self.playlist_queue.extend(json.loads(data))
        self.edit_playlist_queue(name)

    def edit_playlist_queue(self, name: str):
        """ Options to edit the current playlist """
        while True:
            if not self.playlist_queue:
                print(colored("Playlist is empty!", 'red', attrs=['bold']))
                return

            query = input(colored("\nEdit the playlist ", 'cyan', attrs=['bold']) +
                            colored("[(P)lay, (R)emove, (M)ove, (S)huffle, (B)ack, (L)ist tracks]: ", 'red'))

            if not query.strip():
                continue

            query = query.strip()

            if query.lower() == 'b':
                break

            elif query.lower() == 'p':
                self.queue_manager.play_queue(self.playlist_queue)

            elif check_integers_with_spaces(query):
                self.queue_manager.play_indexes(query, self.playlist_queue)
                continue

            elif query.lower() == 'l':
                self.list_playlist_content(name, json.dumps(self.playlist_queue))
                break

            elif query.lower() == 'r': ## Remove a track from the queue

                index = input(colored(f"\nPick [1-{len(self.playlist_queue)}, (B)ack] to remove: ", 'red'))

                if index.lower() == "b": ## Allow exiting the remove sequence
                    continue

                try:
                    if check_integers_with_spaces(index):

                        for i in sorted(index.split(" "), key=int, reverse=True): ## If multiple inputs are entered
                            if i is None:
                                 pass
                            print(colored(f"\nRemoved {self.playlist_queue[int(i) - 1]['title']} - {self.playlist_queue[int(i) - 1]['artist']}  ",
                                'green', attrs=['bold']))
                            self.playlist_queue.pop(int(i) - 1)
                            self.playlist_db.update_playlist_db(name, self.playlist_queue)
                        continue
                    else: # Handle single index removal
                        idx = int(index) - 1
                        if 0 <= idx < len(self.playlist_queue):
                            print(colored(f"\nRemoved {self.playlist_queue[idx]['title']} - {self.playlist_queue[idx]['artist']}  ",
                                'green', attrs=['bold']))
                            self.playlist_queue.pop(idx)
                            self.playlist_db.update_playlist_db(name, self.playlist_queue)
                        else:
                            print(colored("\nIndex out of range!", 'red', attrs=['bold']))


                except ValueError:
                    print(colored("\nInvalid input!", 'red', attrs=['bold']))
                except IndexError:
                    print(colored("\nIndex out of range!", 'red', attrs=['bold']))

            elif query.lower() == 's':

                shuffle(self.playlist_queue) ## Shuffle the queue
                print(colored("\nShuffled the playlist!", 'green', attrs=['bold']))

            elif query.lower() == 'm': ## Move tracks within the queue

                curent_index = input(colored(f"\nPick [1-{len(self.playlist_queue)}, (B)ack] to move: ", 'red'))
                if curent_index.lower() == "b": ## Allow exiting the remove sequence
                    continue

                final_index = input(colored(f"\nPick [1-{len(self.playlist_queue)}, (B)ack] to move to: ", 'red'))
                if final_index.lower() == "b": ## Allow exiting the remove sequence
                    continue

                try:
                    self.playlist_queue.insert(int(final_index) - 1, self.playlist_queue.pop(int(curent_index) - 1))
                    print(colored(f"\nMoved track to position {final_index} ", 'green', attrs=['bold']))
                except:
                    print(colored("\nTrack index out of range!", 'red', attrs=['bold']))

            else:
                print(colored("\nInvalid option entered!", 'red', attrs=['bold']))

            self.playlist_db.update_playlist_db(name, self.playlist_queue)