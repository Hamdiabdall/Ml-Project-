"""
Main module for energy consumption analysis application.

This module contains the entry point for the application.
"""

import sys
import os
import logging
from PyQt5 import QtWidgets

from interface import MainWindow
from utils import setup_logging


def main():
    """Main entry point for the application."""
    # Set up logging
    logger = setup_logging()
    logger.info("Application starting")
    
    # Create the application
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')  # Set the style to Fusion for a consistent look across platforms
    
    # Create the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    logger.info("Entering event loop")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
