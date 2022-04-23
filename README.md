<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>An easy way to stream videos or music from Youtube from the command line while regaining your privacy.</h4>
</div>

<div align="center" width="60%" height="auto">
  <br>
    <img src="Showcase/2022-04-22 11-47-05.gif">
</div>

# 📖 Table Of Contents

* [`What's this?`](#-whats-this)
* [`Features`](#-features)
* [`Requirements`](#-requirements)
* [`Installation`](#-installation)
* [`Usage`](#-usage)

## ❔ What's this?

Harmony is a command line tool to stream music and videos without worrying about prying eyes from the likes of Youtube. Instead of directly scraping Youtube, Harmony uses [`Piped`](https://github.com/TeamPiped/Piped) instead. This results in not only quicker fetching of results but also prevents Youtube from seeing your IP, all from the comfort of the terminal. 

## 🎧 Features

- [x] Minimal Resource Usage. (Around 1-2% CPU usage while streaming music and 5-10% while playing videos thanks to [`mpv`](https://mpv.io))
- [x] No requests made to Youtube to fetch results.
- [x] No tracking from Youtube.
- [x] Ability to filter search queries by music, videos, albums or playlists.
- [x] A proper queue system. 

## 📜 Requirements

1. [`mpv`](https://mpv.io) - An open source command line video player.

2. [`youtube-dl`](https://github.com/ytdl-org/youtube-dl) - Command-line program to download videos from YouTube.com and other video sites.

## 💻 Installation

Simply download the release binary from the [`releases section`](https://github.com/ZingyTomato/harmonymusic/releases) or enter the following commands below in any Linux terminal. (No windows binaries yet!)

```
sudo wget https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -O /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

## 👨‍🔧 Usage

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
