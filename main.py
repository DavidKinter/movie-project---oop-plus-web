"""
Main entry point for the Movie Database application.

This module creates the storage and application instances and runs
the movie database application.
"""

from movie_app import MovieApp
from storage import StorageCsv, StorageJson

def main() -> None:
    """
    Main function that initializes and runs the movie application.
    """
    # Define user storage configurations
    users = {
        "1": {"name": "John", "storage": StorageJson("data/john_movies.json")},
        "2": {"name": "Sara", "storage": StorageCsv("data/sara_movies.csv")},
        "3": {"name": "Jack", "storage": StorageJson("data/jack_movies.json")}
        }

    # Display user selection menu
    print("\n*** Movie Database - User Selection ***")
    print("1. John (uses JSON storage)")
    print("2. Sara (uses CSV storage)")
    print("3. Jack (uses JSON storage)")
    print("0. Exit")

    # Get user choice
    choice = input("\nSelect user (0-3): ").strip()

    # Handle exit
    if choice == "0":
        print("\nGoodbye!")
        return

    # Get user configuration
    user_config = users.get(choice)
    if user_config:
        print(f"\nWelcome {user_config['name']}! Loading your movies...")
        storage = user_config["storage"]
    else:
        print("\nInvalid choice. Please try again.")
        main()  # Restart the selection
        return

    # Creates movie app with the selected storage
    movie_app = MovieApp(storage)

    # Runs the application
    movie_app.run()


if __name__ == "__main__":
    main()
