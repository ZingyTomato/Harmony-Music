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
* [`Force mpv to use yt-dlp over youtube-dl`](#-force-mpv-to-use-yt-dlp-over-youtube-dl)
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

2. [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) - A youtube-dl fork with additional features and fixes. This is preferred over youtube-dl for a better experience.

## 🛑 Force mpv to use yt-dlp over youtube-dl

yt-dlp is recommended over youtube-dl as it tends to load videos quicker and more importantly works with the **--playlist** flag.

If you already have youtube-dl installed, either remove youtube-dl and install yt-dlp instead or add this line to `~/.config/MPV/mpv.conf`

```
sript-opts=ytdl_hook-ytdl_path=/usr/bin/yt-dlp
```
If this doesn't work, find out where yt-dlp is located using `whereis yt-dlp` and replace `/usr/bin/yt-dlp` with it.

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
