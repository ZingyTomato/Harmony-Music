<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>An easy way to stream music from the command line while regaining your privacy.</h4>
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

- [x] Minimal Resource Usage. **1-5%** CPU usage while streaming music.
- [x] No tracking whatsoever.
- [x] Streams **320 kbps** audio.
- [x] Support for real-time synced lyrics.
- [x] A proper queue system: Can delete, reorder, remove and move tracks.
- [x] Support for locally stored playlists.
- [x] Supports Spotify tracks, albums & playlists.
- [x] Displays the top trending tracks right now.

## 📜 Requirements

1. [`mpv`](https://mpv.io) - An open source command line video player.

## 💻 Installation

Simply download the release binary from the [`releases section`](https://github.com/ZingyTomato/harmonymusic/releases) or enter the following commands below in any Linux terminal. (No windows binaries yet!)

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