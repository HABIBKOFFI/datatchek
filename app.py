# app.py - DataTchek Premium V2
"""
DataTchek - Plateforme Premium d'Analyse de Qualite des Donnees
Design dark theme inspire de DataTchek_Premium_v2.html
"""

import streamlit as st
import pandas as pd
import json
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

# Imports des modules avances
try:
    from utils.advanced_visualization import (
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

    def get_text(key, lang='fr', **kwargs):
        translations = {
            'quality_excellent': 'Qualite Exceptionnelle' if lang == 'fr' else 'Exceptional Quality',
            'quality_good': 'Excellente Qualite' if lang == 'fr' else 'Excellent Quality',
            'quality_average': 'Bonne Qualite' if lang == 'fr' else 'Good Quality',
            'quality_poor': 'Qualite A Ameliorer' if lang == 'fr' else 'Quality Needs Improvement',
            'level_expert': 'Expert Data Quality',
            'level_master': 'Data Quality Master',
            'level_advanced': 'Data Quality Avance' if lang == 'fr' else 'Data Quality Advanced',
            'level_beginner': 'Data Quality Debutant' if lang == 'fr' else 'Data Quality Beginner',
            'lines_analyzed': 'Lignes Analysees' if lang == 'fr' else 'Lines Analyzed',
            'columns_detected': 'Colonnes Detectees' if lang == 'fr' else 'Columns Detected',
            'duplicates': 'Doublons' if lang == 'fr' else 'Duplicates',
            'missing': 'Donnees Manquantes' if lang == 'fr' else 'Missing Data',
            'quality_avg': 'Qualite Moyenne' if lang == 'fr' else 'Average Quality',
            'conformity': 'Conformite' if lang == 'fr' else 'Conformity',
            'generate_pdf': 'Generer Rapport PDF' if lang == 'fr' else 'Generate PDF Report',
            'clean_data': 'Nettoyer Donnees' if lang == 'fr' else 'Clean Data',
            'export_analysis': 'Exporter Analyse' if lang == 'fr' else 'Export Analysis',
            'recommendations': 'Recommandations Prioritaires' if lang == 'fr' else 'Priority Recommendations',
            'priority_high': 'HAUTE PRIORITE' if lang == 'fr' else 'HIGH PRIORITY',
            'priority_medium': 'PRIORITE MOYENNE' if lang == 'fr' else 'MEDIUM PRIORITY',
            'priority_low': 'PRIORITE BASSE' if lang == 'fr' else 'LOW PRIORITY',
            'tab_data': 'Donnees' if lang == 'fr' else 'Data',
            'tab_graphs': 'Graphiques' if lang == 'fr' else 'Charts',
            'tab_distribution': 'Distribution',
            'tab_correlations': 'Correlations' if lang == 'fr' else 'Correlations',
            'tab_outliers': 'Anomalies' if lang == 'fr' else 'Outliers',
            'tab_duplicates': 'Doublons' if lang == 'fr' else 'Duplicates',
            'tab_missing': 'Valeurs Manquantes' if lang == 'fr' else 'Missing Values',
            'no_duplicates': 'Aucun doublon detecte - Excellent' if lang == 'fr' else 'No duplicates detected - Excellent',
            'no_missing': 'Aucune donnee manquante - Parfait' if lang == 'fr' else 'No missing data - Perfect',
        }
        return translations.get(key, key)

    def interpret_percentage(pct, lang='fr'):
        if pct == 0:
            return "Aucune" if lang == 'fr' else "None"
        elif pct < 5:
            return "Quelques donnees" if lang == 'fr' else "Few records"
        elif pct < 12.5:
            return "1 donnee sur 8" if lang == 'fr' else "1 in 8"
        elif pct < 25:
            return f"{pct:.1f}% (Modere)" if lang == 'fr' else f"{pct:.1f}% (Moderate)"
        elif pct < 50:
            return "La moitie" if lang == 'fr' else "Nearly half"
        else:
            return "La majorite" if lang == 'fr' else "Most"

    def format_missing_value(value):
        if pd.isna(value) or value is None or value == 'NaN' or value == 'None':
            return "Donnee manquante"
        return value

# Import optionnel du data cleaner
try:
    from utils.data_cleaner import DataCleaner
    DATA_CLEANER_AVAILABLE = True
except ImportError:
    DATA_CLEANER_AVAILABLE = False

try:
    from utils.files_naming import FileNamingManager
    FILE_NAMING_AVAILABLE = True
except ImportError:
    FILE_NAMING_AVAILABLE = False


# ======================
# CONFIGURATION
# ======================
st.set_page_config(
    page_title="DataTchek Premium - Analyse de Qualite",
    page_icon="https://raw.githubusercontent.com/HABIBKOFFI/datatchek/main/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'


# ======================
# CSS PREMIUM V2 - DARK THEME
# ======================
PREMIUM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {
    --primary: #5B4FD3;
    --primary-light: #7B72E5;
    --primary-dark: #3D34A8;
    --secondary: #00C9A7;
    --accent: #FF6B6B;
    --warning: #FFB347;
    --danger: #FF4757;
    --success: #2ED573;
    --bg: #0F0E17;
    --bg-secondary: #1A1830;
    --bg-tertiary: #221F38;
    --surface: #1E1C2E;
    --surface-elevated: #252340;
    --text: #FFFFFE;
    --text-secondary: #A7A4C0;
    --text-tertiary: #6B6882;
    --border: rgba(255,255,255,0.08);
    --border-bright: rgba(255,255,255,0.15);
    --shadow: rgba(0, 0, 0, 0.4);
    --shadow-color: rgba(91, 79, 211, 0.3);
    --glow: 0 0 40px rgba(91, 79, 211, 0.2);
    --radius: 14px;
    --radius-sm: 8px;
    --radius-lg: 20px;
}

/* Global Streamlit overrides */
.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', system-ui, sans-serif !important;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(91,79,211,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,201,167,0.08) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

* { font-family: 'DM Sans', system-ui, sans-serif !important; }
h1, h2, h3, h4, h5, h6, .section-title, .page-title {
    font-family: 'Syne', sans-serif !important;
}

/* Hide Streamlit defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden !important;}
[data-testid="stHeader"] { display: none !important; }

/* Sidebar Premium */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1830 0%, #0F0E17 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-secondary) !important;
    border-radius: 30px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.25s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--primary) !important;
    color: white !important;
    border-color: var(--primary) !important;
    box-shadow: 0 2px 8px rgba(91,79,211,0.4) !important;
}

