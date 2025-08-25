"""
Storage package for movie data persistence.

This package provides different storage implementations (JSON, CSV)
for the movie database application.
"""

# Imports for easier access
from .istorage import IStorage
from .storage_csv import StorageCsv
from .storage_json import StorageJson

__all__ = ['IStorage', 'StorageJson', 'StorageCsv']
