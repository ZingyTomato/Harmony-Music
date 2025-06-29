from pathlib import Path
import syncedlyrics


def create_lyrics_file(query: str, directory: str, synced: bool):
    """Creates a .vtt file for current track"""
    vtt_path = Path(directory) / "lyrics.vtt"

    if not synced:
        vtt_path.write_text("WEBVTT\n\n")
        return

    try:
        syncedlyrics.search(
            query,
            plain_only=False,
            synced_only=True,
            save_path=f"{directory}/lyrics.lrc",
            providers=['NetEase', 'Lrclib']
        )
        convert_lrc_to_vtt(f"{directory}/lyrics.lrc", vtt_path)
    except:
        vtt_path.write_text("WEBVTT\n\n")


def convert_lrc_to_vtt(lrc_path: str, vtt_path: str):
    """Convert LRC lyrics to VTT format"""
    try:
        with open(lrc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        timestamps = []
        lyrics = []

        for line in lines:
            line = line.strip()
            if line.startswith('[') and ']' in line:
                timestamp = line[1:line.index(']')]
                lyric = line[line.index(']') + 1:].strip()
                timestamps.append(timestamp)
                lyrics.append(lyric)

        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")

            for i, (timestamp, lyric) in enumerate(zip(timestamps, lyrics)):
                start_time = timestamp.replace(',', '.')

                if i < len(timestamps) - 1:
                    end_time = timestamps[i + 1].replace(',', '.')
                else:
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
        Path(vtt_path).write_text("WEBVTT\n\n")

    Path(lrc_path).unlink(missing_ok=True)