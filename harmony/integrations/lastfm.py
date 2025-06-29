"""
Enables LastFM Scrobbling
"""

import pylast
from utils.core_utils import get_config_value, create_config_folder
import time

API_KEY = get_config_value("LASTFM_API_KEY", f"{create_config_folder()}/config.json") 
API_SECRET = get_config_value("LASTFM_API_SECRET", f"{create_config_folder()}/config.json") 

USERNAME = get_config_value("LASTFM_USERNAME", f"{create_config_folder()}/config.json") 
PASSWORD_HASH = pylast.md5(get_config_value("LASTFM_PASSWORD", f"{create_config_folder()}/config.json"))

ENABLED = False

if API_KEY != None and API_SECRET != None and USERNAME != None and PASSWORD_HASH != None: ## If all the relevant fields are entered
    network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH,
    )
    
    ENABLED = True

def scrobbleTrack(artist: str, title: str) -> None:
    if ENABLED:
        network.scrobble(artist=artist, title=title, timestamp=int(time.time()))
    return