"""
Main module for 'My Movies Database'
This script initializes the application and starts the main program loopc
"""

import random
import statistics as stats
import sys
from datetime import date

import movie_storage as ms
from movie_storage import NoMoviesFoundError

MIN_CHOICE = 0
MAX_CHOICE = 10

def show_title():
    """
    Shows title of program
    """
    print("\n********** My Movies Database **********")


def show_menu():
    """
    Shows list of available commands. Gets re-opened after command is
    executed by user and/or invalid input
    """
    print(
        "\n"
        "Menu: \n"
        "0. Exit \n"
        "1. List movies \n"
        "2. Add movie \n"
        "3. Delete movie \n"
        "4. Update movie \n"
        "5. Stats \n"
        "6. Random movie \n"
        "7. Search movie \n"
        "8. Movies sorted by rating \n"
        "9. Movies sorted by year \n"
        "10. Filter movies \n"
        )


def user_choice():
    """
    Prompts user to select a command from menu
    """
    while True:
        try:
            show_menu()
            choice = input("Enter choice (0 - 10): ")
            if not MIN_CHOICE <= int(choice) <= MAX_CHOICE:
                raise ValueError
            return choice
        except ValueError:
            print("Invalid choice \n")


def user_exit():
    """
    Runs command '0. Exit' from menu
    Exits the program
    """
    print("\nBye!")
    sys.exit()


def mean_median_rating(movies, calc_type):
    """
    Calculates mean/median ('stat_func') rating for all movies in 'data.json'
    """
    stat_func = None  # Will be assigned stats.mean()/stats.median()
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message=f"Error determining {calc_type} rating: "
                                  f"No ratings in database."
            )
        if calc_type == 'average':
            stat_func = stats.mean
        elif calc_type == 'median':
            stat_func = stats.median
        else:
            raise ValueError(f"Invalid calc_type: {calc_type}")
        if stat_func:
            mean_median = stat_func(  # Calculates mean/median film ratings
                [float(movies["Movies"][title]["Rating"])
                 for title in movies["Movies"]]
                )
            return mean_median
    except NoMoviesFoundError as e:
        print(f"{e}")
    except (ValueError, ZeroDivisionError):
        return None
    return None


def best_worst_movie(movies, rating_type):
    """
    Identifies best-rated movie in 'data.json'; if there are multiple values
    with the same max rating, print all of them
    """
    rating_func = None  # Will be assigned min()/max()
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message=f"Error determining {rating_type}-rated "
                                  f"movie(s): No ratings in database."
            )
        if rating_type == "best":
            rating_func = max
        elif rating_type == "worst":
            rating_func = min
        else:
            raise ValueError(f"Invalid calc_type: {rating_type}")
        if rating_func:
            movie_rating = rating_func(  # Calculates min/max rating in DB
                float(movies["Movies"][title]["Rating"])
                for title in movies["Movies"]
                )
            # Assembles all movies that have exactly min / max rating
            rated_movies = [title for title in movies["Movies"] if
                            float(movies["Movies"][title]["Rating"])
                            == movie_rating]
            return rated_movies, movie_rating
    except NoMoviesFoundError as e:
        print(f"{e}")
    except (ValueError, TypeError):
        return None  # function could not determin best/worst movies
    return None  # function could not determin best/worst movies


def movie_stats(movies):
    """
    For all movies in database: shows average rating, median rating,
    best-rated movie(s) and worst-rated movie(s)
    """
    # Get and print average / median movie ratings
    average_rating = mean_median_rating(movies, calc_type="average")
    if average_rating is not None:
        print(f"\nAverage rating: {average_rating:.1f}")
    median_rating = mean_median_rating(movies, calc_type="median")
    if median_rating is not None:
        print(f"Median rating: {median_rating:.1f}")

    # Get and print best/worst movies + their ratings (multiple if same rating)
    try:
        best_movies, best_rating = (
            best_worst_movie(movies, rating_type="best")
        )
        if best_movies is not None and best_rating is not None:
            print(f"Best movie(s): {", ".join(best_movies)}, {best_rating}")
    except TypeError:
        pass  # Avoiding "cannot unpack non-iterable NoneType object" error
    try:
        worst_movies, worst_rating = (
            best_worst_movie(movies, rating_type="worst")
        )
        if worst_movies is not None and worst_rating is not None:
            print(f"Worst movie(s): {", ".join(worst_movies)}, {worst_rating}")
    except TypeError:
        pass  # Avoiding "cannot unpack non-iterable NoneType object" error
    return movies


def random_movie(movies):
    """
    Prints a random movie and its rating, loaded from 'data.json'
    """
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message="Error determining random movie: "
                                  "No movie in database."
            )
        random_title = random.choice(list(movies["Movies"].keys()))
        details = movies["Movies"].get(random_title, {})
        rating_str = details.get("Rating", "N/A")
        try:
            rating = float(rating_str)
            print(f"Your movie for tonight: {random_title}, "
                  f"it's rated {rating:.1f}"
                  )
        except (ValueError, TypeError):
            print(
                f"\nYour movie for tonight: {random_title}, "
                f"Rating: {rating_str} (invalid format)"
                )
    except NoMoviesFoundError as e:
        print(f"{e}")
    except ValueError as e:
        print(f"Error: {e}")
    except IndexError:
        pass  # Avoid "Cannot choose from an empty sequence" error
    return movies


def search_movie(movies):
    """
    Prompts user to enter part of a movie name, search all movies containing
    user query in 'data.json', and print corresponding movies, incl. rating.
    """
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message="Cannot search for movie. "
                                  "No movie in database."
            )
        movies_sorted = sorted(  # Ensures results listed in asc. alphab. order
            movies["Movies"].items(),
            key=lambda item: item[0].lower()
            )
        # Case-insensitive search for user-specified search string
        search_string = input("Enter part of movie name: ").lower()
        if not search_string:
            raise ValueError("Movie name cannot be empty.")
        str_in_database = []  # list for error check if user str not in DB
        for title, details in dict(movies_sorted).items():
            if search_string in title.lower():
                rating = details.get('Rating', 'N/A')
                str_in_database.append(title.lower())
                print(f"{title}, {rating}")
        # Prints an error message if search_string not in database
        if not str_in_database:  # Check if the list is empty
            print(
                f'Error: no movie in database with search item '
                f'"{search_string}"'
                )
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error: {e}")
    return movies


def sorted_by_rating(movies):
    """
    Prints movies from 'data.json' in descending order by rating
    """
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message="No movie in database."
            )
        sort_by_rating = sorted(
            movies["Movies"].items(),
            key=lambda item: float(item[1].get("Rating", 0.0)),
            reverse=True
            )
        ms.print_movie_items(sort_by_rating)  # Prints movies by rating
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error: {e}")
    return movies


def sorted_by_year(movies):
    """
    Prints movies from 'data.json' in ascending or descending order by year
    based on user selection
    """
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message="No movie in database."
            )
        sort_order = input(
            "Do you want the latest movies first? (Y/N): "
            ).lower()
        if sort_order not in ("y", "n"):  # Checks for correct input
            raise ValueError('Please enter "Y" or "N"\n')
        # Sets sorting in asc./desc. order based on user choice
        year_desc = sort_order == "y"  # True=ltst., False=oldst. 1st
        sorted_movies = sorted(
            movies["Movies"].items(),
            key=lambda item: (int(item[1].get("Year", 0)),
                              float(item[1].get("Rating", 0.0))),
            reverse=year_desc
            )
        ms.print_movie_items(sorted_movies)  # Prints movies by year
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error: {e}")
    return movies


