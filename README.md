# Harmony Music

## What's this?

Harmony is a command line tool to stream music and videos without worrying about prying eyes from the likes of Youtube. It has minimal resource usage thanks to mpv and does not make requests to youtube to get results. It uses [`piped`](https://piped.kavin.rocks) which is an alternative frontend to Youtube.

## Requirements

1. [`mpv`](https://mpv.io) - An open source command line video player.

2. [`youtube-dl`](https://github.com/ytdl-org/youtube-dl) - Command-line program to download videos from YouTube.com and other video sites.

## Installation

Simply download the release binary (Linux only for now) from the [releases section](https://github.com/ZingyTomato/harmonymusic/releases) or enter the commands below in any Linux terminal.

```
sudo curl -L https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -o /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

```
sudo wget https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -O /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

## Commands

```
  -h, --help           show this help message and exit
  --song, -s, --s      Searches for songs based on query. Example: harmony
                       --song "Never gonna give you up"
  --video, -v, --v     Searches for videos based on the query. Example:
                       harmony --video "Never gonna give you up"
  --album, -a, --a     Searches for albums based on the query. Example:
                       harmony --album "All Over The Place"
  --playlist, -p, --p  Searches for playlists based on the query. Example:
                       harmony --playlist "All Over The Place"
```
