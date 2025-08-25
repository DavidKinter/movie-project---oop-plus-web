"""
Utility functions for storage operations to enforce pylint compliance.

This module provides common utility functions used across different storage
implementations to reduce code duplication and maintain consistency.
"""

import os


def ensure_directory_exists(file_path: str) -> None:
    """Creates directory for file if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print(f"Error creating directory: {e}")
