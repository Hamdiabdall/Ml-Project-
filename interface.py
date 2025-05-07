"""
UI interface module for energy consumption analysis.

This module handles the loading of the UI and connecting signals to slots.
"""

import os
import sys
import logging
from datetime import datetime
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDateEdit
from PyQt5.QtCore import QDate

from data_loader import DataLoader
from data_analysis import DataAnalysis
from visualisation import EnergyConsumptionVisualization
from utils import validate_date_format, validate_threshold_value, setup_logging

logger = logging.getLogger('energy_consumption')

class MainWindow(QtWidgets.QMainWindow):
    """Main window for the energy consumption analysis application."""
    
    def __init__(self):
        """Initialize the main window."""
        super(MainWindow, self).__init__()
        
        # Load the UI
        ui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui_interface.ui')
        uic.loadUi(ui_file, self)
        
        # Initialize components
        self.data_loader = DataLoader()
        self.data_analysis = DataAnalysis()
        self.visualizer = EnergyConsumptionVisualization()
        
        # Connect signals to slots
        self.connect_signals()
        
        # Set up the start and end date fields with default values
        self.setup_date_ranges()
        
        # Set up the visualization area
        self.setup_visualization()
        
        # Display a ready message
        self.statusBar().showMessage("Ready")
        
    def connect_signals(self):
        """Connect UI signals to slots."""
        # Menu actions
        self.actionLoad_File.triggered.connect(self.load_file)
        self.actionLoad_From_URL.triggered.connect(self.load_from_url)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionExport_Plot.triggered.connect(self.export_plot)
        
        # Buttons
        self.btnLoadFile.clicked.connect(self.load_file)
        self.btnAnalyze.clicked.connect(self.run_analysis)
        self.btnPlot.clicked.connect(self.create_plot)
        
        # Radio buttons for plot type
        self.radioLine.toggled.connect(self.update_plot_type)
        self.radioBar.toggled.connect(self.update_plot_type)
        
        # Radio buttons for consumption type
        self.radioElectricity.toggled.connect(self.update_consumption_type)
        self.radioGas.toggled.connect(self.update_consumption_type)
        
        # Checkbox for approximation
        self.chkApproximation.stateChanged.connect(self.toggle_approximation)
        
        # Combo box for approximation degree
        self.cmbDegree.currentIndexChanged.connect(self.update_approximation_degree)
    
    def setup_date_ranges(self):
        """Set up the date range widgets with default values."""
        # Set the date format
        for date_edit in [self.dateStart, self.dateEnd]:
            date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # Default to December 2024 since that's what seems to be in the data
        # This can be adjusted based on the actual data loaded
        year = 2024
        month = 12
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, 31)
        
        self.dateStart.setDate(QDate(first_day.year, first_day.month, first_day.day))
        self.dateEnd.setDate(QDate(last_day.year, last_day.month, last_day.day))
    
    def setup_visualization(self):
        """Set up the visualization area."""
        # Create a figure and canvas
        self.canvas = self.visualizer.create_figure()
        
        # Add the canvas to the plot area
        self.plotLayout.addWidget(self.canvas)
    
    def load_file(self):
        """Load data from a local file."""
        try:
            # Open a file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Update status
            self.statusBar().showMessage(f"Loading file: {file_path}...")
            
            # Load the file
            success = self.data_loader.load_from_file(file_path)
            
            if success:
                # Update the data in the analysis and visualization components
                self.data_analysis.set_data(self.data_loader.get_data())
                self.visualizer.set_data(self.data_loader.get_data())
                
                # Update status
                self.statusBar().showMessage(f"File loaded: {os.path.basename(file_path)}")
                
                # Enable analysis and plot buttons
                self.btnAnalyze.setEnabled(True)
                self.btnPlot.setEnabled(True)
                
                # Show a summary in the result area
                self.txtResults.setText(f"File loaded: {file_path}\n")
                self.txtResults.append(f"Data shape: {self.data_loader.get_data().shape}\n")
                self.txtResults.append(f"Date range: {self.data_loader.get_data().iloc[0, 0]} to {self.data_loader.get_data().iloc[-1, 0]}\n")
                
            else:
                # Show error message
                QMessageBox.critical(self, "Error", "Failed to load the file. Please check the format.")
                self.statusBar().showMessage("Failed to load file")
                
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.statusBar().showMessage("Error loading file")
    
    def load_from_url(self):
        """Load data from a URL with special handling for OpenData platform."""
        try:
            # Create a custom dialog with explanation and default URL
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Charger depuis une URL")
            dialog.setMinimumWidth(500)
            
            layout = QtWidgets.QVBoxLayout(dialog)
            
            # Add explanation label
            explanation = QtWidgets.QLabel(
                "Vous pouvez charger des données depuis une URL directe ou depuis la plateforme OpenData ODRE.\n"
                "Pour utiliser OpenData, vous pouvez simplement copier l'URL de la page du dataset ou utiliser l'URL directe ci-dessous:"
            )
            explanation.setWordWrap(True)
            layout.addWidget(explanation)
            
            # Add URL input field with default OpenData URL
            url_layout = QtWidgets.QHBoxLayout()
            url_label = QtWidgets.QLabel("URL:")
            url_input = QtWidgets.QLineEdit()
            url_input.setText("https://odre.opendatasoft.com/explore/dataset/consommation-quotidienne-brute")
            url_input.setMinimumWidth(400)
            
            url_layout.addWidget(url_label)
            url_layout.addWidget(url_input)
            layout.addLayout(url_layout)
            
            # Add buttons
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            # Show the dialog
            result = dialog.exec_()
            
            if result != QtWidgets.QDialog.Accepted:
                return
            
            url = url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "Avertissement", "Veuillez entrer une URL valide.")
                return
            
            # Update status
            self.statusBar().showMessage(f"Chargement des données depuis l'URL: {url}...")
            
            # Load the data
            success = self.data_loader.load_from_url(url)
            
            if success:
                # Update the data in the analysis and visualization components
                self.data_analysis.set_data(self.data_loader.get_data())
                self.visualizer.set_data(self.data_loader.get_data())
                
                # Update status
                self.statusBar().showMessage(f"Données chargées avec succès depuis l'URL")
                
                # Enable analysis and plot buttons
                self.btnAnalyze.setEnabled(True)
                self.btnPlot.setEnabled(True)
                
                # Update the date range based on the loaded data
                self._update_date_range_from_data()
                
                # Show a summary in the result area
                self.txtResults.setText(f"Données chargées depuis: {url}\n")
                self.txtResults.append(f"Dimensions: {self.data_loader.get_data().shape[0]} lignes × {self.data_loader.get_data().shape[1]} colonnes\n")
                
                # Format dates properly
                start_date = self.data_loader.get_data()['date'].min().strftime('%Y-%m-%d')
                end_date = self.data_loader.get_data()['date'].max().strftime('%Y-%m-%d')
                self.txtResults.append(f"Plage de dates disponible: {start_date} à {end_date}\n")
                
                # Add additional information
                self.txtResults.append("\nVous pouvez maintenant:")
                self.txtResults.append("1. Cliquer sur 'Lancer l'analyse' pour obtenir des statistiques")
                self.txtResults.append("2. Cliquer sur 'Tracer le graphique' pour visualiser les données")
                
                QMessageBox.information(self, "Succès", "Les données ont été chargées avec succès.\n\nVous pouvez maintenant lancer l'analyse ou tracer le graphique.")
                
            else:
                # Show error message
                QMessageBox.critical(self, "Erreur", "Impossible de charger les données depuis l'URL spécifiée. Vérifiez l'URL et votre connexion internet.")
                self.statusBar().showMessage("Échec du chargement des données depuis l'URL")
                
        except Exception as e:
            logger.error(f"Error loading data from URL: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.statusBar().showMessage("Error loading data from URL")
    
    def _update_date_range_from_data(self):
        """
        Mettre à jour la plage de dates en fonction des données chargées.
        Cette fonction est appelée après le chargement de données depuis un fichier ou une URL.
        """
        if not self.data_loader.has_data():
            return
            
        try:
            # Récupérer les dates min et max des données
            data = self.data_loader.get_data()
            min_date = data['date'].min()
            max_date = data['date'].max()
            
            # Convertir en QDate
            min_qdate = QDate(min_date.year, min_date.month, min_date.day)
            max_qdate = QDate(max_date.year, max_date.month, max_date.day)
            
            # Mettre à jour les widgets de date
            self.dateStart.setDate(min_qdate)
            self.dateEnd.setDate(max_qdate)
            
            # Mettre à jour également les limites des widgets pour éviter les erreurs
            self.dateStart.setMinimumDate(min_qdate)
            self.dateStart.setMaximumDate(max_qdate)
            self.dateEnd.setMinimumDate(min_qdate)
            self.dateEnd.setMaximumDate(max_qdate)
            
            logger.info(f"Plage de dates mise à jour: {min_date.strftime('%Y-%m-%d')} à {max_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la plage de dates: {str(e)}")
    
    def run_analysis(self):
        """Run the analysis on the loaded data."""
        try:
            if not self.data_loader.has_data():
                QMessageBox.warning(self, "Warning", "No data loaded. Please load data first.")
                return
            
            # Get the date range
            start_date = self.dateStart.date().toString("yyyy-MM-dd")
            end_date = self.dateEnd.date().toString("yyyy-MM-dd")
            
            # Get the threshold values
            threshold_above = self.txtThresholdAbove.text()
            threshold_below = self.txtThresholdBelow.text()
            
            # Validate threshold values
            if threshold_above and not validate_threshold_value(threshold_above):
                QMessageBox.warning(self, "Warning", "Invalid threshold value for 'above'.")
                return
                
            if threshold_below and not validate_threshold_value(threshold_below):
                QMessageBox.warning(self, "Warning", "Invalid threshold value for 'below'.")
                return
            
            # Get the consumption type
            consumption_type = 'electricity' if self.radioElectricity.isChecked() else 'gas'
            
            # Update status
            self.statusBar().showMessage(f"Analyzing data for {start_date} to {end_date}...")
            
            # Run the analysis
            min_value, min_date = self.data_analysis.get_minimum(start_date, end_date, consumption_type)
            max_value, max_date = self.data_analysis.get_maximum(start_date, end_date, consumption_type)
            avg_value = self.data_analysis.get_average(start_date, end_date, consumption_type)
            
            # Count days above/below threshold if provided
            days_above = None
            days_below = None
            
            if threshold_above:
                days_above = self.data_analysis.count_days_above_threshold(
                    start_date, end_date, float(threshold_above), consumption_type
                )
                
            if threshold_below:
                days_below = self.data_analysis.count_days_below_threshold(
                    start_date, end_date, float(threshold_below), consumption_type
                )
            
            # Show the results
            self.txtResults.clear()
            self.txtResults.append(f"Analysis Results for {consumption_type.capitalize()} Consumption\n")
            self.txtResults.append(f"Date Range: {start_date} to {end_date}\n\n")
            
            if min_value is not None:
                self.txtResults.append(f"Minimum: {min_value:.2f} on {min_date.strftime('%Y-%m-%d')}\n")
                
            if max_value is not None:
                self.txtResults.append(f"Maximum: {max_value:.2f} on {max_date.strftime('%Y-%m-%d')}\n")
                
            if avg_value is not None:
                self.txtResults.append(f"Average: {avg_value:.2f}\n")
            
            if days_above is not None:
                self.txtResults.append(f"Days above {threshold_above}: {days_above}\n")
                
            if days_below is not None:
                self.txtResults.append(f"Days below {threshold_below}: {days_below}\n")
            
            # Update status
            self.statusBar().showMessage("Analysis completed")
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred during analysis: {str(e)}")
            self.statusBar().showMessage("Error during analysis")
    
    def create_plot(self):
        """Create a plot of the data."""
        try:
            if not self.data_loader.has_data():
                QMessageBox.warning(self, "Warning", "No data loaded. Please load data first.")
                return
            
            # Get the date range
            start_date = self.dateStart.date().toString("yyyy-MM-dd")
            end_date = self.dateEnd.date().toString("yyyy-MM-dd")
            
            # Get the consumption type
            consumption_type = 'electricity' if self.radioElectricity.isChecked() else 'gas'
            
            # Get the plot type
            plot_type = 'line' if self.radioLine.isChecked() else 'bar'
            
            # Update status
            self.statusBar().showMessage(f"Creating {plot_type} plot for {start_date} to {end_date}...")
            
            # Get the data for the period
            period_data = self.data_analysis.get_data_for_period(start_date, end_date, consumption_type)
            
            if period_data is None or period_data.empty:
                QMessageBox.warning(self, "Warning", "No data found for the selected period.")
                self.statusBar().showMessage("No data for selected period")
                return
            
            # Set the data for visualization
            self.visualizer.set_data(period_data)
            
            # Create the plot
            title = f"{consumption_type.capitalize()} Consumption ({start_date} to {end_date})"
            self.visualizer.plot_consumption(consumption_type, plot_type, title)
            
            # Add approximation if selected
            if self.chkApproximation.isChecked():
                degree = self.cmbDegree.currentText()
                if degree and degree.isdigit():
                    self.visualizer.add_approximation(int(degree))
            
            # Update status
            self.statusBar().showMessage("Plot created")
            
        except Exception as e:
            logger.error(f"Error creating plot: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while creating the plot: {str(e)}")
            self.statusBar().showMessage("Error creating plot")
    
    def update_plot_type(self):
        """Update the plot type based on the radio button selection."""
        # Only update if data is loaded and plot exists
        if self.data_loader.has_data() and hasattr(self, 'canvas'):
            self.create_plot()
    
    def update_consumption_type(self):
        """Update the consumption type based on the radio button selection."""
        # Only update if data is loaded and plot exists
        if self.data_loader.has_data() and hasattr(self, 'canvas'):
            self.create_plot()
    
    def toggle_approximation(self, state):
        """Toggle the approximation on the plot."""
        # Enable/disable the degree combo box
        self.cmbDegree.setEnabled(state)
        
        # Only update if data is loaded and plot exists
        if self.data_loader.has_data() and hasattr(self, 'canvas'):
            self.create_plot()
    
    def update_approximation_degree(self):
        """Update the approximation degree on the plot."""
        # Only update if data is loaded, plot exists, and approximation is checked
        if self.data_loader.has_data() and hasattr(self, 'canvas') and self.chkApproximation.isChecked():
            self.create_plot()
    
    def export_plot(self):
        """Export the plot to an image file."""
        try:
            if not hasattr(self, 'canvas'):
                QMessageBox.warning(self, "Warning", "No plot to export.")
                return
            
            # Open a file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Plot", "", "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Update status
            self.statusBar().showMessage(f"Exporting plot to {file_path}...")
            
            # Save the plot
            success = self.visualizer.save_plot(file_path)
            
            if success:
                self.statusBar().showMessage(f"Plot exported to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export the plot.")
                self.statusBar().showMessage("Failed to export plot")
                
        except Exception as e:
            logger.error(f"Error exporting plot: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while exporting the plot: {str(e)}")
            self.statusBar().showMessage("Error exporting plot")
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Energy Consumption Analysis",
            "Energy Consumption Analysis\n\n"
            "Version 1.0\n\n"
            "An application for analyzing electricity and gas consumption data."
        )
