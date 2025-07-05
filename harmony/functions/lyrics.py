from pathlib import Path
import logging
from typing import List, Tuple, Optional
import syncedlyrics


class LyricsConverter:
    """Handles conversion between different lyrics formats."""
    
    @staticmethod
    def lrc_to_vtt(lrc_path: Path, vtt_path: Path) -> bool:
        """Convert LRC lyrics to VTT format."""
        try:
            with open(lrc_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            timestamps_lyrics = LyricsConverter._parse_lrc_lines(lines)
            if not timestamps_lyrics:
                return False

            LyricsConverter._write_vtt_file(vtt_path, timestamps_lyrics)
            return True

        except Exception as e:
            logging.debug(f"Failed to convert LRC to VTT: {e}")
            return False

    @staticmethod
    def _parse_lrc_lines(lines: List[str]) -> List[Tuple[str, str]]:
        """Parse LRC file lines and extract timestamps and lyrics."""
        timestamps_lyrics = []
        
        for line in lines:
            line = line.strip()
            if not line.startswith('[') or ']' not in line:
                continue
                
            timestamp = line[1:line.index(']')]
            lyric = line[line.index(']') + 1:].strip()
            timestamps_lyrics.append((timestamp, lyric))
        
        return timestamps_lyrics

    @staticmethod
    def _write_vtt_file(vtt_path: Path, timestamps_lyrics: List[Tuple[str, str]]) -> None:
        """Write VTT file with timestamps and lyrics."""
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, (timestamp, lyric) in enumerate(timestamps_lyrics):
                start_time = timestamp.replace(',', '.')
                end_time = LyricsConverter._calculate_end_time(
                    start_time, 
                    timestamps_lyrics[i + 1][0] if i < len(timestamps_lyrics) - 1 else None
                )
                
                f.write(f"{start_time} --> {end_time}\n{lyric}\n\n")

    @staticmethod
    def _calculate_end_time(start_time: str, next_timestamp: Optional[str]) -> str:
        """Calculate end time for VTT subtitle entry."""
        if next_timestamp:
            return next_timestamp.replace(',', '.')
        
        try:
            minutes, rest = start_time.split(':')
            seconds = float(rest)
            if seconds >= 60:
                seconds -= 60
                minutes = str(int(minutes))
            return f"{minutes}:{seconds:06.3f}"
        except (ValueError, IndexError):
            return start_time


class LyricsProvider:
    """Handles fetching lyrics from external providers."""
    
    DEFAULT_PROVIDERS = ['NetEase', 'Lrclib']
    
    def __init__(self, providers: List[str] = None):
        self.providers = providers or self.DEFAULT_PROVIDERS
    
    def fetch_synced_lyrics(self, query: str, save_path: Path) -> bool:
        """Fetch synced lyrics and save to LRC file."""
        try:
            syncedlyrics.search(
                query,
                plain_only=False,
                synced_only=True,
                save_path=str(save_path),
                providers=self.providers
            )
            return save_path.exists()
        except Exception as e:
            logging.debug(f"Failed to fetch lyrics for '{query}': {e}")
            return False


class LyricsManager:
    """Main class for managing lyrics operations."""
    
    def __init__(self, providers: List[str] = None):
        self.provider = LyricsProvider(providers)
        self.converter = LyricsConverter()
    
    def create_lyrics_file(self, query: str, directory: str, synced: bool = True) -> Path:
        """Creates a .vtt file for current track."""
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        vtt_path = dir_path / "lyrics.vtt"
        
        if not synced:
            self._create_empty_vtt(vtt_path)
            return vtt_path
        
        if self._create_synced_lyrics(query, dir_path, vtt_path):
            return vtt_path
        
        # Fallback to empty VTT if synced lyrics failed
        self._create_empty_vtt(vtt_path)
        return vtt_path
    
    def _create_synced_lyrics(self, query: str, dir_path: Path, vtt_path: Path) -> bool:
        """Attempt to create synced lyrics VTT file."""
        lrc_path = dir_path / "lyrics.lrc"
        
        try:
            # Fetch lyrics to LRC format
            if not self.provider.fetch_synced_lyrics(query, lrc_path):
                return False
            
            # Convert LRC to VTT
            success = self.converter.lrc_to_vtt(lrc_path, vtt_path)
            
            # Clean up temporary LRC file
            lrc_path.unlink(missing_ok=True)
            
            return success
            
        except Exception as e:
            logging.debug(f"Error creating synced lyrics: {e}")
            # Clean up any partial files
            lrc_path.unlink(missing_ok=True)
            return False
    
    def _create_empty_vtt(self, vtt_path: Path) -> None:
        """Create an empty VTT file."""
        vtt_path.write_text("WEBVTT\n\n", encoding='utf-8')


# Legacy function compatibility
def create_lyrics_file(query: str, directory: str, synced: bool):
    """Creates a .vtt file for current track"""
    manager = LyricsManager()
    manager.create_lyrics_file(query, directory, synced)


def convert_lrc_to_vtt(lrc_path: str, vtt_path: str):
    """Convert LRC lyrics to VTT format"""
    converter = LyricsConverter()
    success = converter.lrc_to_vtt(Path(lrc_path), Path(vtt_path))
    
    if not success:
        Path(vtt_path).write_text("WEBVTT\n\n", encoding='utf-8')
    
    Path(lrc_path).unlink(missing_ok=True)