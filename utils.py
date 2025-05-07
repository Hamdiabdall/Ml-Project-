"""
Utility functions for the energy consumption analysis application.

This module contains helper functions used across the application.
"""

import os
import logging
from datetime import datetime


def setup_logging():
    """
    Set up logging configuration for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Set up logging
    log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logger
    logger = logging.getLogger('energy_consumption')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_date_format(date_str):
    """
    Validate if the provided string is in the correct date format (YYYY-MM-DD).
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if the date format is valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_threshold_value(value):
    """
    Validate if the provided threshold value is a valid number.
    
    Args:
        value: Value to validate
        
    Returns:
        bool: True if the value is a valid number, False otherwise
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_file_extension(file_path):
    """
    Get the extension of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension
    """
    return os.path.splitext(file_path)[1].lower()
