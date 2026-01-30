# app.py - DataTchek V2 Pro Edition
"""
DataTchek - Plateforme professionnelle d'analyse de qualité des données
Interface moderne et gamifiée
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

from utils.validators import validate_dataframe, generate_recommendations
from utils.visualizations import (
    create_score_gauge,
    create_problems_bar_chart,
    create_missing_data_chart,
    create_quality_distribution_pie,
    create_column_quality_bar,
)
from utils.pdf_generator import create_pdf_report


# ======================
# CONFIGURATION
# ======================
st.set_page_config(
    page_title="DataTchek Pro - Analyse de Qualité",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ======================
# CSS PROFESSIONNEL & GAMIFIÉ
# ======================
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Variables globales */
:root {
    --primary-color: #2563EB;
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --danger-color: #EF4444;
    --dark-bg: #1E293B;
    --light-bg: #F8FAFC;
    --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Reset & Base */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
    padding: 2rem 1rem;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .sidebar-content {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

/* Cards professionnelles */
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

/* Score principal */
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

/* Badges de qualité */
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
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.badge-platinum {
    background: linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%);
    color: #4338CA;
    box-shadow: 0 4px 12px rgba(67, 56, 202, 0.3);
}

.badge-gold {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    color: #92400E;
    box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
}

.badge-silver {
    background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
    color: #374151;
    box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}

.badge-bronze {
    background: linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%);
    color: #9A3412;
    box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3);
}

/* Métriques modernes */
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

/* Barre de progression gamifiée */
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

/* Recommandations stylées */
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

/* Boutons stylés */
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

/* Tabs stylés */
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

/* Animations */
@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animated-card {
    animation: slideInUp 0.6s ease-out;
}

/* Upload zone */
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

/* Icônes emoji plus grandes */
.big-emoji {
    font-size: 3rem;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

/* Confetti effect */
@keyframes confetti {
    0% { transform: translateY(0) rotate(0deg); }
    100% { transform: translateY(100vh) rotate(360deg); }
}

.confetti {
    position: fixed;
    width: 10px;
    height: 10px;
    background: #667EEA;
    animation: confetti 3s linear infinite;
}

/* Hide Streamlit branding */
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
    if score >= 90:
        return {
            'name': 'PLATINUM',
            'emoji': '💎',
            'class': 'badge-platinum',
            'message': 'Qualité Exceptionnelle',
            'points': 1000
        }
    elif score >= 75:
        return {
            'name': 'GOLD',
            'emoji': '🏆',
            'class': 'badge-gold',
            'message': 'Excellente Qualité',
            'points': 750
        }
    elif score >= 60:
        return {
            'name': 'SILVER',
            'emoji': '🥈',
            'class': 'badge-silver',
            'message': 'Bonne Qualité',
            'points': 500
        }
    else:
        return {
            'name': 'BRONZE',
            'emoji': '🥉',
            'class': 'badge-bronze',
            'message': 'Qualité À Améliorer',
            'points': 250
        }

def get_level(score):
    """Calcule le niveau de qualité"""
    if score >= 90:
        return "Expert Data Quality", "🎓"
    elif score >= 75:
        return "Data Quality Master", "⭐"
    elif score >= 60:
        return "Data Quality Advanced", "📊"
    else:
        return "Data Quality Débutant", "🌱"


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
    
    st.markdown("---")
    
    st.markdown("""
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>✨ Fonctionnalités</h3>
        <ul style='line-height: 2; padding-left: 1.5rem;'>
            <li>Détection intelligente</li>
            <li>Validation CI (+225)</li>
            <li>Scoring gamifié</li>
            <li>Rapports PDF Pro</li>
            <li>Graphiques interactifs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='sidebar-content'>
        <h3 style='margin-top: 0;'>🎮 Niveaux de Qualité</h3>
        <div style='padding: 0.5rem 0;'>
            💎 90-100: Platinum<br>
            🏆 75-89: Gold<br>
            🥈 60-74: Silver<br>
            🥉 0-59: Bronze
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
st.markdown("""
<div style='text-align: center; padding: 2rem 0 3rem 0;'>
    <h1 style='font-size: 3rem; margin: 0; color: #1E293B;'>
        Analysez la Qualité de Vos Données
    </h1>
    <p style='font-size: 1.25rem; color: #64748B; margin-top: 1rem;'>
        Uploadez votre fichier et obtenez une analyse professionnelle en quelques secondes
    </p>
</div>
""", unsafe_allow_html=True)


# ======================
# UPLOAD SECTION
# ======================
st.markdown("<div class='pro-card animated-card'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    uploaded_file = st.file_uploader(
        "📁 Glissez-déposez votre fichier ici",
        type=["csv", "xlsx", "xls"],
        help="Formats: CSV, Excel (.xlsx, .xls) | Taille max: 200MB"
    )

st.markdown("</div>", unsafe_allow_html=True)


