import pandas as pd
import re

def detect_column_type(series, column_name):
    """
    Détecte automatiquement le type d'une colonne en analysant son contenu
    
    Args:
        series: Série pandas à analyser
        column_name: Nom de la colonne (pour info)
    
    Returns:
        str: 'email', 'phone', 'name', 'numeric', 'text', 'unknown'
    """
    # Ignorer les valeurs nulles
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return 'unknown'
    
    # Prendre un échantillon (max 100 valeurs pour la performance)
    sample_size = min(100, len(non_null))
    sample = non_null.head(sample_size)
    
    # Patterns de détection
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^[\+\d\s\-\(\)]{8,20}$'
    
    # Compteurs
    email_count = 0
    phone_count = 0
    numeric_count = 0
    alpha_only_count = 0
    
    for val in sample:
        val_str = str(val).strip()
        
        # Test Email
        if re.match(email_pattern, val_str):
            email_count += 1
            continue
        
        # Test Téléphone (doit contenir des chiffres)
        if re.match(phone_pattern, val_str) and any(c.isdigit() for c in val_str):
            # Vérifier qu'il y a au moins 8 chiffres
            digits = ''.join(c for c in val_str if c.isdigit())
            if len(digits) >= 8:
                phone_count += 1
                continue
        
        # Test Numérique pur
        try:
            float(str(val).replace(',', '.').replace(' ', ''))
            numeric_count += 1
            continue
        except:
            pass
        
        # Test Alphabétique (nom/prénom)
        if val_str.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            alpha_only_count += 1
    
    total = len(sample)
    
    # Seuil de détection : 70%
    threshold = 0.7
    
    # Déterminer le type (ordre d'importance)
    if email_count / total >= threshold:
        return 'email'
    elif phone_count / total >= threshold:
        return 'phone'
    elif alpha_only_count / total >= threshold:
        return 'name'
    elif numeric_count / total >= threshold:
        return 'numeric'
    else:
        return 'text'


def auto_detect_columns(df):
    """
    Détecte automatiquement les colonnes importantes dans un DataFrame
    en analysant leur CONTENU, pas leur nom
    
    Args:
        df: DataFrame pandas
    
    Returns:
        dict: {
            'email': [liste des colonnes email],
            'phone': [liste des colonnes téléphone],
            'name': [liste des colonnes nom],
            'all_types': {colonne: type, ...}
        }
    """
    detected = {
        'email': [],
        'phone': [],
        'name': [],
        'numeric': [],
        'text': [],
        'all_types': {}
    }
    
    # Analyser chaque colonne
    for col in df.columns:
        col_type = detect_column_type(df[col], col)
        detected['all_types'][col] = col_type
        
        # Ajouter à la catégorie appropriée
        if col_type in detected:
            detected[col_type].append(col)
    
    return detected


def get_detection_confidence(series, detected_type):
    """
    Calcule le niveau de confiance de la détection (0-100%)
    """
    non_null = series.dropna()
    if len(non_null) == 0:
        return 0
    
    sample = non_null.head(min(100, len(non_null)))
    matches = 0
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^[\+\d\s\-\(\)]{8,20}$'
    
    for val in sample:
        val_str = str(val).strip()
        
        if detected_type == 'email' and re.match(email_pattern, val_str):
            matches += 1
        elif detected_type == 'phone':
            if re.match(phone_pattern, val_str) and any(c.isdigit() for c in val_str):
                digits = ''.join(c for c in val_str if c.isdigit())
                if len(digits) >= 8:
                    matches += 1
    
    return round((matches / len(sample)) * 100, 1)