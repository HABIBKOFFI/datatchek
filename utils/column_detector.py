# column_detector.py
"""
Détecteur de types de colonnes intelligent
Analyse sémantique basée sur le nom et le contenu
"""

import pandas as pd
import re
from typing import Dict, Any


# Règles sémantiques basées sur les noms de colonnes
SEMANTIC_RULES = {
    "numeric": [
        "age", "montant", "prix", "price", "total", "score", 
        "quantite", "quantity", "nombre", "amount", "cout", "cost",
        "valeur", "value", "taux", "rate"
    ],
    "date": [
        "date", "dt", "naissance", "birth", "created", "updated",
        "modified", "expiration", "debut", "fin", "start", "end"
    ],
    "boolean": [
        "is_", "has_", "flag", "actif", "active", "enabled", 
        "valide", "valid", "confirm"
    ],
    "categorical": [
        "type", "statut", "status", "niveau", "level", "category",
        "categorie", "classe", "class", "genre", "sexe", "gender"
    ],
    "identifier": [
        "id", "code", "ref", "reference", "key", "uuid"
    ],
    "name": [
        "nom", "name", "prenom", "firstname", "lastname",
        "label", "title", "designation"
    ]
}


def infer_expected_type(column_name: str) -> str:
    """
    Infère le type attendu basé sur le nom de la colonne
    
    Args:
        column_name: Nom de la colonne
        
    Returns:
        str: Type attendu (numeric, date, boolean, categorical, identifier, name, text)
    """
    name_lower = column_name.lower()
    
    # Parcourir les règles sémantiques
    for expected_type, keywords in SEMANTIC_RULES.items():
        for keyword in keywords:
            if keyword in name_lower:
                return expected_type
    
    return "text"


def is_numeric(value: Any) -> bool:
    """
    Vérifie si une valeur peut être convertie en numérique
    
    Args:
        value: Valeur à tester
        
    Returns:
        bool: True si numérique
    """
    if pd.isna(value):
        return False
    
    try:
        # Nettoyage des espaces et virgules
        str_val = str(value).replace(",", ".").replace(" ", "").strip()
        float(str_val)
        return True
    except (ValueError, TypeError):
        return False


