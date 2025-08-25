"""
Storage interface for movie data persistence.

This module defines the abstract interface that all storage
implementations must follow, ensuring consistent behavior across
different storage types (JSON, CSV, database, etc.).
"""

from abc import ABC, abstractmethod


class IStorage(ABC):
    """
    Interface for movie storage implementations.
    """

    @abstractmethod
    def list_movies(self) -> dict:
        """
        Returns a dictionary of dictionaries that
        contains the movies information in the database.
        
        The function loads the information from the storage
        and returns the data.
        """

    @abstractmethod
    def add_movie(
            self,
            title: str,
            year: int,
            rating: float,
            poster: str
            ) -> None:
        """
        Adds a movie to the movies database.
        Loads the information from storage, adds the movie,
        and saves it. The function does not need to validate the input
        --> storage interface is "dumb" and trusts caller to provide
        valid data.
        """

    @abstractmethod
    def delete_movie(self, title: str) -> None:
        """
        Deletes a movie from the movies database.
        Loads the information from storage, deletes the movie,
        and saves it. The function does not need to validate the input
        --> storage interface is "dumb" and trusts caller to provide
        valid data.
        """

    @abstractmethod
    def update_movie(self, title: str, rating: float) -> None:
        """
        Updates a movie from the movies database.
        Loads the information from storage, updates the movie,
        and saves it. The function does not need to validate the input
        --> storage interface is "dumb" and trusts caller to provide
        valid data.
        """
