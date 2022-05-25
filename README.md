<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>An easy way to stream music or videos from online sources like Youtube from the command line while regaining your privacy.</h4>
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

Harmony is a command line tool to stream music from the command line without worrying about tracking/profiling. Harmony uses a [`Jiosaavn API`](https://github.com/sumitkolhe/jiosaavn-api) to both fetch results and stream music. [`Piped`](https://github.com/TeamPiped/Piped) is used to both fetch videos and stream videos. It has support for features that are normally only found on mainstream services like Spotify. (Real-time synced lyrics)
 
## 🎧 Features

- [x] Minimal Resource Usage. **1-5%** CPU usage while streaming music, **5-15%** CPU usage while streaming videos
- [x] No tracking whatsoever either while streaming music or videos.
- [x] Streams **320 kbps** audio and streams the **highest** quality video.
- [x] Support for real-time synced lyrics.
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
usage: harmony [-h] [-v] [SEARCH_QUERY ...]

An open souce CLI music/video streamer based on MPV.

positional arguments:
  SEARCH_QUERY  Name of the song/video to search for. Example: harmony 2step Ed Sheeran

options:
  -h, --help    show this help message and exit
  -v, --video   Allows to search for videos instead of music. Example harmony -v 2step Ed Sheeran
```
