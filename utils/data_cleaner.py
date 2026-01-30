import pandas as pd
import re

def clean_email(email):
    """Nettoie et valide un email"""
    if pd.isna(email) or email == "":
        return email
    
    email_str = str(email).strip().lower()
    
    # Pattern email basique
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email_str):
        return email_str
    else:
        return email  # Retourner tel quel si invalide (pour que l'utilisateur décide)


def clean_phone_ci(phone):
    """Nettoie et standardise un numéro de téléphone ivoirien"""
    if pd.isna(phone) or phone == "":
        return phone
    
    # Nettoyer : garder que les chiffres et le +
    phone_str = str(phone).strip()
    digits = ''.join(c for c in phone_str if c.isdigit())
    
    # Si commence par 225, enlever
    if digits.startswith('225'):
        digits = digits[3:]
    
    # Si commence par 0, enlever
    if digits.startswith('0'):
        digits = digits[1:]
    
    # Doit avoir 9 ou 10 chiffres
    if len(digits) in [9, 10]:
        # Format standard : +225 XX XX XX XX XX
        return f"+225 {digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:]}"
    else:
        return phone  # Retourner tel quel si invalide


def remove_duplicates(df):
    """
    Supprime les lignes dupliquées
    
    Returns:
        tuple: (df_nettoyé, nombre_supprimés)
    """
    original_count = len(df)
    df_clean = df.drop_duplicates()
    removed_count = original_count - len(df_clean)
    
    return df_clean, removed_count


def clean_dataframe(df, detected_columns=None, remove_dupes=True, clean_emails=True, clean_phones=True):
    """
    Nettoie un DataFrame complet
    
    Args:
        df: DataFrame à nettoyer
        detected_columns: Dict des colonnes détectées (email, phone, etc.)
        remove_dupes: Supprimer les doublons
        clean_emails: Nettoyer les emails
        clean_phones: Nettoyer les téléphones
    
    Returns:
        tuple: (df_nettoyé, stats_nettoyage)
    """
    df_clean = df.copy()
    stats = {
        'duplicates_removed': 0,
        'emails_cleaned': 0,
        'phones_cleaned': 0,
        'original_rows': len(df),
        'final_rows': 0
    }
    
    # Supprimer les doublons
    if remove_dupes:
        df_clean, stats['duplicates_removed'] = remove_duplicates(df_clean)
    
    # Nettoyer les emails
    if clean_emails and detected_columns and 'email' in detected_columns:
        for col in detected_columns['email']:
            if col in df_clean.columns:
                original = df_clean[col].copy()
                df_clean[col] = df_clean[col].apply(clean_email)
                stats['emails_cleaned'] += (original != df_clean[col]).sum()
    
    # Nettoyer les téléphones
    if clean_phones and detected_columns and 'phone' in detected_columns:
        for col in detected_columns['phone']:
            if col in df_clean.columns:
                original = df_clean[col].copy()
                df_clean[col] = df_clean[col].apply(clean_phone_ci)
                stats['phones_cleaned'] += (original != df_clean[col]).sum()
    
    stats['final_rows'] = len(df_clean)
    
    return df_clean, stats


def get_cleaning_preview(df, detected_columns, sample_size=5):
    """
    Génère un aperçu des modifications qui seront faites
    
    Returns:
        dict: Exemples de nettoyage par type
    """
    preview = {
        'emails': [],
        'phones': []
    }
    
    # Aperçu emails
    if detected_columns and 'email' in detected_columns:
        for col in detected_columns['email']:
            if col in df.columns:
                sample = df[col].dropna().head(sample_size)
                for original in sample:
                    cleaned = clean_email(original)
                    if str(original) != str(cleaned):
                        preview['emails'].append({
                            'original': str(original),
                            'cleaned': str(cleaned),
                            'column': col
                        })
    
    # Aperçu téléphones
    if detected_columns and 'phone' in detected_columns:
        for col in detected_columns['phone']:
            if col in df.columns:
                sample = df[col].dropna().head(sample_size)
                for original in sample:
                    cleaned = clean_phone_ci(original)
                    if str(original) != str(cleaned):
                        preview['phones'].append({
                            'original': str(original),
                            'cleaned': str(cleaned),
                            'column': col
                        })
    
    return preview