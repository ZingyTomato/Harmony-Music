"""
Enables LastFM Scrobbling
"""

import pylast
from utils.core_utils import get_config_value, create_config_folder
import time

directory = create_config_folder()
API_KEY = get_config_value("LASTFM_API_KEY", f"{directory}/config.json", directory) 
API_SECRET = get_config_value("LASTFM_API_SECRET", f"{directory}/config.json", directory) 

USERNAME = get_config_value("LASTFM_USERNAME", f"{directory}/config.json", directory) 
PASSWORD_HASH = pylast.md5(get_config_value("LASTFM_PASSWORD", f"{directory}/config.json", directory))

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