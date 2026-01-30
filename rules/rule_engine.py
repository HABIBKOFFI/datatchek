import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re

class RuleEngine:
    """
    Moteur d'exécution de règles de qualité de données
    """
    
    def __init__(self, catalog_path: str = "rules/rules_catalog.json"):
        """Charge le catalogue de règles"""
        self.catalog_path = Path(catalog_path)
        self.rules = []
        self.categories = {}
        self.load_catalog()
    
    def load_catalog(self):
        """Charge les règles depuis le fichier JSON"""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")
        
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        self.categories = catalog.get('categories', {})
        self.rules = catalog.get('rules', [])
        
        print(f"✅ Loaded {len(self.rules)} rules from catalog")
    
    def is_rule_applicable(self, rule: Dict, column_name: str, column_type: str) -> bool:
        """Vérifie si une règle s'applique à une colonne donnée"""
        
        # Règles au niveau dataset (pas de filtre colonne)
        if rule.get('scope') == 'dataset':
            return True
        
        # Vérifier applies_to
        applies_to = rule.get('applies_to', [])
        if applies_to:
            col_lower = column_name.lower()
            if not any(keyword in col_lower for keyword in applies_to):
                return False
        
        return True
    
    def execute_rule(self, rule: Dict, df: pd.DataFrame, column: str = None) -> Dict:
        """Exécute une règle sur un dataset"""
        
        rule_id = rule['rule_id']
        
        # Règles au niveau dataset
        if rule['scope'] == 'dataset':
            if rule_id == 'R002_DUPLICATE_ROWS':
                return self._check_duplicates(df, rule)
        
        # Règles au niveau colonne
        elif rule['scope'] == 'column' and column:
            if rule_id == 'R001_MISSING_VALUES':
                return self._check_missing_values(df, column, rule)
            
            elif rule_id == 'R003_TYPE_MISMATCH':
                return self._check_type_mismatch(df, column, rule)
            
            elif rule_id == 'R004_EMAIL_FORMAT':
                return self._check_email_format(df, column, rule)
            
            elif rule_id == 'R005_PHONE_FORMAT':
                return self._check_phone_format(df, column, rule)
            
            elif rule_id == 'R006_LOW_CARDINALITY':
                return self._check_low_cardinality(df, column, rule)
            
            elif rule_id == 'R007_HIGH_NULL_RATE':
                return self._check_high_null_rate(df, column, rule)
            
            elif rule_id == 'R008_CONSTANT_COLUMN':
                return self._check_constant_column(df, column, rule)
        
        return None
    
    def _check_duplicates(self, df: pd.DataFrame, rule: Dict) -> Dict:
        """Vérifie les doublons"""
        duplicates = df[df.duplicated(keep=False)]
        count = len(duplicates)
        percentage = (count / len(df) * 100) if len(df) > 0 else 0
        
        threshold_warning = rule['threshold'].get('warning', 1)
        threshold_critical = rule['threshold'].get('critical', 5)
        
        if percentage >= threshold_critical:
            severity = 'critical'
        elif percentage >= threshold_warning:
            severity = 'warning'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'scope': 'dataset',
            'severity': severity,
            'value': count,
            'percentage': round(percentage, 2),
            'passed': severity == 'ok',
            'message': f"{count} lignes dupliquées ({percentage:.1f}%)"
        }
    
    def _check_missing_values(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie les valeurs manquantes"""
        missing_count = df[column].isnull().sum()
        total = len(df)
        percentage = (missing_count / total * 100) if total > 0 else 0
        
        threshold_warning = rule['threshold'].get('warning', 5)
        threshold_critical = rule['threshold'].get('critical', 20)
        
        if percentage >= threshold_critical:
            severity = 'critical'
        elif percentage >= threshold_warning:
            severity = 'warning'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': missing_count,
            'percentage': round(percentage, 2),
            'passed': severity == 'ok',
            'message': f"{missing_count} valeurs manquantes ({percentage:.1f}%)"
        }
    
    def _check_type_mismatch(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie la cohérence de type"""
        # Logique simplifiée - à enrichir avec column_detector
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': 'ok',
            'passed': True,
            'message': "Type cohérent"
        }
    
    def _check_email_format(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie le format des emails"""
        pattern = rule.get('pattern', r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        non_null = df[column].dropna()
        if len(non_null) == 0:
            return None
        
        valid_count = non_null.apply(lambda x: bool(re.match(pattern, str(x)))).sum()
        conformity = (valid_count / len(non_null) * 100)
        
        threshold_warning = rule['threshold'].get('warning', 90)
        threshold_critical = rule['threshold'].get('critical', 70)
        
        if conformity < threshold_critical:
            severity = 'critical'
        elif conformity < threshold_warning:
            severity = 'warning'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': len(non_null) - valid_count,
            'conformity': round(conformity, 2),
            'passed': severity == 'ok',
            'message': f"Conformité email: {conformity:.1f}%"
        }
    
    def _check_phone_format(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie le format des téléphones"""
        pattern = rule.get('pattern', r'^[\+\d\s\-\(\)]{8,20}$')
        
        non_null = df[column].dropna()
        if len(non_null) == 0:
            return None
        
        valid_count = non_null.apply(lambda x: bool(re.match(pattern, str(x)))).sum()
        conformity = (valid_count / len(non_null) * 100)
        
        threshold_warning = rule['threshold'].get('warning', 90)
        threshold_critical = rule['threshold'].get('critical', 70)
        
        if conformity < threshold_critical:
            severity = 'critical'
        elif conformity < threshold_warning:
            severity = 'warning'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': len(non_null) - valid_count,
            'conformity': round(conformity, 2),
            'passed': severity == 'ok',
            'message': f"Conformité téléphone: {conformity:.1f}%"
        }
    
    def _check_low_cardinality(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie la cardinalité sur colonnes identifiants"""
        unique_count = df[column].nunique()
        total = len(df)
        uniqueness = (unique_count / total * 100) if total > 0 else 0
        
        threshold_warning = rule['threshold'].get('warning', 80)
        threshold_critical = rule['threshold'].get('critical', 60)
        
        if uniqueness < threshold_critical:
            severity = 'critical'
        elif uniqueness < threshold_warning:
            severity = 'warning'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': unique_count,
            'uniqueness': round(uniqueness, 2),
            'passed': severity == 'ok',
            'message': f"Unicité: {uniqueness:.1f}% ({unique_count}/{total})"
        }
    
    def _check_high_null_rate(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie les colonnes très vides"""
        missing_count = df[column].isnull().sum()
        total = len(df)
        percentage = (missing_count / total * 100) if total > 0 else 0
        
        threshold_critical = rule['threshold'].get('critical', 80)
        
        if percentage >= threshold_critical:
            severity = 'critical'
        else:
            severity = 'ok'
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': missing_count,
            'percentage': round(percentage, 2),
            'passed': severity == 'ok',
            'message': f"Colonne très vide: {percentage:.1f}%"
        }
    
    def _check_constant_column(self, df: pd.DataFrame, column: str, rule: Dict) -> Dict:
        """Vérifie les colonnes constantes"""
        unique_count = df[column].nunique()
        
        if unique_count <= 1:
            severity = 'warning'
            passed = False
        else:
            severity = 'ok'
            passed = True
        
        return {
            'rule_id': rule['rule_id'],
            'column': column,
            'scope': 'column',
            'severity': severity,
            'value': unique_count,
            'passed': passed,
            'message': f"Valeurs uniques: {unique_count}"
        }
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse complète d'un dataset avec toutes les règles applicables
        
        Returns:
            dict: {
                'timestamp': datetime,
                'dataset_rules': [...],
                'column_rules': {...},
                'summary': {...}
            }
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'dataset_rules': [],
            'column_rules': {},
            'summary': {
                'total_rules_executed': 0,
                'rules_passed': 0,
                'rules_warning': 0,
                'rules_critical': 0
            }
        }
        
        # Exécuter règles au niveau dataset
        for rule in self.rules:
            if rule['scope'] == 'dataset':
                result = self.execute_rule(rule, df)
                if result:
                    results['dataset_rules'].append(result)
                    results['summary']['total_rules_executed'] += 1
                    
                    if result['severity'] == 'ok':
                        results['summary']['rules_passed'] += 1
                    elif result['severity'] == 'warning':
                        results['summary']['rules_warning'] += 1
                    elif result['severity'] == 'critical':
                        results['summary']['rules_critical'] += 1
        
        # Exécuter règles au niveau colonne
        for column in df.columns:
            results['column_rules'][column] = []
            
            for rule in self.rules:
                if rule['scope'] == 'column':
                    # Vérifier si la règle s'applique
                    if self.is_rule_applicable(rule, column, str(df[column].dtype)):
                        result = self.execute_rule(rule, df, column)
                        if result:
                            results['column_rules'][column].append(result)
                            results['summary']['total_rules_executed'] += 1
                            
                            if result['severity'] == 'ok':
                                results['summary']['rules_passed'] += 1
                            elif result['severity'] == 'warning':
                                results['summary']['rules_warning'] += 1
                            elif result['severity'] == 'critical':
                                results['summary']['rules_critical'] += 1
        
        return results