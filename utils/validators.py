# validators.py
"""
Validateurs robustes pour DataTchek
Inclut validateurs spécifiques Côte d'Ivoire
"""

import pandas as pd
import re
from typing import Dict, Any, List
from .column_detector import analyze_columns


class CIValidators:
    """Validateurs spécifiques Côte d'Ivoire"""
    
    @staticmethod
    def validate_phone_ci(phone: Any) -> bool:
        """
        Valide les numéros de téléphone ivoiriens
        
        Formats acceptés :
        - +225 XX XX XX XX XX (10 chiffres après +225)
        - +225XXXXXXXXXX
        - 07 12 34 56 78 (format local)
        - 0712345678 (format local sans espaces)
        - 225XXXXXXXXXX (sans +)
        
        Returns:
            bool: True si valide, False sinon
        """
        if pd.isna(phone):
            return False
        
        # Conversion en string et nettoyage
        phone_str = str(phone).strip()
        
        # Si vide après nettoyage
        if not phone_str or phone_str == '' or phone_str == 'nan':
            return False
        
        # Suppression de tous les espaces, tirets, parenthèses
        phone_clean = re.sub(r'[\s\-\(\)\.]', '', phone_str)
        
        # Patterns valides pour CI
        patterns = [
            r'^\+225\d{10}$',           # +225XXXXXXXXXX
            r'^225\d{10}$',              # 225XXXXXXXXXX (sans +)
            r'^\d{10}$',                 # XXXXXXXXXX (10 chiffres)
            r'^0[0-9]{9}$',              # 0XXXXXXXXX (commence par 0)
        ]
        
        # Test de tous les patterns
        for pattern in patterns:
            if re.match(pattern, phone_clean):
                # Validation supplémentaire : préfixes valides CI
                # En CI, les mobiles commencent par 01, 05, 07, etc.
                if phone_clean.startswith('+225'):
                    first_digits = phone_clean[4:6]
                elif phone_clean.startswith('225'):
                    first_digits = phone_clean[3:5]
                elif len(phone_clean) == 10:
                    first_digits = phone_clean[0:2]
                else:
                    return False
                
                # Préfixes mobiles valides CI (liste non exhaustive)
                valid_prefixes = ['01', '02', '03', '05', '07', '08', '09']
                if first_digits in valid_prefixes:
                    return True
        
        return False
    
    @staticmethod
    def validate_email(email: Any) -> bool:
        """
        Valide les adresses email
        
        Returns:
            bool: True si valide, False sinon
        """
        if pd.isna(email):
            return False
        
        email_str = str(email).strip().lower()
        
        if not email_str or email_str == 'nan':
            return False
        
        # Regex email standard
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_str))
    
    @staticmethod
    def validate_bank_account_bceao(account: Any) -> bool:
        """
        Valide les comptes bancaires BCEAO (format IBAN CI)
        Format: CI + 2 chiffres + 1 lettre + 23 chiffres
        Exemple: CI93A12345678901234567890
        
        Returns:
            bool: True si valide, False sinon
        """
        if pd.isna(account):
            return False
        
        account_str = str(account).strip().upper().replace(' ', '')
        
        if not account_str or account_str == 'NAN':
            return False
        
        pattern = r'^CI\d{2}[A-Z]\d{23}$'
        return bool(re.match(pattern, account_str))
    
    @staticmethod
    def validate_currency_fcfa(value: Any) -> bool:
        """
        Vérifie si la devise est FCFA/XOF
        
        Returns:
            bool: True si FCFA/XOF, False sinon
        """
        if pd.isna(value):
            return False
        
        value_str = str(value).strip().upper()
        
        if not value_str or value_str == 'NAN':
            return False
        
        valid_currencies = ['FCFA', 'XOF', 'F CFA', 'CFA']
        return value_str in valid_currencies


def detect_column_type(column_name: str) -> str:
    """
    Détecte le type de colonne basé sur son nom
    
    Args:
        column_name: Nom de la colonne
        
    Returns:
        str: Type détecté (phone, email, name, etc.)
    """
    name = column_name.lower()
    
    # Téléphones
    phone_keywords = ['tel', 'phone', 'mobile', 'numero', 'contact', 'gsm']
    if any(keyword in name for keyword in phone_keywords):
        return 'phone'
    
    # Emails
    if 'email' in name or 'mail' in name or 'courriel' in name:
        return 'email'
    
    # Noms
    name_keywords = ['nom', 'name', 'prenom', 'firstname', 'lastname']
    if any(keyword in name for keyword in name_keywords):
        return 'name'
    
    # Comptes bancaires
    account_keywords = ['compte', 'account', 'iban', 'rib']
    if any(keyword in name for keyword in account_keywords):
        return 'bank_account'
    
    # Devise
    if 'devise' in name or 'currency' in name or 'monnaie' in name:
        return 'currency'
    
    return 'unknown'


