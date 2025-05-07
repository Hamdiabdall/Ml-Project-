"""
Data loading module for energy consumption analysis.

This module provides functions to load data from various sources.
"""

import os
import requests
import pandas as pd
import logging
import shutil
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger('energy_consumption')


class DataLoader:
    """Class for loading energy consumption data from various sources."""
    
    def __init__(self):
        """Initialize the DataLoader."""
        self.data = None
        self.data_source = None
    
    def load_from_url(self, url):
        """
        Load data from a URL. Special handling for OpenData Réseaux Énergies (ODRE) platform.
        
        Args:
            url (str): URL to download the data from. Can be direct URL or OpenData platform URL.
            
        Returns:
            bool: True if data loading was successful, False otherwise
        """
        try:
            logger.info(f"Attempting to download data from: {url}")
            
            # Check if this is an ODRE OpenData URL and adjust if needed
            if 'opendatasoft.com' in url and not url.endswith('.csv'):
                # If this is the dataset exploration URL, transform it to the direct download URL
                if 'explore/dataset/consommation-quotidienne-brute' in url:
                    logger.info("Converting OpenData exploration URL to direct download URL")
                    download_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/consommation-quotidienne-brute/exports/csv"
                    logger.info(f"Using direct download URL: {download_url}")
                    url = download_url
            
            # Parse URL to get filename (or use a default if we can't extract one)
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or "downloaded_data.csv"
            
            # If filename doesn't have .csv extension, add it
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Download the file
            logger.info(f"Downloading data from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Save to a temporary file
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            temp_file = os.path.join(temp_dir, f"temp_{filename}")
            logger.info(f"Saving to temporary file: {temp_file}")
            
            with open(temp_file, 'wb') as f:
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            logger.info(f"Downloaded {total_size/1024:.2f} KB of data")
            
            # Load the data
            try:
                logger.info(f"Parsing downloaded CSV file...")
                self.data = self._load_csv(temp_file)
                logger.info(f"Successfully parsed CSV with {len(self.data)} rows and {len(self.data.columns)} columns")
                
                # Keep the temporary file for a while in case of problems
                # We'll create a backup in the resources directory
                resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ressources', 'exemples')
                if not os.path.exists(resources_dir):
                    os.makedirs(resources_dir)
                    
                backup_file = os.path.join(resources_dir, f"odre_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                shutil.copy(temp_file, backup_file)
                logger.info(f"Saved a backup of the data to {backup_file}")
                
                # Now clean up the temporary file
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Could not remove temporary file: {str(e)}")
                    
            except Exception as csv_error:
                logger.error(f"Error parsing downloaded CSV: {str(csv_error)}")
                # Keep the temporary file for debugging
                logger.info(f"The downloaded file is preserved at {temp_file} for debugging")
                raise ValueError(f"Could not parse the downloaded CSV file: {str(csv_error)}")
            
            self.data_source = url
            logger.info("Data loaded successfully from URL")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from URL: {str(e)}")
            return False
    
    def load_from_file(self, file_path):
        """
        Load data from a local file.
        
        Args:
            file_path (str): Path to the file to load
            
        Returns:
            bool: True if data loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading data from file: {file_path}")
            self.data = self._load_csv(file_path)
            self.data_source = file_path
            logger.info("Data loaded successfully from file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from file: {str(e)}")
            return False
    
    def _load_csv(self, file_path):
        """
        Load data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pandas.DataFrame: Loaded data
            
        Raises:
            ValueError: If the file format is invalid
        """
        try:
            # Essayons d'abord de détecter le séparateur automatiquement
            logger.info(f"Tentative de détection du séparateur du fichier CSV...")
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                
            # Détection du séparateur
            if ';' in first_line:
                separator = ';'
            elif ',' in first_line:
                separator = ','
            else:
                separator = None  # Laissons pandas détecter
                
            logger.info(f"Séparateur détecté: {separator}")
            
            # Charger le CSV avec le séparateur détecté
            try:
                df = pd.read_csv(file_path, sep=separator, encoding='utf-8')
            except UnicodeDecodeError:
                # Si l'encodage utf-8 échoue, essayons d'autres encodages
                logger.info(f"Tentative avec l'encodage latin-1...")
                df = pd.read_csv(file_path, sep=separator, encoding='latin-1')
            
            # Afficher les colonnes pour le débogage
            logger.info(f"Colonnes trouvées dans le CSV: {list(df.columns)}")
            
            # Vérifier si le dataframe a suffisamment de colonnes
            if df.shape[1] < 2:
                raise ValueError("File does not have enough columns")
                
            # Recherche des colonnes de date et de consommation
            # Définir les motifs de recherche pour les noms de colonnes
            date_patterns = ['date', 'Date', 'temps', 'Temps', 'time', 'Time', 'période', 'Période']
            elec_patterns = ['électricité', 'electricite', 'électr', 'electr', 'RTE']
            gas_patterns = ['gaz', 'gas', 'GRTgaz', 'Teréga']
            
            # Trouver la colonne de date
            date_col = None
            for pattern in date_patterns:
                date_candidates = [col for col in df.columns if pattern in col]
                if date_candidates:
                    date_col = date_candidates[0]
                    break
                    
            # Si aucune colonne de date n'est trouvée par motif, essayons de trouver par position
            if date_col is None:
                # Vérifions si la première colonne ressemble à une date
                first_col = df.columns[0]
                try:
                    pd.to_datetime(df[first_col].iloc[0])
                    date_col = first_col
                    logger.info(f"Utilisé la première colonne comme date: {date_col}")
                except:
                    pass
                    
            if date_col is None:
                # Dernière tentative - chercher une colonne qui ressemble à une date
                for col in df.columns:
                    try:
                        # Prenons quelques échantillons
                        samples = df[col].dropna().head(5).astype(str)
                        if any('-' in str(x) for x in samples) or any('/' in str(x) for x in samples):
                            pd.to_datetime(samples, errors='coerce')
                            date_col = col
                            logger.info(f"Détecté colonne de date: {date_col}")
                            break
                    except:
                        continue
                        
            if date_col is None:
                raise ValueError("No date column found in the CSV file")
                
            # Trouver les colonnes de consommation
            elec_col = None
            for pattern in elec_patterns:
                elec_candidates = [col for col in df.columns if pattern.lower() in col.lower()]
                if elec_candidates:
                    elec_col = elec_candidates[0]
                    break
                    
            gas_col = None
            for pattern in gas_patterns:
                gas_candidates = [col for col in df.columns if pattern.lower() in col.lower()]
                if gas_candidates:
                    gas_col = gas_candidates[0]
                    break
                    
            # Si aucune colonne spécifique n'est trouvée, utilisons les colonnes numériques disponibles
            if elec_col is None and gas_col is None:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 1:
                    elec_col = numeric_cols[0]
                if len(numeric_cols) >= 2:
                    gas_col = numeric_cols[1]
                    
            # Créer un nouveau DataFrame avec les colonnes nécessaires
            columns_to_keep = [date_col]
            if elec_col:
                columns_to_keep.append(elec_col)
            if gas_col:
                columns_to_keep.append(gas_col)
                
            # Vérifier que les colonnes existent avant de les utiliser
            columns_to_keep = [col for col in columns_to_keep if col in df.columns]
            
            if len(columns_to_keep) < 2:  # Au moins date + une consommation
                raise ValueError(f"Couldn't find required columns in the CSV file. Found: {columns_to_keep}")
                
            # Créer un nouveau DataFrame
            new_df = df[columns_to_keep].copy()
            
            # Renommer les colonnes pour faciliter l'accès
            column_mapping = {date_col: 'date'}
            if elec_col:
                column_mapping[elec_col] = 'electricity_consumption'
            if gas_col:
                column_mapping[gas_col] = 'gas_consumption'
                
            # Renommer les colonnes
            new_df = new_df.rename(columns=column_mapping)
            
            # Conversion de la colonne de date en datetime
            try:
                new_df['date'] = pd.to_datetime(new_df['date'], utc=True)
            except:
                try:
                    # Essayer un parsing plus basique
                    new_df['date'] = pd.to_datetime(new_df['date'], errors='coerce', utc=True)
                except Exception as e:
                    logger.error(f"Impossible de convertir la colonne date: {str(e)}")
                    raise ValueError(f"Cannot parse date column: {str(e)}")
            
            # Supprimer les lignes avec des dates NaT
            new_df = new_df.dropna(subset=['date'])
            
            # Convertir les colonnes de consommation en numérique
            for col in new_df.columns[1:]:
                new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
            
            # Filtrer les lignes marquées à ignorer si cette colonne existe
            if 'flag_ignore' in df.columns:
                filtered_indices = df[df['flag_ignore'] != 'oui'].index
                new_df = new_df[new_df.index.isin(filtered_indices)]
                logger.info(f"Filtered out rows with flag_ignore='oui'")
                
            # Informations sur le dataframe traité
            logger.info(f"DataFrame traité avec succès: {len(new_df)} lignes, colonnes: {list(new_df.columns)}")
            if not new_df.empty:
                logger.info(f"Plage de dates: {new_df['date'].min()} à {new_df['date'].max()}")
                
            return new_df
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {str(e)}")
            raise ValueError(f"Invalid file format: {str(e)}")
    
    def get_data(self):
        """
        Get the loaded data.
        
        Returns:
            pandas.DataFrame: Loaded data or None if no data is loaded
        """
        return self.data
    
    def has_data(self):
        """
        Check if data is loaded.
        
        Returns:
            bool: True if data is loaded, False otherwise
        """
        return self.data is not None
