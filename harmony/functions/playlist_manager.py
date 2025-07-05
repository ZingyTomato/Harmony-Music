"""
Playlist management: Creation, Deletion & Editing
"""

import json
from utils.core_utils import (
    check_integers_with_spaces, extract_range_numbers
)
from utils.track_utils import create_track
from random import shuffle
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

class PlaylistManager:
    def __init__(self, playlist_db, playlist_queue: list, queue_manager,
                 loop: bool) -> None:
        
        self.playlist_db = playlist_db
        self.playlist_queue = playlist_queue
        self.queue_manager = queue_manager # To use play_queue, play_specific_index, play_indexes
        self.loop = loop

    def playlist_info(self) -> None:
        """ Various options for playlists"""
        self.playlist_db.create_table()

        while True:
            
            console.print("\n")
            controls_panel = Panel(
            "[bold cyan](S)how Playlists • (C)reate Playlist • (R)emove Playlist • (Q)uit[/bold cyan]",
            title="Options",
            border_style="dim",
            padding=(0,2)
            )

            console.print(controls_panel, justify="center")
            
            choice = Prompt.ask(
                "\n[bold red]Command[/bold red]",
                choices=['s', 'c', 'r', 'q'],
                show_choices=False
            )
            
            if choice.lower() == "c":

                options_panel = Panel(
                        "[bold cyan](B)ack[/bold cyan]",
                        title="Controls",
                        border_style="dim",
                        padding=(0,2)
                    )
                    
                console.print(options_panel, justify="center")
                
                
                name = Prompt.ask(
                "\n[bold red]\nEnter playlist name[/bold red]",
                show_choices=False
                    )
                
                if not name or name.lower() == "b":
                    continue

                else:
                    self.playlist_db.create_playlist(name)
                    continue

            elif choice.lower() == "s":
                name, data = self.list_playlists()
                if name is False and data is False:
                    console.print(Panel(
                        "[red]Invalid input![/red]",
                        title="⚠ Invalid Input",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                elif name is not None and data is not None:
                    self.list_playlist_content(name, data)
                continue

            elif choice.lower() == "r":
                try:
                    name, data = self.list_playlists()
                except Exception:
                    console.print(Panel(
                        "[red]Invalid input![/red]",
                        title="⚠ Invalid Input",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                    continue

                if name is None and data is None:
                    continue
                elif name is None or name is False:
                    console.print(Panel(
                        "[red]Invalid input![/red]",
                        title="⚠ Invalid Input",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                    continue

                self.playlist_db.delete_playlist(name)
                console.print(Panel(
                    f"[red]Deleted playlist {name}![/red]",
                    title="✗ Playlist Deleted",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
                continue

            elif choice.lower() == "q":
                self.playlist_db.commit_db()
                return

            else:
                console.print(Panel(
                    "[red]Invalid input![/red]",
                    title="⚠ Invalid Input",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
        return

    def list_playlists(self) -> None:
        """ List all playlists in the db """
        self.playlist_db.create_table()

        results = self.playlist_db.get_all_playlists()

        if not results:
            console.print(Panel(
                "[red]No playlists found![/red]",
                title="⚠ No Playlists",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return None, None

        table = Table(
            title=f"\n[bold cyan]Current Playlists: \n[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )
        
        table.add_column("#", style="green", width=3, justify="right")
        table.add_column("Name", style="red", min_width=20)
        table.add_column("No. Of Tracks", style="yellow", width=8, justify="center")
        
        for i, row in enumerate(results, 1):
            name, metadata = row
            table.add_row(str(i), name, str(len(json.loads((metadata)))))

        console.print(table, justify="center")
        
        count = self.playlist_db.get_playlist_count()
        
        console.print("\n")
        options_panel = Panel(
            "[bold red]Pick[/bold red] [dim]1-{}[/dim] • [bold cyan](B)ack[/bold cyan]".format(count),
            title="Options",
            border_style="dim",
            padding=(0,2)
        )

        console.print(options_panel, justify="center")
        
        choice = Prompt.ask(
                f"\n[bold red]\nSelect Playlist[/bold red]",
                show_choices=False
            )

        if choice == "b":
            return None, None

        try:
            result = self.playlist_db.get_playlist_by_index(int(choice) - 1) ## Identify the playlist at the index specified
            if result is None:
                return False, False
            return result
        except ValueError:
            return False, False
        return

    def list_playlist_content(self, name: str, data: dict) -> None:
        """ List contents of a playlist in the db """
        table = Table(
            title=f"\n[bold cyan]Contents of: {name}[/bold cyan]\n",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )
        
        table.add_column("#", style="green", width=3, justify="right")
        table.add_column("Title", style="red", min_width=20)
        table.add_column("Artist", style="cyan", min_width=15)
        table.add_column("Duration", style="yellow", width=8, justify="center")
        
        for i, track in enumerate(json.loads(data), 1):
            table.add_row(str(i), track['title'], track['artist'], track['duration'])

        console.print(table, justify="center")
        
        self.playlist_queue.clear() # Clear existing playlist queue before loading new one
        self.playlist_queue.extend(json.loads(data))
        self.edit_playlist_queue(name)
        return

    def edit_playlist_queue(self, name: str) -> None:
        """ Options to edit the current playlist """
        while True:
            if not self.playlist_queue:
                console.print(Panel(
                    "[red]Playlist is empty![/red]",
                    title="⚠ Empty Playlist",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
                return
            
            options_panel = Panel(
                "[bold red]Pick[/bold red] [dim]1-{}[/dim] • [bold cyan](P)lay • (R)emove • (M)ove • (SH)uffle • (B)ack • (L)oop • (A)dd to queue • (S)how Tracks[/bold cyan]".format(len(self.playlist_queue)),
                border_style="dim",
                title="Options",
                padding=(0,2)
            )
            
            console.print(options_panel, justify="center")

            query = Prompt.ask(
                "\n[bold cyan]Edit the playlist[/bold cyan]",
                show_choices=False
            )
            
            if not query.strip():
                continue

            query = query.strip()

            if query.lower() == 'b':
                break
            
            elif query.lower() == 'l':

                if self.loop == False: ## Provide option to enable the loop after entering interactive mode
                    self.loop = True
                    console.print(Panel(
                        "[green]Enabled the Queue/Track loop![/green]",
                        title="✓ Loop Enabled",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                else:
                    self.loop = False
                    console.print(Panel(
                        "[red]Disabled the Queue/Track loop![/red]",
                        title="✗ Loop Disabled",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            elif query.lower() == 'p':
                self.queue_manager.play_queue(self.playlist_queue, self.loop)

            elif check_integers_with_spaces(query):
                self.queue_manager.play_indexes(query, self.playlist_queue, self.loop)
                continue

            elif query.lower() == 's':
                self.list_playlist_content(name, json.dumps(self.playlist_queue))
                break

            elif query.lower() == 'r': ## Remove a track from the queue
                
                console.print("\n")
                options_panel = Panel(
                    "[bold red]Pick[/bold red] [dim]1-{} to remove[/dim] • [bold cyan](B)ack[/bold cyan]".format(len(self.playlist_queue)),
                    border_style="dim",
                    title="Options",
                    padding=(0,2)
                )
                
                console.print(options_panel, justify="center")
                
                index = Prompt.ask(
                "\n[bold red]Remove Track[/bold red]",
                show_choices=False
                    )

                if index.lower() == "b": ## Allow exiting the remove sequence
                    continue

                try:
                    if check_integers_with_spaces(index):

                        for i in sorted(index.split(" "), key=int, reverse=True): ## If multiple inputs are entered
                            if i is None:
                                 pass
                            console.print(Panel(
                                f"[green]Removed {self.playlist_queue[int(i) - 1]['title']} - {self.playlist_queue[int(i) - 1]['artist']}![/green]",
                                title="✓ Track Removed",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                            self.playlist_queue.pop(int(i) - 1)
                            self.playlist_db.update_playlist_db(name, self.playlist_queue)
                        continue
                    
                    elif extract_range_numbers(index) is not None: ## If indexes are separated by ..
                        
                        for i in sorted(extract_range_numbers(index), key=int, reverse=True): ## If multiple inputs are entered
                            if i is None:
                                pass
                            console.print(Panel(
                                f"[green]Removed {self.playlist_queue[int(i) - 1]['title']} - {self.playlist_queue[int(i) - 1]['artist']}![/green]",
                                title="✓ Track Removed",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                            self.playlist_queue.pop(int(i) - 1)
                            
                        self.playlist_db.update_playlist_db(name, self.playlist_queue)
                        return
                    
                    else: # Handle single index removal
                        idx = int(index) - 1
                        if 0 <= idx < len(self.playlist_queue):
                            console.print(Panel(
                                f"[green]Removed {self.playlist_queue[idx]['title']} - {self.playlist_queue[idx]['artist']}![/green]",
                                title="✓ Track Removed",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                            self.playlist_queue.pop(idx)
                            self.playlist_db.update_playlist_db(name, self.playlist_queue)
                        else:
                            console.print(Panel(
                                "[red]Index out of range![/red]",
                                title="⚠ Invalid Index",
                                border_style="red",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                            
                except ValueError:
                    console.print(Panel(
                        "[red]Invalid Input![/red]",
                        title="⚠ Invalid Input",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                except IndexError:
                    console.print(Panel(
                        "[red]Index out of range![/red]",
                        title="⚠ Invalid Index",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            elif query.lower() == 'a': ## Add a track from the playlist to the queue

                try:
                    console.print("\n")
                    options_panel = Panel(
                        "[bold red]Pick[/bold red] [dim]1-{} to add[/dim] • [bold cyan](B)ack[/bold cyan]".format(len(self.playlist_queue)),
                        border_style="dim",
                        title="Options",
                        padding=(0,2)
                    )
                    
                    console.print(options_panel, justify="center")
        
                    index = Prompt.ask(
                        "\n[bold red]Add track[/bold red]",
                        show_choices=False
                    )

                    if index.lower() == "b": ## Allow exiting the add sequence
                        continue
                    elif check_integers_with_spaces(index):
                        for i in sorted(index.split(" "), key=int): ## If multiple inputs are entered
                            if i is None:
                                 pass             
                            self.queue_manager.add_playlist_to_queue(self.playlist_queue[int(i) - 1])
                            
                    elif extract_range_numbers(index) is not None:
                        for i in sorted(extract_range_numbers(index), key=int): ## If multiple inputs are entered
                            if i is None:
                                 pass             
                            self.queue_manager.add_playlist_to_queue(self.playlist_queue[int(i) - 1])
                    
                except:
                    console.print(Panel(
                        "[red]Invalid input entered![/red]",
                        title="⚠ Invalid Input",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                              
            elif query.lower() == 'sh':

                shuffle(self.playlist_queue) ## Shuffle the queue
                console.print(Panel(
                    "[green]Shuffled the playlist![/green]",
                    title="🔀 Playlist Shuffled",
                    border_style="green",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))

            elif query.lower() == 'm': ## Move tracks within the queue

                console.print("\n")
                options_panel = Panel(
                    "[bold red]Pick[/bold red] [dim]1-{} to move from[/dim] • [bold cyan](B)ack[/bold cyan]".format(len(self.playlist_queue)),
                    border_style="dim",
                    title="Options",
                    padding=(0,2)
                )
                    
                console.print(options_panel, justify="center")
        
                current_index = Prompt.ask(
                    "\n[bold red]Move track[/bold red]",
                    show_choices=False
                )
                
                if current_index.lower() == "b": ## Allow exiting the remove sequence
                    continue
                
                console.print("\n")
                options_panel = Panel(
                    "[bold red]Pick[/bold red] [dim]1-{} to move to[/dim] • [bold cyan](B)ack[/bold cyan]".format(len(self.playlist_queue)),
                    border_style="dim",
                    title="Options",
                    padding=(0,2)
                )
                    
                console.print(options_panel, justify="center")
        
                final_index = Prompt.ask(
                    "\n[bold red]Move track to[/bold red]",
                    show_choices=False
                )

                if final_index.lower() == "b": ## Allow exiting the remove sequence
                    continue

                try:
                    self.playlist_queue.insert(int(final_index) - 1, self.playlist_queue.pop(int(current_index) - 1))
                    console.print(Panel(
                        f"[green]Moved track to position {final_index}![/green]",
                        title="✓ Track Moved",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                except:
                    console.print(Panel(
                        "[red]Track index out of range![/red]",
                        title="⚠ Invalid Index",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            else:
                console.print(Panel(
                    "[red]Invalid input entered![/red]",
                    title="⚠ Invalid Input",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))

            self.playlist_db.update_playlist_db(name, self.playlist_queue)
        return