.sidebar-content {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* Score Circle */
.score-circle-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 3rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}

.score-circle {
    width: 160px; height: 160px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-direction: column; color: white;
    box-shadow: 0 8px 40px rgba(46,213,115,0.35);
}
.score-circle .val {
    font-family: 'Syne', sans-serif !important;
    font-size: 3.5rem; font-weight: 800; line-height: 1;
}
.score-circle .lbl { font-size: 0.8rem; opacity: 0.9; margin-top: 0.25rem; }

/* KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--kpi-color, var(--primary));
    opacity: 0; transition: opacity 0.3s;
}
.kpi-card:hover {
    border-color: var(--border-bright);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px var(--shadow);
}
.kpi-card:hover::after { opacity: 1; }
.kpi-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
.kpi-label {
    font-size: 0.75rem; font-weight: 600; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.05em;
}
.kpi-icon {
    width: 36px; height: 36px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.kpi-val {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem; font-weight: 700; line-height: 1;
    margin-bottom: 0.3rem; color: var(--text);
}
.kpi-sub { font-size: 0.75rem; color: var(--text-tertiary); margin-top: 0.25rem; }

/* Quality Rings Section */
.quality-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    margin-bottom: 2rem;
}
.quality-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 2rem;
}
.quality-metric { text-align: center; }
.quality-label {
    font-size: 0.82rem; font-weight: 600; color: var(--text-secondary);
    margin-bottom: 1rem; display: flex; align-items: center;
    justify-content: center; gap: 0.5rem;
}
.progress-ring { width: 120px; height: 120px; margin: 0 auto; position: relative; }
.progress-ring svg { transform: rotate(-90deg); }
.progress-ring-circle { stroke: var(--bg-tertiary); fill: none; stroke-width: 7; }
.progress-ring-progress { fill: none; stroke-width: 7; stroke-linecap: round; transition: stroke-dashoffset 1.5s ease; }
.progress-ring-text {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
    font-family: 'Syne', sans-serif !important; font-size: 1.5rem; font-weight: 700;
}

/* Recommendation Cards */
.rec-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    transition: all 0.3s;
    margin-bottom: 0.75rem;
}
.rec-item:hover { transform: translateX(4px); box-shadow: 0 4px 20px var(--shadow); }
.rec-item.critical { border-left-color: var(--danger); background: rgba(255,71,87,0.05); }
.rec-item.high { border-left-color: var(--warning); background: rgba(255,179,71,0.05); }
.rec-item.medium { border-left-color: var(--primary-light); background: rgba(91,79,211,0.05); }
.rec-item.low { border-left-color: var(--success); background: rgba(46,213,115,0.05); }
.rec-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem; }
.rec-priority {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; display: flex; align-items: center; gap: 0.4rem;
}
.rec-title {
    font-family: 'Syne', sans-serif !important; font-size: 0.95rem;
    font-weight: 700; color: var(--text); margin-bottom: 0.4rem;
}
.rec-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; }
.ai-badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: rgba(91,79,211,0.15); border: 1px solid rgba(91,79,211,0.3);
    border-radius: 20px; padding: 0.15rem 0.5rem; font-size: 0.7rem;
    font-weight: 600; color: var(--primary-light); margin-bottom: 0.5rem;
}

/* Badge cards for gamification */
.badge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; }
.badge-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem; text-align: center;
    transition: all 0.3s;
}
.badge-card.unlocked:hover {
    border-color: var(--primary-light);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(91,79,211,0.3);
}
.badge-card.locked { opacity: 0.4; filter: grayscale(0.7); }
.badge-icon {
    width: 56px; height: 56px; margin: 0 auto 0.75rem; border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
}
.badge-card.locked .badge-icon { background: var(--bg-tertiary); }
.badge-name {
    font-family: 'Syne', sans-serif !important; font-size: 0.82rem;
    font-weight: 700; color: var(--text); margin-bottom: 0.2rem;
}
.badge-desc { font-size: 0.7rem; color: var(--text-tertiary); line-height: 1.4; }

/* XP bar */
.xp-container {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;
}
.xp-bar { height: 10px; background: var(--bg-tertiary); border-radius: 10px; overflow: hidden; }
.xp-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    border-radius: 10px; transition: width 1.5s ease;
}

/* Profile Card */
.profile-card {
    background: linear-gradient(135deg, var(--primary-dark) 0%, #1A1060 50%, rgba(0,201,167,0.3) 100%);
    border: 1px solid rgba(91,79,211,0.4); border-radius: var(--radius-lg);
    padding: 2rem; margin-bottom: 2rem; position: relative; overflow: hidden;
}
.profile-card::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 300px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,201,167,0.15), transparent 70%);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 20px rgba(91,79,211,0.4) !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(91,79,211,0.5) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--surface) !important;
    padding: 0.5rem;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(91,79,211,0.15) !important;
    color: var(--primary-light) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border-bright) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--primary-light) !important;
    box-shadow: var(--glow) !important;
}
[data-testid="stFileUploader"] * {
    color: var(--text-secondary) !important;
}

