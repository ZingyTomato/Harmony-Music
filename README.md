<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>Stream music from your terminal without compromising your privacy.</h4>
</div>

<div align="center" width="60%" height="auto">
  <br>
    <img src="showcase/2025-06-13 22-14-08.gif">
</div>

# 📖 Table Of Contents

* [`❔ What's this?`](#-whats-this)
* [`🎧 Features`](#-features)
* [`📜 Requirements`](#-requirements)
* [`💻 Installation`](#-installation)
* [`👨‍🔧 Usage`](#-usage)
* [`🏥 Contributing`](#-contributing)

## ❔ What's this?

Harmony is a command line tool to stream music from the command line without worrying about tracking/profiling. Harmony streams music from [`Jiosaavn`](https://jiosaavn.com), using a [`Jiosaavn API`](https://github.com/sumitkolhe/jiosaavn-api) to both fetch results and stream music.
 
## 🎧 Features

- [x] **Efficient performance** - Minimal 1-5% CPU footprint during playback.
- [x] **Privacy-first design** - No data collection or user tracking.
- [x] **Premium audio quality** - 320 kbps bitrate streaming.
- [x] **Synchronized lyrics** - Displays real-time synced lyrics.
- [x] **Persistent session state** - Queue automatically saves between sessions.
- [x] **Offline playlist support** - Device-local playlist storage.
- [x] **Spotify compatibility** - Supports Spotify tracks, albums & playlists as links.
- [x] **Live trending feed** - See what's trending right now.

## 📜 Requirements

1. [`mpv`](https://mpv.io) - An open source command line video player.

## 💻 Installation

Simply download the release binary from the [`releases section`](https://github.com/ZingyTomato/harmonymusic/releases) or enter the following commands below in any Linux terminal. (No Windows binaries yet!)

```
sudo wget https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -O /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

## 👨‍🔧 Usage

```
usage: harmony [-h] [-t] [-p] [-v] [-dl] [query ...]

Harmony - An open souce TUI music streamer based on MPV.
https://github.com/ZingyTomato/Harmony-Music

positional arguments:
  query                 Search for a song (e.g., 'harmony Never Gonna Give You      
  
                          Up'), Use a valid Spotify track/album/playlist URL (e.g, 'harmony https://open.spotify.com/xxxx)'

options:
  -h, --help            show this help message and exit
  -t, --trending        Displays the top 20 trending tracks worldwide.
  -p, --playlist        View existing playlists or create new ones.
  -v, --version         Display the current version of the program.
  -dl, --disable-lyrics
                        Disable synchronized lyrics display in MPV.
```

## 🏥 Contributing

Feel free to create an issue if you encounter any bugs or would like to suggest something!