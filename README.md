<div align="center">
<h1>🎶 Harmony Music</h1>
<h4>Stream music from your terminal without compromising your privacy.</h4>
</div>

<div align="center" width="60%" height="auto">
  <br>
    <img src="showcase/2025-07-05 10-04-08.gif">
</div>

# 📖 Table Of Contents

* [What's this?](#-whats-this)
* [Features](#-features)
* [Requirements](#-requirements)
* [Installation](#-installation)
* [Usage](#-usage)
* [Configuration](#-configuration)
* [Contributing](#-contributing)

## ❔ What's this?

Harmony is a command-line music player that streams audio directly from JioSaavn without data collection or user tracking. It uses the [JioSaavn API](https://github.com/sumitkolhe/jiosaavn-api) to fetch search results and stream music through your terminal.

## 🎧 Features

- **Low resource usage** - Runs with 1-5% CPU usage during playback
- **Privacy focused** - No data collection or user tracking
- **High-quality audio** - 320 kbps bitrate streaming
- **Synchronized lyrics** - Real-time lyrics display
- **Session persistence** - Queue saves automatically between sessions
- **Local playlists** - Create and manage playlists stored on your device
- **Spotify integration** - Import tracks, albums, and playlists from Spotify URLs
- **Trending music** - Browse currently trending tracks
- **Last.fm scrobbling** - Optional Last.fm integration for tracking listening history. See [`Last.FM Integration`](#lastfm-integration) for more information.

## 📜 Requirements

- [mpv](https://mpv.io) - Media player for audio playback
- Linux system (Windows binaries not yet available)

## 💻 Installation

Download the latest binary from the [releases section](https://github.com/ZingyTomato/harmonymusic/releases) or install directly:

```bash
sudo wget https://github.com/ZingyTomato/harmonymusic/releases/latest/download/harmony -O /usr/local/bin/harmony
sudo chmod a+rx /usr/local/bin/harmony
```

## 👨‍🔧 Usage

### Track Selection

**Single track:**
```bash
1. Track1 - Artist1 (02:59)
2. Track2 - Artist2 (03:33)
3. Track3 - Artist3 (03:30)
4. Track4 - Artist4 (03:01)

[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear, (V)iew playlists]: 1
```

**Multiple tracks:**
```bash
[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear, (V)iew playlists]: 1 2 3
```

**Range selection:**
```bash
[(P)lay, (S)how queue, (Q)uit, (E)dit, (C)lear, (V)iew playlists]: 1..3
```
*Selects tracks 1, 2, and 3*

### Command-line Options

```
usage: harmony [-h] [-t] [-p] [-v] [-dl] [query ...]

Harmony - Terminal-based music streamer powered by MPV
https://github.com/ZingyTomato/Harmony-Music

positional arguments:
  query                 Search query (e.g., 'harmony Never Gonna Give You Up')
                        or Spotify URL (e.g., 'harmony https://open.spotify.com/xxxx')

options:
  -h, --help            show this help message and exit
  -t, --trending        show top 20 trending tracks worldwide
  -p, --playlist        manage playlists (view existing or create new)
  -v, --version         display program version
  -dl, --disable-lyrics disable synchronized lyrics in MPV
```

## 🔨 Configuration

Harmony creates a config file at `~/.config/harmony` on first run. All settings can be modified in this file or overridden with command-line arguments.

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `SHOW_SYNCED_LYRICS` | Display synchronized lyrics in MPV | `false` |
| `PERSISTENT_QUEUE` | Save queue between sessions | `true` |
| `LOOP_QUEUE` | Loop tracks in queue | `false` |
| `LASTFM_API_KEY` | Last.fm API key for scrobbling | `null` |
| `LASTFM_API_SECRET` | Last.fm API secret | `null` |
| `LASTFM_USERNAME` | Last.fm username | `null` |
| `LASTFM_PASSWORD` | Last.fm password | `null` |

### Last.fm Integration

To enable Last.fm scrobbling:
1. [Create a Last.fm API account](https://www.last.fm/api/account/create)
2. Add your credentials to the config file
3. [View existing API keys](https://www.last.fm/api/accounts)

## 🏥 Contributing

Bug reports and feature requests are welcome. Please open an issue to discuss any problems or suggestions.