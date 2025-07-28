"""
CSV storage implementation for movie data.

This module provides a concrete implementation of the IStorage interface
using CSV files for data persistence.
"""

import csv
import os
from typing import Dict, Any

from istorage import IStorage


class StorageCsv(IStorage):
    """
    CSV file storage implementation for movies.
    """

    # CSV column headers
    FIELDNAMES = ["title", "year", "rating", "poster"]

    def __init__(self, file_path: str) -> None:
        """
        Initializes the storage with a specific CSV file path.
        """
        self._file_path = file_path
        # Creates file with headers if it does not exist
        self._initialize_file()

    def _initialize_file(self) -> None:
        """
        Creates CSV file with headers if it does not exist.
        """
        # Checks if file exists
        if not os.path.exists(self._file_path):
            # Creates directory if needed
            directory = os.path.dirname(self._file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            # Creates file with headers
            with open(
                    self._file_path, "w", newline="", encoding="utf-8"
                    ) as file:
                writer = csv.writer(file)
                # Writes header row
                writer.writerow(self.FIELDNAMES)

    def list_movies(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary of dictionaries that contains the movies
        information in the database.
        """
        movies = {}
        # Checks if file exists
        if not os.path.exists(self._file_path):
            return movies
        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                # Converts each CSV row to our dictionary format
                for row in reader:
                    # Uses title as the key
                    title = row["title"]
                    # Creates the movie data dictionary
                    # Using 0 for missing years to distinguish from actuals
                    # MovieApp will display missing values as "N/A" to users
                    movie_data = {
                        "year":   int(row["year"]) if row["year"] else 0,
                        "rating": (float(row["rating"])
                                   if row["rating"] else 0.0),
                        "poster": row["poster"]
                        }
                    # Adds to movies dictionary
                    movies[title] = movie_data
        except FileNotFoundError:
            # File does not exist, returns empty dict
            return movies
        except (csv.Error, ValueError, KeyError) as e:
            print(f"Error reading CSV file: {e}")
            return movies
        return movies

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
        # Appends new row to CSV file
        try:
            with open(
                    self._file_path, "a",
                    newline="",
                    encoding="utf-8"
                    ) as file:
                writer = csv.writer(file)
                # Writes the movie data as a new row
                writer.writerow([title, year, rating, poster])
        except OSError as e:
            print(f"Error adding movie to CSV: {e}")

    def delete_movie(self, title: str) -> None:
        """
        Deletes a movie from the movies database.
        """
        # Reads all movies except the one to delete
        movies_to_keep = []
        movie_found = False
        try:
            # Reads existing movies
            with open(self._file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["title"] != title:
                        movies_to_keep.append(row)
                    else:
                        movie_found = True
            # Only rewrites if movie was found
            if movie_found:
                # Rewrites the file without the deleted movie
                with open(
                        self._file_path, "w",
                        newline="",
                        encoding="utf-8"
                        ) as file:
                    writer = csv.DictWriter(
                        file,
                        fieldnames=self.FIELDNAMES
                        )
                    # Writes header
                    writer.writeheader()
                    # Writes remaining movies
                    writer.writerows(movies_to_keep)
        except FileNotFoundError:
            # File does not exist, nothing to delete
            pass
        except (csv.Error, OSError) as e:
            print(f"Error deleting movie from CSV: {e}")

    def update_movie(self, title: str, rating: float) -> None:
        """
        Updates a movie from the movies database.
        """
        movies = []
        movie_found = False
        try:
            # Reads all movies
            with open(self._file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["title"] == title:
                        # Updates the rating
                        row["rating"] = str(rating)
                        movie_found = True
                    movies.append(row)
            # Only rewrites if movie was found
            if movie_found:
                # Rewrites the file with updated data
                with open(
                        self._file_path, "w",
                        newline="",
                        encoding="utf-8"
                        ) as file:
                    writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                    # Writes header
                    writer.writeheader()
                    # Writes all movies (including updated one)
                    writer.writerows(movies)
        except FileNotFoundError:
            # File does not exist, nothing to update
            pass
        except (csv.Error, OSError) as e:
            print(f"Error updating movie in CSV: {e}")
