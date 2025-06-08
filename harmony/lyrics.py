"""
Lyrics search and conversion functionality
"""

from pathlib import Path
import syncedlyrics


def create_lyrics_file(query: str):
    """Create lyrics file for current track"""
    try:
        syncedlyrics.search(query, plain_only=False, save_path="lyrics.lrc",
                            providers=["Lrclib", "NetEase"]) ## Seems to provide the most accurate synced lyrics amongst other providers.
        
        convert_lrc_to_vtt("lyrics.lrc", "lyrics.vtt")
    except:
        # If lyrics fail, create empty file so mpv doesn't error
        Path("lyrics.vtt").write_text("WEBVTT\n\n")


def convert_lrc_to_vtt(lrc_path: str, vtt_path: str):
    """Convert LRC lyrics to VTT format"""
    try:
        with open(lrc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        timestamps = []
        lyrics = []
        
        for line in lines:
            line = line.strip()
            if line and line.startswith('[') and ']' in line:
                timestamp = line[1:line.index(']')]
                lyric = line[line.index(']') + 1:].strip()
                if lyric:
                    timestamps.append(timestamp)
                    lyrics.append(lyric)
        
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, (timestamp, lyric) in enumerate(zip(timestamps, lyrics)):
                start_time = timestamp.replace(',', '.')
                
                # Calculate end time
                if i < len(timestamps) - 1:
                    end_time = timestamps[i + 1].replace(',', '.')
                else:
                    # For last line, add 3 seconds
                    try:
                        minutes, rest = start_time.split(':')
                        seconds = float(rest) + 3
                        if seconds >= 60:
                            seconds -= 60
                            minutes = str(int(minutes) + 1)
                        end_time = f"{minutes}:{seconds:06.3f}"
                    except:
                        end_time = start_time
                
                f.write(f"{start_time} --> {end_time}\n{lyric}\n\n")
                
    except Exception:
        # Create empty VTT file on error
        Path(vtt_path).write_text("WEBVTT\n\n")