"""
Utility functions for text formatting, screen clearing, and file operations
"""

import os
import re
import time
import html
from pathlib import Path


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def format_text(text: str) -> str:
    """Clean and format text for display"""
    cleaned = html.unescape(str(text))
    return cleaned


def format_duration(seconds: int) -> str:
    """Format duration in MM:SS format"""
    return time.strftime('%M:%S', time.gmtime(seconds))


def cleanup_files():
    """Clean up temporary files"""
    for file in ['lyrics.vtt', 'lyrics.lrc']:
        try:
            Path(file).unlink(missing_ok=True)
        except:
            pass
        
def is_integer(val):
    """ Check if input is a valid integer to be used as index in the queue """
    try:
        int(val)
        return True
    except ValueError:
        return False