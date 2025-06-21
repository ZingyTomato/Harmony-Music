import sqlite3
import json
from termcolor import colored

class PlaylistDB:
    def __init__(self, config_folder: str):
        self.playlist_conn = sqlite3.connect(f'{config_folder}/playlist.db') ## DB to store playlists
        self.playlist_cursor = self.playlist_conn.cursor()
        self.create_table()

    def create_table(self):
        self.playlist_cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                name TEXT,
                metadata JSON
            )
        ''')
        self.commit_db()

    def commit_db(self):
        """ Commit changes to the database """
        self.playlist_conn.commit()

    def create_playlist(self, name: str):
        self.playlist_cursor.execute('''
            INSERT INTO playlists (name, metadata) VALUES (?, ?)''', (name, json.dumps([])))
        self.commit_db()
        print(colored(f"\nCreated playlist {name}!", 'green', attrs=['bold']))


    def get_all_playlists(self):
        return self.playlist_cursor.execute('SELECT name, metadata FROM playlists').fetchall()

    def get_playlist_count(self):
        self.playlist_cursor.execute("SELECT COUNT(*) FROM playlists")
        return self.playlist_cursor.fetchone()[0]

    def get_playlist_by_index(self, index: int):
        query = 'SELECT name, metadata FROM playlists LIMIT 1 OFFSET ?'
        return self.playlist_cursor.execute(query, (index,)).fetchone()

    def update_playlist_db(self, name: str, metadata: dict):
        self.playlist_cursor.execute('''
            UPDATE playlists SET metadata = ? WHERE name = ?
        ''', (json.dumps(metadata), name))
        self.commit_db()
        return

    def add_track_to_playlist(self, name: str, track: dict):
        self.playlist_cursor.execute('SELECT metadata FROM playlists WHERE name = ?', (name,))
        result = self.playlist_cursor.fetchone()
        current_metadata = json.loads(result[0]) if result and result[0] else []

        if isinstance(current_metadata, dict): # Added this check
            current_metadata = []

        current_metadata.append(track)

        self.playlist_cursor.execute('''
            UPDATE playlists SET metadata = ? WHERE name = ?
        ''', (json.dumps(current_metadata), name))
        self.commit_db()
        print(f"\nAdded {colored(track['title'], 'red', attrs=['bold'])} - "
                      f"{colored(track['artist'], 'cyan')} to {colored(name, 'red', attrs=['bold'])}")

    def delete_playlist(self, name: str):
        self.playlist_cursor.execute('''
            DELETE FROM playlists WHERE name = ?''', (name,))
        self.commit_db()