import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class MetricsStore:
    """
    Stockage et historisation des métriques de qualité
    """
    
    def __init__(self, db_path: str = "data/metrics.db"):
        """Initialise la connexion à la base SQLite"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()
    
    def create_tables(self):
        """Crée les tables si elles n'existent pas"""
        cursor = self.conn.cursor()
        
        # Table des analyses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                global_score REAL,
                total_rows INTEGER,
                total_columns INTEGER,
                rule_results TEXT,
                scoring_details TEXT,
                recommendations TEXT
            )
        """)
        
        # Table des métriques par catégorie
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                category TEXT,
                score REAL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        """)
        
        self.conn.commit()
    
    def store_analysis(self, 
                      dataset_name: str,
                      df_shape: tuple,
                      rule_results: Dict,
                      scoring: Dict,
                      recommendations: List[Dict]) -> int:
        """
        Stocke une analyse complète
        
        Returns:
            int: ID de l'analyse créée
        """
        cursor = self.conn.cursor()
        
        total_rows, total_cols = df_shape
        
        cursor.execute("""
            INSERT INTO analyses 
            (dataset_name, timestamp, global_score, total_rows, total_columns, 
             rule_results, scoring_details, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_name,
            datetime.now().isoformat(),
            scoring['global_score'],
            total_rows,
            total_cols,
            json.dumps(rule_results),
            json.dumps(scoring),
            json.dumps(recommendations)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Stocker les scores par catégorie
        for category, score in scoring.get('category_scores', {}).items():
            cursor.execute("""
                INSERT INTO category_scores (analysis_id, category, score)
                VALUES (?, ?, ?)
            """, (analysis_id, category, score))
        
        self.conn.commit()
        return analysis_id
    
    def get_analysis_history(self, dataset_name: str, limit: int = 10) -> List[Dict]:
        """Récupère l'historique des analyses pour un dataset"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, global_score, total_rows, total_columns
            FROM analyses
            WHERE dataset_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (dataset_name, limit))
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'global_score': row[2],
                'total_rows': row[3],
                'total_columns': row[4]
            }
            for row in rows
        ]
    
    def get_score_evolution(self, dataset_name: str) -> List[Dict]:
        """Récupère l'évolution du score dans le temps"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, global_score
            FROM analyses
            WHERE dataset_name = ?
            ORDER BY timestamp ASC
        """, (dataset_name,))
        
        rows = cursor.fetchall()
        
        return [
            {'timestamp': row[0], 'score': row[1]}
            for row in rows
        ]
    
    def close(self):
        """Ferme la connexion"""
        self.conn.close()