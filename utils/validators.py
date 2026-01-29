import re
import pandas as pd

def validate_email(email):
    """Valide le format d'un email"""
    if pd.isna(email) or email == "":
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))


def validate_phone_ci(phone):
    """Valide le format d'un numéro de téléphone ivoirien"""
    if pd.isna(phone) or phone == "":
        return False
    
    # Nettoyer le numéro
    phone_clean = str(phone).replace(' ', '').replace('-', '').replace('+', '')
    
    # Formats acceptés:
    # +225 XX XX XX XX XX (10 chiffres après 225)
    # 225XXXXXXXXXX
    # 0XXXXXXXXX (10 chiffres commençant par 0)
    # XXXXXXXXX (9 chiffres)
    
    patterns = [
        r'^225[0-9]{10}$',      # 225 + 10 chiffres
        r'^0[0-9]{9}$',         # 0 + 9 chiffres
        r'^[0-9]{10}$',         # 10 chiffres
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone_clean):
            return True
    
    return False


def detect_duplicates(df):
    """Détecte les lignes dupliquées"""
    duplicates = df[df.duplicated(keep=False)]
    n_duplicates = len(duplicates)
    duplicate_rows = duplicates.index.tolist()
    
    return {
        'count': n_duplicates,
        'rows': duplicate_rows,
        'data': duplicates
    }


def detect_missing_values(df):
    """Détecte les valeurs manquantes"""
    missing = df.isnull().sum()
    total_cells = len(df) * len(df.columns)
    total_missing = missing.sum()
    percentage = (total_missing / total_cells) * 100
    
    return {
        'total': int(total_missing),
        'percentage': round(percentage, 2),
        'by_column': missing.to_dict()
    }


def validate_dataframe(df):
    """Analyse complète d'un DataFrame"""
    results = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'duplicates': detect_duplicates(df),
        'missing_values': detect_missing_values(df)
    }
    
    # Détecter les colonnes email
    email_columns = [col for col in df.columns if 'mail' in col.lower()]
    if email_columns:
        results['emails'] = {}
        for col in email_columns:
            valid = df[col].apply(validate_email)
            results['emails'][col] = {
                'total': len(df),
                'valid': int(valid.sum()),
                'invalid': int((~valid).sum()),
                'invalid_rows': df[~valid].index.tolist()
            }
    
    # Détecter les colonnes téléphone
    phone_columns = [col for col in df.columns if any(word in col.lower() for word in ['phone', 'tel', 'telephone'])]
    if phone_columns:
        results['phones'] = {}
        for col in phone_columns:
            valid = df[col].apply(validate_phone_ci)
            results['phones'][col] = {
                'total': len(df),
                'valid': int(valid.sum()),
                'invalid': int((~valid).sum()),
                'invalid_rows': df[~valid].index.tolist()
            }
    
    # Calculer le score de qualité
    results['quality_score'] = calculate_quality_score(results, df)
    
    return results


def calculate_quality_score(results, df):
    """Calcule un score de qualité de 0 à 100"""
    score = 100
    total_rows = len(df)
    
    # Pénalités
    if total_rows > 0:
        # Doublons: -20 points max
        duplicate_penalty = min(20, (results['duplicates']['count'] / total_rows) * 100)
        score -= duplicate_penalty
        
        # Valeurs manquantes: -30 points max
        missing_penalty = min(30, results['missing_values']['percentage'])
        score -= missing_penalty
        
        # Emails invalides: -25 points max
        if 'emails' in results:
            for col, data in results['emails'].items():
                if data['total'] > 0:
                    invalid_rate = (data['invalid'] / data['total']) * 100
                    email_penalty = min(25, invalid_rate)
                    score -= email_penalty
                    break  # Pénalité sur la première colonne email seulement
        
        # Téléphones invalides: -25 points max
        if 'phones' in results:
            for col, data in results['phones'].items():
                if data['total'] > 0:
                    invalid_rate = (data['invalid'] / data['total']) * 100
                    phone_penalty = min(25, invalid_rate)
                    score -= phone_penalty
                    break  # Pénalité sur la première colonne téléphone seulement
    
    return max(0, round(score, 1))