def is_date(value: Any) -> bool:
    """
    Vérifie si une valeur est une date
    
    Args:
        value: Valeur à tester
        
    Returns:
        bool: True si date
    """
    if pd.isna(value):
        return False
    
    try:
        pd.to_datetime(value, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def is_boolean(value: Any) -> bool:
    """
    Vérifie si une valeur est booléenne
    
    Args:
        value: Valeur à tester
        
    Returns:
        bool: True si booléen
    """
    if pd.isna(value):
        return False
    
    str_val = str(value).lower().strip()
    boolean_values = [
        "true", "false", "yes", "no", "oui", "non",
        "1", "0", "t", "f", "y", "n", "vrai", "faux"
    ]
    
    return str_val in boolean_values


def is_identifier(value: Any) -> bool:
    """
    Vérifie si une valeur ressemble à un identifiant
    
    Args:
        value: Valeur à tester
        
    Returns:
        bool: True si identifiant
    """
    if pd.isna(value):
        return False
    
    str_val = str(value).strip()
    
    # Patterns d'identifiants
    patterns = [
        r'^[A-Z0-9\-_]{5,}$',  # ID alphanumérique
        r'^\d{5,}$',            # ID numérique long
        r'^[0-9a-f]{8}-[0-9a-f]{4}',  # UUID
    ]
    
    return any(re.match(pattern, str_val, re.IGNORECASE) for pattern in patterns)


def detect_actual_type(series: pd.Series) -> str:
    """
    Détecte le type réel d'une série de données
    
    Args:
        series: Série pandas à analyser
        
    Returns:
        str: Type détecté
    """
    # Supprimer les valeurs nulles
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return "empty"
    
    # Échantillon pour performance (max 1000 valeurs)
    sample_size = min(1000, len(non_null))
    sample = non_null.sample(n=sample_size, random_state=42) if len(non_null) > sample_size else non_null
    
    # Compteurs
    counters = {
        'numeric': 0,
        'date': 0,
        'boolean': 0,
        'identifier': 0
    }
    
    # Analyse de chaque valeur
    for val in sample:
        if is_numeric(val):
            counters['numeric'] += 1
        if is_date(val):
            counters['date'] += 1
        if is_boolean(val):
            counters['boolean'] += 1
        if is_identifier(val):
            counters['identifier'] += 1
    
    total = len(sample)
    threshold = 0.7  # 70% des valeurs doivent correspondre
    
    # Déterminer le type principal
    for type_name, count in counters.items():
        if count / total >= threshold:
            return type_name
    
    # Si aucun type dominant, vérifier si catégorique
    unique_ratio = sample.nunique() / total
    
    if unique_ratio < 0.3:  # Moins de 30% de valeurs uniques
        return "categorical"
    
    # Si aucun pattern clair, vérifier la longueur moyenne
    avg_length = sample.astype(str).str.len().mean()
    
    if avg_length > 50:
        return "text_long"
    
    return "text"


def calculate_conformity_rate(series: pd.Series, expected_type: str, actual_type: str) -> float:
    """
    Calcule le taux de conformité entre type attendu et type réel
    
    Args:
        series: Série à analyser
        expected_type: Type attendu
        actual_type: Type réel détecté
        
    Returns:
        float: Taux de conformité (0-100)
    """
    # Si les types correspondent exactement
    if expected_type == actual_type:
        return 100.0
    
    # Correspondances acceptables
    compatible_types = {
        'numeric': ['numeric', 'identifier'],
        'date': ['date', 'text'],
        'boolean': ['boolean', 'categorical'],
        'categorical': ['categorical', 'text'],
        'identifier': ['identifier', 'numeric', 'text'],
        'name': ['text', 'text_long'],
        'text': ['text', 'text_long', 'categorical']
    }
    
    if actual_type in compatible_types.get(expected_type, []):
        return 85.0  # Conformité partielle
    
    # Calcul basé sur les valeurs réelles
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return 0.0
    
    # Échantillon
    sample_size = min(500, len(non_null))
    sample = non_null.sample(n=sample_size, random_state=42) if len(non_null) > sample_size else non_null
    
    # Validation selon type attendu
    validation_func = {
        'numeric': is_numeric,
        'date': is_date,
        'boolean': is_boolean,
        'identifier': is_identifier
    }.get(expected_type)
    
    if validation_func:
        valid_count = sum(validation_func(val) for val in sample)
        return round((valid_count / len(sample)) * 100, 1)
    
    # Pour les autres types, conformité basique
    return 50.0


def analyze_columns(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Analyse toutes les colonnes d'un DataFrame
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Analyse par colonne
    """
    analysis = {}
    
    for col in df.columns:
        # Type attendu basé sur le nom
        expected = infer_expected_type(col)
        
        # Type réel basé sur le contenu
        actual = detect_actual_type(df[col])
        
        # Taux de conformité
        conformity = calculate_conformity_rate(df[col], expected, actual)
        
        # Nombre de valeurs invalides
        non_null = df[col].dropna()
        if len(non_null) > 0:
            invalid_count = int(len(non_null) * (1 - conformity / 100))
        else:
            invalid_count = 0
        
        analysis[col] = {
            "expected_type": expected,
            "actual_type": actual,
            "conformity_rate": conformity,
            "invalid_count": invalid_count,
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).tolist() if len(df[col].dropna()) > 0 else []
        }
    
    return analysis


def detect_column_patterns(df: pd.DataFrame) -> Dict[str, list]:
    """
    Détecte les patterns de colonnes (noms, téléphones, emails, etc.)
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Colonnes groupées par pattern
    """
    patterns = {
        'identifiers': [],
        'names': [],
        'phones': [],
        'emails': [],
        'dates': [],
        'amounts': [],
        'categories': []
    }
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Identifiants
        if any(kw in col_lower for kw in ['id', 'code', 'ref', 'key']):
            patterns['identifiers'].append(col)
        
        # Noms
        if any(kw in col_lower for kw in ['nom', 'name', 'prenom', 'firstname', 'lastname']):
            patterns['names'].append(col)
        
        # Téléphones
        if any(kw in col_lower for kw in ['tel', 'phone', 'mobile', 'contact']):
            patterns['phones'].append(col)
        
        # Emails
        if any(kw in col_lower for kw in ['email', 'mail', 'courriel']):
            patterns['emails'].append(col)
        
        # Dates
        if any(kw in col_lower for kw in ['date', 'dt', 'created', 'updated', 'naissance']):
            patterns['dates'].append(col)
        
        # Montants
        if any(kw in col_lower for kw in ['montant', 'prix', 'price', 'amount', 'total', 'cout']):
            patterns['amounts'].append(col)
        
        # Catégories
        if any(kw in col_lower for kw in ['type', 'statut', 'status', 'category', 'niveau']):
            patterns['categories'].append(col)
    
    # Supprimer les listes vides
    return {k: v for k, v in patterns.items() if v}