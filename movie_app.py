"""
Movie application class that provides a CLI interface for movie management.

This module contains the MovieApp class which handles all user interactions,
menu display, and command execution while using a storage interface for
data persistence.
"""

import random
import statistics as stats
import sys
from datetime import date

from istorage import IStorage

# Constants
EARLIEST_MOVIE_YEAR = 1888  # Year of first motion picture (Roundhay Garden)
TITLE_DISPLAY_WIDTH = 40  # Width for centered title display
MIN_RATING = 0.0
MAX_RATING = 10.0
RATING_DECIMAL_PLACES = 1


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
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return

        # Use helper functions
        movies_sorted = self._sort_movies_by_title(movies)
        print(f"\n{len(movies_sorted)} movie(s) in total")
        self._print_movie_list(movies_sorted)

    def _command_add_movie(self) -> None:
        """
        Adds a new movie to the database.
        """
        try:
            # Gets movie details from user using helper
            title = self._get_non_empty_input(
                "Enter new movie name: ",
                "Movie name cannot be empty"
                )
            # Checks if movie already exists (case-insensitive)
            movies = self._storage.list_movies()
            existing_key = self._find_movie_key(movies, title)
            if existing_key is not None:
                raise ValueError(f"Movie '{title}' already exists")
            # Gets year
            year_str = self._get_non_empty_input(
                "Enter new movie year: ",
                "Year cannot be empty"
                )
            year = self._validate_year(year_str)
            # Gets rating
            rating_str = self._get_non_empty_input(
                "Enter new movie rating: ",
                "Rating cannot be empty"
                )
            rating = self._validate_rating(rating_str)
            # Adds movie (poster will be empty for now)
            self._storage.add_movie(title, year, rating, "")
            print(f"Movie '{title}' successfully added")
        except ValueError as e:
            print(f"Error adding movie: {e}")

    def _command_delete_movie(self) -> None:
        """
        Deletes a movie from the database.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        try:
            title = self._get_non_empty_input(
                "\nEnter name of movie to delete: ",
                "Movie name cannot be empty"
                )
        except ValueError as e:
            print(f"{e}")
            return
            # Case-insensitive search
        existing_key = self._find_movie_key(movies, title)
        if existing_key:
            self._storage.delete_movie(existing_key)
            print(f"Movie '{title}' successfully deleted")
        else:
            print(f"Movie '{title}' does not exist")

    def _command_update_movie(self) -> None:
        """
        Updates a movie's rating in the database.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        try:
            title = self._get_non_empty_input(
                "Enter movie name: ",
                "Movie name cannot be empty"
                )
            # Checks if movie exists
            existing_key = self._find_movie_key(movies, title)
            if existing_key is None:
                raise ValueError(f"Movie '{title}' does not exist")
            # Gets new rating
            rating_str = self._get_non_empty_input(
                "Enter new movie rating: ",
                "Rating cannot be empty"
                )
            rating = self._validate_rating(rating_str)
            # Updates movie
            self._storage.update_movie(existing_key, rating)
            print(f"Movie '{title}' successfully updated")
        except ValueError as e:
            print(f"Error updating movie: {e}")

    def _command_movie_stats(self) -> None:
        """
        Shows statistics for all movies in database.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
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
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        # Pick random movie
        random_title = random.choice(list(movies.keys()))
        movie_data = movies[random_title]
        rating = movie_data.get("rating", "N/A")

        print(f"\nYour movie for tonight: {random_title}, it's rated {rating}")

    def _command_search_movie(self) -> None:
        """
        Searches for movies containing a given string.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        try:
            search_input = self._get_non_empty_input(
                "Enter part of movie name: ",
                "Search term cannot be empty"
                )
            search_term = search_input.lower()
        except ValueError as e:
            print(f"{e}")
            return
        # Find matching movies
        found_movies = []
        for title, details in movies.items():
            if search_term in title.lower():
                found_movies.append((title, details))
        if not found_movies:
            print(f'No movie found with "{search_term}"')
            return
        # Sort and display results using helper
        found_movies.sort(key=lambda x: x[0].lower())
        self._print_movie_list(found_movies)

    def _command_sorted_by_rating(self) -> None:
        """
        Shows movies sorted by rating (highest first).
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        # Use helper function
        sorted_movies = self._sort_movies_by_rating(movies, descending=True)
        self._print_movie_list(sorted_movies)

    def _command_sorted_by_year(self) -> None:
        """
        Shows movies sorted by year.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        # Use helper function for yes/no input
        descending = self._get_yes_no_input(
            "Do you want the latest movies first? (Y/N): "
            )
        # Use helper function for sorting
        sorted_movies = self._sort_movies_by_year_and_rating(
            movies, descending=descending
            )
        self._print_movie_list(sorted_movies)

    def _command_filter_movies(self) -> None:
        """
        Filters movies based on user criteria.
        """
        movies = self._storage.list_movies()
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            print("No movies in database.")
            return
        # Gets filter criteria
        min_rating = None
        rating_str = input(
            "Enter minimum rating (leave blank for no minimum rating): "
            ).strip()
        if rating_str:
            try:
                min_rating = self._validate_rating(rating_str)
            except ValueError as e:
                print(f"Error: {e}")
                return
        start_year = None
        start_year_str = input(
            "Enter start year (leave blank for no start year): "
            ).strip()
        if start_year_str:
            try:
                start_year = self._validate_year(start_year_str)
            except ValueError as e:
                print(f"Error: {e}")
                return
        end_year = None
        end_year_str = input(
            "Enter end year (leave blank for no end year): "
            ).strip()
        if end_year_str:
            try:
                end_year = self._validate_year(end_year_str)
            except ValueError as e:
                print(f"Error: {e}")
                return
        # Validate year range
        if start_year and end_year and start_year > end_year:
            print("Start year cannot be after end year")
            return
        # Filter and display movies
        filtered_movies = self._filter_movies_by_criteria(
            movies, min_rating, start_year, end_year
            )
        self._display_filtered_results(filtered_movies)

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
            error_msg: str = "Input cannot be empty"
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
        Handles valid cases first with early returns, then invalid case
        with print statement at the end.
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
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            return None

        ratings = []
        for movie_data in movies.values():
            rating = movie_data.get("rating", 0)
            ratings.append(float(rating))
        return stats.mean(ratings)

    def _calculate_median_rating(self, movies: dict) -> float:
        """
        Calculates median rating of all movies.
        """
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            return None

        ratings = []
        for movie_data in movies.values():
            rating = movie_data.get("rating", 0)
            ratings.append(float(rating))
        return stats.median(ratings)

    def _find_best_worst_movies(self, movies: dict, rating_type: str) -> tuple:
        """
        Finds movies with best or worst ratings.
        """
        if not movies:  # Inline pattern balances DRY, readability, flexibility
            # [] = Empty list (no movies found), None = No rating -> no movies
            return [], None

        # Gets all ratings
        ratings = []
        for movie_data in movies.values():
            rating = float(movie_data.get("rating", 0))
            ratings.append(rating)
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
            print("No movies found matching criteria")
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
