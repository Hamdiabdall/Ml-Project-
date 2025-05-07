"""
Visualization module for energy consumption analysis.

This module provides functions to visualize energy consumption data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

logger = logging.getLogger('energy_consumption')

class EnergyConsumptionVisualization:
    """Class for visualizing energy consumption data."""
    
    def __init__(self, data=None):
        """
        Initialize the visualization class.
        
        Args:
            data (pandas.DataFrame, optional): Data to visualize
        """
        self.data = data
        self.figure = None
        self.canvas = None
    
    def set_data(self, data):
        """
        Set the data to visualize.
        
        Args:
            data (pandas.DataFrame): Data to visualize
        """
        self.data = data
    
    def create_figure(self):
        """
        Create a new matplotlib figure.
        
        Returns:
            FigureCanvasQTAgg: Canvas for the figure
        """
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        return self.canvas
    
    def plot_consumption(self, consumption_type='electricity', plot_type='line', title=None):
        """
        Plot the consumption data.
        
        Args:
            consumption_type (str): Type of consumption to plot ('electricity' or 'gas')
            plot_type (str): Type of plot ('line' or 'bar')
            title (str, optional): Title for the plot
            
        Raises:
            ValueError: If the data is not loaded or the plot type is invalid
        """
        if self.data is None:
            logger.error("No data loaded for visualization")
            raise ValueError("No data loaded for visualization")
        
        if self.figure is None:
            logger.error("Figure not created yet")
            raise ValueError("Figure not created yet")
        
        # Clear the figure
        self.figure.clf()
        
        # Create a new axis
        ax = self.figure.add_subplot(111)
        
        # Determine column name based on available columns - use more flexible matching
        if consumption_type == 'gas':
            # Try exact match first, then try partial match
            if 'gas_consumption' in self.data.columns:
                column = 'gas_consumption'
            else:
                # Look for columns containing 'gas' or 'gaz'
                gas_columns = [col for col in self.data.columns if 'gas' in col.lower() or 'gaz' in col.lower()]
                if gas_columns:
                    column = gas_columns[0]
                else:
                    logger.error(f"No gas consumption data available")
                    raise ValueError(f"No gas consumption data available")
                    
        elif consumption_type == 'electricity':
            # Try exact match first, then try partial match
            if 'electricity_consumption' in self.data.columns:
                column = 'electricity_consumption'
            else:
                # Look for columns containing 'electric' or 'électric'
                elec_columns = [col for col in self.data.columns if 'electr' in col.lower() or 'électr' in col.lower()]
                if elec_columns:
                    column = elec_columns[0]
                else:
                    logger.error(f"No electricity consumption data available")
                    raise ValueError(f"No electricity consumption data available")
        
        elif 'consumption' in self.data.columns:
            column = 'consumption'
        else:
            # Last resort - try to find any column that might contain consumption data (not the date column)
            non_date_columns = [col for col in self.data.columns if col != 'date']
            if non_date_columns:
                column = non_date_columns[0]  # Use the first non-date column
                logger.warning(f"Using {column} as fallback for {consumption_type} consumption")
            else:
                logger.error(f"No {consumption_type} consumption data available")
                raise ValueError(f"No {consumption_type} consumption data available")
        
        dates = self.data.iloc[:, 0]
        values = self.data[column]
        
        # Plot the data
        if plot_type == 'line':
            ax.plot(dates, values, '-', label=f'{consumption_type.capitalize()} Consumption')
        elif plot_type == 'bar':
            ax.bar(dates, values, label=f'{consumption_type.capitalize()} Consumption')
        else:
            logger.error(f"Invalid plot type: {plot_type}")
            raise ValueError(f"Invalid plot type: {plot_type}")
        
        # Set the title
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'{consumption_type.capitalize()} Consumption Over Time')
        
        # Set the axis labels
        ax.set_xlabel('Date')
        ax.set_ylabel(f'{consumption_type.capitalize()} Consumption')
        
        # Rotate the date labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add a grid
        ax.grid(True)
        
        # Add a legend
        ax.legend()
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Refresh the canvas
        self.canvas.draw()
        
        logger.info(f"Created {plot_type} plot for {consumption_type} consumption")
    
    def add_approximation(self, degree=1):
        """
        Add an approximation curve to the plot.
        
        Args:
            degree (int): Degree of the polynomial for the approximation
            
        Raises:
            ValueError: If the data is not loaded or the figure is not created
        """
        if self.data is None:
            logger.error("No data loaded for approximation")
            raise ValueError("No data loaded for approximation")
        
        if self.figure is None:
            logger.error("Figure not created yet")
            raise ValueError("Figure not created yet")
        
        # Get the current axis
        ax = self.figure.gca()
        
        # Determine column name based on available columns
        if 'electricity_consumption' in self.data.columns:
            column = 'electricity_consumption'
        elif 'gas_consumption' in self.data.columns:
            column = 'gas_consumption'
        elif 'consumption' in self.data.columns:
            column = 'consumption'
        else:
            logger.error("No consumption data available")
            raise ValueError("No consumption data available")
        
        # Convert dates to numerical values for approximation
        dates = self.data.iloc[:, 0]
        values = self.data[column]
        
        # Create X as numeric values (days since first date)
        first_date = dates.min()
        X = np.array([(date - first_date).days for date in dates]).reshape(-1, 1)
        
        # Create the approximation model
        if degree == 1:
            model = LinearRegression()
        else:
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        
        # Fit the model
        model.fit(X, values)
        
        # Create a range of X values for prediction
        X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        
        # Predict Y values
        Y_pred = model.predict(X_range)
        
        # Convert X_range back to dates
        dates_range = [first_date + pd.Timedelta(days=int(x[0])) for x in X_range]
        
        # Plot the approximation curve
        ax.plot(dates_range, Y_pred, 'r-', label=f'Degree {degree} Approximation')
        
        # Update the legend
        ax.legend()
        
        # Refresh the canvas
        self.canvas.draw()
        
        logger.info(f"Added degree {degree} approximation to the plot")
    
    def save_plot(self, file_path):
        """
        Save the current plot to a file.
        
        Args:
            file_path (str): Path to save the file to
            
        Returns:
            bool: True if the plot was saved successfully, False otherwise
        """
        if self.figure is None:
            logger.error("No figure to save")
            return False
        
        try:
            self.figure.savefig(file_path)
            logger.info(f"Plot saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving plot: {str(e)}")
            return False