/* Selectbox, inputs, etc */
[data-testid="stSelectbox"], .stSelectbox > div {
    color: var(--text) !important;
}
.stSelectbox [data-baseweb="select"] {
    background: var(--surface) !important;
    border-color: var(--border-bright) !important;
}
.stSelectbox [data-baseweb="select"] * {
    color: var(--text) !important;
}

/* Data frame dark */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* Warning/Success/Error boxes */
.stAlert {
    border-radius: var(--radius) !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--secondary), #0EA5E9) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
}

/* Export section */
.export-section {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem; text-align: center; margin: 2rem 0;
}

/* Animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
.animated { animation: fadeUp 0.4s ease; }

/* Hero section */
.hero-section {
    max-width: 800px; margin: 2rem auto; text-align: center; padding: 0 1rem;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(91,79,211,0.2); border: 1px solid rgba(91,79,211,0.4);
    border-radius: 40px; padding: 0.4rem 1rem; font-size: 0.78rem;
    font-weight: 600; color: var(--primary-light); margin-bottom: 1.5rem;
    letter-spacing: 0.05em; text-transform: uppercase;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800; line-height: 1.1;
    letter-spacing: -0.03em; margin-bottom: 1.25rem;
    color: var(--text);
}
.hero-title em {
    font-style: normal;
    background: linear-gradient(135deg, var(--primary-light), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 1.05rem; color: var(--text-secondary);
    line-height: 1.7; max-width: 560px; margin: 0 auto 2rem;
}

/* Upload zone */
.upload-zone {
    background: var(--surface); border: 2px dashed var(--border-bright);
    border-radius: var(--radius-lg); padding: 3rem 2rem;
    max-width: 600px; margin: 0 auto 2rem; text-align: center;
    transition: all 0.35s;
}
.upload-zone:hover {
    border-color: var(--primary-light); transform: translateY(-3px);
    box-shadow: var(--glow);
}
.upload-icon {
    width: 64px; height: 64px; margin: 0 auto 1.25rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 32px rgba(91,79,211,0.4);
    font-size: 1.8rem;
}
.format-badges {
    display: flex; gap: 0.5rem; justify-content: center;
    flex-wrap: wrap; margin-top: 1.25rem;
}
.fmt-badge {
    background: var(--bg-tertiary); border: 1px solid var(--border-bright);
    padding: 0.3rem 0.65rem; border-radius: 6px; font-size: 0.7rem;
    font-weight: 700; color: var(--text-tertiary);
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.05em;
}

/* Feature cards */
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; max-width: 700px; margin: 0 auto; }
.feature-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem; text-align: center;
    transition: all 0.3s;
}
.feature-card:hover { border-color: var(--border-bright); transform: translateY(-3px); box-shadow: 0 8px 24px var(--shadow); }
.feature-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.feature-title { font-family: 'Syne', sans-serif !important; font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.3rem; }
.feature-desc { font-size: 0.8rem; color: var(--text-secondary); }

/* Dash file header */
.dash-top { display: flex; justify-content: space-between; align-items: center; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }
.dash-file { display: flex; align-items: center; gap: 1rem; }
.dash-file-icon {
    width: 50px; height: 50px; border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; box-shadow: 0 4px 16px rgba(91,79,211,0.35);
    font-size: 1.3rem;
}
.dash-file h2 { font-family: 'Syne', sans-serif !important; font-size: 1.15rem; font-weight: 700; color: var(--text); margin: 0; }
.dash-file .meta { font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem; }
.score-pill {
    background: linear-gradient(135deg, rgba(46,213,115,0.15), rgba(0,201,167,0.15));
    border: 1px solid rgba(46,213,115,0.3); border-radius: 50px;
    padding: 0.6rem 1.25rem; text-align: center;
    display: flex; flex-direction: column; align-items: center; gap: 0.1rem;
}
.score-pill .label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--secondary);
}
.score-pill .value {
    font-family: 'Syne', sans-serif !important; font-size: 2.2rem;
    font-weight: 800; color: var(--success); line-height: 1;
}

/* Logo */
.logo-container {
    text-align: center; padding: 1.5rem 0;
}
.logo-text {
    font-family: 'Syne', sans-serif !important; font-weight: 800;
    font-size: 1.5rem; color: var(--text);
}
.logo-text span { color: var(--secondary); }
.logo-icon {
    width: 34px; height: 34px; display: inline-flex;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 9px; align-items: center; justify-content: center;
    box-shadow: 0 0 20px rgba(91,79,211,0.5);
    margin-right: 0.5rem; vertical-align: middle;
    font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
    .kpi-grid { grid-template-columns: 1fr 1fr; }
    .quality-grid { grid-template-columns: 1fr 1fr; }
    .feature-grid { grid-template-columns: 1fr; }
    .dash-top { flex-direction: column; align-items: flex-start; }
}
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


# ======================
# HELPER FUNCTIONS
# ======================
def get_quality_badge(score):
    lang = st.session_state.lang
    if score >= 90:
        return {'name': 'PLATINUM', 'emoji': '💎', 'class': 'badge-platinum',
                'message': get_text('quality_excellent', lang), 'points': 1000,
                'color': '#7B72E5'}
    elif score >= 75:
        return {'name': 'GOLD', 'emoji': '🏆', 'class': 'badge-gold',
                'message': get_text('quality_good', lang), 'points': 750,
                'color': '#FFB347'}
    elif score >= 60:
        return {'name': 'SILVER', 'emoji': '🥈', 'class': 'badge-silver',
                'message': get_text('quality_average', lang), 'points': 500,
                'color': '#A7A4C0'}
    else:
        return {'name': 'BRONZE', 'emoji': '🥉', 'class': 'badge-bronze',
                'message': get_text('quality_poor', lang), 'points': 250,
                'color': '#CD7F32'}


