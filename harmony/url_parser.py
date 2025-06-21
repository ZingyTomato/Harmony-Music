import re

class URLParser:
    def __init__(self):
        self.track_id = ""
        self.album_id = ""
        self.playlist_id = ""

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