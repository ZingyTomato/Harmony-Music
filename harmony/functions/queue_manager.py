"""
Queue management: Creation, Deletion & Editing
"""

from random import shuffle
from utils.core_utils import clear_screen, cleanup_files, format_duration, format_text, is_integer, check_integers_with_spaces, get_artist_names, extract_range_numbers
from functions.lyrics import create_lyrics_file
import subprocess
import integrations.lastfm as lastfm
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import random

console = Console()

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
        if list(track):
            length = len(track)
        else:
            length = 1

        for i in range(length):
            title = format_text(track[i]['name'])
            artist = get_artist_names(track[i]['artists']['primary'])
            duration = format_duration(int(track[i]['duration']))
            url = track[i]['downloadUrl'][4]['url']

            self.queue.append({
                'title': title,
                'artist': artist,
                'duration': duration,
                'url': url
            })

            console.print(Panel(
                f"[green]Added: {title} - {artist} to the queue![/green]",
                title="✓ Track Added",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            
            if self.persistent_queue:
                self.playlist_db.add_queue_to_db(self.queue)
        return

    def add_playlist_to_queue(self, track: dict) -> None:
        self.queue.append({
            'title': track['title'],
            'artist': track['artist'],
            'duration': track['duration'],
            'url': track['url']
        })

        console.print(Panel(
            f"[green]Added: {track['title']} - {track['artist']} to the queue![/green]",
            title="✓ Track Added",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        
        if self.persistent_queue:
            self.playlist_db.add_queue_to_db(self.queue)
        return

    def show_queue(self) -> None:
        if not self.queue:
            console.print(Panel(
                "[red]The Queue is empty![/red]",
                title="⚠ Empty Queue",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        console.clear()

        table = Table(
            title=f"Current Queue ({len(self.queue)} tracks)",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )

        table.add_column("#", style="green bold", width=3, justify="right")
        table.add_column("Title", style="red bold", min_width=25)
        table.add_column("Artist", style="cyan", min_width=20)
        table.add_column("Duration", style="yellow", width=8, justify="center")

        for i, track in enumerate(self.queue, 1):
            title = format_text(track.get('title', 'Unknown'))
            artist = format_text(track.get('artist', 'Unknown'))
            duration = track.get('duration', '0:00')

            table.add_row(str(i), title, artist, duration)

        console.print(table, justify="center")

    def clear_queue(self) -> None:
        if not self.queue:
            console.print(Panel(
                "[red]The Queue is empty![/red]",
                title="⚠ Empty Queue",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        self.queue.clear()
        console.print(Panel(
            "[green]Cleared the queue![/green]",
            title="✓ Queue Cleared",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        
        if self.persistent_queue:
            self.playlist_db.add_queue_to_db(self.queue)
        return

    def play_media(self, url: str, lyrics: str, track_position: int, queue: list) -> None:
        cmd = [
            'mpv',
            '--no-video',  
            '--term-osd-bar',
            '--no-resume-playback',
            f'--sub-file={self.config_folder}/lyrics.vtt',
            url
        ]

        try:
            subprocess.run(cmd, check=False)
            lastfm.scrobbleTrack(queue[track_position]['artist'], queue[track_position]['title'])
        except KeyboardInterrupt:
            pass
        finally:
            cleanup_files(self.config_folder)

    def play_queue(self, queue_to_play: list = None, loop: bool = None) -> None:
        if queue_to_play is None:
            queue_to_play = self.queue

        if loop is not None:
            self.loop = loop

        if not queue_to_play:
            console.print(Panel(
                "[red]The Queue is empty![/red]",
                title="⚠ Empty Queue",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task(description="Initializing queue playback...", total=None)

        while True:
            i = 0
            queue_copy = queue_to_play.copy()

            while i < len(queue_copy):
                track = queue_copy[i]

                clear_screen()
                console.rule(f"[bold magenta]▶ Playing Track {i + 1} of {len(queue_copy)}")
                
                options_panel = Panel(
                        "[bold cyan]Next Track (Q) • Exit (Ctrl + C) • Seek with arrow keys[/bold cyan]",
                        title="Controls",
                        border_style="dim",
                        padding=(0,2)
                    )
                    
                console.print(options_panel, justify="center")
                
                if self.loop and len(queue_to_play) > 1:
                    console.print(Panel(
                        "[bold green]Queue Loop: Enabled[/bold green]",
                        title="Loop Status",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                elif self.loop and len(queue_to_play) == 1:
                    console.print(Panel(
                        "[bold green]Track Loop: Enabled[/bold green]",
                        title="Loop Status",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

                if len(queue_to_play) > 1:
                    if i < len(queue_copy) - 1:
                        next_tracks = queue_copy[i + 1:]
                        self._display_up_next_widget(next_tracks)
                    elif self.loop:
                        next_tracks = queue_copy[0]
                        self._display_up_next_widget(next_tracks)
                elif self.loop and len(queue_to_play) == 1:
                    next_tracks = queue_copy[0]
                    self._display_up_next_widget(next_tracks)

                self._display_now_playing_widget(track)

                create_lyrics_file(
                    f"{track['title']} - {track['artist'].split(',')[0]}",
                    self.config_folder,
                    self.synced_lyrics
                )

                try:
                    self.play_media(
                        track['url'],
                        f"{self.config_folder}/lyrics.vtt",
                        int(i),
                        queue_copy
                    )

                except KeyboardInterrupt:
                    return
                finally:
                    cleanup_files(self.config_folder)

                i += 1

            if not self.loop:
                break

            cleanup_files(self.config_folder)
            
    def _display_now_playing_widget(self, track: dict) -> None:
        """Display a minimal now playing widget with panel"""

        now_playing = Text()
        now_playing.append("♪ ", style="bold green")
        now_playing.append(f"{track.get('title', 'Unknown')}", style="bold white")
        now_playing.append(" • ", style="dim white")
        now_playing.append(f"{track.get('artist', 'Unknown')}", style="cyan")
        
        if track.get('duration'):
            now_playing.append(f" [{track['duration']}]", style="dim yellow")
        
        panel = Panel(
            Align.center(now_playing),
            title="Now Playing",
            title_align="center",
            border_style="bold green",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        console.print(panel)
        
    def _display_up_next_widget(self, track: dict) -> None:
        """Display a minimal up next widget with a different styling than now playing"""
        
        is_list = False
        up_next = Text()
        
        try:
            print(track.get("title"))
        except:
            is_list = True
        
        track_num = 0                
        if is_list:
            if len(track) > 2:
                track_num = 3 ## Only display the top 3 if there's more than 3 tracks
            else:
                track_num = len(track)
                
            for i in range(track_num): ## Display the next 5 tracks
                up_next.append("♪ ", style="bold green")
                up_next.append(f"{list(track)[i].get('title', 'Unknown')}", style="bold white")
                up_next.append(" • ", style="dim white")
                up_next.append(f"{list(track)[i].get('artist', 'Unknown')}", style="bright_blue")
                up_next.append(f" [{list(track)[i]['duration']}]", style="dim orange1")
                if i != track_num - 1: ## Don't display | for the third track
                    up_next.append(" | ", style="bold white")
                
        else:
            up_next.append("♪ ", style="bold green")
            up_next.append(f"{track.get('title', 'Unknown')}", style="bold white")
            up_next.append(" • ", style="dim white")
            up_next.append(f"{track.get('artist', 'Unknown')}", style="bright_blue")
            up_next.append(f" [{track.get('duration', 'Unknown')}]", style="dim orange1")    
        
        # Create panel with different color scheme
        panel = Panel(
            Align.center(up_next),
            title="Up Next",
            title_align="left",
            border_style="bold blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        console.print(panel)

    def play_specific_index(self, index: int, queue_to_play: list = None, next_track_index=None) -> None:
        if queue_to_play is None:
            queue_to_play = self.queue

        if not queue_to_play:
            console.print(Panel(
                "[bold red]The Queue is empty![/bold red]",
                title="⚠ Empty Queue",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        try:
            track = queue_to_play[int(index) - 1]
        except IndexError:
            console.print(Panel(
                "[bold red]Index out of range![/bold red]",
                title="⚠ Invalid Index",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        while True:
            clear_screen()
        
            console.rule(f"[bold magenta]▶ Playing Track {int(index)} of {len(queue_to_play)}")
            options_panel = Panel(
                "[bold cyan]Next Track (Q) • Exit (Ctrl + C) • Seek with arrow keys[/bold cyan]",
                title="Controls",
                border_style="dim",
                padding=(0,2)
            )
                    
            console.print(options_panel, justify="center")
            
            if self.loop:
                console.print(Panel(
                    "[bold green]Track Loop: Enabled[/bold green]",
                    title="Loop Status",
                    border_style="green",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))

            if next_track_index is not None:
                try:
                    next_track = queue_to_play[int(next_track_index) - 1]
                    self._display_up_next_widget(next_track)
                except IndexError:
                    pass
            elif self.loop:
                self._display_up_next_widget(next_track)

            self._display_now_playing_widget(track)

            create_lyrics_file(
                f"{track['title']} - {track['artist']}",
                self.config_folder,
                self.synced_lyrics
            )

            try:
                self.play_media(
                    track['url'],
                    f"{self.config_folder}/lyrics.vtt",
                    int(index) - 1,
                    queue_to_play
                )

                if not self.loop:
                    break

            except KeyboardInterrupt:
                return
            finally:
                cleanup_files(self.config_folder)

    def play_indexes(self, indexes: str, queue_to_play: list = None, loop: bool = None) -> None:
        if queue_to_play is None:
            queue_to_play = self.queue

        if loop is not None:
            self.loop = loop

        if not queue_to_play:
            console.print(Panel(
                "[bold red]The Queue is empty![/bold red]",
                title="⚠ Empty Queue",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1)
            ))
            return

        try:
            parts = [int(p) for p in indexes.split()]
        except ValueError:
            parts = extract_range_numbers(indexes)

        while True:
            i = 0

            while i < len(parts):
                current_index = parts[i]

                try:
                    track = queue_to_play[current_index - 1]
                except IndexError:
                    console.print(Panel(
                        f"[bold red]Index {current_index} out of range![/bold red]",
                        title="⚠ Invalid Index",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                    i += 1
                    continue

                clear_screen()
                console.rule(f"[bold magenta]▶ Playing indexes: {', '.join(map(str, parts))}")
            
                options_panel = Panel(
                        "[bold cyan]Next Track (Q) • Exit (Ctrl + C) • Seek with arrow keys[/bold cyan]",
                        title="Controls",
                        border_style="dim",
                        padding=(0,2)
                    )
                
                console.print(options_panel, justify="center")
                            
                if self.loop:
                    console.print(Panel(
                        "[bold green]Queue Loop: Enabled[/bold green]",
                        title="Loop Status",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

                if i + 1 < len(parts):
                    next_index = parts[i + 1]
                    try:
                            # Get all tracks from next_index to the last index in parts
                            remaining_indexes = parts[i + 1:]  # Get remaining indexes
                            next_tracks = []
                            for idx in remaining_indexes:
                                try:
                                    next_tracks.append(queue_to_play[idx - 1])
                                except IndexError:
                                    continue  # Skip invalid indexes
                        
                            # Display the next track (first in the remaining list)
                            if next_tracks:
                                self._display_up_next_widget(next_tracks)
                    
                    except IndexError:
                        pass
                
                elif self.loop and i == len(parts) - 1 and len(parts) > 1:
                    first_index = parts[0]
                    try:
                        next_track = queue_to_play[first_index - 1]
                        self._display_up_next_widget(next_track)
                    except IndexError:
                        pass

                self._display_now_playing_widget(track)

                create_lyrics_file(
                    f"{track['title']} - {track['artist']}",
                    self.config_folder,
                    self.synced_lyrics
                )

                try:
                    self.play_media(
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
            
    def edit_queue(self) -> None:
        while True:
            if not self.queue:
                console.print(Panel(
                    "[red]The Queue is empty![/red]",
                    title="⚠ Empty Queue",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
                return

            options_panel = Panel(
                "[bold cyan](R)emove • (M)ove • (S)huffle • (B)ack • L(oop) • (D)isable Lyrics[/bold cyan]",
                border_style="dim",
                title="Options",
                padding=(0,2)
            )
            console.print(options_panel, justify="center")

            query = Prompt.ask("\n[bold cyan]Edit the Queue[/bold cyan]", show_choices=False).strip().lower()

            if query == 'b':
                break

            elif query == 'l':
                self.loop = not self.loop
                if self.loop:
                    console.print(Panel(
                        "[green]Enabled the Queue/Track loop![/green]",
                        title="✓ Loop Enabled",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                else:
                    console.print(Panel(
                        "[red]Disabled the Queue/Track loop![/red]",
                        title="✗ Loop Disabled",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            elif query == 's':
                shuffle(self.queue)
                console.print(Panel(
                    "[green]Shuffled the queue![/green]",
                    title="Queue Shuffled",
                    border_style="green",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
                if self.persistent_queue:
                    self.playlist_db.add_queue_to_db(self.queue)

            elif query == 'r':
                console.print(Panel(
                    f"[bold red]Pick[/bold red] [dim]1-{len(self.queue)} to remove[/dim] • [bold cyan](B)ack[/bold cyan]",
                    border_style="dim",
                    padding=(0,2)
                ))
                index = Prompt.ask("\n[bold red]Remove track[/bold red]", show_choices=False).strip()
                if index.lower() == "b":
                    continue
                try:
                    if check_integers_with_spaces(index):
                        for i in sorted(index.split(" "), key=int, reverse=True):
                            removed = self.queue.pop(int(i) - 1)
                            console.print(Panel(
                                f"[green]Removed {removed['title']} - {removed['artist']}[/green]",
                                title="✓ Track Removed",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                    elif extract_range_numbers(index):
                        for i in sorted(extract_range_numbers(index), key=int, reverse=True):
                            removed = self.queue.pop(int(i) - 1)
                            console.print(Panel(
                                f"[green]Removed {removed['title']} - {removed['artist']}[/green]",
                                title="✓ Track Removed",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(0, 1)
                            ))
                    else:
                        removed = self.queue.pop(int(index) - 1)
                        console.print(Panel(
                            f"[green]Removed {removed['title']} - {removed['artist']}[/green]",
                            title="✓ Track Removed",
                            border_style="green",
                            box=box.ROUNDED,
                            padding=(0, 1)
                        ))
                    if self.persistent_queue:
                        self.playlist_db.add_queue_to_db(self.queue)
                except:
                    console.print(Panel(
                        "[red]Invalid or out-of-range index![/red]",
                        title="⚠ Invalid Index",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            elif query == 'm':
                console.print(Panel(
                    f"[bold red]Pick[/bold red] [dim]1-{len(self.queue)} to move from[/dim] • [bold cyan](B)ack[/bold cyan]",
                    border_style="dim",
                    title="Options",
                    padding=(0,2)
                ))
                current_index = Prompt.ask("\n[bold red]Move track[/bold red]", show_choices=False).strip()
                if current_index.lower() == 'b':
                    continue
                console.print(Panel(
                    f"[bold red]Pick[/bold red] [dim]1-{len(self.queue)} to move to[/dim] • [bold cyan](B)ack[/bold cyan]",
                    border_style="dim",
                    title="Options",
                    padding=(0,2)
                ))
                final_index = Prompt.ask("\n[bold red]Move track to[/bold red]", show_choices=False).strip()
                if final_index.lower() == 'b':
                    continue
                try:
                    self.queue.insert(int(final_index) - 1, self.queue.pop(int(current_index) - 1))
                    console.print(Panel(
                        f"[green]Moved track to position {final_index}![/green]",
                        title="✓ Track Moved",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                    if self.persistent_queue:
                        self.playlist_db.add_queue_to_db(self.queue)
                except:
                    console.print(Panel(
                        "[red]Track index out of range![/red]",
                        title="⚠ Invalid Index",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            elif query == 'd':
                self.synced_lyrics = not self.synced_lyrics
                if self.synced_lyrics:
                    console.print(Panel(
                        "[green]Enabled Synced Lyrics![/green]",
                        title="✓ Lyrics Enabled",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))
                else:
                    console.print(Panel(
                        "[red]Disabled Synced Lyrics![/red]",
                        title="✗ Lyrics Disabled",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(0, 1)
                    ))

            else:
                console.print(Panel(
                    "[red]Invalid option entered![/red]",
                    title="⚠ Invalid Option",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))