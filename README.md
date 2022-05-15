<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>An easy way to stream videos or music from Youtube from the command line while regaining your privacy.</h4>
</div>

<div align="center" width="60%" height="auto">
  <br>
    <img src="showcase/2022-05-15 21-45-16.gif">
</div>

# 📖 Table Of Contents

* [`❔ What's this?`](#-whats-this)
* [`🎧 Features`](#-features)
* [`📜 Requirements`](#-requirements)
* [`💻 Installation`](#-installation)
* [`👨‍🔧 Usage`](#-usage)

## ❔ What's this?

Harmony is a command line tool to stream music and videos without worrying about prying eyes from the likes of Youtube. Instead of directly scraping Youtube, Harmony uses [`Piped`](https://github.com/TeamPiped/Piped) instead. This results in not only quicker fetching of results but also prevents Youtube from seeing your IP by proxying videos, all from the comfort of the terminal. 

## 🎧 Features

- [x] Minimal Resource Usage. (Around **1-2%** CPU usage while streaming music and **5-10%** while playing videos)
- [x] No requests made to Youtube to fetch results.
- [x] Avoid Youtube's georestrictions by using Piped's inbuilt proxy. Works with both the **--song** and **--video** flag.
- [x] Ability to filter search queries by music, videos, albums or playlists.
- [x] A proper queue system. 

## 📜 Requirements

1. [`mpv`](https://mpv.io) - An open source command line video player.

## 💻 Installation

Harmony is available in the AUR. You can find it [`here`](https://aur.archlinux.org/packages/harmony).

```
yay -S harmony
```

Simply download the release binary from the [`releases section`](https://github.com/ZingyTomato/harmonymusic/releases) or enter the following commands below in any Linux terminal. (No windows binaries yet!)

```
sudo wget https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -O /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

## 👨‍🔧 Usage

```
usage: harmony.py [-h] [SONG_NAME ...]

An open souce video/music streamer based on MPV and piped.

positional arguments:
  SONG_NAME   Searches for songs based on the query. Example: harmony 2step Ed Sheeran

options:
  -h, --help  show this help message and exit
```