# pylint: disable=too-many-locals
def filter_movies(movies):
    """
    Filters list of movies based on user-provided criteria; if user leaves
    any input blank, the program will not filter for that specific criterion
    """
    try:
        ms.check_movie_data(  # Checks if any movie in DB
            movies, error_message="No movie in database."
            )
        # Validates rating input
        rating_str = input(
            "Enter minimum rating "
            "(leave blank for no minimum rating): "
            )
        min_rating = ms.validate_numeric_input(
            input_str=rating_str,
            value_type=float,
            value_range=(ms.MIN_VALID_RATING, ms.MAX_VALID_RATING),
            value_name="Rating",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="could not convert string to float"
            )
        # Validates start_year input
        start_year_str = input(
            "Enter start year (leave blank for no start year): "
            )
        current_year = date.today().year
        start_year = ms.validate_numeric_input(
            input_str=start_year_str,
            value_type=int,
            value_range=(ms.MIN_VALID_YEAR, current_year),
            value_name="Year",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="invalid literal for int()"  # e.g. if input = "a"
            )
        end_year_str = input(
            "Enter end year (leave blank for no end year):  "
            )
        end_year = ms.validate_numeric_input(
            input_str=end_year_str,
            value_type=int,
            value_range=(ms.MIN_VALID_YEAR, current_year),
            value_name="Year",
            # error_substring = orig. message for specific error;
            # func replaces 'cryptic' message with user-friendly version
            error_substring="invalid literal for int()"  # e.g. if input = "a"
            )
        if (start_year is not None  # Valid user input
                and end_year is not None  # Valid user input
                and end_year < start_year):  # Invalid user input
            raise ValueError("Start year cannot exceed end year")
        # Find and print movies that match filter criteria
        print("\nFiltered Movies:")
        movies_found = 0  # Counter var for error message if no matches found
        for movie_title, details in movies.get("Movies", {}).items():
            year = int(details.get("Year"))
            rating = float(details.get("Rating"))
            # Check for each movie if user-specified filter criteria apply
            rating_condition = (min_rating is None or rating >= min_rating)
            year_condition = (
                    (start_year is None or year >= start_year)
                    and (end_year is None or year <= end_year)
            )
            if rating_condition and year_condition:  # print of criteria apply
                movies_found += 1
                print(f"{movie_title} ({year}), {rating:.1f}")
        if movies_found == 0:
            print("No movies found matching criteria.")
    except (NoMoviesFoundError, ValueError) as e:
        print(f"Error: {e}")
    return movies


def enter_continue():
    """
    Prompts user to press enter to continue
    """
    input("\nPress enter to continue ")


def call_command(movies, chosen_command):
    """
    Calls user-selected command from menu from dict of funcs 'command_dict'
    Returns the potentially modified movies dictionary.
    """
    command_dict = {
        "0":  user_exit,
        "1":  ms.list_movies,
        "2":  ms.add_movie,
        "3":  ms.delete_movie,
        "4":  ms.update_movie,
        "5":  movie_stats,
        "6":  random_movie,
        "7":  search_movie,
        "8":  sorted_by_rating,
        "9":  sorted_by_year,
        "10": filter_movies,
        }

    func_to_call = command_dict.get(chosen_command)
    if func_to_call:
        if chosen_command in ["1", "2", "3", "4", "5",
                              "6", "7", "8", "9", "10"]:
            return func_to_call(movies)
        if chosen_command == "0":
            user_exit()  # This exits, so no return needed here
    else:
        print("Invalid choice")
    return movies


def main():
    """
    Runs main application loop for the My Movies Database. Allows user to
    load and modify movie data and check statistics through various repeatedly
    prompted commands, until the user chooses to exit.
    """
    movies = ms.deserialize_movies()  # Initial JSON load
    show_title()
    while True:  # Loop indefinitely until explicitly exited
        chosen_command = user_choice()
        movies = call_command(movies, chosen_command)
        if chosen_command != "0":
            enter_continue()  # Pause before showing the menu again


if __name__ == "__main__":
    main()
