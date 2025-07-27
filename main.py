"""
Main entry point for the Movie Database application.

This module creates the storage and application instances and runs
the movie database application.
"""

from movie_app import MovieApp
from storage_json import StorageJson


def main():
    """
    Main function that initializes and runs the movie application.
    """
    # Creates storage instance
    storage = StorageJson("movies.json")
    
    # Creates movie app with the storage
    movie_app = MovieApp(storage)
    
    # Runs the application
    movie_app.run()
    
    
if __name__ == "__main__":
    main()