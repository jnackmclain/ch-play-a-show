import csv
import random
import argparse
from fuzzywuzzy import process
import os
import configparser
import json
import sys

def read_json(json_file_path, instrument_filter=None):
    # Enclose the file path in double quotes only if there are spaces in the path
    json_file_path = f'"{json_file_path}"' if " " in json_file_path else json_file_path

    # Remove any existing double quotes around the file path
    json_file_path = json_file_path.strip('"')

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Filter data based on the specified instrument
    if instrument_filter:
        instrument_names = ["guitar", "bass", "rhythm", "guitar_coop", "ghl_guitar", "ghl_bass", "drums", "keys", "band", "pro_drums"]
        instrument_index = instrument_names.index(instrument_filter)
        if instrument_index < 0:
            # TODO: handle error
            pass

        # Create a mask with 1s at positions corresponding to difficulties
        instrument_mask = 0x0F << (instrument_index * 4)
        # print(f"Instrument Mask: {bin(instrument_mask)}")

        data = [song for song in data if (int(song.get('chartsAvailable', 0)) & instrument_mask) != 0]

    return data

def get_json_file_path(config):
    if config.has_option("Paths", "json_file_path"):
        json_file_path = config.get("Paths", "json_file_path")
    else:
        json_file_path = input("Enter the path for the JSON file: ")
        config.set("Paths", "json_file_path", json_file_path)
        with open(config_file_path, "w") as config_file:
            config.write(config_file)
    
    return json_file_path

def get_random_year(data, year_index):
    years = set(row[year_index] for row in data)
    return random.choice(list(years))

def get_random_artist(data, artist_index):
    artists = set(row[artist_index] for row in data)
    return random.choice(list(artists))

def get_random_genre(data, genre_index):
    genres = set(row[genre_index] for row in data)
    return random.choice(list(genres))

def get_random_song(data, song_title_index, artist_index):
    song = random.choice(data)
    return song[song_title_index], song[artist_index]

def eval_random_song(data, song_title_index, artist_index, short_name_index):
    song = random.choice(data)
    return song[song_title_index], song[artist_index], song[short_name_index]

def clear_playlist():
    print("Clearing the playlist (removed output file functionality).")

def get_random_song_from_artist(data, artist, song_title_index, artist_index):
    artist_songs = [song for song in data if song[artist_index] == artist]

    if not artist_songs:
        print(f"No songs found for the artist '{artist}'.")
        return None

    song = random.choice(artist_songs)
    return song[song_title_index], song[artist_index]

def fuzzy_search(data, song_title_index, artist_index, year_index, genre_index, short_name_index, config_file, target_title):
    if config_file:
        config = configparser.ConfigParser()
        config.read(config_file)
    else:
        config = None

    # Check if it's a genre search
    if target_title.startswith('genre:'):
        genre_to_search = target_title[len('genre:'):].strip()
        genre_matches = [(row[song_title_index], row[artist_index], row[short_name_index]) for row in data if genre_to_search.lower() in row[genre_index].lower()]

        if genre_matches:
            random_song_title, random_artist, random_short_name = random.choice(genre_matches)
            print(f"Random song matching genre '{genre_to_search}': '{random_song_title}' by '{random_artist}'")
        else:
            print(f"No songs found in the genre '{genre_to_search}'.")
    elif target_title.startswith('year:'):
        year_to_search = target_title[len('year:'):].strip()
        year_matches = [(row[song_title_index], row[artist_index], row[short_name_index]) for row in data if year_to_search == row[year_index]]

        if year_matches:
            random_song_title, random_artist, random_short_name = random.choice(year_matches)
            print(f"Random song from the year '{year_to_search}': '{random_song_title}' by '{random_artist}'")
        else:
            print(f"No songs found in the year '{year_to_search}'.")
    elif target_title == 'csv':
        song_title, artist = get_random_song(data, song_title_index, artist_index)
        print(f"Random song title from the CSV file: '{song_title}' by '{artist}'")
    else:
        matches = [(row[song_title_index], row[artist_index], row[short_name_index], score) for row in data for _, score in [process.extractOne(target_title, [row[song_title_index], row[artist_index]])]]

        top_matches = sorted(matches, key=lambda x: x[3], reverse=True)[:5]

        for i, (match_title, match_artist, _, score) in enumerate(top_matches, start=1):
            print(f"{i}. '{match_title}' by '{match_artist}' (Score: {score})")

        confirmation = input("Enter the number (1-5), 'n' to abort: ")

        if confirmation.lower() == 'y':
            best_match, best_artist, best_short_name, _ = max(top_matches, key=lambda x: x[3])
            print(f"Best match: '{best_match}' by '{best_artist}' (Score: {_})")
        elif confirmation.lower() == 'n':
            print("Operation aborted.")
        elif confirmation.isdigit() and 1 <= int(confirmation) <= 5:
            selected_match, _, selected_short_name, _ = top_matches[int(confirmation) - 1]
            print(f"Selected match: '{selected_match}' by '{best_artist}' (Score: {_})")
        else:
            print("Invalid input. Please enter 'y', 'n', 'genre:GenreName', 'year:Year', 'csv', or a number (1-5).")

def refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index):
    year = get_random_year(data, year_index)
    artist = get_random_artist(data, artist_index)
    song_title, _ = get_random_song(data, song_title_index, artist_index)
    genre = get_random_genre(data, genre_index)
    song_title_direct, artist_direct, short_name_direct = eval_random_song(data, song_title_index, artist_index, short_name_index)
    print(" ")
    return year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct

def main():
    parser = argparse.ArgumentParser(description="Clone Hero Play A Show")
    parser.add_argument("--instrument_filter", help="Filter songs based on instrument")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config_file_path = "config.ini"

    if not os.path.exists(config_file_path):
        print("Configuration file not found. Creating a new one.")
        config.add_section("Paths")
        json_file_path = input("Enter the path for the JSON file: ")
        config.set("Paths", "json_file_path", json_file_path)

        with open(config_file_path, "w") as config_file:
            config.write(config_file)
    else:
        config.read(config_file_path)
        json_file_path = get_json_file_path(config)

    data = read_json(json_file_path, instrument_filter=args.instrument_filter)

    if data:
        song_title_index = "Name"
        artist_index = "Artist"
        year_index = "Year"
        genre_index = "Genre"
        short_name_index = "Charter"

        year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)

        while True:
            print("Welcome to Clone Hero Play A Show!")
            print("Choose an option:")
            print(f"1. A random song from {year}")
            print(f"2. A random song by {artist}")
            print(f"3. '{song_title_direct}' by '{artist_direct}'")
            print(f"4. A random {genre} song")
            print("5. Refresh options")
            print("6. Manual fuzzy search")
            # print("7. Clear the playlist")
            print("0. Exit")

            choice = input("Enter the number of your choice: ")

            if choice == '1':
                fuzzy_search(data, song_title_index, artist_index, year_index, genre_index, short_name_index, None, f'year:{year}')
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '2':
                song_title, _ = get_random_song_from_artist(data, artist, song_title_index, artist_index)
                if song_title:
                    print(f"Random song from {artist}: '{song_title}'")
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '3':
                print(f"Selected option 3: '{song_title_direct}' by '{artist_direct}'")
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '4':
                fuzzy_search(data, song_title_index, artist_index, year_index, genre_index, short_name_index, None, f'genre:{genre}')
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '5':
                print("Options refreshed.")
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '6':
                search_string = input("Enter a Song Title or Artist to search for: ")
                fuzzy_search(data, song_title_index, artist_index, year_index, genre_index, short_name_index, None, search_string)
                print(" ")
            elif choice == '7':
                clear_playlist()
                year, artist, song_title, genre, song_title_direct, artist_direct, short_name_direct = refresh_options(data, song_title_index, artist_index, year_index, genre_index, short_name_index)
            elif choice == '0':
                print("Exiting Play A Show. Goodbye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
