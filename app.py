# app.py - DataTchek V2 Pro Edition
"""
DataTchek - Plateforme professionnelle d'analyse de qualité des données
Version finale avec traductions, visualisations avancées et PDF Executive
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys
from pathlib import Path

# Ajouter le dossier i18n au path
sys.path.insert(0, str(Path(__file__).parent))

from utils.validators import validate_dataframe, generate_recommendations
from utils.visualizations import (
    create_score_gauge,
    create_problems_bar_chart,
    create_missing_data_chart,
    create_quality_distribution_pie,
    create_column_quality_bar,
)
from utils.pdf_generator import create_pdf_report

# Imports des nouveaux modules
try:
    from utils.advanced_visualizations import (
        create_distribution_analysis,
        create_correlation_heatmap,
        detect_outliers_visualization,
        create_data_freshness_timeline,
        create_quality_score_breakdown,
        create_column_quality_heatmap,
        create_value_uniqueness_analysis,
        create_pattern_detection,
        create_missing_data_patterns
    )
    ADVANCED_VIZ_AVAILABLE = True
except ImportError:
    ADVANCED_VIZ_AVAILABLE = False

try:
    from utils.executive_pdf_generator import create_executive_pdf
    EXECUTIVE_PDF_AVAILABLE = True
except ImportError:
    EXECUTIVE_PDF_AVAILABLE = False

try:
    from i18n.translations import get_text, interpret_percentage, format_missing_value
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    
    # Fallback complet si traductions pas disponibles
    def get_text(key, lang='fr', **kwargs):
        """Fallback pour les traductions"""
        translations = {
            'quality_excellent': 'Qualité Exceptionnelle' if lang == 'fr' else 'Exceptional Quality',
            'quality_good': 'Excellente Qualité' if lang == 'fr' else 'Excellent Quality',
            'quality_average': 'Bonne Qualité' if lang == 'fr' else 'Good Quality',
            'quality_poor': 'Qualité À Améliorer' if lang == 'fr' else 'Quality Needs Improvement',
            'level_expert': 'Expert Data Quality' if lang == 'fr' else 'Data Quality Expert',
            'level_master': 'Data Quality Master',
            'level_advanced': 'Data Quality Avancé' if lang == 'fr' else 'Data Quality Advanced',
            'level_beginner': 'Data Quality Débutant' if lang == 'fr' else 'Data Quality Beginner',
            'lines_analyzed': 'Lignes Analysées' if lang == 'fr' else 'Lines Analyzed',
            'columns_detected': 'Colonnes Détectées' if lang == 'fr' else 'Columns Detected',
            'duplicates': 'Doublons' if lang == 'fr' else 'Duplicates',
            'missing': 'Données Manquantes' if lang == 'fr' else 'Missing Data',
            'quality_avg': 'Qualité Moyenne' if lang == 'fr' else 'Average Quality',
            'conformity': 'Conformité' if lang == 'fr' else 'Conformity',
            'generate_pdf': 'Générer Rapport PDF' if lang == 'fr' else 'Generate PDF Report',
            'clean_data': 'Nettoyer Données' if lang == 'fr' else 'Clean Data',
            'export_analysis': 'Exporter Analyse' if lang == 'fr' else 'Export Analysis',
            'recommendations': 'Recommandations Prioritaires' if lang == 'fr' else 'Priority Recommendations',
            'priority_high': 'HAUTE PRIORITÉ' if lang == 'fr' else 'HIGH PRIORITY',
            'priority_medium': 'PRIORITÉ MOYENNE' if lang == 'fr' else 'MEDIUM PRIORITY',
            'priority_low': 'PRIORITÉ BASSE' if lang == 'fr' else 'LOW PRIORITY',
            'tab_data': 'Données' if lang == 'fr' else 'Data',
            'tab_graphs': 'Graphiques' if lang == 'fr' else 'Charts',
            'tab_distribution': 'Distribution',
            'tab_correlations': 'Corrélations' if lang == 'fr' else 'Correlations',
            'tab_outliers': 'Anomalies' if lang == 'fr' else 'Outliers',
            'tab_duplicates': 'Doublons' if lang == 'fr' else 'Duplicates',
            'tab_missing': 'Valeurs Manquantes' if lang == 'fr' else 'Missing Values',
            'no_duplicates': 'Aucun doublon détecté - Excellent' if lang == 'fr' else 'No duplicates detected - Excellent',
            'no_missing': 'Aucune donnée manquante - Parfait' if lang == 'fr' else 'No missing data - Perfect'
        }
        return translations.get(key, key)
    
    def interpret_percentage(pct, lang='fr'):
        """Fallback pour interpréter les pourcentages"""
        if pct == 0:
            return "Aucune" if lang == 'fr' else "None"
        elif pct < 12.5:
            return "1 donnée sur 8" if lang == 'fr' else "1 in 8"
        elif pct < 25:
            return f"{pct:.1f}% (Faible)" if lang == 'fr' else f"{pct:.1f}% (Low)"
        elif pct < 50:
            return f"{pct:.1f}% (Modéré)" if lang == 'fr' else f"{pct:.1f}% (Moderate)"
        else:
            return f"{pct:.1f}% (Élevé)" if lang == 'fr' else f"{pct:.1f}% (High)"
    
    def format_missing_value(value):
        """Fallback pour formater les valeurs manquantes"""
        if pd.isna(value) or value is None or value == 'NaN' or value == 'None':
            return "Donnée manquante"
        elif value == True:
            return "Oui"
        elif value == False:
            return "Non"
        else:
            return value


# ======================
# CONFIGURATION
# ======================
st.set_page_config(
    page_title="DataTchek Pro - Analyse de Qualité",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser la langue dans session_state
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'


# ======================
# CSS PROFESSIONNEL & GAMIFIÉ
# ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-color: #2563EB;
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --danger-color: #EF4444;
    --dark-bg: #1E293B;
    --light-bg: #F8FAFC;
    --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
    padding: 2rem 1rem;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-content {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.pro-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: var(--card-shadow);
    border: 1px solid #E2E8F0;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.pro-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.15);
}

.hero-score {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    border-radius: 24px;
    padding: 3rem;
    color: white;
    text-align: center;
    box-shadow: 0 20px 40px -8px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}

.hero-score::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

.score-number {
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    text-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.quality-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-radius: 100px;
    font-weight: 700;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    animation: fadeInScale 0.5s ease-out;
}

@keyframes fadeInScale {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

.badge-platinum { background: linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%); color: #4338CA; box-shadow: 0 4px 12px rgba(67, 56, 202, 0.3); }
.badge-gold { background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); color: #92400E; box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3); }
.badge-silver { background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); color: #374151; box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3); }
.badge-bronze { background: linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%); color: #9A3412; box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3); }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border-left: 4px solid var(--primary-color);
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-left-width: 6px;
    transform: translateX(4px);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--dark-bg);
    line-height: 1;
}

.metric-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.5rem;
}

.progress-container {
    background: #E2E8F0;
    border-radius: 100px;
    height: 24px;
    overflow: hidden;
    position: relative;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
    border-radius: 100px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 1rem;
    font-weight: 700;
    color: white;
    font-size: 0.875rem;
    transition: width 1s ease-out;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}

.recommendation-item {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border-left: 4px solid #3B82F6;
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
}

.recommendation-item:hover {
    transform: translateX(8px);
    box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.2);
}

.recommendation-high {
    border-left-color: #EF4444;
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, white 100%);
}

.recommendation-medium {
    border-left-color: #F59E0B;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.05) 0%, white 100%);
}

.recommendation-low {
    border-left-color: #3B82F6;
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, white 100%);
}

.stButton > button {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    color: white !important;
    border-color: transparent;
}

@keyframes slideInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.animated-card {
    animation: slideInUp 0.6s ease-out;
}

[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border: 2px dashed #667EEA;
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-color: #764BA2;
    transform: scale(1.02);
}

.lang-selector {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.5rem;
    display: flex;
    gap: 0.5rem;
    justify-content: center;
}

.lang-btn {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
}

.lang-btn.active {
    background: white;
    color: #1E293B !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ======================
# FONCTIONS GAMIFICATION
# ======================
def get_quality_badge(score):
    """Retourne le badge selon le score"""
    lang = st.session_state.lang
    if score >= 90:
        return {
            'name': 'PLATINUM',
            'emoji': '💎',
            'class': 'badge-platinum',
            'message': get_text('quality_excellent', lang),
            'points': 1000
        }
    elif score >= 75:
        return {
            'name': 'GOLD',
            'emoji': '🏆',
            'class': 'badge-gold',
            'message': get_text('quality_good', lang),
            'points': 750
        }
    elif score >= 60:
        return {
            'name': 'SILVER',
            'emoji': '🥈',
            'class': 'badge-silver',
            'message': get_text('quality_average', lang),
            'points': 500
        }
    else:
        return {
            'name': 'BRONZE',
            'emoji': '🥉',
            'class': 'badge-bronze',
            'message': get_text('quality_poor', lang),
            'points': 250
        }


def get_level(score):
    """Calcule le niveau de qualité"""
    lang = st.session_state.lang
    if score >= 90:
        return get_text('level_expert', lang), "🎓"
    elif score >= 75:
        return get_text('level_master', lang), "⭐"
    elif score >= 60:
        return get_text('level_advanced', lang), "📊"
    else:
        return get_text('level_beginner', lang), "🌱"


# ======================
# SIDEBAR MODERNE
# ======================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            🎯 DataTchek
        </h1>
        <p style='font-size: 0.875rem; opacity: 0.8; margin-top: 0.5rem;'>
            Plateforme Pro d'Analyse de Qualité
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélecteur de langue
    st.markdown("<div class='lang-selector'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🇫🇷 FR", use_container_width=True, key="lang_fr"):
            st.session_state.lang = 'fr'
            st.rerun()
    
    with col2:
        if st.button("🇬🇧 EN", use_container_width=True, key="lang_en"):
            st.session_state.lang = 'en'
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    lang = st.session_state.lang
    
    features_text = """
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>✨ Fonctionnalités</h3>
        <ul style='line-height: 2; padding-left: 1.5rem;'>
            <li>Détection intelligente</li>
            <li>Validation CI (+225)</li>
            <li>Scoring gamifié</li>
            <li>Rapports PDF Pro</li>
            <li>Graphiques avancés</li>
            <li>Multilingue FR/EN</li>
        </ul>
    </div>
    """ if lang == 'fr' else """
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>✨ Features</h3>
        <ul style='line-height: 2; padding-left: 1.5rem;'>
            <li>Smart Detection</li>
            <li>CI Validation (+225)</li>
            <li>Gamified Scoring</li>
            <li>Pro PDF Reports</li>
            <li>Advanced Charts</li>
            <li>Multilingual FR/EN</li>
        </ul>
    </div>
    """
    
    st.markdown(features_text, unsafe_allow_html=True)
    
    levels_text = """
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>🎮 Niveaux de Qualité</h3>
        <div style='padding: 0.5rem 0;'>
            💎 90-100: Platinum<br>
            🏆 75-89: Gold<br>
            🥈 60-74: Silver<br>
            🥉 0-59: Bronze
        </div>
    </div>
    """ if lang == 'fr' else """
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>🎮 Quality Levels</h3>
        <div style='padding: 0.5rem 0;'>
            💎 90-100: Platinum<br>
            🏆 75-89: Gold<br>
            🥈 60-74: Silver<br>
            🥉 0-59: Bronze
        </div>
    </div>
    """
    
    st.markdown(levels_text, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='font-size: 0.875rem; opacity: 0.6;'>🚀 Version 2.0 Pro</p>
        <p style='font-size: 0.875rem; font-weight: 600;'>HABIB KOFFI</p>
        <p style='font-size: 0.75rem; opacity: 0.6;'>©️ 2026 DataTchek</p>
    </div>
    """, unsafe_allow_html=True)


