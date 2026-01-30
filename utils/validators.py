# validators.py
"""
Validateurs sémantiques pour DataTchek
Focus sur la cohérence type de données vs nom de colonne (style Dataiku DSS)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .column_detector import analyze_columns


def detect_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Détecte les doublons dans le DataFrame
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Informations sur les doublons
    """
    duplicates = df[df.duplicated(keep=False)]
    
    # Identifier les colonnes clés potentielles (ID, code, etc.)
    key_columns = [col for col in df.columns 
                   if any(kw in col.lower() for kw in ['id', 'code', 'key', 'ref'])]
    
    # Doublons sur clés spécifiques
    duplicates_by_key = {}
    for col in key_columns:
        dup_on_col = df[df.duplicated(subset=[col], keep=False)]
        if len(dup_on_col) > 0:
            duplicates_by_key[col] = {
                'count': len(dup_on_col),
                'sample': dup_on_col.head(5)
            }
    
    return {
        "count": len(duplicates),
        "percentage": round((len(duplicates) / len(df)) * 100, 2) if len(df) > 0 else 0,
        "rows": duplicates.index.tolist()[:100],  # Limiter à 100
        "data": duplicates.head(100),  # Limiter à 100 lignes
        "by_key": duplicates_by_key
    }


def detect_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Détecte les valeurs manquantes avec analyse détaillée
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Statistiques sur les valeurs manquantes
    """
    missing = df.isnull().sum()
    total_cells = len(df) * len(df.columns)
    total_missing = missing.sum()
    
    # Colonnes avec le plus de valeurs manquantes
    missing_sorted = missing[missing > 0].sort_values(ascending=False)
    
    # Pourcentage par colonne
    missing_percentage = {}
    for col in missing_sorted.index:
        pct = (missing[col] / len(df)) * 100
        missing_percentage[col] = round(pct, 2)
    
    return {
        "total": int(total_missing),
        "percentage": round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0,
        "by_column": missing.to_dict(),
        "by_column_percentage": missing_percentage,
        "columns_most_missing": list(missing_sorted.head(10).index)
    }


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyse complète de la qualité des données (style Dataiku DSS)
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Métriques de qualité
    """
    quality_metrics = {}
    
    for col in df.columns:
        col_data = df[col]
        non_null = col_data.dropna()
        
        metrics = {
            'total_count': len(col_data),
            'non_null_count': len(non_null),
            'null_count': int(col_data.isnull().sum()),
            'null_percentage': round((col_data.isnull().sum() / len(col_data)) * 100, 2) if len(col_data) > 0 else 0,
            'unique_count': int(col_data.nunique()),
            'unique_percentage': round((col_data.nunique() / len(col_data)) * 100, 2) if len(col_data) > 0 else 0,
        }
        
        # Pour colonnes numériques
        if pd.api.types.is_numeric_dtype(col_data):
            metrics.update({
                'min': float(non_null.min()) if len(non_null) > 0 else None,
                'max': float(non_null.max()) if len(non_null) > 0 else None,
                'mean': float(non_null.mean()) if len(non_null) > 0 else None,
                'median': float(non_null.median()) if len(non_null) > 0 else None,
                'std': float(non_null.std()) if len(non_null) > 0 else None,
            })
        
        # Pour colonnes texte
        elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
            if len(non_null) > 0:
                lengths = non_null.astype(str).str.len()
                metrics.update({
                    'min_length': int(lengths.min()),
                    'max_length': int(lengths.max()),
                    'avg_length': round(float(lengths.mean()), 2),
                    'most_common': non_null.value_counts().head(5).to_dict()
                })
        
        quality_metrics[col] = metrics
    
    return quality_metrics


