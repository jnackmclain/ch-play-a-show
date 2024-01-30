# Clone Hero Play A Show

## Overview

Clone Hero Play A Show is a Python script that provides a simple and interactive way to select and play random songs from a Clone Hero song library via the generated songs.json. This provides an interactive way for users to filter and choose songs based on various criteria such as instrument, year, artist, and genre.

This application does not interface with Clone Hero in any way, only reads the songs.json file.

## Features

- **Random Song Selection:** Choose a random song based on the year, artist, or genre.
- **Filter by Instrument:** Specify an instrument to filter songs available for that instrument.
- **Fuzzy Search:** Perform a fuzzy search to find songs based on a provided search string.
- **Interactive Menu:** Use a menu-driven interface to easily navigate through different options.

## Prerequisites

- Python 3.x
- `fuzzywuzzy` library (install using `pip install fuzzywuzzy`)

## Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your_username/ch-play-a-show.git
   cd ch-play-a-show
   ```
2. **Run the Script**

   ```bash
   python ch_play_a_show.py --instrument_filter keys
   ```
   Replace keys with the desired instrument filter (optional).

   Available filters =
   ```bash
   "guitar", "bass", "rhythm", "guitar_coop", "ghl_guitar", "ghl_bass", "drums", "keys", "band", "pro_drums"
   ```
   
4. **Follow the on-screen menu to choose from various song selection options.**

   ```bash
   # Example Run:
   python ch_play_a_show.py --instrument_filter keys

   Welcome to Clone Hero Play A Show!
   Choose an option:
   1. A random song from {year}
   2. A random song by {artist}
   3. '{song_title_direct}' by '{artist_direct}'
   4. A random {genre} song
   5. Refresh options
   6. Manual fuzzy search
   7. Clear the playlist
   0. Exit

   Enter the number of your choice:
   ```

## Configuration
The script uses a configuration file (config.ini) to store the path to the Clone Hero songs.json.
If the configuration file is not found, the script will prompt you to enter the Clone Hero songs.json file path.
A playlist.txt is generated to store the selected options
