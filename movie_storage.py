"""
CRUD module connecting 'movies.py' and 'data.json'
"""

import json
from datetime import date

MIN_VALID_YEAR = 1888  # Year of first-ever made film
MIN_VALID_RATING = 0.0  # Min movie rating in database
MAX_VALID_RATING = 10.0  # Max movie rating in database


class NoMoviesFoundError(Exception):
    """
    Exception raised when the movie database is empty or inaccessible.
    """


def _file_existing(file_path="data.json"):
    """
    Checks if 'data.json' exists,
    if yes: return data from 'data.json'
    if no or corrupted: create JSON file with empty dictionary '{"Movies":{}}'
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    # If 'data.json' not found or corrupted, create new JSON:'{"Movies":{}}'
    except (FileNotFoundError, TypeError, json.decoder.JSONDecodeError):
        try:
            empty_data = {"Movies": {}}
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(empty_data, file)
            return empty_data
        except OSError as e:  # Handle potential errors during file creation
            print(f"Error: Could not create file '{file_path}': {e}")
            raise  # Re-raise the OSError


def deserialize_movies(file_path="data.json"):
    """
    Opens "data.json" and returns dict '{"Movies":{}}' as variable 'movies'
    """
    movies = _file_existing(file_path)
    return movies


def serialize_movies(movies, file_path="data.json"):
    """
    Serializes updated 'movies' dict to 'data.json'
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(movies, file, indent=4)
        return movies
    # If 'data.json' not found or corrupted, create new JSON:'{"Movies":{}}'
    except (FileNotFoundError, TypeError, json.decoder.JSONDecodeError):
        empty_data = {"Movies": {}}
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(empty_data, file)
        return empty_data
    except OSError as e:
        print(f"Error: Could not write to file '{file_path}': {e}")
        raise  # Re-raise the OSError


def check_movie_data(movies, error_message=None):
    """
    Check if movie data is valid and contains movies.
    Raises NoMoviesFoundError if invalid or empty.
    """
    if not movies or not movies.get("Movies"):
        raise NoMoviesFoundError(error_message)


def print_movie_items(movie_items_iterable):
    """
    Iterates through movie items and prints details (Title (Year): Rating).
    Handles missing year/rating using 'N/A'. movie_items_iterable == dict or
    sorted dict
    """
    for title, details in movie_items_iterable:  # dict or sorted dict
        year = details.get("Year", "N/A")
        rating = details.get("Rating", "N/A")
        try:
            # Attempt conversion to float for formatting
            rating_str = f"{float(rating):.1f}" if rating != "N/A" else "N/A"
        except (ValueError, TypeError):
            rating_str = str(rating)
        print(f"{title} ({year}): {rating_str}")


def find_movie_key(movies, search_title):
    """
    Performs a case-insensitive search for a movie title in the database.
    """
    if not search_title:
        raise ValueError("Movie title cannot be empty.")
    search_title_lower = search_title.lower()
    for original_key in movies["Movies"].keys():
        if original_key.lower() == search_title_lower:
            return original_key  # Return the original (case-sensitive) key
    return None  # Return None if loop completes without match


def list_movies(movies):
    """
    Runs command '1. List movies' from user menu in movies.py
    Prints total no. of movies + details for each movie from 'data.json'
    """
    try:
        check_movie_data(  # Check if movies exist before proceeding
            movies,
            error_message="Cannot list movies: "
                          "No movies found in database."
            )
        # Sort movies if they exist
        movies_sorted = sorted(  # Ensures movies listed in alphab. ord. (asc.)
            movies["Movies"].items(),
            key=lambda item: item[0].lower()
            )
        print(f"\n{len(movies_sorted)} movie(s) in total in database")
        print_movie_items(movies_sorted)  # Prints list of all movies in DB
    except NoMoviesFoundError as e:
        print(f"{e}")
    return movies


def validate_numeric_input(input_str,
                           value_type,
                           value_range,  # Tuple to conform w/ PEP8 max. arg.
                           value_name,
                           error_substring=None
                           ):
    """
    Validates string for conversion to numeric type and checks range.
    """
    if input_str:  # Proceed if input string not empty, i.e. NOT 'Enter'
        try:
            value = value_type(input_str)  # int/float(input_str)
            min_value, max_value = value_range  # Tuple to conform w/ max. arg.
            if not min_value <= value <= max_value:  # min/max year or rating
                raise ValueError(  # value_name = "year" or "rating"
                    f"{value_name} must be between {min_value} and "
                    f"{max_value}."
                    )
            return value
        except ValueError as e:
            # Ensures substring is not None/empty and checks specific substr.
            if error_substring and error_substring in str(e):
                raise ValueError(  # input_str = year_str or rating_str
                    f"Invalid {value_name.lower()} format: '{input_str}'. "
                    f"Please enter a valid number."
                    ) from e
            raise e
    return None  # If input_str is None / empty


