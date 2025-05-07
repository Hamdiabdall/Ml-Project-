"""
Data analysis module for energy consumption analysis.

This module provides functions to analyze energy consumption data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger('energy_consumption')

class DataAnalysis:
    """Class for analyzing energy consumption data."""
    
    def __init__(self, data=None):
        """
        Initialize the DataAnalysis class.
        
        Args:
            data (pandas.DataFrame, optional): Data to analyze
        """
        self.data = data
    
    def set_data(self, data):
        """
        Set the data to analyze.
        
        Args:
            data (pandas.DataFrame): Data to analyze
        """
        self.data = data
    
    def _validate_date_range(self, start_date, end_date):
        """
        Validate the date range.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            
        Returns:
            tuple: (start_date, end_date) as datetime objects
            
        Raises:
            ValueError: If the date range is invalid
        """
        try:
            # Convert to UTC datetime to match the format in the loaded data
            start = pd.to_datetime(start_date, utc=True)
            end = pd.to_datetime(end_date, utc=True)
            
            # Make sure end date is at the end of the day (23:59:59)
            end = end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            
            if start > end:
                raise ValueError("Start date cannot be after end date")
                
            logger.info(f"Validated date range: {start} to {end}")
            return start, end
            
        except Exception as e:
            logger.error(f"Error validating date range: {str(e)}")
            raise ValueError(f"Invalid date range: {str(e)}")
    
    def _filter_data_by_date(self, start_date, end_date, consumption_type='electricity'):
        """
        Filter data by date range.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            pandas.DataFrame: Filtered data
            
        Raises:
            ValueError: If the data is not loaded or does not have the required columns
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        # Determine column name based on available columns - use flexible matching
        if consumption_type == 'gas':
            # Try exact match first, then try partial match
            if 'gas_consumption' in self.data.columns:
                column = 'gas_consumption'
            else:
                # Look for columns containing 'gas' or 'gaz'
                gas_columns = [col for col in self.data.columns if 'gas' in col.lower() or 'gaz' in col.lower()]
                if gas_columns:
                    column = gas_columns[0]
                    logger.info(f"Using column '{column}' for gas consumption analysis")
                else:
                    logger.error(f"No gas consumption data available in columns: {list(self.data.columns)}")
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
                    logger.info(f"Using column '{column}' for electricity consumption analysis")
                else:
                    logger.error(f"No electricity consumption data available in columns: {list(self.data.columns)}")
                    raise ValueError(f"No electricity consumption data available")
        
        elif 'consumption' in self.data.columns:
            column = 'consumption'
        else:
            # Last resort - try to find any column that might contain consumption data (not the date column)
            non_date_columns = [col for col in self.data.columns if col != 'date']
            if non_date_columns:
                column = non_date_columns[0]  # Use the first non-date column
                logger.warning(f"Using {column} as fallback for {consumption_type} consumption analysis")
            else:
                logger.error(f"No {consumption_type} consumption data available in columns: {list(self.data.columns)}")
                raise ValueError(f"No {consumption_type} consumption data available")
        
        # Filter by date range
        date_column = 'date'  # We renamed this column in data_loader
        
        # Make sure dates are in UTC for proper comparison
        filtered = self.data.copy()
        
        # Ensure proper date comparison by explicitly filtering with UTC timestamps
        filtered = filtered[(filtered[date_column] >= start_date) & 
                            (filtered[date_column] <= end_date)]
        
        if filtered.empty:
            logger.warning(f"No data found between {start_date} and {end_date}")
        
        return filtered, column
    
    def get_minimum(self, start_date, end_date, consumption_type='electricity'):
        """
        Get the minimum consumption value in the date range.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            tuple: (min_value, min_date) or (None, None) if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                return None, None
            
            min_idx = filtered[column].idxmin()
            min_value = filtered.loc[min_idx, column]
            min_date = filtered.loc[min_idx, filtered.columns[0]]
            
            return min_value, min_date
            
        except Exception as e:
            logger.error(f"Error calculating minimum: {str(e)}")
            return None, None
    
    def get_maximum(self, start_date, end_date, consumption_type='electricity'):
        """
        Get the maximum consumption value in the date range.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            tuple: (max_value, max_date) or (None, None) if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                return None, None
            
            max_idx = filtered[column].idxmax()
            max_value = filtered.loc[max_idx, column]
            max_date = filtered.loc[max_idx, filtered.columns[0]]
            
            return max_value, max_date
            
        except Exception as e:
            logger.error(f"Error calculating maximum: {str(e)}")
            return None, None
    
    def get_average(self, start_date, end_date, consumption_type='electricity'):
        """
        Get the average consumption value in the date range.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            float: Average value or None if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                return None
            
            return filtered[column].mean()
            
        except Exception as e:
            logger.error(f"Error calculating average: {str(e)}")
            return None
    
    def count_days_above_threshold(self, start_date, end_date, threshold, consumption_type='electricity'):
        """
        Count the number of days where consumption is above the threshold.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            threshold (float): Threshold value
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            int: Number of days or None if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                return None
            
            return (filtered[column] > threshold).sum()
            
        except Exception as e:
            logger.error(f"Error counting days above threshold: {str(e)}")
            return None
    
    def count_days_below_threshold(self, start_date, end_date, threshold, consumption_type='electricity'):
        """
        Count the number of days where consumption is below the threshold.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            threshold (float): Threshold value
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            int: Number of days or None if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                return None
            
            return (filtered[column] < threshold).sum()
            
        except Exception as e:
            logger.error(f"Error counting days below threshold: {str(e)}")
            return None
            
    def get_data_for_period(self, start_date, end_date, consumption_type='electricity'):
        """
        Get the data for a specific period.
        
        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD
            consumption_type (str): Type of consumption to analyze ('electricity' or 'gas')
            
        Returns:
            pandas.DataFrame: Filtered data or None if no data
        """
        try:
            start, end = self._validate_date_range(start_date, end_date)
            filtered, column = self._filter_data_by_date(start, end, consumption_type)
            
            if filtered.empty:
                logger.warning(f"No data available between {start_date} and {end_date}")
                return None
            
            # Remove rows where the consumption column has missing values
            non_empty_data = filtered.dropna(subset=[column])
            
            if non_empty_data.empty:
                logger.warning(f"All {consumption_type} data in the selected period has missing values")
                # Fall back to gas if electricity was selected and is empty
                if consumption_type == 'electricity':
                    logger.info("Attempting to use gas consumption data instead")
                    try:
                        _, gas_column = self._filter_data_by_date(start, end, 'gas')
                        non_empty_gas = filtered.dropna(subset=[gas_column])
                        if not non_empty_gas.empty:
                            logger.info(f"Using gas consumption data as fallback")
                            return non_empty_gas[[filtered.columns[0], gas_column]]
                    except Exception as gas_error:
                        logger.error(f"Could not use gas data as fallback: {str(gas_error)}")
                return None
            
            return non_empty_data[[filtered.columns[0], column]]
            
        except Exception as e:
            logger.error(f"Error getting data for period: {str(e)}")
            return None
