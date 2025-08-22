"""
JSON storage implementation for movie data.

This module provides a concrete implementation of the IStorage interface
using JSON files for data persistence. It handles reading from and writing
to JSON files while maintaining the required data structure.
"""

import json
import os

from istorage import IStorage


class StorageJson(IStorage):
    """
    JSON file storage implementation for movies.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initializes the storage with a specific JSON file path.
        """
        self._file_path = file_path

    def list_movies(self) -> dict:
        """
        Returns a dictionary of dictionaries that
        contains the movies information in the database.
        """
        # Checks if file exists
        if not os.path.exists(self._file_path):
            # Returns empty dictionary if file does not exist
            return {}
        try:  # Opens and reads the JSON file
            with open(self._file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            # Handles both old format {"Movies": {...}} and new format {...}
            if isinstance(data, dict) and "Movies" in data:
                return data["Movies"]
            return data
        except json.JSONDecodeError:  # If file corrupted, return empty dict
            print(
                f"Error: Could not read {self._file_path}. "
                f"File may be corrupted."
                )
            return {}
        except OSError as e:  # Handles file system errors (permission, disk)
            print(f"Error reading file: {e}")
            return {}

    def add_movie(
            self,
            title: str,
            year: int,
            rating: float,
            poster: str
            ) -> None:
        """
        Adds a movie to the movies database.
        """
        movies = self.list_movies()  # Loads current movies
        # Adds the new movie
        movies[title] = {"rating": rating, "year": year, "poster": poster}
        self._save_movies(movies)  # Saves dict back to file

    def delete_movie(self, title: str) -> None:
        """
        Deletes a movie from the movies database.
        """
        movies = self.list_movies()  # Loads current movies
        if title in movies:  # Checks if movie exists
            del movies[title]  # Deletes the movie
            self._save_movies(movies)  # Saves dict back to file

    def update_movie(self, title: str, rating: float) -> None:
        """
        Updates a movie from the movies database.
        """
        movies = self.list_movies()  # Loads current movies
        if title in movies:  # Checks if movie exists
            movies[title]["rating"] = rating  # Updates only the rating
            self._save_movies(movies)  # Saves dict back to file

    def _ensure_file_exists(self) -> None:
        """
        Creates JSON file with empty structure if it does not exist.
        Called lazily only when needed.
        """
        # Checks if file exists
        if not os.path.exists(self._file_path):
            try:
                # Creates directory if needed
                directory = os.path.dirname(self._file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                # Creates file with empty movie dict
                with open(self._file_path, "w", encoding="utf-8") as file:
                    json.dump({}, file, indent=4)
            except OSError as e:
                print(f"Error creating JSON file: {e}")

    def _save_movies(self, movies: dict) -> None:
        """
        Helper method to save movies to the JSON file.
        """
        try:
            # Creates directory if it does not exist
            directory = os.path.dirname(self._file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            # Saves dict to file with proper formatting
            with open(self._file_path, "w", encoding="utf-8") as file:
                json.dump(movies, file, indent=4)
        except OSError as e:
            print(f"Error saving file: {e}")
