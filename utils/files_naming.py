# file_naming.py
"""
Module de nommage intelligent pour les fichiers générés
Basé sur le nom du fichier source (style Dataiku DSS)
"""

import os
import re
from datetime import datetime
from typing import Optional


class FileNamingManager:
    """Gestionnaire de nommage intelligent des fichiers"""
    
    def __init__(self, source_filename: str):
        """
        Initialise le gestionnaire
        
        Args:
            source_filename: Nom du fichier source (ex: "donnees_clients_2024.csv")
        """
        self.source_filename = source_filename
        self.base_name = self._extract_base_name(source_filename)
        self.extension = self._extract_extension(source_filename)
    
    def _extract_base_name(self, filename: str) -> str:
        """
        Extrait le nom de base sans extension
        
        Args:
            filename: Nom complet du fichier
            
        Returns:
            str: Nom de base
        """
        # Supprimer le chemin si présent
        filename = os.path.basename(filename)
        
        # Supprimer l'extension
        base = os.path.splitext(filename)[0]
        
        # Nettoyer le nom (supprimer caractères spéciaux)
        base = re.sub(r'[^\w\s-]', '_', base)
        base = re.sub(r'\s+', '_', base)
        base = re.sub(r'_+', '_', base)
        base = base.strip('_')
        
        return base.lower()
    
    def _extract_extension(self, filename: str) -> str:
        """Extrait l'extension du fichier"""
        return os.path.splitext(filename)[1].lower()
    
    def _add_timestamp(self, include_time: bool = True) -> str:
        """
        Génère un timestamp
        
        Args:
            include_time: Inclure l'heure
            
        Returns:
            str: Timestamp formaté
        """
        if include_time:
            return datetime.now().strftime('%Y%m%d_%H%M%S')
        else:
            return datetime.now().strftime('%Y%m%d')
    
    def generate_cleaned_filename(self, suffix: str = "cleaned") -> str:
        """
        Génère le nom pour le fichier nettoyé
        
        Exemple:
        - Input: "donnees_clients_2024.csv"
        - Output: "donnees_clients_2024_cleaned_20260130_151234.csv"
        
        Args:
            suffix: Suffixe à ajouter (default: "cleaned")
            
        Returns:
            str: Nom du fichier nettoyé
        """
        timestamp = self._add_timestamp()
        return f"{self.base_name}_{suffix}_{timestamp}.csv"
    
    def generate_report_filename(self, format: str = "pdf") -> str:
        """
        Génère le nom pour le rapport
        
        Exemple:
        - Input: "donnees_clients_2024.csv"
        - Output: "rapport_donnees_clients_2024_20260130_151234.pdf"
        
        Args:
            format: Format du rapport ('pdf', 'html', 'xlsx')
            
        Returns:
            str: Nom du fichier rapport
        """
        timestamp = self._add_timestamp()
        return f"rapport_{self.base_name}_{timestamp}.{format}"
    
    def generate_analysis_filename(self) -> str:
        """
        Génère le nom pour le fichier d'analyse JSON
        
        Returns:
            str: Nom du fichier analyse
        """
        timestamp = self._add_timestamp()
        return f"analyse_{self.base_name}_{timestamp}.json"
    
    def generate_sample_filename(self, n_rows: int = 1000) -> str:
        """
        Génère le nom pour un échantillon de données
        
        Args:
            n_rows: Nombre de lignes dans l'échantillon
            
        Returns:
            str: Nom du fichier échantillon
        """
        timestamp = self._add_timestamp(include_time=False)
        return f"{self.base_name}_sample_{n_rows}rows_{timestamp}.csv"
    
    def generate_profiling_filename(self) -> str:
        """
        Génère le nom pour le fichier de profiling
        
        Returns:
            str: Nom du fichier profiling
        """
        timestamp = self._add_timestamp()
        return f"profil_{self.base_name}_{timestamp}.html"
    
    def generate_backup_filename(self) -> str:
        """
        Génère le nom pour une sauvegarde du fichier original
        
        Returns:
            str: Nom du fichier backup
        """
        timestamp = self._add_timestamp()
        return f"{self.base_name}_backup_{timestamp}{self.extension}"
    
    @staticmethod
    def standardize_dataset_name(name: str) -> str:
        """
        Standardise un nom de dataset (style Dataiku)
        
        Règles:
        - Tout en minuscules
        - Remplacer espaces et caractères spéciaux par _
        - Pas de _ multiples
        - Pas de _ au début/fin
        
        Args:
            name: Nom à standardiser
            
        Returns:
            str: Nom standardisé
        """
        # Minuscules
        name = name.lower()
        
        # Remplacer caractères spéciaux et espaces
        name = re.sub(r'[^\w\s-]', '_', name)
        name = re.sub(r'\s+', '_', name)
        
        # Supprimer underscores multiples
        name = re.sub(r'_+', '_', name)
        
        # Supprimer underscores début/fin
        name = name.strip('_')
        
        # Limiter longueur
        if len(name) > 50:
            name = name[:50]
        
        return name
    
    def get_all_filenames(self) -> dict:
        """
        Retourne tous les noms de fichiers générés
        
        Returns:
            dict: Dictionnaire avec tous les noms
        """
        return {
            'source': self.source_filename,
            'base_name': self.base_name,
            'cleaned': self.generate_cleaned_filename(),
            'report_pdf': self.generate_report_filename('pdf'),
            'report_html': self.generate_report_filename('html'),
            'analysis_json': self.generate_analysis_filename(),
            'sample_1000': self.generate_sample_filename(1000),
            'profiling': self.generate_profiling_filename(),
            'backup': self.generate_backup_filename()
        }


def create_naming_manager(filename: str) -> FileNamingManager:
    """
    Fonction helper pour créer un gestionnaire de nommage
    
    Args:
        filename: Nom du fichier source
        
    Returns:
        FileNamingManager: Instance du gestionnaire
    """
    return FileNamingManager(filename)


# Exemples d'utilisation
if __name__ == "__main__":
    # Test
    test_files = [
        "donnees_clients_2024.csv",
        "Transactions Janvier 2024.xlsx",
        "base-produits (copie).csv",
        "DATA_EXPORT_20240115.csv"
    ]
    
    for file in test_files:
        manager = FileNamingManager(file)
        print(f"\n📁 Fichier source: {file}")
        print(f"   Base name: {manager.base_name}")
        print(f"   Cleaned: {manager.generate_cleaned_filename()}")
        print(f"   Report: {manager.generate_report_filename()}")
        print(f"   Analysis: {manager.generate_analysis_filename()}")