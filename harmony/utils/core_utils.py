"""
Utility functions for text formatting, screen clearing, and file operations
"""

import os
import re
import time
import html
from pathlib import Path
import subprocess
import json

def clear_screen() -> None:
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def format_text(text: str) -> str:
    """Clean and format text for display"""
    cleaned = html.unescape(str(text))
    return cleaned

def format_duration(seconds: int) -> str:
    """Format duration in MM:SS format"""
    return time.strftime('%M:%S', time.gmtime(seconds))

def get_artist_names(artist_list: list) -> str:
    """Return list of artists separated by a comma"""
    return ', '.join(format_text(artist['name']) for artist in artist_list)

def cleanup_files(directory: str) -> None:
    """Clean up temporary files"""
    for file in ['lyrics.vtt']:
        try:
            Path(f"{directory}/{file}").unlink(missing_ok=True)
        except:
            pass

def is_integer(val: str) -> bool:
    """ Check if input is a valid integer to be used as index in the queue """
    try:
        int(val)
        return True
    except ValueError:
        return False

def check_integers_with_spaces(input_str: str) -> bool:
    """ Check if input is multiples integers separated by spaces """
    if not input_str.strip():  # Handle empty string
        return False

    parts = input_str.split()
    return all(part.isdigit() for part in parts)

def is_range_format(input_str: str) -> bool:
    """Check if input is 2 integers separated by .. """
    pattern = r'^\d+\.\.\d+$'
    return bool(re.match(pattern, input_str))

def extract_range_numbers(input_str: str) -> bool:
    """Extract numbers in range format"""
    if '..' not in input_str:
        return None
    
    parts = input_str.split('..')
    if len(parts) != 2:
        return None
    
    try:
        start = int(parts[0])
        end = int(parts[1])
        return [i for i in range(start, end + 1)]
    except ValueError:
        return None

def create_config_folder() -> str:
    """Create folder in ~/.config only if it doesn't exist to store the queue and playlists"""
    config_dir = Path.home() / '.config' / "harmony" / "lyrics"

    if not config_dir.exists():
        config_dir.mkdir(parents=True)

    return config_dir

def create_config_file(directory: str) -> str:
    """Create config.json ~/.config/harmony only if it doesn't exist to store user preferences"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, "config.json")
    
    data = {"SHOW_SYNCED_LYRICS": True,
            "PERSISTENT_QUEUE": True,
            "LOOP_QUEUE": False,
            "LASTFM_API_KEY": None,
            "LASTFM_API_SECRET": None,
            "LASTFM_USERNAME": None,
            "LASTFM_PASSWORD": None}
    
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
    return filepath

def get_config_value(key, filepath):
    """Retrieve specific values from the config file"""
    if not os.path.exists(filepath):
        data = {"SHOW_SYNCED_LYRICS": True,
            "PERSISTENT_QUEUE": True,
            "LOOP_QUEUE": False,
            "LASTFM_API_KEY": None,
            "LASTFM_API_SECRET": None,
            "LASTFM_USERNAME": None,
            "LASTFM_PASSWORD": None}
        
        os.makedirs(directory, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    with open(filepath, 'r') as f:
        config = json.load(f)
    
    return config[key]