# ======================
# ANALYSE
# ======================
if uploaded_file:
    try:
        # Chargement
        with st.spinner("🔄 Chargement du fichier..."):
            if uploaded_file.name.endswith(".csv"):
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="iso-8859-1")
            else:
                df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ **{uploaded_file.name}** chargé : {len(df):,} lignes × {len(df.columns)} colonnes")
        
        # Analyse
        with st.spinner("🧠 Analyse intelligente en cours..."):
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
                    +{badge['points']} Points de Qualité
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding: 2rem;'>
                <h2 style='color: #1E293B; margin-bottom: 1.5rem;'>Niveau Atteint</h2>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>{level_emoji}</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #667EEA; margin-bottom: 2rem;'>
                    {level_name}
                </div>
                
                <h3 style='color: #64748B; font-size: 1rem; margin-bottom: 1rem;'>Progression vers Expert</h3>
                <div class='progress-container'>
                    <div class='progress-bar' style='width: {score}%;'>
                        {score}%
                    </div>
                </div>
                
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem;'>
                    <div class='metric-card'>
                        <div class='metric-value'>{results['total_rows']:,}</div>
                        <div class='metric-label'>Lignes Analysées</div>
                    </div>
                    <div class='metric-card'>
                        <div class='metric-value'>{results['total_columns']}</div>
                        <div class='metric-label'>Colonnes Détectées</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ======================
        # MÉTRIQUES
        # ======================
        st.markdown("<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>📊 Métriques Détaillées</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("🔄", "Doublons", results['duplicates']['count'], "inverse"),
            ("❌", "Manquants", f"{results['missing_values']['percentage']}%", "inverse"),
            ("✅", "Qualité Moy", f"{score}%", "normal"),
            ("📈", "Conformité", f"{95}%", "normal")  # Exemple
        ]
        
        for idx, (emoji, label, value, delta_color) in enumerate(metrics):
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
        st.markdown("<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>⚡ Actions Rapides</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Générer Rapport PDF", use_container_width=True):
                with st.spinner("Génération..."):
                    try:
                        pdf = create_pdf_report(df, results)
                        st.download_button(
                            "⬇️ Télécharger PDF",
                            pdf,
                            file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Erreur: {e}")
        
        with col2:
            st.button("🧹 Nettoyer Données", use_container_width=True)
        
        with col3:
            st.button("📤 Exporter Analyse", use_container_width=True)
        
        # ======================
        # RECOMMANDATIONS
        # ======================
        st.markdown("<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>💡 Recommandations Prioritaires</h2>", unsafe_allow_html=True)
        
        recommendations = generate_recommendations(results)
        
        if recommendations:
            for idx, rec in enumerate(recommendations[:5]):
                priority_class = "recommendation-high" if idx < 2 else "recommendation-medium" if idx < 4 else "recommendation-low"
                priority_badge = "🔴 HAUTE" if idx < 2 else "🟠 MOYENNE" if idx < 4 else "🔵 BASSE"
                
                st.markdown(f"""
                <div class='recommendation-item {priority_class} animated-card' style='animation-delay: {idx * 0.1}s;'>
                    <div style='display: flex; justify-content: space-between; align-items: start;'>
                        <div style='flex: 1;'>
                            <div style='font-weight: 700; font-size: 0.875rem; color: #64748B; margin-bottom: 0.5rem;'>
                                {priority_badge}
                            </div>
                            <div style='font-weight: 600; color: #1E293B;'>
                                {rec}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ======================
        # TABS D'ANALYSE
        # ======================
        st.markdown("<h2 style='color: #1E293B; margin: 3rem 0 1.5rem 0;'>🔬 Analyse Approfondie</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Données",
            "📊 Graphiques",
            "🔄 Doublons",
            "❌ Manquants"
        ])
        
        with tab1:
            st.dataframe(df.head(50), use_container_width=True, height=400)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                try:
                    st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
                except: pass
            with col2:
                try:
                    st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
                except: pass
        
        with tab3:
            if results["duplicates"]["count"] > 0:
                st.warning(f"⚠️ {results['duplicates']['count']} doublons détectés")
                st.dataframe(results["duplicates"]["data"], use_container_width=True)
            else:
                st.success("✅ Aucun doublon")
        
        with tab4:
            if results["missing_values"]["total"] > 0:
                st.warning(f"⚠️ {results['missing_values']['total']:,} valeurs manquantes")
            else:
                st.success("✅ Aucune donnée manquante")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        with st.expander("Détails"):
            import traceback
            st.code(traceback.format_exc())

else:
    # ======================
    # LANDING PAGE
    # ======================
    st.markdown("""
    <div class='pro-card animated-card' style='text-align: center; padding: 4rem 2rem;'>
        <div class='big-emoji'>🚀</div>
        <h2 style='color: #1E293B; margin: 2rem 0 1rem 0;'>Prêt à Analyser Vos Données ?</h2>
        <p style='color: #64748B; font-size: 1.125rem; max-width: 600px; margin: 0 auto 2rem auto;'>
            Uploadez votre fichier CSV ou Excel pour commencer une analyse professionnelle
            avec scoring gamifié et recommandations actionnables.
        </p>
        
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-top: 3rem;'>
            <div>
                <div style='font-size: 2.5rem; margin-bottom: 1rem;'>⚡</div>
                <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>Rapide</h3>
                <p style='color: #64748B;'>Résultats en moins de 10 secondes</p>
            </div>
            <div>
                <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🎯</div>
                <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>Précis</h3>
                <p style='color: #64748B;'>Analyse intelligente multi-niveaux</p>
            </div>
            <div>
                <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🎮</div>
                <h3 style='color: #1E293B; margin-bottom: 0.5rem;'>Gamifié</h3>
                <p style='color: #64748B;'>Badges et niveaux de qualité</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)