def get_level(score):
    lang = st.session_state.lang
    if score >= 90:
        return get_text('level_expert', lang), "🎓", 8
    elif score >= 75:
        return get_text('level_master', lang), "⭐", 6
    elif score >= 60:
        return get_text('level_advanced', lang), "📊", 4
    else:
        return get_text('level_beginner', lang), "🌱", 2


def make_progress_ring(pct, color, size=120):
    """Generate SVG progress ring"""
    r = (size / 2) - 6
    circumference = 2 * 3.14159 * r
    offset = circumference * (1 - pct / 100)
    return f"""
    <div class="progress-ring" style="width:{size}px;height:{size}px;">
        <svg width="{size}" height="{size}">
            <circle class="progress-ring-circle" cx="{size//2}" cy="{size//2}" r="{r}"/>
            <circle class="progress-ring-progress" cx="{size//2}" cy="{size//2}" r="{r}"
                stroke="{color}" stroke-dasharray="{circumference:.3f}" stroke-dashoffset="{offset:.3f}"/>
        </svg>
        <div class="progress-ring-text" style="color:{color}">{pct:.0f}%</div>
    </div>
    """


def compute_quality_dimensions(results):
    """Compute real quality dimension scores"""
    completeness = 100 - results.get('missing_values', {}).get('percentage', 0)

    semantic = results.get('semantic_validation', {})
    if semantic:
        conformity_rates = [v.get('conformity_rate', 100) for v in semantic.values()]
        validity = sum(conformity_rates) / len(conformity_rates) if conformity_rates else 100
    else:
        validity = min(100, completeness + 5)

    total_rows = results.get('total_rows', 1)
    dup_count = results.get('duplicates', {}).get('count', 0)
    uniqueness = 100 - (dup_count / total_rows * 100) if total_rows > 0 else 100

    total_cols = results.get('total_columns', 1)
    quality_metrics = results.get('quality_metrics', {})
    low_card = sum(1 for m in quality_metrics.values() if m.get('unique_percentage', 100) < 5)
    consistency = max(0, 100 - (low_card / total_cols * 100)) if total_cols > 0 else 100

    return {
        'completeness': round(completeness, 1),
        'validity': round(validity, 1),
        'uniqueness': round(uniqueness, 1),
        'consistency': round(consistency, 1),
    }


# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div><span class="logo-icon">✓</span><span class="logo-text">Data<span>Tchek</span></span></div>
        <p style="font-size:0.78rem; color:var(--text-secondary); margin-top:0.5rem;">
            Plateforme Premium d'Analyse de Qualite
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Language switcher
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇫🇷 FR", use_container_width=True, key="lang_fr"):
            st.session_state.lang = 'fr'
            st.rerun()
    with col2:
        if st.button("🇬🇧 EN", use_container_width=True, key="lang_en"):
            st.session_state.lang = 'en'
            st.rerun()

    st.markdown("---")
    lang = st.session_state.lang

    features_title = "Fonctionnalites" if lang == 'fr' else "Features"
    st.markdown(f"""
    <div class="sidebar-content">
        <h4 style="margin:0 0 0.75rem 0; font-size:0.9rem;">✨ {features_title}</h4>
        <ul style="line-height:2; padding-left:1.25rem; font-size:0.82rem; color:var(--text-secondary);">
            <li>Detection intelligente</li>
            <li>Scoring gamifie</li>
            <li>Rapports PDF Executive</li>
            <li>Visualisations avancees</li>
            <li>Nettoyage automatique</li>
            <li>Multilingue FR/EN</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    levels_title = "Niveaux de Qualite" if lang == 'fr' else "Quality Levels"
    st.markdown(f"""
    <div class="sidebar-content">
        <h4 style="margin:0 0 0.75rem 0; font-size:0.9rem;">🎮 {levels_title}</h4>
        <div style="font-size:0.82rem; color:var(--text-secondary); line-height:2;">
            💎 90-100 : Platinum<br>
            🏆 75-89 : Gold<br>
            🥈 60-74 : Silver<br>
            🥉 0-59 : Bronze
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:0.75rem 0;">
        <p style="font-size:0.78rem; color:var(--text-tertiary);">🚀 Version 2.0 Premium</p>
        <p style="font-size:0.82rem; font-weight:600; color:var(--text-secondary);">HABIB KOFFI</p>
        <p style="font-size:0.7rem; color:var(--text-tertiary);">2026 DataTchek</p>
    </div>
    """, unsafe_allow_html=True)


# ======================
# MAIN CONTENT
# ======================
lang = st.session_state.lang

upload_label = "Deposez votre fichier ici" if lang == 'fr' else "Drop your file here"
upload_help = "Formats: CSV, Excel (.xlsx, .xls) | Max: 200MB"

uploaded_file = st.file_uploader(upload_label, type=["csv", "xlsx", "xls"], help=upload_help)


# ======================
# ANALYSE
# ======================
if uploaded_file:
    try:
        loading_text = "Analyse en cours..." if lang == 'fr' else "Analyzing..."
        with st.spinner(loading_text):
            if uploaded_file.name.endswith(".csv"):
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="iso-8859-1")
            else:
                df = pd.read_excel(uploaded_file)

        # Run analysis
        with st.spinner("🧠 Analyse intelligente..." if lang == 'fr' else "🧠 Smart analysis..."):
            results = validate_dataframe(df)

        score = results["quality_score"]
        badge = get_quality_badge(score)
        level_name, level_emoji, level_num = get_level(score)
        dims = compute_quality_dimensions(results)

        # ---- DASH TOP ----
        analyzed_text = f"{'Analyse' if lang == 'fr' else 'Analyzed'} : {datetime.now().strftime('%d %b %Y %H:%M')}"
        size_text = f"{len(df):,} {'lignes' if lang == 'fr' else 'rows'} x {len(df.columns)} {'colonnes' if lang == 'fr' else 'columns'}"
        score_label = "Score Qualite" if lang == 'fr' else "Quality Score"

        st.markdown(f"""
        <div class="dash-top animated">
            <div class="dash-file">
                <div class="dash-file-icon">📄</div>
                <div>
                    <h2>{uploaded_file.name}</h2>
                    <div class="meta">{analyzed_text} &middot; {size_text}</div>
                </div>
            </div>
            <div class="score-pill">
                <div class="label">{score_label}</div>
                <div class="value">{score}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- KPI GRID ----
        missing_pct = results['missing_values']['percentage']
        try:
            missing_text_val = interpret_percentage(missing_pct, lang)
        except Exception:
            missing_text_val = f"{missing_pct:.1f}%"

        dup_count = results['duplicates']['count']
        dup_rate = (dup_count / results['total_rows'] * 100) if results['total_rows'] > 0 else 0
        unique_count = sum(m.get('unique_count', 0) for m in results.get('quality_metrics', {}).values())
        unique_ratio = (unique_count / (results['total_rows'] * results['total_columns']) * 100) if (results['total_rows'] * results['total_columns']) > 0 else 0

        # Compute real conformity
        conformity = round(dims['validity'], 1)

        kpi_records = "Total Enregistrements" if lang == 'fr' else "Total Records"
        kpi_complete = "Completude" if lang == 'fr' else "Completeness"
        kpi_issues = "Problemes Detectes" if lang == 'fr' else "Detected Issues"
        kpi_dupes = get_text('duplicates', lang)
        kpi_conformity = get_text('conformity', lang)
        kpi_cols = "Types de Donnees" if lang == 'fr' else "Data Types"

        num_cols = len(df.select_dtypes(include=['number']).columns)
        text_cols = len(df.columns) - num_cols

        st.markdown(f"""
        <div class="kpi-grid animated">
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#5B4FD3,#7B72E5)">
                <div class="kpi-head"><div class="kpi-label">{kpi_records}</div><div class="kpi-icon" style="background:rgba(91,79,211,0.15)">📊</div></div>
                <div class="kpi-val">{results['total_rows']:,}</div>
                <div class="kpi-sub">{results['total_columns']} {'colonnes' if lang == 'fr' else 'columns'}</div>
            </div>
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#2ED573,#00C9A7)">
                <div class="kpi-head"><div class="kpi-label">{kpi_complete}</div><div class="kpi-icon" style="background:rgba(46,213,115,0.12)">✅</div></div>
                <div class="kpi-val">{dims['completeness']:.1f}%</div>
                <div class="kpi-sub">{results['missing_values']['total']:,} {'manquantes' if lang == 'fr' else 'missing'}</div>
            </div>
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#FFB347,#FF9A3C)">
                <div class="kpi-head"><div class="kpi-label">{kpi_issues}</div><div class="kpi-icon" style="background:rgba(255,179,71,0.15)">⚠️</div></div>
                <div class="kpi-val">{dup_count + results['missing_values']['total']:,}</div>
                <div class="kpi-sub">{'doublons + manquants' if lang == 'fr' else 'duplicates + missing'}</div>
            </div>
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#FF6B6B,#FF4757)">
                <div class="kpi-head"><div class="kpi-label">{kpi_dupes}</div><div class="kpi-icon" style="background:rgba(255,107,107,0.12)">🔄</div></div>
                <div class="kpi-val">{dup_count}</div>
                <div class="kpi-sub">{dup_rate:.2f}% {'de duplication' if lang == 'fr' else 'duplication rate'}</div>
            </div>
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#00C9A7,#0EA5E9)">
                <div class="kpi-head"><div class="kpi-label">{kpi_conformity}</div><div class="kpi-icon" style="background:rgba(0,201,167,0.12)">📈</div></div>
                <div class="kpi-val">{conformity}%</div>
                <div class="kpi-sub">{'validite calculee' if lang == 'fr' else 'computed validity'}</div>
            </div>
            <div class="kpi-card" style="--kpi-color: linear-gradient(90deg,#14B8A6,#00C9A7)">
                <div class="kpi-head"><div class="kpi-label">{kpi_cols}</div><div class="kpi-icon" style="background:rgba(20,184,166,0.12)">📋</div></div>
                <div class="kpi-val">{results['total_columns']}</div>
                <div class="kpi-sub">{num_cols} {'numeriques' if lang == 'fr' else 'numeric'} &middot; {text_cols} {'texte' if lang == 'fr' else 'text'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- QUALITY DIMENSIONS (Progress Rings) ----
        dims_title = "Analyse des Dimensions Qualite" if lang == 'fr' else "Quality Dimensions Analysis"
        dim_labels = {
            'completeness': 'Completude' if lang == 'fr' else 'Completeness',
            'validity': 'Validite' if lang == 'fr' else 'Validity',
            'consistency': 'Coherence' if lang == 'fr' else 'Consistency',
            'uniqueness': 'Unicite' if lang == 'fr' else 'Uniqueness',
        }
        dim_colors = {
            'completeness': '#2ED573',
            'validity': '#00C9A7',
            'consistency': '#7B72E5',
            'uniqueness': '#8B5CF6',
        }

        rings_html = ""
        for key in ['completeness', 'validity', 'consistency', 'uniqueness']:
            rings_html += f"""
            <div class="quality-metric">
                <div class="quality-label">{dim_labels[key]}</div>
                {make_progress_ring(dims[key], dim_colors[key])}
            </div>
            """

        st.markdown(f"""
        <div class="quality-section animated">
            <h3 class="section-title" style="margin-bottom:1.5rem;">{dims_title}</h3>
            <div class="quality-grid">{rings_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # ---- ACTIONS ----
        actions_title = "Actions Rapides" if lang == 'fr' else "Quick Actions"
        st.markdown(f"<h3 style='color:var(--text); margin:2rem 0 1rem 0;'>⚡ {actions_title}</h3>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            pdf_label = get_text('generate_pdf', lang)
            if st.button(f"📄 {pdf_label}", use_container_width=True):
                with st.spinner("Generating..." if lang == 'en' else "Generation..."):
                    try:
                        if EXECUTIVE_PDF_AVAILABLE:
                            pdf = create_executive_pdf(df, results, uploaded_file.name, lang)
                        else:
                            pdf = create_pdf_report(df, results)
                        dl_text = "Telecharger PDF" if lang == 'fr' else "Download PDF"
                        st.download_button(
                            f"⬇️ {dl_text}", pdf,
                            file_name=f"rapport_executive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf", use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"{'Erreur' if lang == 'fr' else 'Error'}: {e}")

        with col2:
            clean_label = get_text('clean_data', lang)
            if st.button(f"🧹 {clean_label}", use_container_width=True):
                if DATA_CLEANER_AVAILABLE:
                    with st.spinner("Nettoyage..." if lang == 'fr' else "Cleaning..."):
                        try:
                            cleaner = DataCleaner(df.copy())
                            cleaned_df, log = cleaner.auto_clean()
                            st.success(f"{'Nettoyage termine' if lang == 'fr' else 'Cleaning complete'} - {len(log)} {'operations' if lang == 'fr' else 'operations'}")

                            for entry in log[:5]:
                                st.markdown(f"- {entry}")

                            csv_buffer = io.BytesIO()
                            cleaned_df.to_csv(csv_buffer, index=False, encoding='utf-8')
                            csv_data = csv_buffer.getvalue()

                            if FILE_NAMING_AVAILABLE:
                                naming = FileNamingManager(uploaded_file.name)
                                clean_filename = naming.generate_cleaned_filename()
                            else:
                                clean_filename = f"{uploaded_file.name.rsplit('.', 1)[0]}_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                            st.download_button(
                                "⬇️ " + ("Telecharger CSV nettoye" if lang == 'fr' else "Download cleaned CSV"),
                                csv_data, file_name=clean_filename,
                                mime="text/csv", use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"{'Erreur' if lang == 'fr' else 'Error'}: {e}")
                else:
                    st.info("Module DataCleaner non disponible" if lang == 'fr' else "DataCleaner module not available")

        with col3:
            export_label = get_text('export_analysis', lang)
            if st.button(f"📤 {export_label}", use_container_width=True):
                try:
                    export_data = {
                        "dataset": uploaded_file.name,
                        "timestamp": datetime.now().isoformat(),
                        "quality_score": score,
                        "total_rows": results['total_rows'],
                        "total_columns": results['total_columns'],
                        "dimensions": dims,
                        "duplicates_count": dup_count,
                        "missing_total": results['missing_values']['total'],
                        "missing_percentage": missing_pct,
                        "missing_by_column": results['missing_values'].get('by_column', {}),
                    }
                    json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)

                    if FILE_NAMING_AVAILABLE:
                        naming = FileNamingManager(uploaded_file.name)
                        json_filename = naming.generate_analysis_filename()
                    else:
                        json_filename = f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                    st.download_button(
                        "⬇️ " + ("Telecharger JSON" if lang == 'fr' else "Download JSON"),
                        json_data, file_name=json_filename,
                        mime="application/json", use_container_width=True
                    )
                except Exception as e:
                    st.error(f"{'Erreur' if lang == 'fr' else 'Error'}: {e}")

        # ---- RECOMMENDATIONS ----
        reco_title = get_text('recommendations', lang)
        st.markdown(f"<h3 style='color:var(--text); margin:2.5rem 0 1rem 0;'>💡 {reco_title}</h3>", unsafe_allow_html=True)

        recommendations = generate_recommendations(results)

        if recommendations:
            recs_html = ""
            for idx, rec in enumerate(recommendations[:8]):
                # Extract message from dict or use string directly
                if isinstance(rec, dict):
                    msg = rec.get('message', str(rec))
                    priority = rec.get('priority', 'MOYENNE')
                    action = rec.get('action', '')
                else:
                    msg = str(rec)
                    priority = 'HAUTE' if idx < 2 else 'MOYENNE' if idx < 5 else 'BASSE'
                    action = ''

                # Map priority to CSS class and color
                priority_upper = priority.upper()
                if priority_upper in ('HAUTE', 'HIGH', 'CRITIQUE', 'CRITICAL'):
                    css_class = 'critical' if 'CRITIQ' in priority_upper or 'CRITICAL' in priority_upper else 'high'
                    priority_label = get_text('priority_high', lang)
                    priority_color = '#FF4757' if css_class == 'critical' else '#FFB347'
                    priority_icon = '⬤' if css_class == 'critical' else '▲'
                elif priority_upper in ('MOYENNE', 'MEDIUM'):
                    css_class = 'medium'
                    priority_label = get_text('priority_medium', lang)
                    priority_color = '#7B72E5'
                    priority_icon = '●'
                else:
                    css_class = 'low'
                    priority_label = get_text('priority_low', lang)
                    priority_color = '#2ED573'
                    priority_icon = '✓'

                ai_tag = '<div class="ai-badge">🤖 AI Analysis</div>' if idx < 3 else ''

                recs_html += f"""
                <div class="rec-item {css_class}">
                    <div class="rec-head">
                        <div class="rec-priority" style="color:{priority_color}">{priority_icon} {priority_label}</div>
                    </div>
                    {ai_tag}
                    <div class="rec-title">{msg}</div>
                    {'<div class="rec-desc">' + action + '</div>' if action else ''}
                </div>
                """

            st.markdown(recs_html, unsafe_allow_html=True)
        else:
            perfect_msg = "Aucune recommandation - Donnees de qualite excellente !" if lang == 'fr' else "No recommendations - Excellent data quality!"
            st.success(f"✅ {perfect_msg}")

        # ---- GAMIFICATION SECTION ----
        gami_title = "Progression" if lang == 'fr' else "Progress"
        st.markdown(f"<h3 style='color:var(--text); margin:2.5rem 0 1rem 0;'>🎮 {gami_title}</h3>", unsafe_allow_html=True)

        xp = badge['points']
        xp_max = 1000
        xp_pct = min(100, (xp / xp_max) * 100)

        st.markdown(f"""
        <div class="profile-card animated">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; position:relative;">
                <div style="display:flex; align-items:center; gap:1rem;">
                    <div style="width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,0.15);
                         display:flex;align-items:center;justify-content:center;font-size:2rem;
                         border:2px solid rgba(255,255,255,0.25);">{badge['emoji']}</div>
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:white;">{badge['name']}</div>
                        <div style="font-size:0.82rem;opacity:0.8;color:rgba(255,255,255,0.85);">
                            {'Niveau' if lang == 'fr' else 'Level'} {level_num} &middot; {level_name}
                        </div>
                    </div>
                </div>
                <div style="display:flex;gap:2rem;text-align:right;">
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:white;">{xp}</div>
                        <div style="font-size:0.7rem;opacity:0.75;color:rgba(255,255,255,0.8);">{'Points' if lang == 'fr' else 'Points'}</div>
                    </div>
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:white;">{score}</div>
                        <div style="font-size:0.7rem;opacity:0.75;color:rgba(255,255,255,0.8);">Score</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # XP Bar
        next_level = "Expert" if level_num < 8 else "Max"
        st.markdown(f"""
        <div class="xp-container">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;">
                    {'Progression vers' if lang == 'fr' else 'Progress to'} {next_level}
                </div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--primary-light);">{xp_pct:.0f}%</div>
            </div>
            <div class="xp-bar"><div class="xp-fill" style="width:{xp_pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Badges earned
        badges_title = "Badges" if lang == 'fr' else "Badges"
        badge_items = [
            ("⭐", "Premiers Pas" if lang == 'fr' else "First Steps", "Premier dataset" if lang == 'fr' else "First dataset", True),
            ("📊", "Analyste" if lang == 'fr' else "Analyst", f"Score {score}" if score >= 50 else "Score 50+", score >= 50),
            ("🏆", "Champion" if lang == 'fr' else "Champion", "Score 90+" if lang == 'fr' else "Score 90+", score >= 90),
            ("💎", "Perfectionniste" if lang == 'fr' else "Perfectionist", "Score 95+" if lang == 'fr' else "Score 95+", score >= 95),
            ("🧹", "Nettoyeur" if lang == 'fr' else "Cleaner", "Donnees nettoyees" if lang == 'fr' else "Data cleaned", False),
            ("⚡", "Speed Demon", "< 10s", True),
        ]

        badges_html = '<div class="badge-grid">'
        for icon, name, desc, unlocked in badge_items:
            state = "unlocked" if unlocked else "locked"
            badges_html += f"""
            <div class="badge-card {state}">
                <div class="badge-icon">{'🔒' if not unlocked else icon}</div>
                <div class="badge-name">{name}</div>
                <div class="badge-desc">{desc}</div>
            </div>
            """
        badges_html += '</div>'

        st.markdown(f"""
        <div class="quality-section" style="margin-top:1rem;">
            <h4 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:1rem;">{badges_title}</h4>
            {badges_html}
        </div>
        """, unsafe_allow_html=True)

        # ---- TABS D'ANALYSE ----
        analysis_title = "Analyse Approfondie" if lang == 'fr' else "In-Depth Analysis"
        st.markdown(f"<h3 style='color:var(--text); margin:2.5rem 0 1rem 0;'>🔬 {analysis_title}</h3>", unsafe_allow_html=True)

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

            with tabs[0]:
                st.dataframe(df.head(50), use_container_width=True, height=400)

            with tabs[1]:
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
                    except Exception:
                        pass
                    try:
                        st.plotly_chart(create_quality_score_breakdown(results), use_container_width=True)
                    except Exception:
                        pass
                with col2:
                    try:
                        st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
                    except Exception:
                        pass
                    try:
                        st.plotly_chart(create_column_quality_heatmap(df), use_container_width=True)
                    except Exception:
                        pass

            with tabs[2]:
                sel_label = "Selectionnez une colonne" if lang == 'fr' else "Select a column"
                selected_col = st.selectbox(sel_label, df.columns.tolist())
                try:
                    fig_dist = create_distribution_analysis(df, selected_col)
                    if fig_dist:
                        st.plotly_chart(fig_dist, use_container_width=True)
                except Exception as e:
                    st.warning(f"{'Impossible d afficher' if lang == 'fr' else 'Cannot display'}: {e}")
                try:
                    fig_pattern = create_pattern_detection(df, selected_col)
                    if fig_pattern:
                        st.plotly_chart(fig_pattern, use_container_width=True)
                except Exception:
                    pass

            with tabs[3]:
                try:
                    fig_corr = create_correlation_heatmap(df)
                    if fig_corr:
                        st.plotly_chart(fig_corr, use_container_width=True)
                    else:
                        st.info("Pas assez de colonnes numeriques" if lang == 'fr' else "Not enough numeric columns")
                except Exception as e:
                    st.warning(f"{'Erreur' if lang == 'fr' else 'Error'}: {e}")
                try:
                    fig_unique = create_value_uniqueness_analysis(df)
                    if fig_unique:
                        st.plotly_chart(fig_unique, use_container_width=True)
                except Exception:
                    pass

            with tabs[4]:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    sel_num = st.selectbox(
                        "Colonne numerique" if lang == 'fr' else "Numeric column",
                        numeric_cols
                    )
                    try:
                        fig_out = detect_outliers_visualization(df, sel_num)
                        if fig_out:
                            st.plotly_chart(fig_out, use_container_width=True)
                    except Exception as e:
                        st.warning(f"{'Erreur' if lang == 'fr' else 'Error'}: {e}")
                else:
                    st.info("Aucune colonne numerique" if lang == 'fr' else "No numeric columns found")

            with tabs[5]:
                dup_count_val = results["duplicates"]["count"]
                if dup_count_val > 0:
                    st.warning(f"⚠️ {dup_count_val} {'doublons detectes' if lang == 'fr' else 'duplicates detected'}")
                    st.dataframe(results["duplicates"]["data"], use_container_width=True, height=400)
                else:
                    st.success(f"✅ {get_text('no_duplicates', lang)}")

            with tabs[6]:
                missing_total = results["missing_values"]["total"]
                if missing_total > 0:
                    st.warning(f"⚠️ {missing_total:,} {'valeurs manquantes' if lang == 'fr' else 'missing values'} ({results['missing_values']['percentage']}%)")
                    try:
                        fig_mp = create_missing_data_patterns(df)
                        if fig_mp:
                            st.plotly_chart(fig_mp, use_container_width=True)
                    except Exception:
                        pass

                    missing_by_col = pd.DataFrame.from_dict(
                        results["missing_values"]["by_column"], orient='index',
                        columns=['Valeurs Manquantes' if lang == 'fr' else 'Missing Values']
                    )
                    col_name = 'Valeurs Manquantes' if lang == 'fr' else 'Missing Values'
                    missing_by_col = missing_by_col[missing_by_col[col_name] > 0]
                    missing_by_col = missing_by_col.sort_values(col_name, ascending=False)
                    pct_name = 'Pourcentage' if lang == 'fr' else 'Percentage'
                    missing_by_col[pct_name] = (missing_by_col[col_name] / len(df) * 100).round(2)
                    st.dataframe(missing_by_col, use_container_width=True)
                else:
                    st.success(f"✅ {get_text('no_missing', lang)}")
        else:
            # Fallback basique
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
                    except Exception:
                        pass
                with col2:
                    try:
                        st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
                    except Exception:
                        pass
            with tabs[2]:
                if results["duplicates"]["count"] > 0:
                    st.warning(f"⚠️ {results['duplicates']['count']} {'doublons' if lang == 'fr' else 'duplicates'}")
                    st.dataframe(results["duplicates"]["data"], use_container_width=True)
                else:
                    st.success(f"✅ {get_text('no_duplicates', lang)}")
            with tabs[3]:
                if results["missing_values"]["total"] > 0:
                    st.warning(f"⚠️ {results['missing_values']['total']:,} {'manquants' if lang == 'fr' else 'missing'}")
                else:
                    st.success(f"✅ {get_text('no_missing', lang)}")

    except Exception as e:
        error_title = "Erreur lors de l'analyse" if lang == 'fr' else "Error analyzing file"
        st.error(f"❌ {error_title}")
        st.code(str(e))
        with st.expander("🔍 Details"):
            import traceback
            st.code(traceback.format_exc())

else:
    # ---- LANDING PAGE ----
    hero_title = "Transformez" if lang == 'fr' else "Transform"
    hero_rest = "la qualite de vos donnees" if lang == 'fr' else "your data quality"
    hero_sub = "Profilage automatique, recommandations intelligentes et scoring en temps reel pour des donnees d'excellence." if lang == 'fr' else "Automatic profiling, intelligent recommendations and real-time quality scoring for excellent data."
    hero_badge_text = "Propulse par l'IA" if lang == 'fr' else "Powered by AI"

    st.markdown(f"""
    <div class="hero-section animated">
        <div class="hero-badge">● {hero_badge_text}</div>
        <h1 class="hero-title"><em>{hero_title}</em> {hero_rest}</h1>
        <p class="hero-subtitle">{hero_sub}</p>
    </div>
    """, unsafe_allow_html=True)

    # Upload zone visual
    upload_title = "Deposez votre fichier ici" if lang == 'fr' else "Drop your file here"
    upload_sub = "ou cliquez pour parcourir vos fichiers" if lang == 'fr' else "or click to browse your files"

    st.markdown(f"""
    <div class="upload-zone animated">
        <div class="upload-icon">📂</div>
        <h3 style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:0.4rem;">{upload_title}</h3>
        <p style="color:var(--text-secondary);font-size:0.85rem;">{upload_sub}</p>
        <div class="format-badges">
            <span class="fmt-badge">.CSV</span>
            <span class="fmt-badge">.XLSX</span>
            <span class="fmt-badge">.XLS</span>
            <span class="fmt-badge">.JSON</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features
    fast = "Rapide" if lang == 'fr' else "Fast"
    fast_d = "Resultats en moins de 10 secondes" if lang == 'fr' else "Results in under 10 seconds"
    precise = "Precis" if lang == 'fr' else "Accurate"
    precise_d = "Analyse intelligente multi-niveaux" if lang == 'fr' else "Smart multi-level analysis"
    gamified = "Gamifie" if lang == 'fr' else "Gamified"
    gamified_d = "Badges et niveaux de qualite" if lang == 'fr' else "Quality badges and levels"

    st.markdown(f"""
    <div class="feature-grid animated" style="margin-top:2rem;">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">{fast}</div>
            <div class="feature-desc">{fast_d}</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">{precise}</div>
            <div class="feature-desc">{precise_d}</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎮</div>
            <div class="feature-title">{gamified}</div>
            <div class="feature-desc">{gamified_d}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