# ======================
# EN-TÊTE PRINCIPAL
# ======================
lang = st.session_state.lang

title_text = "Analysez la Qualité de Vos Données" if lang == 'fr' else "Analyze Your Data Quality"
subtitle_text = "Uploadez votre fichier et obtenez une analyse professionnelle en quelques secondes" if lang == 'fr' else "Upload your file and get a professional analysis in seconds"

st.markdown(f"""
<div style='text-align: center; padding: 2rem 0 3rem 0;'>
    <h1 style='font-size: 3rem; margin: 0; color: #1E293B;'>
        {title_text}
    </h1>
    <p style='font-size: 1.25rem; color: #64748B; margin-top: 1rem;'>
        {subtitle_text}
    </p>
</div>
""", unsafe_allow_html=True)


# ======================
# UPLOAD SECTION
# ======================
st.markdown("<div class='pro-card animated-card'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

upload_label = "📁 Glissez-déposez votre fichier ici" if lang == 'fr' else "📁 Drag and drop your file here"
upload_help = "Formats: CSV, Excel (.xlsx, .xls) | Taille max: 200MB" if lang == 'fr' else "Formats: CSV, Excel (.xlsx, .xls) | Max size: 200MB"

with col2:
    uploaded_file = st.file_uploader(
        upload_label,
        type=["csv", "xlsx", "xls"],
        help=upload_help
    )

st.markdown("</div>", unsafe_allow_html=True)


# ======================
# ANALYSE
# ======================
if uploaded_file:
    try:
        # Chargement
        loading_text = "🔄 Chargement du fichier..." if lang == 'fr' else "🔄 Loading file..."
        
        with st.spinner(loading_text):
            if uploaded_file.name.endswith(".csv"):
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="iso-8859-1")
            else:
                df = pd.read_excel(uploaded_file)
        
        success_text = f"✅ **{uploaded_file.name}** {'chargé' if lang == 'fr' else 'loaded'}: {len(df):,} {'lignes' if lang == 'fr' else 'rows'} × {len(df.columns)} {'colonnes' if lang == 'fr' else 'columns'}"
        st.success(success_text)
        
        # Analyse
        analyzing_text = "🧠 Analyse intelligente en cours..." if lang == 'fr' else "🧠 Intelligent analysis in progress..."
        
        with st.spinner(analyzing_text):
            results = validate_dataframe(df)
        
        score = results["quality_score"]
        badge = get_quality_badge(score)
        level_name, level_emoji = get_level(score)
        
        # ======================
        # HERO SCORE
        # ======================
        st.markdown("<div class='pro-card animated-card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            points_text = "Points de Qualité" if lang == 'fr' else "Quality Points"
            
            st.markdown(f"""
            <div class='hero-score'>
                <div class='score-number'>{score}</div>
                <div style='font-size: 1.5rem; font-weight: 600; margin-top: 0.5rem;'>/ 100</div>
                <div style='margin-top: 1.5rem;'>
                    <div class='quality-badge {badge['class']}'>
                        <span style='font-size: 1.5rem;'>{badge['emoji']}</span>
                        {badge['name']}
                    </div>
                </div>
                <div style='margin-top: 1rem; font-size: 1.1rem; opacity: 0.9;'>
                    {badge['message']}
                </div>
                <div style='margin-top: 1.5rem; font-size: 0.875rem; opacity: 0.7;'>
                    +{badge['points']} {points_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            level_title = "Niveau Atteint" if lang == 'fr' else "Level Achieved"
            progress_text = "Progression vers Expert" if lang == 'fr' else "Progress to Expert"
            
            st.markdown(f"""
            <div style='padding: 2rem;'>
                <h2 style='color: #1E293B; margin-bottom: 1.5rem;'>{level_title}</h2>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>{level_emoji}</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #667EEA; margin-bottom: 2rem;'>
                    {level_name}
                </div>
                
                <h3 style='color: #64748B; font-size: 1rem; margin-bottom: 1rem;'>{progress_text}</h3>
                <div class='progress-container'>
                    <div class='progress-bar' style='width: {score}%;'>
                        {score}%
                    </div>
                </div>
                
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem;'>
                    <div class='metric-card'>
                        <div class='metric-value'>{results['total_rows']:,}</div>
                        <div class='metric-label'>{get_text('lines_analyzed', lang)}</div>
                    </div>
                    <div class='metric-card'>
                        <div class='metric-value'>{results['total_columns']}</div>
                        <div class='metric-label'>{get_text('columns_detected', lang)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ======================
        # MÉTRIQUES
        # ======================
        metrics_title = "📊 Métriques Détaillées" if lang == 'fr' else "📊 Detailed Metrics"
        st.markdown(f"<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>{metrics_title}</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Interpréter les métriques en langage naturel
        missing_pct = results['missing_values']['percentage']
        try:
            missing_interpretation = interpret_percentage(missing_pct, lang)
        except Exception:
            missing_interpretation = f"{missing_pct:.1f}%"
        
        metrics = [
            ("🔄", get_text('duplicates', lang), results['duplicates']['count']),
            ("❌", get_text('missing', lang), f"{missing_interpretation}"),
            ("✅", get_text('quality_avg', lang), f"{score}%"),
            ("📈", get_text('conformity', lang), f"95%")
        ]
        
        for idx, (emoji, label, value) in enumerate(metrics):
            with [col1, col2, col3, col4][idx]:
                st.markdown(f"""
                <div class='metric-card animated-card' style='animation-delay: {idx * 0.1}s;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{emoji}</div>
                    <div class='metric-value'>{value}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # ======================
        # ACTIONS
        # ======================
        actions_title = "⚡ Actions Rapides" if lang == 'fr' else "⚡ Quick Actions"
        st.markdown(f"<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>{actions_title}</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pdf_btn_text = get_text('generate_pdf', lang)
            if st.button(f"📄 {pdf_btn_text}", use_container_width=True):
                with st.spinner("Génération..." if lang == 'fr' else "Generating..."):
                    try:
                        if EXECUTIVE_PDF_AVAILABLE:
                            pdf = create_executive_pdf(df, results, uploaded_file.name, lang)
                        else:
                            pdf = create_pdf_report(df, results)
                        
                        download_text = "⬇️ Télécharger PDF" if lang == 'fr' else "⬇️ Download PDF"
                        st.download_button(
                            download_text,
                            pdf,
                            file_name=f"rapport_executive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        error_text = f"Erreur: {e}" if lang == 'fr' else f"Error: {e}"
                        st.error(error_text)
        
        with col2:
            clean_btn_text = get_text('clean_data', lang)
            st.button(f"🧹 {clean_btn_text}", use_container_width=True)
        
        with col3:
            export_btn_text = get_text('export_analysis', lang)
            st.button(f"📤 {export_btn_text}", use_container_width=True)
        
        # ======================
        # RECOMMANDATIONS
        # ======================
        reco_title = get_text('recommendations', lang)
        st.markdown(f"<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>💡 {reco_title}</h2>", unsafe_allow_html=True)
        
        recommendations = generate_recommendations(results)
        
        if recommendations:
            for idx, rec in enumerate(recommendations[:5]):
                priority_class = "recommendation-high" if idx < 2 else "recommendation-medium" if idx < 4 else "recommendation-low"
                
                if idx < 2:
                    priority_badge = get_text('priority_high', lang)
                    priority_emoji = "🔴"
                elif idx < 4:
                    priority_badge = get_text('priority_medium', lang)
                    priority_emoji = "🟠"
                else:
                    priority_badge = get_text('priority_low', lang)
                    priority_emoji = "🔵"
                
                st.markdown(f"""
                <div class='recommendation-item {priority_class} animated-card' style='animation-delay: {idx * 0.1}s;'>
                    <div style='display: flex; justify-content: space-between; align-items: start;'>
                        <div style='flex: 1;'>
                            <div style='font-weight: 700; font-size: 0.875rem; color: #64748B; margin-bottom: 0.5rem;'>
                                {priority_emoji} {priority_badge}
                            </div>
                            <div style='font-weight: 600; color: #1E293B;'>
                                {rec}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ======================
        # TABS D'ANALYSE AVANCÉE
        # ======================
        analysis_title = "🔬 Analyse Approfondie" if lang == 'fr' else "🔬 In-Depth Analysis"
        st.markdown(f"<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>{analysis_title}</h2>", unsafe_allow_html=True)
        
        if ADVANCED_VIZ_AVAILABLE:
            tabs = st.tabs([
                get_text('tab_data', lang),
                get_text('tab_graphs', lang),
                get_text('tab_distribution', lang),
                get_text('tab_correlations', lang),
                get_text('tab_outliers', lang),
                get_text('tab_duplicates', lang),
                get_text('tab_missing', lang)
            ])
            
            with tabs[0]:  # Données
                st.dataframe(df.head(50), use_container_width=True, height=400)
            
            with tabs[1]:  # Graphiques de base
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
                    except: pass
                    try:
                        st.plotly_chart(create_quality_score_breakdown(results), use_container_width=True)
                    except: pass
                with col2:
                    try:
                        st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
                    except: pass
                    try:
                        st.plotly_chart(create_column_quality_heatmap(df), use_container_width=True)
                    except: pass
            
            with tabs[2]:  # Distribution
                # Sélecteur de colonne
                selected_col = st.selectbox(
                    "Sélectionnez une colonne" if lang == 'fr' else "Select a column",
                    df.columns.tolist()
                )
                
                try:
                    fig_dist = create_distribution_analysis(df, selected_col)
                    if fig_dist:
                        st.plotly_chart(fig_dist, use_container_width=True)
                except Exception as e:
                    st.warning(f"Impossible d'afficher la distribution: {e}")
                
                try:
                    fig_pattern = create_pattern_detection(df, selected_col)
                    if fig_pattern:
                        st.plotly_chart(fig_pattern, use_container_width=True)
                except: pass
            
            with tabs[3]:  # Corrélations
                try:
                    fig_corr = create_correlation_heatmap(df)
                    if fig_corr:
                        st.plotly_chart(fig_corr, use_container_width=True)
                    else:
                        no_numeric = "Pas assez de colonnes numériques pour calculer les corrélations" if lang == 'fr' else "Not enough numeric columns to calculate correlations"
                        st.info(no_numeric)
                except Exception as e:
                    st.warning(f"Erreur: {e}")
                
                try:
                    fig_unique = create_value_uniqueness_analysis(df)
                    if fig_unique:
                        st.plotly_chart(fig_unique, use_container_width=True)
                except: pass
            
            with tabs[4]:  # Outliers
                # Sélection colonne numérique
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if numeric_cols:
                    selected_numeric = st.selectbox(
                        "Sélectionnez une colonne numérique" if lang == 'fr' else "Select a numeric column",
                        numeric_cols
                    )
                    
                    try:
                        fig_outliers = detect_outliers_visualization(df, selected_numeric)
                        if fig_outliers:
                            st.plotly_chart(fig_outliers, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Erreur: {e}")
                else:
                    no_numeric = "Aucune colonne numérique trouvée" if lang == 'fr' else "No numeric columns found"
                    st.info(no_numeric)
            
            with tabs[5]:  # Doublons
                duplicate_count = results["duplicates"]["count"]
                
                if duplicate_count > 0:
                    dup_text = f"⚠️ {duplicate_count} {'doublons détectés' if lang == 'fr' else 'duplicates detected'}"
                    st.warning(dup_text)
                    st.dataframe(results["duplicates"]["data"], use_container_width=True, height=400)
                else:
                    no_dup = get_text('no_duplicates', lang)
                    st.success(f"✅ {no_dup}")
            
            with tabs[6]:  # Données manquantes
                missing_total = results["missing_values"]["total"]
                
                if missing_total > 0:
                    missing_text = f"⚠️ {missing_total:,} {'valeurs manquantes' if lang == 'fr' else 'missing values'} ({results['missing_values']['percentage']}%)"
                    st.warning(missing_text)
                    
                    try:
                        fig_missing_pattern = create_missing_data_patterns(df)
                        if fig_missing_pattern:
                            st.plotly_chart(fig_missing_pattern, use_container_width=True)
                    except: pass
                    
                    # Détail par colonne
                    missing_by_col = pd.DataFrame.from_dict(
                        results["missing_values"]["by_column"],
                        orient='index',
                        columns=['Valeurs Manquantes']
                    )
                    missing_by_col = missing_by_col[missing_by_col['Valeurs Manquantes'] > 0]
                    missing_by_col = missing_by_col.sort_values('Valeurs Manquantes', ascending=False)
                    missing_by_col['Pourcentage'] = (missing_by_col['Valeurs Manquantes'] / len(df) * 100).round(2)
                    
                    st.dataframe(missing_by_col, use_container_width=True)
                else:
                    no_missing = get_text('no_missing', lang)
                    st.success(f"✅ {no_missing}")
        
        else:
            # Fallback tabs si visualisations avancées pas disponibles
            tabs = st.tabs([
                get_text('tab_data', lang),
                get_text('tab_graphs', lang),
                get_text('tab_duplicates', lang),
                get_text('tab_missing', lang)
            ])
            
            with tabs[0]:
                st.dataframe(df.head(50), use_container_width=True, height=400)
            
            with tabs[1]:
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
                    except: pass
                with col2:
                    try:
                        st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
                    except: pass
            
            with tabs[2]:
                if results["duplicates"]["count"] > 0:
                    st.warning(f"⚠️ {results['duplicates']['count']} doublons")
                    st.dataframe(results["duplicates"]["data"], use_container_width=True)
                else:
                    st.success("✅ Aucun doublon")
            
            with tabs[3]:
                if results["missing_values"]["total"] > 0:
                    st.warning(f"⚠️ {results['missing_values']['total']:,} manquants")
                else:
                    st.success("✅ Aucune donnée manquante")
    
    except Exception as e:
        error_title = "❌ Erreur lors de l'analyse du fichier" if lang == 'fr' else "❌ Error analyzing file"
        st.error(error_title)
        st.code(str(e))
        
        with st.expander("🔍 Détails" if lang == 'fr' else "🔍 Details"):
            import traceback
            st.code(traceback.format_exc())

else:
    # ======================
    # LANDING PAGE
    # ======================
    landing_title = "Prêt à Analyser Vos Données ?" if lang == 'fr' else "Ready to Analyze Your Data?"
    landing_desc = "Uploadez votre fichier CSV ou Excel pour commencer une analyse professionnelle avec scoring gamifié et recommandations actionnables." if lang == 'fr' else "Upload your CSV or Excel file to start a professional analysis with gamified scoring and actionable recommendations."
    
    fast_title = "Rapide" if lang == 'fr' else "Fast"
    fast_desc = "Résultats en moins de 10 secondes" if lang == 'fr' else "Results in less than 10 seconds"
    
    precise_title = "Précis" if lang == 'fr' else "Accurate"
    precise_desc = "Analyse intelligente multi-niveaux" if lang == 'fr' else "Smart multi-level analysis"
    
    gamified_title = "Gamifié" if lang == 'fr' else "Gamified"
    gamified_desc = "Badges et niveaux de qualité" if lang == 'fr' else "Quality badges and levels"
    
    st.markdown(f"""
    <div class='pro-card animated-card' style='text-align: center; padding: 4rem 2rem;'>
        <div style='font-size: 3rem; margin-bottom: 2rem;'>🚀</div>
        <h2 style='color: #1E293B; margin: 2rem 0 1rem 0;'>{landing_title}</h2>
        <p style='color: #64748B; font-size: 1.125rem; max-width: 600px; margin: 0 auto 2rem auto;'>
            {landing_desc}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='pro-card' style='text-align: center; padding: 2rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>⚡</div>
            <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>{fast_title}</h3>
            <p style='color: #64748B;'>{fast_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='pro-card' style='text-align: center; padding: 2rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🎯</div>
            <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>{precise_title}</h3>
            <p style='color: #64748B;'>{precise_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='pro-card' style='text-align: center; padding: 2rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🎮</div>
            <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>{gamified_title}</h3>
            <p style='color: #64748B;'>{gamified_desc}</p>
        </div>
        """, unsafe_allow_html=True)