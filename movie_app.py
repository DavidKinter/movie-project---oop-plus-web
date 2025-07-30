"""
Movie application class that provides a CLI interface for movie management.

This module contains the MovieApp class which handles all user interactions,
menu display, and command execution while using a storage interface for
data persistence.
"""

import os
import random
import re
import statistics as stats
import sys
from datetime import date

import requests  # Add this import for API calls
from dotenv import load_dotenv  # Add this import for environment variables

from istorage import IStorage

# Load environment variables from .env file
load_dotenv()

# Constants
EARLIEST_MOVIE_YEAR = 1888  # Year of first motion picture (Roundhay Garden)
TITLE_DISPLAY_WIDTH = 40  # Width for centered title display
MIN_RATING = 0.0
MAX_RATING = 10.0
RATING_DECIMAL_PLACES = 1

# API Constants
# SECURITY: Using dotenv to load API key from .env file
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
if not OMDB_API_KEY:
    print("WARNING: OMDB_API_KEY not found in environment variables!")
    print("Please create a .env file with your API key.")
OMDB_BASE_URL = "http://www.omdbapi.com/"
API_TIMEOUT_SECONDS = 10  # Timeout for API requests
REQUIRED_API_FIELDS = ["Title", "Year", "imdbRating", "Poster"]


