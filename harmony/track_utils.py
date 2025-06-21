from utils import format_text, format_duration

def create_track(track_json: dict):
    """
    Creates a standardized track dictionary from raw track JSON data.
    This function is now responsible for formatting track information consistently.
    """
    title = format_text(track_json['name'])
    artist = format_text(track_json['artists']['primary'][0]['name'])
    duration = format_duration(int(track_json['duration']))
    url = track_json['downloadUrl'][4]['url']  # Get the streaming URL

    return {
        'title': title,
        'artist': artist,
        'duration': duration,
        'url': url
    }