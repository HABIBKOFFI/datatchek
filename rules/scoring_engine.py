from typing import Dict, Any

class ScoringEngine:
    """
    Calcule le score de qualité basé sur les résultats du Rule Engine
    """
    
    def __init__(self, catalog_weights: Dict = None):
        """
        Initialise avec les poids des catégories
        
        Args:
            catalog_weights: dict des poids par catégorie (ex: {'completeness': 0.25})
        """
        self.weights = catalog_weights or {
            'completeness': 0.25,
            'validity': 0.35,
            'uniqueness': 0.20,
            'consistency': 0.20
        }
    
    def calculate_score(self, rule_results: Dict[str, Any], df_shape: tuple) -> Dict[str, Any]:
        """
        Calcule le score global de qualité
        
        Args:
            rule_results: Résultats du RuleEngine.analyze_dataset()
            df_shape: (rows, columns) du DataFrame
        
        Returns:
            dict: {
                'global_score': 0-100,
                'category_scores': {...},
                'details': {...}
            }
        """
        total_rows, total_cols = df_shape
        
        # Initialiser les scores par catégorie
        category_scores = {
            'completeness': 100.0,
            'validity': 100.0,
            'uniqueness': 100.0,
            'consistency': 100.0
        }
        
        # Traiter les règles au niveau dataset
        for result in rule_results.get('dataset_rules', []):
            penalty = self._calculate_penalty(result, total_rows, total_cols)
            category = self._get_rule_category(result['rule_id'])
            
            if category:
                category_scores[category] = max(0, category_scores[category] - penalty)
        
        # Traiter les règles au niveau colonne
        for column, results in rule_results.get('column_rules', {}).items():
            for result in results:
                penalty = self._calculate_penalty(result, total_rows, total_cols)
                category = self._get_rule_category(result['rule_id'])
                
                if category:
                    category_scores[category] = max(0, category_scores[category] - penalty)
        
        # Calculer le score global pondéré
        global_score = sum(
            category_scores[cat] * self.weights[cat]
            for cat in category_scores
        )
        
        return {
            'global_score': round(global_score, 1),
            'category_scores': {k: round(v, 1) for k, v in category_scores.items()},
            'details': {
                'total_rules_executed': rule_results['summary']['total_rules_executed'],
                'rules_passed': rule_results['summary']['rules_passed'],
                'rules_warning': rule_results['summary']['rules_warning'],
                'rules_critical': rule_results['summary']['rules_critical']
            }
        }
    
    def _get_rule_category(self, rule_id: str) -> str:
        """Détermine la catégorie d'une règle depuis son ID"""
        rule_categories = {
            'R001': 'completeness',
            'R002': 'uniqueness',
            'R003': 'validity',
            'R004': 'validity',
            'R005': 'validity',
            'R006': 'consistency',
            'R007': 'completeness',
            'R008': 'consistency',
            'R009': 'consistency',
            'R010': 'validity'
        }
        
        prefix = rule_id.split('_')[0]  # Ex: 'R001' de 'R001_MISSING_VALUES'
        return rule_categories.get(prefix)
    
    def _calculate_penalty(self, result: Dict, total_rows: int, total_cols: int) -> float:
        """
        Calcule la pénalité basée sur la sévérité et le pourcentage
        
        Returns:
            float: Pénalité entre 0 et 100
        """
        if result.get('passed', False):
            return 0.0
        
        severity = result.get('severity', 'ok')
        
        # Facteur de sévérité
        severity_multiplier = {
            'ok': 0.0,
            'warning': 0.5,
            'critical': 1.0
        }.get(severity, 0.5)
        
        # Calculer la pénalité selon le type de métrique
        if 'percentage' in result:
            # Basé sur pourcentage
            base_penalty = min(result['percentage'] * 0.5, 30)
        elif 'conformity' in result:
            # Basé sur conformité (inverse)
            conformity = result['conformity']
            base_penalty = (100 - conformity) * 0.3
        elif 'uniqueness' in result:
            # Basé sur unicité (inverse)
            uniqueness = result['uniqueness']
            base_penalty = (100 - uniqueness) * 0.2
        else:
            # Pénalité par défaut selon sévérité
            base_penalty = {'warning': 5, 'critical': 15}.get(severity, 0)
        
        return base_penalty * severity_multiplier
    
    def generate_recommendations(self, rule_results: Dict, score: Dict) -> list:
        """
        Génère des recommandations priorisées
        
        Returns:
            list: [{'priority': 'HAUTE/MOYENNE/BASSE', 'message': '...', 'action': '...'}]
        """
        recommendations = []
        
        # Règles critiques = priorité HAUTE
        for result in rule_results.get('dataset_rules', []):
            if result.get('severity') == 'critical':
                recommendations.append({
                    'priority': 'HAUTE',
                    'category': 'Dataset',
                    'message': f"🔴 {result['message']}",
                    'action': self._get_action_for_rule(result['rule_id'])
                })
        
        for column, results in rule_results.get('column_rules', {}).items():
            for result in results:
                if result.get('severity') == 'critical':
                    recommendations.append({
                        'priority': 'HAUTE',
                        'category': f"Colonne '{column}'",
                        'message': f"🔴 {result['message']}",
                        'action': self._get_action_for_rule(result['rule_id'])
                    })
        
        # Règles warning = priorité MOYENNE
        for result in rule_results.get('dataset_rules', []):
            if result.get('severity') == 'warning':
                recommendations.append({
                    'priority': 'MOYENNE',
                    'category': 'Dataset',
                    'message': f"🟠 {result['message']}",
                    'action': self._get_action_for_rule(result['rule_id'])
                })
        
        for column, results in rule_results.get('column_rules', {}).items():
            for result in results:
                if result.get('severity') == 'warning':
                    recommendations.append({
                        'priority': 'MOYENNE',
                        'category': f"Colonne '{column}'",
                        'message': f"🟠 {result['message']}",
                        'action': self._get_action_for_rule(result['rule_id'])
                    })
        
        # Score faible = recommandation générale BASSE
        if score['global_score'] < 60:
            recommendations.append({
                'priority': 'BASSE',
                'category': 'Général',
                'message': f"ℹ️ Score global faible ({score['global_score']}/100)",
                'action': "Prioriser le nettoyage des problèmes critiques ci-dessus"
            })
        
        return recommendations
    
    def _get_action_for_rule(self, rule_id: str) -> str:
        """Retourne l'action recommandée pour une règle"""
        actions = {
            'R001_MISSING_VALUES': "Imputer les valeurs manquantes ou supprimer les lignes",
            'R002_DUPLICATE_ROWS': "Supprimer ou fusionner les lignes dupliquées",
            'R003_TYPE_MISMATCH': "Convertir les données au bon type",
            'R004_EMAIL_FORMAT': "Nettoyer et standardiser les emails",
            'R005_PHONE_FORMAT': "Nettoyer et standardiser les téléphones",
            'R006_LOW_CARDINALITY': "Vérifier l'intégrité de la clé primaire",
            'R007_HIGH_NULL_RATE': "Supprimer la colonne ou imputer massivement",
            'R008_CONSTANT_COLUMN': "Supprimer la colonne (pas d'information)",
            'R009_SEMANTIC_COHERENCE': "Corriger les valeurs incohérentes",
            'R010_OUTLIERS_NUMERIC': "Traiter ou supprimer les valeurs aberrantes"
        }
        
        return actions.get(rule_id, "Corriger manuellement")