# pylint: disable=too-few-public-methods
class MovieApp:
    """
    Main application class for the movie database.
    """

    def __init__(self, storage: IStorage):
        """
        Initializes the MovieApp with a storage implementation.
        """
        self._storage = storage

    def _show_title(self) -> None:
        """
        Shows title of program.
        """
        title = " My Movies Database "
        print(f"\n{title.center(TITLE_DISPLAY_WIDTH, '*')}")

    def _show_menu(self) -> None:
        """
        Shows list of available commands.
        """
        print(
            "\n"
            "Menu:\n"
            "0. Exit\n"
            "1. List movies\n"
            "2. Add movie\n"
            "3. Delete movie\n"
            "4. Update movie\n"
            "5. Stats\n"
            "6. Random movie\n"
            "7. Search movie\n"
            "8. Movies sorted by rating\n"
            "9. Movies sorted by year\n"
            "10. Filter movies"
            )

    def _command_list_movies(self) -> None:
        """
        Lists all movies in the database.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return

        # Use helper functions
        movies_sorted = self._sort_movies_by_title(movies)
        print(f"\n{len(movies_sorted)} movie(s) in total.")
        self._print_movie_list(movies_sorted)

    def _check_movies_exist(self, movies: dict) -> bool:
        """
        Returns True if movies exist, prints message and returns False if not.
        """
        if not movies:
            print("No movies in database.")
            return False
        return True

    def _get_ratings_list(self, movies: dict) -> list[float]:
        """
        Extracts all ratings from movies dict as a list of floats.
        """
        ratings = []
        for movie_data in movies.values():
            rating = movie_data.get("rating", 0)
            ratings.append(float(rating))
        return ratings

    def _validate_api_response(self, data: dict, title: str) -> bool:
        """
        Validates that API response contains all required fields.
        Returns True if valid, False otherwise.
        """
        # Check if movie was found
        if data.get("Response") == "False":
            print(f'Movie "{title}" not found in OMDb API')
            return False

        # Validate required fields exist
        for field in REQUIRED_API_FIELDS:
            if field not in data:
                print(f"Warning: Missing {field} in API response.")
                return False
        return True

    def _extract_movie_data(self, data: dict, title: str) -> dict:
        """
        Extracts relevant movie data from API response.
        """
        return {
            "title":  data.get("Title", title),
            "year":   data.get("Year", "N/A"),
            "rating": data.get("imdbRating", "N/A"),
            "poster": data.get("Poster", "")
            }

    def _fetch_movie_from_api(self, title: str) -> dict | None:
        """
        Fetches movie data from OMDb API.
        Returns movie data dict on success, None on failure.
        """
        # Builds the API URL with parameters
        params = {
            "apikey": OMDB_API_KEY,
            "t":      title  # "t" parameter searches by title
            }
        try:
            # Makes the API request
            response = requests.get(
                OMDB_BASE_URL,
                params=params,
                timeout=API_TIMEOUT_SECONDS
                )
            # Checks if request was successful
            response.raise_for_status()
            # Parses JSON response
            data = response.json()
            # Validates response
            if not self._validate_api_response(data, title):
                return None
            # Extracts and returns relevant data
            return self._extract_movie_data(data, title)
        except requests.exceptions.ConnectionError:
            print(
                "Error: Could not connect to movie database. "
                "Check your internet connection."
                )
            return None
        except requests.exceptions.Timeout:
            print("Error: Request timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movie data: {e}.")
            return None

    def _get_and_validate_new_movie_title(self) -> str:
        """
        Gets movie title from user and validates it doesn't already exist. 
        Returns the title if valid. Raises ValueError if title is empty
        or already exists.
        """
        # Gets movie title from user
        title = self._get_non_empty_input(
            "Enter new movie name: ",
            "Movie name cannot be empty."
            )
        # Checks if movie already exists (case-insensitive)
        movies = self._storage.list_movies()
        existing_key = self._find_movie_key(movies, title)
        if existing_key is not None:
            raise ValueError(f'Movie "{title}" already exists.')
        return title

    def _command_add_movie(self) -> None:
        """
        Adds a new movie to the database by fetching data from API.
        """
        try:
            # Gets and validates movie title
            title = self._get_and_validate_new_movie_title()
            # Fetches movie data from API
            print(f'Fetching movie data for "{title}"...')
            movie_data = self._fetch_movie_from_api(title)
            # Checks if API fetch was successful
            if movie_data is None:
                raise ValueError("Could not fetch movie data.")
            # Extracts data from API response
            api_title = movie_data["title"]
            year_str = movie_data["year"]
            rating_str = movie_data["rating"]
            poster = movie_data["poster"]
            # Check if the fetched movie already exists
            movies = self._storage.list_movies()
            existing_key = self._find_movie_key(movies, api_title)
            if existing_key is not None:
                raise ValueError(f'Movie "{api_title}" already exists.')
            # Validates and converts year and rating
            year = self._parse_year_from_api(year_str)
            rating = self._parse_rating_from_api(rating_str)
            # Adds movie with API data
            self._storage.add_movie(api_title, year, rating, poster)
            print(f'Movie "{api_title}" successfully added.')
        except ValueError as e:
            print(f"Error adding movie: {e}.")

    def _parse_year_from_api(self, year_str: str) -> int:
        """
        Parses and validates year string from API response.
        """
        if year_str == "N/A":
            raise ValueError("Movie year not available in database.")
        try:
            # Extracts first 4-digit year from string
            year_match = re.search(r"\d{4}", year_str)
            if year_match:
                return int(year_match.group())
            raise ValueError(f"No valid year found in: {year_str}.")
        except ValueError as exc:
            raise ValueError(
                f"Invalid year format from API: {year_str}."
                ) from exc

    def _parse_rating_from_api(self, rating_str: str) -> float:
        """
        Parses and validates rating string from API response.
        """
        if rating_str == "N/A":
            raise ValueError("Movie rating not available in database.")
        try:
            rating = float(rating_str)
            # IMDb ratings are X out of 10, matching implementation
            return round(rating, RATING_DECIMAL_PLACES)
        except ValueError as exc:
            raise ValueError(
                f"Invalid rating format from API: {rating_str}."
                ) from exc

    def _command_delete_movie(self) -> None:
        """
        Deletes a movie from the database.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        try:
            title = self._get_non_empty_input(
                "\nEnter name of movie to delete: ",
                "Movie name cannot be empty."
                )
        except ValueError as e:
            print(f"{e}.")
            return
        # Case-insensitive search
        existing_key = self._find_movie_key(movies, title)
        if existing_key:
            self._storage.delete_movie(existing_key)
            print(f'Movie "{title}" successfully deleted.')
        else:
            print(f'Movie "{title}" does not exist.')

    def _command_update_movie(self) -> None:
        """
        Updates a movie's rating in the database.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        try:
            title = self._get_non_empty_input(
                "Enter movie name: ",
                "Movie name cannot be empty."
                )
            # Checks if movie exists
            existing_key = self._find_movie_key(movies, title)
            if existing_key is None:
                raise ValueError(f'Movie "{title}" does not exist.')
            # Gets new rating
            rating_str = self._get_non_empty_input(
                "Enter new movie rating: ",
                "Rating cannot be empty."
                )
            rating = self._validate_rating(rating_str)
            # Updates movie
            self._storage.update_movie(existing_key, rating)
            print(f'Movie "{title}" successfully updated.')
        except ValueError as e:
            print(f"Error updating movie: {e}.")

    def _command_movie_stats(self) -> None:
        """
        Shows statistics for all movies in database.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        # Calculate average rating
        avg_rating = self._calculate_average_rating(movies)
        if avg_rating is not None:
            print(f"\nAverage rating: {avg_rating:.1f}")
        # Calculate median rating
        median_rating = self._calculate_median_rating(movies)
        if median_rating is not None:
            print(f"Median rating: {median_rating:.1f}")
        # Find best- and worst-rated movies
        best_movies, best_rating = self._find_best_worst_movies(
            movies,
            "best"
            )
        if best_movies:
            print(f"Best movie(s): {', '.join(best_movies)}, {best_rating}")
        worst_movies, worst_rating = self._find_best_worst_movies(
            movies, "worst"
            )
        if worst_movies:
            print(f"Worst movie(s): {', '.join(worst_movies)}, {worst_rating}")

    def _command_random_movie(self) -> None:
        """
        Suggests a random movie from the database.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        # Picks random movie
        random_title = random.choice(list(movies.keys()))
        movie_data = movies[random_title]
        rating = movie_data.get("rating", "N/A")
        print(f"\nYour movie for tonight: {random_title}, it's rated {rating}")

    def _command_search_movie(self) -> None:
        """
        Searches for movies containing a given string.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        try:
            search_input = self._get_non_empty_input(
                "Enter part of movie name: ",
                "Search term cannot be empty."
                )
            search_term = search_input.lower()
        except ValueError as e:
            print(f"{e}.")
            return
        # Finds matching movies
        found_movies = []
        for title, details in movies.items():
            if search_term in title.lower():
                found_movies.append((title, details))
        if not found_movies:
            print(f'No movie found with "{search_term}".')
            return
        # Sorts and displays results using helper
        found_movies.sort(key=lambda x: x[0].lower())
        self._print_movie_list(found_movies)

    def _command_sorted_by_rating(self) -> None:
        """
        Shows movies sorted by rating (highest first).
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        # Uses helper function
        sorted_movies = self._sort_movies_by_rating(movies, descending=True)
        self._print_movie_list(sorted_movies)

    def _command_sorted_by_year(self) -> None:
        """
        Shows movies sorted by year.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        # Uses helper function for yes/no input
        descending = self._get_yes_no_input(
            "Do you want the latest movies first? (Y/N): "
            )
        # Uses helper function for sorting
        sorted_movies = self._sort_movies_by_year_and_rating(
            movies,
            descending=descending
            )
        self._print_movie_list(sorted_movies)

    def _get_optional_validated_input(
            self,
            prompt: str,
            validator_func
            ) -> any:
        """
        Gets optional input from user and validates it if provided. Returns
        None if input is blank, validated value if valid. Raises ValueError
        if validation fails.
        """
        input_str = input(prompt).strip()
        if not input_str:
            return None
        return validator_func(input_str)

    def _command_filter_movies(self) -> None:
        """
        Filters movies based on user criteria.
        """
        movies = self._storage.list_movies()
        if not self._check_movies_exist(movies):
            return
        try:
            # Gets filter criteria
            min_rating = self._get_optional_validated_input(
                "Enter minimum rating "
                "(leave blank for no minimum rating): ",
                self._validate_rating
                )
            start_year = self._get_optional_validated_input(
                "Enter start year (leave blank for no start year): ",
                self._validate_year
                )
            end_year = self._get_optional_validated_input(
                "Enter end year (leave blank for no end year): ",
                self._validate_year
                )
            # Validates year range
            if start_year and end_year and start_year > end_year:
                print("Start year cannot be after end year.")
                return
            # Filters and displays movies
            filtered_movies = self._filter_movies_by_criteria(
                movies, min_rating, start_year, end_year
                )
            self._display_filtered_results(filtered_movies)
        except ValueError as e:
            print(f"Error: {e}.")

    def _find_movie_key(self, movies: dict, search_title: str) -> str:
        """
        Performs case-insensitive search for movie title.
        """
        if not search_title:
            return None
        search_title_lower = search_title.lower()
        for original_key in movies.keys():
            if original_key.lower() == search_title_lower:
                return original_key
        return None

    def _validate_year(self, year_str: str) -> int:
        """
        Validates year input.
        """
        try:
            year = int(year_str)
            current_year = date.today().year
            if not EARLIEST_MOVIE_YEAR <= year <= current_year:
                raise ValueError(
                    f"Year must be between {EARLIEST_MOVIE_YEAR} and "
                    f"{current_year}"
                    )
            return year
        except ValueError as exc:
            raise ValueError("Invalid year format") from exc

    def _validate_rating(self, rating_str: str) -> float:
        """
        Validates rating input.
        """
        try:
            rating = float(rating_str)
            if not MIN_RATING <= rating <= MAX_RATING:
                raise ValueError(
                    f"Rating must be between {MIN_RATING} and {MAX_RATING}"
                    )
            return round(rating, RATING_DECIMAL_PLACES)
        except ValueError as exc:
            raise ValueError("Invalid rating format") from exc

    def _get_non_empty_input(
            self,
            prompt: str,
            error_msg: str = "Input cannot be empty."
            ) -> str:
        """
        Gets non-empty input from user with error handling.
        """
        value = input(prompt).strip()
        if not value:
            raise ValueError(error_msg)
        return value

    def _get_yes_no_input(self, prompt: str) -> bool:
        """
        Gets validated yes/no input from user. Uses "guard clause" pattern: 
        Handles valid cases first with early returns, then invalid case with
        print statement at the end.
        """
        while True:
            response = input(prompt).strip().lower()
            if response in ["y", "yes"]:
                return True
            if response in ["n", "no"]:
                return False
            print("Please enter Y or N")

    def _format_movie_line(self, title: str, year: int, rating: float) -> str:
        """
        Formats a movie line for consistent display.
        """
        return f"{title} ({year}): {rating}"

    def _print_movie_list(self, movies: list[tuple]) -> None:
        """
        Prints a formatted list of movies.
        """
        for title, details in movies:
            year = details.get("year", "N/A")
            rating = details.get("rating", "N/A")
            print(self._format_movie_line(title, year, rating))

    def _sort_movies_by_title(self, movies: dict) -> list[tuple]:
        """
        Sorts movies alphabetically by title.
        """
        return sorted(movies.items(), key=lambda item: item[0].lower())

    def _sort_movies_by_rating(
            self,
            movies: dict,
            descending: bool = True
            ) -> list[tuple]:
        """
        Sorts movies by rating.
        """
        return sorted(
            movies.items(),
            key=lambda x: float(x[1].get("rating", 0)),
            reverse=descending
            )

    def _sort_movies_by_year_and_rating(
            self,
            movies: dict,
            descending: bool = True
            ) -> list[tuple]:
        """
        Sorts movies by year, then by rating.
        """
        return sorted(
            movies.items(),
            key=lambda x: (int(x[1].get("year", 0)),
                           float(x[1].get("rating", 0))),
            reverse=descending
            )

    def _calculate_average_rating(self, movies: dict) -> float:
        """
        Calculates average rating of all movies.
        """
        if not movies:
            return None

        ratings = self._get_ratings_list(movies)
        return stats.mean(ratings)

    def _calculate_median_rating(self, movies: dict) -> float:
        """
        Calculates median rating of all movies.
        """
        if not movies:
            return None

        ratings = self._get_ratings_list(movies)
        return stats.median(ratings)

    def _find_best_worst_movies(self, movies: dict, rating_type: str) -> tuple:
        """
        Finds movies with best or worst ratings.
        """
        if not movies:
            # [] = Empty list (no movies found), None = No rating -> no movies
            return [], None

        # Gets all ratings
        ratings = self._get_ratings_list(movies)
        # Finds target rating
        if rating_type == "best":
            target_rating = max(ratings)
        else:  # worst
            target_rating = min(ratings)
        # Finds all movies with target rating
        matching_movies = []
        for title, movie_data in movies.items():
            if float(movie_data.get("rating", 0)) == target_rating:
                matching_movies.append(title)
        return matching_movies, target_rating

    def _filter_movies_by_criteria(
            self,
            movies: dict,
            min_rating: float,
            start_year: int,
            end_year: int
            ) -> list[tuple]:
        """
        Filters movies based on rating and year criteria.
        """
        filtered_movies = []
        for title, details in movies.items():
            year = int(details.get("year", 0))
            rating = float(details.get("rating", 0))
            # Checks all criteria
            rating_ok = (min_rating is None or rating >= min_rating)
            start_year_ok = (start_year is None or year >= start_year)
            end_year_ok = (end_year is None or year <= end_year)
            if rating_ok and start_year_ok and end_year_ok:
                filtered_movies.append((title, details))
        return filtered_movies

    def _display_filtered_results(self, filtered_movies: list[tuple]) -> None:
        """
        Displays filtered movie results.
        """
        print("\nFiltered movies:")
        if not filtered_movies:
            print("No movies found matching criteria.")
            return

        # Sorts by title for consistent display
        filtered_movies.sort(key=lambda x: x[0].lower())
        self._print_movie_list(filtered_movies)

    def _get_user_choice(self) -> str:
        """
        Gets and validates user menu choice.
        """
        valid_choices = [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
            ]
        while True:
            choice = input("\nEnter choice (0-10): ").strip()
            if choice in valid_choices:
                return choice
            print("Invalid choice. Please enter 0-10.")

    def _execute_command(self, choice: str) -> None:
        """
        Executes the command based on user choice.
        """
        commands = {
            "1":  self._command_list_movies,
            "2":  self._command_add_movie,
            "3":  self._command_delete_movie,
            "4":  self._command_update_movie,
            "5":  self._command_movie_stats,
            "6":  self._command_random_movie,
            "7":  self._command_search_movie,
            "8":  self._command_sorted_by_rating,
            "9":  self._command_sorted_by_year,
            "10": self._command_filter_movies
            }
        command = commands.get(choice)
        if command:
            command()

    def _generate_website(self) -> None:
        """
        Placeholder for website generation.
        """

    def run(self) -> None:
        """
        Runs the movie application main loop.
        """
        self._show_title()
        while True:
            self._show_menu()
            choice = self._get_user_choice()

            if choice == "0":
                print("\nBye!")
                sys.exit()
            self._execute_command(choice)

            # Pauses before showing menu again
            input("\nPress enter to continue...")
