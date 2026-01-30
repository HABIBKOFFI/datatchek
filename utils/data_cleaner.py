# data_cleaner.py
"""
Module de nettoyage automatique des données
Style Dataiku DSS - Prepare Recipe
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import re
from datetime import datetime


class DataCleaner:
    """Nettoyeur automatique de données"""
    
    def __init__(self, df: pd.DataFrame, source_filename: str = None):
        """
        Initialise le nettoyeur
        
        Args:
            df: DataFrame à nettoyer
            source_filename: Nom du fichier source
        """
        self.df_original = df.copy()
        self.df = df.copy()
        self.source_filename = source_filename or "dataset"
        self.cleaning_log = []
        
    def remove_empty_columns(self) -> 'DataCleaner':
        """Supprime les colonnes totalement vides"""
        empty_cols = [col for col in self.df.columns if self.df[col].isnull().all()]
        
        if empty_cols:
            self.df = self.df.drop(columns=empty_cols)
            self.cleaning_log.append({
                'operation': 'remove_empty_columns',
                'columns': empty_cols,
                'count': len(empty_cols)
            })
        
        return self
    
    def remove_high_missing_columns(self, threshold: float = 0.8) -> 'DataCleaner':
        """
        Supprime les colonnes avec trop de valeurs manquantes
        
        Args:
            threshold: Seuil (0.8 = 80% de valeurs manquantes)
        """
        high_missing = []
        for col in self.df.columns:
            missing_pct = self.df[col].isnull().sum() / len(self.df)
            if missing_pct >= threshold:
                high_missing.append(col)
        
        if high_missing:
            self.df = self.df.drop(columns=high_missing)
            self.cleaning_log.append({
                'operation': 'remove_high_missing_columns',
                'threshold': threshold,
                'columns': high_missing,
                'count': len(high_missing)
            })
        
        return self
    
    def remove_duplicates(self) -> 'DataCleaner':
        """Supprime les lignes dupliquées"""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        duplicates_removed = initial_rows - len(self.df)
        
        if duplicates_removed > 0:
            self.cleaning_log.append({
                'operation': 'remove_duplicates',
                'rows_removed': duplicates_removed
            })
        
        return self
    
    def remove_constant_columns(self) -> 'DataCleaner':
        """Supprime les colonnes avec une seule valeur unique"""
        constant_cols = [
            col for col in self.df.columns 
            if self.df[col].nunique() == 1
        ]
        
        if constant_cols:
            self.df = self.df.drop(columns=constant_cols)
            self.cleaning_log.append({
                'operation': 'remove_constant_columns',
                'columns': constant_cols,
                'count': len(constant_cols)
            })
        
        return self
    
    def fill_missing_numeric(self, strategy: str = 'median') -> 'DataCleaner':
        """
        Remplit les valeurs manquantes dans les colonnes numériques
        
        Args:
            strategy: 'mean', 'median', ou 'zero'
        """
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        filled_cols = []
        
        for col in numeric_cols:
            if self.df[col].isnull().any():
                if strategy == 'mean':
                    fill_value = self.df[col].mean()
                elif strategy == 'median':
                    fill_value = self.df[col].median()
                elif strategy == 'zero':
                    fill_value = 0
                else:
                    continue
                
                self.df[col].fillna(fill_value, inplace=True)
                filled_cols.append(col)
        
        if filled_cols:
            self.cleaning_log.append({
                'operation': 'fill_missing_numeric',
                'strategy': strategy,
                'columns': filled_cols,
                'count': len(filled_cols)
            })
        
        return self
    
    def fill_missing_categorical(self, strategy: str = 'mode') -> 'DataCleaner':
        """
        Remplit les valeurs manquantes dans les colonnes catégorielles
        
        Args:
            strategy: 'mode' ou 'unknown'
        """
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        filled_cols = []
        
        for col in categorical_cols:
            if self.df[col].isnull().any():
                if strategy == 'mode':
                    mode_val = self.df[col].mode()
                    fill_value = mode_val[0] if len(mode_val) > 0 else 'Unknown'
                elif strategy == 'unknown':
                    fill_value = 'Unknown'
                else:
                    continue
                
                self.df[col].fillna(fill_value, inplace=True)
                filled_cols.append(col)
        
        if filled_cols:
            self.cleaning_log.append({
                'operation': 'fill_missing_categorical',
                'strategy': strategy,
                'columns': filled_cols,
                'count': len(filled_cols)
            })
        
        return self
    
    def standardize_column_names(self) -> 'DataCleaner':
        """Standardise les noms de colonnes (snake_case, pas d'espaces)"""
        old_names = list(self.df.columns)
        
        def clean_name(name):
            # Minuscules
            name = name.lower()
            # Remplacer espaces et caractères spéciaux par _
            name = re.sub(r'[^\w\s]', '_', name)
            name = re.sub(r'\s+', '_', name)
            # Supprimer underscores multiples
            name = re.sub(r'_+', '_', name)
            # Supprimer underscores début/fin
            name = name.strip('_')
            return name
        
        new_names = [clean_name(col) for col in self.df.columns]
        
        # Gérer les doublons
        seen = {}
        final_names = []
        for name in new_names:
            if name in seen:
                seen[name] += 1
                final_names.append(f"{name}_{seen[name]}")
            else:
                seen[name] = 0
                final_names.append(name)
        
        self.df.columns = final_names
        
        if old_names != final_names:
            self.cleaning_log.append({
                'operation': 'standardize_column_names',
                'renamed': dict(zip(old_names, final_names))
            })
        
        return self
    
    def convert_to_numeric(self, columns: List[str] = None) -> 'DataCleaner':
        """
        Convertit des colonnes en numérique
        
        Args:
            columns: Liste de colonnes à convertir (None = auto-détection)
        """
        if columns is None:
            # Auto-détection des colonnes convertibles
            columns = []
            for col in self.df.select_dtypes(include=['object']).columns:
                # Tester si convertible
                try:
                    pd.to_numeric(self.df[col], errors='coerce')
                    # Si >70% non-null après conversion, c'est OK
                    test_conv = pd.to_numeric(self.df[col], errors='coerce')
                    if test_conv.notna().sum() / len(self.df) > 0.7:
                        columns.append(col)
                except:
                    pass
        
        converted = []
        for col in columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    converted.append(col)
                except:
                    pass
        
        if converted:
            self.cleaning_log.append({
                'operation': 'convert_to_numeric',
                'columns': converted,
                'count': len(converted)
            })
        
        return self
    
    def convert_to_datetime(self, columns: List[str] = None) -> 'DataCleaner':
        """
        Convertit des colonnes en datetime
        
        Args:
            columns: Liste de colonnes à convertir (None = auto-détection)
        """
        if columns is None:
            # Auto-détection basée sur nom
            columns = [
                col for col in self.df.columns
                if any(kw in col.lower() for kw in ['date', 'dt', 'time', 'created', 'updated'])
            ]
        
        converted = []
        for col in columns:
            if col in self.df.columns and self.df[col].dtype == 'object':
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    converted.append(col)
                except:
                    pass
        
        if converted:
            self.cleaning_log.append({
                'operation': 'convert_to_datetime',
                'columns': converted,
                'count': len(converted)
            })
        
        return self
    
    def remove_whitespace(self) -> 'DataCleaner':
        """Supprime les espaces inutiles dans les colonnes texte"""
        text_cols = self.df.select_dtypes(include=['object']).columns
        cleaned_cols = []
        
        for col in text_cols:
            original = self.df[col].copy()
            self.df[col] = self.df[col].str.strip()
            
            if not self.df[col].equals(original):
                cleaned_cols.append(col)
        
        if cleaned_cols:
            self.cleaning_log.append({
                'operation': 'remove_whitespace',
                'columns': cleaned_cols,
                'count': len(cleaned_cols)
            })
        
        return self
    
    def auto_clean(self, aggressive: bool = False) -> 'DataCleaner':
        """
        Nettoyage automatique complet
        
        Args:
            aggressive: Si True, applique des transformations plus agressives
        """
        # Toujours faire
        self.remove_empty_columns()
        self.remove_duplicates()
        self.standardize_column_names()
        self.remove_whitespace()
        
        # Moyennement agressif
        self.remove_high_missing_columns(threshold=0.9)
        self.fill_missing_numeric(strategy='median')
        self.fill_missing_categorical(strategy='mode')
        
        if aggressive:
            # Plus agressif
            self.remove_high_missing_columns(threshold=0.5)
            self.remove_constant_columns()
            self.convert_to_numeric()
            self.convert_to_datetime()
        
        return self
    
    def get_cleaned_dataframe(self) -> pd.DataFrame:
        """Retourne le DataFrame nettoyé"""
        return self.df.copy()
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de nettoyage
        
        Returns:
            dict: Rapport détaillé
        """
        return {
            'source_file': self.source_filename,
            'original_shape': self.df_original.shape,
            'cleaned_shape': self.df.shape,
            'rows_removed': len(self.df_original) - len(self.df),
            'columns_removed': len(self.df_original.columns) - len(self.df.columns),
            'operations': self.cleaning_log,
            'cleaning_timestamp': datetime.now().isoformat()
        }
    
    def generate_cleaned_filename(self, suffix: str = "cleaned") -> str:
        """
        Génère un nom de fichier pour le dataset nettoyé
        
        Args:
            suffix: Suffixe à ajouter
            
        Returns:
            str: Nom de fichier
        """
        base_name = self.source_filename.replace('.csv', '').replace('.xlsx', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{base_name}_{suffix}_{timestamp}.csv"


def quick_clean(df: pd.DataFrame, filename: str = None, aggressive: bool = False) -> Tuple[pd.DataFrame, Dict]:
    """
    Fonction de nettoyage rapide
    
    Args:
        df: DataFrame à nettoyer
        filename: Nom du fichier source
        aggressive: Nettoyage agressif ?
        
    Returns:
        tuple: (DataFrame nettoyé, Rapport)
    """
    cleaner = DataCleaner(df, filename)
    cleaner.auto_clean(aggressive=aggressive)
    
    return cleaner.get_cleaned_dataframe(), cleaner.get_cleaning_report()