def add_movie(movies, file_path="data.json"):
    """
    Runs command '2. Add movie' from user menu in movies.py.
    Prompts user to enter a movie name, a rating and a year; if movie not in
    database it will be added to dict and serialized in 'data.json'.
    Check is case-insensitive.
    """
    try:
        # Validate if movie already in database
        added_movie = input("Enter new movie name: ").strip()
        existing_key = find_movie_key(movies, added_movie)  # Iterate database
        if existing_key is not None:  # Check if movie (key) is in database
            raise ValueError(
                f"Movie with title '{added_movie}' already in database."
                )
        # Validate year of new movie
        year_str = input("Enter new movie year: ")
        current_year = date.today().year
        year = validate_numeric_input(
            input_str=year_str,
            value_type=int,
            value_range=(MIN_VALID_YEAR, current_year),
            value_name="Year",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="invalid literal for int()"  # e.g. if input = "a"
            )
        if year is None:  # Blank input, i.e. 'ENTER'
            raise ValueError("Year cannot be blank.")
        # Validate rating
        rating_str = input("Enter new movie rating: ")
        rating_float = validate_numeric_input(
            input_str=rating_str,
            value_type=float,
            value_range=(MIN_VALID_RATING, MAX_VALID_RATING),
            value_name="Rating",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="could not convert string to float"
            )
        if rating_float is None:  # Handle blank input
            raise ValueError("Rating cannot be blank.")
        rating = round(rating_float, 1)
        movies["Movies"][added_movie] = {
            "Year":   year,
            "Rating": rating,
            }
        serialize_movies(movies, file_path)  # serialize JSON
        print(f"Movie '{added_movie}' added successfully.")
    except ValueError as e:
        print(f"Error adding movie: {e}")
    return movies


def delete_movie(movies, file_path="data.json"):
    """
    Runs command '3. Delete movie' from user menu in movies.py.
    Prompts user to enter a movie name. If movie in database: entry is deleted,
    dict updated and serialized in 'data.json'. Check is case-insensitive.
    """
    try:
        check_movie_data(  # Check if movies exist before proceeding
            movies,
            error_message="No movie in database."
            )
        deleted_movie = input(
            "\nEnter name of movie you want to delete: "
            ).strip()
        # Case-insensitive check if 'deleted_movie' in database
        existing_key = find_movie_key(movies, deleted_movie)
        if existing_key:  # Check if movie (key) is in database
            del movies["Movies"][existing_key]
            serialize_movies(movies, file_path)  # serialize JSON
            print(f"Movie '{deleted_movie}' deleted successfully.")
        else:
            print(
                f"Error: Movie '{deleted_movie}' not found in "
                f"database"
                )
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error deleting movie: {e}")
    return movies


def update_movie(movies, file_path="data.json"):
    """
    Runs command '4. Update movie' from user menu in movies.py.
    Prompts user to enter a movie name and its new rating; if movie in
    database, dict is updated and serialized in 'data.json'. Check if movie
    in database is case-insensitive.
    """
    try:
        check_movie_data(  # Check if movies exist before proceeding
            movies,
            error_message="No movie in database."
            )
        # Validate if movie already in database
        updated_movie = input("Enter movie name: ").strip()
        existing_key = find_movie_key(movies, updated_movie)  # Iterate DB
        if existing_key is None:  # Check if movie (key) is NOT in database
            raise ValueError(
                f"Movie with title '{updated_movie}' is not in database."
                )
        # Validate rating
        rating_str = input("Enter new movie rating: ")
        rating_float = validate_numeric_input(
            input_str=rating_str,
            value_type=float,
            value_range=(MIN_VALID_RATING, MAX_VALID_RATING),
            value_name="Rating",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="could not convert string to float"
            )
        if rating_float is None:  # Blank input, i.e. 'ENTER'
            raise ValueError("Rating cannot be blank.")
        rating = round(rating_float, 1)
        movies["Movies"][existing_key]["Rating"] = rating
        serialize_movies(movies, file_path)  # serialize JSON
        print(f"Movie '{updated_movie}' updated successfully.")
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error updating movie: {e}")
    return movies
