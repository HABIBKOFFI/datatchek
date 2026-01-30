# i18n/translations.py
"""
Système de traduction multilingue pour DataTchek
"""

TRANSLATIONS = {
    'fr': {
        # Navigation
        'app_title': 'DataTchek Pro - Analyse de Qualité',
        'tagline': 'Analysez la Qualité de Vos Données',
        'upload_prompt': 'Uploadez votre fichier et obtenez une analyse professionnelle',
        
        # Badges
        'quality_excellent': 'Qualité Exceptionnelle',
        'quality_good': 'Excellente Qualité',
        'quality_average': 'Bonne Qualité',
        'quality_poor': 'Qualité À Améliorer',
        
        # Niveaux
        'level_expert': 'Expert Data Quality',
        'level_master': 'Data Quality Master',
        'level_advanced': 'Data Quality Avancé',
        'level_beginner': 'Data Quality Débutant',
        
        # Métriques
        'lines_analyzed': 'Lignes Analysées',
        'columns_detected': 'Colonnes Détectées',
        'duplicates': 'Doublons',
        'missing': 'Données Manquantes',
        'conformity': 'Conformité',
        'quality_avg': 'Qualité Moyenne',
        
        # Messages
        'no_duplicates': 'Aucun doublon détecté - Excellent',
        'duplicates_found': '{count} doublons détectés',
        'no_missing': 'Aucune donnée manquante - Parfait',
        'missing_found': '{count} valeurs manquantes',
        'data_not_available': 'Donnée non disponible',
        'value_missing': 'Valeur manquante',
        'not_exploitable': 'Non exploitable',
        
        # Interprétations naturelles
        'one_in_eight': '1 donnée sur 8',
        'half_data': 'La moitié des données',
        'most_data': 'La plupart des données',
        'few_data': 'Quelques données',
        'all_data': 'Toutes les données',
        
        # Recommandations
        'recommendations': 'Recommandations Prioritaires',
        'priority_high': 'HAUTE PRIORITÉ',
        'priority_medium': 'PRIORITÉ MOYENNE',
        'priority_low': 'PRIORITÉ BASSE',
        
        # Actions
        'generate_pdf': 'Générer Rapport PDF',
        'clean_data': 'Nettoyer Données',
        'export_analysis': 'Exporter Analyse',
        
        # Tabs
        'tab_data': 'Données',
        'tab_graphs': 'Graphiques',
        'tab_duplicates': 'Doublons',
        'tab_missing': 'Valeurs Manquantes',
        'tab_distribution': 'Distribution',
        'tab_correlations': 'Corrélations',
        'tab_outliers': 'Anomalies',
        'tab_patterns': 'Patterns',
        
        # Visualisations avancées
        'distribution_title': 'Distribution des Valeurs',
        'correlation_title': 'Matrice de Corrélation',
        'outliers_title': 'Détection d\'Anomalies',
        'patterns_title': 'Analyse de Patterns',
        'freshness_title': 'Fraîcheur des Données',
        
        # Executive Summary
        'executive_summary': 'Résumé Exécutif',
        'business_impact': 'Impact Métier',
        'major_issues': 'Problèmes Majeurs',
        'actionable_reco': 'Recommandations Actionnables',
        'data_maturity': 'Niveau de Maturité Data',
    },
    
    'en': {
        # Navigation
        'app_title': 'DataTchek Pro - Quality Analysis',
        'tagline': 'Analyze Your Data Quality',
        'upload_prompt': 'Upload your file and get a professional analysis',
        
        # Badges
        'quality_excellent': 'Exceptional Quality',
        'quality_good': 'Excellent Quality',
        'quality_average': 'Good Quality',
        'quality_poor': 'Quality Needs Improvement',
        
        # Niveaux
        'level_expert': 'Data Quality Expert',
        'level_master': 'Data Quality Master',
        'level_advanced': 'Data Quality Advanced',
        'level_beginner': 'Data Quality Beginner',
        
        # Métriques
        'lines_analyzed': 'Lines Analyzed',
        'columns_detected': 'Columns Detected',
        'duplicates': 'Duplicates',
        'missing': 'Missing Data',
        'conformity': 'Conformity',
        'quality_avg': 'Average Quality',
        
        # Messages
        'no_duplicates': 'No duplicates detected - Excellent',
        'duplicates_found': '{count} duplicates detected',
        'no_missing': 'No missing data - Perfect',
        'missing_found': '{count} missing values',
        'data_not_available': 'Data not available',
        'value_missing': 'Missing value',
        'not_exploitable': 'Not exploitable',
        
        # Interprétations naturelles
        'one_in_eight': '1 in 8 records',
        'half_data': 'Half of the data',
        'most_data': 'Most of the data',
        'few_data': 'Few records',
        'all_data': 'All data',
        
        # Recommandations
        'recommendations': 'Priority Recommendations',
        'priority_high': 'HIGH PRIORITY',
        'priority_medium': 'MEDIUM PRIORITY',
        'priority_low': 'LOW PRIORITY',
        
        # Actions
        'generate_pdf': 'Generate PDF Report',
        'clean_data': 'Clean Data',
        'export_analysis': 'Export Analysis',
        
        # Tabs
        'tab_data': 'Data',
        'tab_graphs': 'Charts',
        'tab_duplicates': 'Duplicates',
        'tab_missing': 'Missing Values',
        'tab_distribution': 'Distribution',
        'tab_correlations': 'Correlations',
        'tab_outliers': 'Outliers',
        'tab_patterns': 'Patterns',
        
        # Visualisations avancées
        'distribution_title': 'Value Distribution',
        'correlation_title': 'Correlation Matrix',
        'outliers_title': 'Outlier Detection',
        'patterns_title': 'Pattern Analysis',
        'freshness_title': 'Data Freshness',
        
        # Executive Summary
        'executive_summary': 'Executive Summary',
        'business_impact': 'Business Impact',
        'major_issues': 'Major Issues',
        'actionable_reco': 'Actionable Recommendations',
        'data_maturity': 'Data Maturity Level',
    }
}


def get_text(key: str, lang: str = 'fr', **kwargs) -> str:
    """
    Récupère un texte traduit
    
    Args:
        key: Clé de traduction
        lang: Langue ('fr' ou 'en')
        **kwargs: Variables à formater dans le texte
    
    Returns:
        Texte traduit et formaté
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS['fr']).get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def format_number(value, lang='fr'):
    """Formate un nombre selon la langue"""
    if lang == 'fr':
        return f"{value:,}".replace(',', ' ')
    else:
        return f"{value:,}"


def interpret_percentage(pct: float, lang='fr') -> str:
    """Interprète un pourcentage en langage naturel"""
    if pct == 0:
        return get_text('all_data', lang) if lang == 'fr' else get_text('all_data', lang)
    elif pct < 12.5:
        return get_text('one_in_eight', lang)
    elif pct < 25:
        return get_text('few_data', lang)
    elif pct < 50:
        return get_text('most_data', lang) if lang == 'en' else "Une partie significative des données"
    elif pct < 75:
        return get_text('half_data', lang)
    else:
        return "La majorité des données" if lang == 'fr' else "Most of the data"


def format_missing_value(value):
    """Remplace les valeurs techniques par du langage naturel"""
    if pd.isna(value) or value is None or value == 'NaN' or value == 'None':
        return "Donnée manquante"
    elif value == True:
        return "Oui"
    elif value == False:
        return "Non"
    else:
        return value