def validate_column_data(df: pd.DataFrame, column: str, column_type: str) -> Dict[str, Any]:
    """
    Valide les données d'une colonne selon son type
    
    Args:
        df: DataFrame
        column: Nom de la colonne
        column_type: Type de la colonne
        
    Returns:
        dict: Résultats de validation
    """
    if column not in df.columns:
        return {
            'valid_count': 0,
            'invalid_count': 0,
            'validity_rate': 0,
            'invalid_samples': []
        }
    
    series = df[column].dropna()
    
    if len(series) == 0:
        return {
            'valid_count': 0,
            'invalid_count': 0,
            'validity_rate': 100,
            'invalid_samples': []
        }
    
    # Sélection du validateur approprié
    if column_type == 'phone':
        validator = CIValidators.validate_phone_ci
    elif column_type == 'email':
        validator = CIValidators.validate_email
    elif column_type == 'bank_account':
        validator = CIValidators.validate_bank_account_bceao
    elif column_type == 'currency':
        validator = CIValidators.validate_currency_fcfa
    else:
        # Pas de validation spécifique
        return {
            'valid_count': len(series),
            'invalid_count': 0,
            'validity_rate': 100,
            'invalid_samples': []
        }
    
    # Validation
    validation_results = series.apply(validator)
    valid_count = validation_results.sum()
    invalid_count = len(series) - valid_count
    
    # Échantillon des invalides (max 5)
    invalid_indices = series[~validation_results].index[:5]
    invalid_samples = series[invalid_indices].tolist()
    
    validity_rate = round((valid_count / len(series)) * 100, 1) if len(series) > 0 else 0
    
    return {
        'valid_count': int(valid_count),
        'invalid_count': int(invalid_count),
        'validity_rate': validity_rate,
        'invalid_samples': invalid_samples
    }


def detect_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Détecte les doublons dans le DataFrame
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Informations sur les doublons
    """
    duplicates = df[df.duplicated(keep=False)]
    
    return {
        "count": len(duplicates),
        "rows": duplicates.index.tolist(),
        "data": duplicates
    }


def detect_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Détecte les valeurs manquantes
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Statistiques sur les valeurs manquantes
    """
    missing = df.isnull().sum()
    total_cells = len(df) * len(df.columns)
    total_missing = missing.sum()
    
    return {
        "total": int(total_missing),
        "percentage": round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0,
        "by_column": missing.to_dict()
    }


def validate_specific_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valide les colonnes spécifiques (téléphones, emails, etc.)
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Résultats de validation par colonne
    """
    results = {}
    
    for column in df.columns:
        column_type = detect_column_type(column)
        
        if column_type != 'unknown':
            validation = validate_column_data(df, column, column_type)
            
            # N'inclure que si des invalides détectés
            if validation['invalid_count'] > 0:
                results[column] = {
                    'type': column_type,
                    'validation': validation
                }
    
    return results


def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyse complète de qualité d'un DataFrame
    
    Args:
        df: DataFrame à analyser
        
    Returns:
        dict: Résultats complets de l'analyse
    """
    # Analyse sémantique des colonnes
    semantic = analyze_columns(df)
    
    # Validation spécifique (téléphones, emails, etc.)
    specific_validation = validate_specific_columns(df)
    
    results = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicates": detect_duplicates(df),
        "missing_values": detect_missing_values(df),
        "semantic_validation": semantic,
        "specific_validation": specific_validation
    }
    
    # Calcul du score de qualité
    results["quality_score"] = calculate_quality_score(results)
    
    return results


def calculate_quality_score(results: Dict[str, Any]) -> float:
    """
    Calcule un score de qualité global
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        float: Score de 0 à 100
    """
    score = 100.0
    
    # Pénalité pour les doublons (max -20 points)
    duplicate_penalty = min(20, results["duplicates"]["count"] * 0.5)
    score -= duplicate_penalty
    
    # Pénalité pour les valeurs manquantes (max -30 points)
    missing_penalty = min(30, results["missing_values"]["percentage"])
    score -= missing_penalty
    
    # Pénalité pour la cohérence sémantique (max -30 points)
    semantic_penalty = 0
    for col, data in results["semantic_validation"].items():
        if data["conformity_rate"] < 70:
            semantic_penalty += (70 - data["conformity_rate"]) * 0.2
    
    score -= min(30, semantic_penalty)
    
    # Pénalité pour validations spécifiques (max -20 points)
    specific_penalty = 0
    for col, data in results.get("specific_validation", {}).items():
        invalid_rate = 100 - data['validation']['validity_rate']
        specific_penalty += invalid_rate * 0.1
    
    score -= min(20, specific_penalty)
    
    return max(0.0, round(score, 1))


def generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """
    Génère des recommandations basées sur l'analyse
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        list: Liste de recommandations
    """
    recommendations = []
    
    # Valeurs manquantes
    if results["missing_values"]["total"] > 0:
        recommendations.append(
            f"Traiter les {results['missing_values']['total']} valeurs manquantes "
            f"({results['missing_values']['percentage']}% des données)"
        )
    
    # Doublons
    if results["duplicates"]["count"] > 0:
        recommendations.append(
            f"Supprimer ou fusionner les {results['duplicates']['count']} lignes dupliquées"
        )
    
    # Validations spécifiques
    for col, data in results.get("specific_validation", {}).items():
        invalid_count = data['validation']['invalid_count']
        if invalid_count > 0:
            col_type = data['type']
            type_label = {
                'phone': 'téléphones',
                'email': 'emails',
                'bank_account': 'comptes bancaires',
                'currency': 'devises'
            }.get(col_type, 'valeurs')
            
            recommendations.append(
                f"Corriger les {invalid_count} {type_label} invalides dans '{col}'"
            )
            
            # Ajouter exemples si disponibles
            if data['validation']['invalid_samples']:
                samples = data['validation']['invalid_samples'][:3]
                recommendations.append(
                    f"  Exemples invalides : {', '.join(str(s) for s in samples)}"
                )
    
    # Cohérence sémantique
    low_conformity = [
        col for col, data in results["semantic_validation"].items()
        if data["conformity_rate"] < 70
    ]
    
    if low_conformity:
        recommendations.append(
            f"Vérifier la cohérence des colonnes : {', '.join(low_conformity[:5])}"
        )
    
    return recommendations