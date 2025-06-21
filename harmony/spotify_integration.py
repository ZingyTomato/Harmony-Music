import spotipy
from spotipy import SpotifyClientCredentials

class SpotifyIntegration:
    def __init__(self):
        
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id="804e387d07ba4ce9b86e10a2acde9804",
            client_secret="83e9384758c341c0bc96296d8d233145"   
            ))

    def get_track_info(self, track_id: str):
        return self.sp.track(track_id)

    def get_album_tracks(self, album_id: str):
        album = self.sp.album(album_id)
        return album['tracks']['items']

    def get_playlist_tracks(self, playlist_id: str):
        results = self.sp.playlist_items(playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks