# Movie Database Application

A comprehensive movie database management system built with Python, featuring OOP design patterns, API integration, and web interface generation.

## 🎬 Features

- **Multiple Storage Backends**: Supports both JSON and CSV file storage through a clean interface design
- **Multi-User Support**: Different users can maintain separate movie collections
- **OMDb API Integration**: Automatically fetches movie details (year, rating, poster) from OMDb API
- **Static Website Generation**: Creates a beautiful HTML website of your movie collection
- **Rich Statistics**: View average ratings, median ratings, best and worst movies
- **Search & Filter**: Search movies by title, filter by year range or minimum rating
- **Sorting Options**: Sort movies by title, rating, or year

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/DavidKinter/movie-project---oop-plus-web.git
cd movie-project---oop-plus-web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OMDb API key:
   - Get a free API key from [OMDb API](https://www.omdbapi.com/apikey.aspx)
   - Create a `.env` file in the project root:
   ```
   OMDB_API_KEY=your_api_key_here
   ```

## 📖 Usage

Run the application:
```bash
python main.py
```

You'll be prompted to select a user profile (John, Sara, or Jack), then presented with a comprehensive menu system.

### Available Commands

1. **List movies** - Display all movies in your collection
2. **Add movie** - Add a new movie (automatically fetches data from OMDb)
3. **Delete movie** - Remove a movie from your collection
4. **Update movie** - Change a movie's rating
5. **Stats** - View statistics (average, median, best, worst)
6. **Random movie** - Get a random movie suggestion
7. **Search movie** - Search for movies by title
8. **Movies sorted by rating** - View movies from highest to lowest rating
9. **Generate website** - Create a static HTML website
10. **Movies sorted by year** - View movies chronologically
11. **Filter movies** - Filter by rating, year range

## 🏗️ Project Structure

```
movie-project---oop-plus-web/
├── storage/                    # Storage package
│   ├── __init__.py            # Package initialization
│   ├── istorage.py            # Storage interface (abstract base)
│   ├── storage_json.py        # JSON storage implementation
│   └── storage_csv.py         # CSV storage implementation
├── data/                      # Data files directory
│   ├── john_movies.json       # John's movie collection
│   ├── sara_movies.csv        # Sara's movie collection
│   └── jack_movies.json       # Jack's movie collection
├── templates/                 # HTML templates
│   └── _static/
│       ├── index_template.html  # HTML template
│       └── style.css            # CSS styles
├── movie_app.py              # Main application class
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in repo)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 Technical Details

### Design Patterns

- **Strategy Pattern**: Different storage implementations (JSON, CSV) implementing the same interface
- **Dependency Injection**: Storage implementation injected into MovieApp
- **Separation of Concerns**: Clear separation between UI, business logic, and data persistence

### Technologies

- **Python 3.x**: Core language
- **Object-Oriented Programming**: Clean architecture with interfaces and implementations
- **requests**: For API communication
- **python-dotenv**: For environment variable management
- **OMDb API**: Movie data source

## 🎯 Future Enhancements

- [ ] Add SQLite database support
- [ ] Implement user authentication
- [ ] Create dynamic web interface with Flask
- [ ] Add movie recommendations based on ratings
- [ ] Export to different formats (PDF, Excel)
- [ ] Add movie poster caching

## 📝 License

This project is part of the Masterschool curriculum.

## 👤 Author

David Kinter

## 🙏 Acknowledgments
```
- Masterschool for the project requirements
- OMDb API for movie data
```

#### Create .gitignore

Create `.gitignore`:
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
ENV/
.venv
.env

# IDE specific files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
data/*.json
data/*.csv
!data/.gitkeep

# Generated website files
index.html
/style.css

# Keep templates
!templates/
!templates/_static/
!templates/_static/*.html
!templates/_static/*.css

# Testing
.pytest_cache/
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/
```

#### Create data/.gitkeep

This ensures the data directory is tracked by Git:
```bash
touch data/.gitkeep
```

#### Verify requirements.txt

Your `requirements.txt` should contain:
```
requests==2.32.4
python-dotenv==1.1.1
```
