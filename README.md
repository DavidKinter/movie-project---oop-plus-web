# Movie Database Application

A Python-based movie database management system featuring object-oriented design, external API integration, and static website generation.

## Features

- **Multiple Storage Formats**: Supports both JSON and CSV file storage through a unified interface
- **Multi-User Support**: Separate movie collections for different users
- **API Integration**: Automatically fetches movie data (year, rating, poster) from OMDb API
- **Website Generation**: Creates static HTML pages to display your movie collection
- **Movie Statistics**: Calculate average ratings, find best/worst rated movies
- **Search and Filter**: Search by title, filter by year range or rating
- **Sorting Options**: Sort movies by title, rating, or release year

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DavidKinter/movie-project---oop-plus-web.git
cd movie-project---oop-plus-web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up OMDb API key:
   - Get a free API key from [OMDb API](https://www.omdbapi.com/apikey.aspx)
   - Create a `.env` file in the project root:
   ```
   OMDB_API_KEY=your_api_key_here
   ```

## Usage

Run the application:
```bash
python main.py
```

Select a user profile when prompted, then use the menu system to manage your movie collection.

### Menu Options

0. **Exit** - Close the application
1. **List movies** - Display all movies in your collection
2. **Add movie** - Add a new movie (fetches data from OMDb API)
3. **Delete movie** - Remove a movie from your collection
4. **Update movie** - Modify a movie's rating
5. **Stats** - View collection statistics
6. **Random movie** - Get a random movie suggestion
7. **Search movie** - Find movies by title
8. **Movies sorted by rating** - View movies by rating (high to low)
9. **Generate website** - Create a static HTML website
10. **Movies sorted by year** - View movies chronologically
11. **Filter movies** - Filter by rating or year range

## Project Structure

```
.
├── storage/                    # Storage implementations package
│   ├── __init__.py            # Package initialization
│   ├── istorage.py            # Abstract storage interface
│   ├── storage_json.py        # JSON storage implementation
│   ├── storage_csv.py         # CSV storage implementation
│   └── storage_utils.py       # Shared utility functions
├── data/                      # User data files
│   └── .gitkeep              # Ensures directory exists in git
├── templates/                 # Website templates
│   └── _static/
│       ├── index_template.html
│       └── style.css
├── movie_app.py              # Main application logic
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore configuration
└── README.md                # This file
```

## Technical Details

### Architecture

- **Interface-based design**: `IStorage` interface defines storage operations
- **Strategy pattern**: Swap between JSON and CSV storage implementations
- **Dependency injection**: Storage implementation passed to `MovieApp` at runtime
- **Separation of concerns**: Clear boundaries between UI, business logic, and data layers

### Dependencies

- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management
- Python 3.x standard library modules

### Data Storage

The application stores movie data with the following structure:
- **Title**: Movie name (used as unique identifier)
- **Year**: Release year
- **Rating**: Numeric rating (0.0-10.0)
- **Poster**: URL to movie poster image

## Implementation Notes

### User Configuration

The application comes with three pre-configured users:
- **John**: Uses JSON storage (`data/john_movies.json`)
- **Sara**: Uses CSV storage (`data/sara_movies.csv`)
- **Jack**: Uses JSON storage (`data/jack_movies.json`)

### Code Standards

- Follows PEP 8 conventions
- Type hints used throughout the codebase
- Comprehensive docstrings for all classes and methods
- Error handling for file operations and API calls

## License

This project is created for educational purposes.