def validate_dataframe(df: pd.DataFrame, filename: str = None) -> Dict[str, Any]:
    """
    Analyse complète de qualité d'un DataFrame (style Dataiku DSS)
    
    Args:
        df: DataFrame à analyser
        filename: Nom du fichier original (pour nommage sorties)
        
    Returns:
        dict: Résultats complets de l'analyse
    """
    # Analyse sémantique des colonnes (type attendu vs type réel)
    semantic = analyze_columns(df)
    
    # Doublons
    duplicates = detect_duplicates(df)
    
    # Valeurs manquantes
    missing_values = detect_missing_values(df)
    
    # Métriques de qualité par colonne
    quality_metrics = analyze_data_quality(df)
    
    results = {
        "filename": filename or "unknown",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "duplicates": duplicates,
        "missing_values": missing_values,
        "semantic_validation": semantic,
        "quality_metrics": quality_metrics
    }
    
    # Calcul du score de qualité global
    results["quality_score"] = calculate_quality_score(results)
    
    return results


def calculate_quality_score(results: Dict[str, Any]) -> float:
    """
    Calcule un score de qualité global (0-100)
    Basé sur plusieurs dimensions comme Dataiku DSS
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        float: Score de 0 à 100
    """
    score = 100.0
    
    # 1. Pénalité pour doublons (max -15 points)
    duplicate_pct = results["duplicates"]["percentage"]
    duplicate_penalty = min(15, duplicate_pct * 1.5)
    score -= duplicate_penalty
    
    # 2. Pénalité pour valeurs manquantes (max -25 points)
    missing_pct = results["missing_values"]["percentage"]
    missing_penalty = min(25, missing_pct * 1.2)
    score -= missing_penalty
    
    # 3. Pénalité pour incohérence sémantique (max -35 points)
    semantic_penalty = 0
    total_cols = len(results["semantic_validation"])
    
    if total_cols > 0:
        for col, data in results["semantic_validation"].items():
            conformity = data["conformity_rate"]
            
            # Pénalité progressive selon conformité
            if conformity < 50:
                semantic_penalty += 3  # Grave
            elif conformity < 70:
                semantic_penalty += 2  # Moyen
            elif conformity < 90:
                semantic_penalty += 1  # Léger
        
        semantic_penalty = min(35, semantic_penalty)
    
    score -= semantic_penalty
    
    # 4. Pénalité pour faible cardinalité sur colonnes clés (max -10 points)
    cardinality_penalty = 0
    for col, metrics in results["quality_metrics"].items():
        # Si colonne contient "id" ou "code" dans le nom
        if any(kw in col.lower() for kw in ['id', 'code', 'key']):
            # Et que la cardinalité est trop faible
            if metrics['unique_percentage'] < 80:
                cardinality_penalty += 2
    
    score -= min(10, cardinality_penalty)
    
    # 5. Bonus pour bonne qualité globale (+10 points max)
    if duplicate_pct == 0 and missing_pct < 5:
        score += min(10, 10 - missing_pct)
    
    return max(0.0, min(100.0, round(score, 1)))


def generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """
    Génère des recommandations actionnables basées sur l'analyse
    Style Dataiku DSS : recommandations priorisées et claires
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        list: Liste de recommandations priorisées
    """
    recommendations = []
    
    # --- PRIORITÉ HAUTE ---
    
    # 1. Doublons critiques
    if results["duplicates"]["percentage"] > 10:
        recommendations.append({
            "priority": "HAUTE",
            "category": "Doublons",
            "message": f"⚠️ {results['duplicates']['count']} doublons détectés ({results['duplicates']['percentage']}% des données)",
            "action": "Supprimer ou fusionner les lignes dupliquées"
        })
    
    # 2. Valeurs manquantes critiques
    for col, pct in results["missing_values"]["by_column_percentage"].items():
        if pct > 50:
            recommendations.append({
                "priority": "HAUTE",
                "category": "Données manquantes",
                "message": f"⚠️ Colonne '{col}' : {pct}% de valeurs manquantes",
                "action": f"Supprimer la colonne ou imputer les valeurs manquantes"
            })
    
    # 3. Incohérences sémantiques graves
    for col, data in results["semantic_validation"].items():
        if data["conformity_rate"] < 50:
            recommendations.append({
                "priority": "HAUTE",
                "category": "Cohérence sémantique",
                "message": f"⚠️ Colonne '{col}' : Type '{data['actual_type']}' ne correspond pas au type attendu '{data['expected_type']}'",
                "action": f"Vérifier le contenu de la colonne et corriger les {data['invalid_count']} valeurs incohérentes"
            })
    
    # --- PRIORITÉ MOYENNE ---
    
    # 4. Valeurs manquantes modérées
    for col, pct in results["missing_values"]["by_column_percentage"].items():
        if 20 < pct <= 50:
            recommendations.append({
                "priority": "MOYENNE",
                "category": "Données manquantes",
                "message": f"⚡ Colonne '{col}' : {pct}% de valeurs manquantes",
                "action": "Analyser la raison et imputer si nécessaire"
            })
    
    # 5. Incohérences sémantiques modérées
    for col, data in results["semantic_validation"].items():
        if 50 <= data["conformity_rate"] < 80:
            recommendations.append({
                "priority": "MOYENNE",
                "category": "Cohérence sémantique",
                "message": f"⚡ Colonne '{col}' : Conformité {data['conformity_rate']}%",
                "action": f"Vérifier et nettoyer les {data['invalid_count']} valeurs suspectes"
            })
    
    # 6. Faible cardinalité sur colonnes clés
    for col, metrics in results["quality_metrics"].items():
        if any(kw in col.lower() for kw in ['id', 'code', 'key']):
            if metrics['unique_percentage'] < 80:
                recommendations.append({
                    "priority": "MOYENNE",
                    "category": "Cardinalité",
                    "message": f"⚡ Colonne '{col}' : Seulement {metrics['unique_percentage']}% de valeurs uniques",
                    "action": "Vérifier si cette colonne est vraiment une clé unique"
                })
    
    # --- PRIORITÉ BASSE ---
    
    # 7. Optimisations possibles
    for col, metrics in results["quality_metrics"].items():
        if metrics['unique_percentage'] < 5:
            recommendations.append({
                "priority": "BASSE",
                "category": "Optimisation",
                "message": f"ℹ️ Colonne '{col}' : Très faible diversité ({metrics['unique_count']} valeurs uniques)",
                "action": "Envisager de convertir en type catégoriel pour optimiser la mémoire"
            })
    
    # Limiter à 20 recommandations et trier par priorité
    priority_order = {"HAUTE": 0, "MOYENNE": 1, "BASSE": 2}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])
    
    return recommendations[:20]


def prepare_cleaned_dataframe(df: pd.DataFrame, results: Dict[str, Any], 
                               remove_duplicates: bool = True,
                               drop_high_missing_cols: bool = True,
                               missing_threshold: float = 70.0) -> pd.DataFrame:
    """
    Prépare un DataFrame nettoyé basé sur l'analyse
    
    Args:
        df: DataFrame original
        results: Résultats de l'analyse
        remove_duplicates: Supprimer les doublons
        drop_high_missing_cols: Supprimer colonnes avec trop de manquants
        missing_threshold: Seuil (%) pour supprimer une colonne
        
    Returns:
        DataFrame nettoyé
    """
    df_cleaned = df.copy()
    
    changes_log = []
    
    # 1. Supprimer les doublons
    if remove_duplicates and results["duplicates"]["count"] > 0:
        initial_rows = len(df_cleaned)
        df_cleaned = df_cleaned.drop_duplicates()
        removed = initial_rows - len(df_cleaned)
        changes_log.append(f"✓ {removed} doublons supprimés")
    
    # 2. Supprimer colonnes avec trop de valeurs manquantes
    if drop_high_missing_cols:
        cols_to_drop = []
        for col, pct in results["missing_values"]["by_column_percentage"].items():
            if pct >= missing_threshold:
                cols_to_drop.append(col)
        
        if cols_to_drop:
            df_cleaned = df_cleaned.drop(columns=cols_to_drop)
            changes_log.append(f"✓ {len(cols_to_drop)} colonnes supprimées (>{missing_threshold}% manquant)")
    
    # Log des changements
    df_cleaned.attrs['cleaning_log'] = changes_log
    
    return df_cleaned