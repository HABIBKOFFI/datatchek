import streamlit as st
import pandas as pd
from datetime import datetime
import io

from utils.validators import validate_dataframe
from utils.visualizations import (
    create_score_gauge,
    create_problems_bar_chart,
    create_missing_data_chart,
    create_quality_distribution_pie,
    create_column_quality_bar,
)
from utils.pdf_generator import create_pdf_report

# Configuration
st.set_page_config(
    page_title="Datatchek - Analyse de Qualité",
    page_icon="🎯",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.big-metric {
    font-size: 3rem;
    font-weight: bold;
}
.metric-label {
    font-size: 1.2rem;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# Titre
st.title("🎯 Datatchek")
st.subheader("Analyse de la cohérence et de la qualité de vos données")

# Sidebar
with st.sidebar:
    st.header("📊 À propos")
    st.write("""
    Datatchek analyse automatiquement la qualité de vos fichiers de données.

    **Fonctionnalités :**
    - Détection intelligente des colonnes
    - Validation de la cohérence type attendu ↔ données réelles
    - Détection de doublons
    - Analyse des données manquantes
    - Score global de qualité
    - Graphiques interactifs
    - Génération de rapports PDF
    """)
    st.divider()
    st.caption("Développé par HABIB KOFFI")

# Upload
st.header("📤 Uploadez votre fichier")
uploaded_file = st.file_uploader(
    "Choisissez un fichier CSV ou Excel",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8", errors="ignore")
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ Fichier chargé : {uploaded_file.name}")

        with st.spinner("🔍 Analyse en cours..."):
            results = validate_dataframe(df)

        # SCORE
        st.header("📊 Score de Qualité")
        score = results["quality_score"]

        if score >= 80:
            color, emoji, label = "green", "🎉", "Excellent"
        elif score >= 60:
            color, emoji, label = "orange", "👍", "Correct"
        else:
            color, emoji, label = "red", "⚠️", "À améliorer"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"<div class='big-metric' style='color:{color}'>{score}/100 {emoji}</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='metric-label'>{label}</div>", unsafe_allow_html=True)

        with col2:
            st.plotly_chart(create_score_gauge(score), use_container_width=True)

        # MÉTRIQUES
        st.header("📈 Métriques Clés")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📋 Lignes", results["total_rows"])
        col2.metric("📊 Colonnes", results["total_columns"])
        col3.metric("🔄 Doublons", results["duplicates"]["count"])
        col4.metric("❌ Données manquantes", results["missing_values"]["total"])

        # PDF
        st.divider()
        if st.button("📄 Générer le rapport PDF", type="primary"):
            with st.spinner("📝 Génération du rapport..."):
                pdf = create_pdf_report(df, results)
                st.download_button(
                    "⬇️ Télécharger le PDF",
                    pdf,
                    file_name=f"rapport_datatchek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

        # ANALYSE DÉTAILLÉE
        st.divider()
        st.header("🔍 Analyse détaillée")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Aperçu", "🧠 Cohérence des types", "📈 Graphiques", "🔄 Doublons"]
        )

        with tab1:
            st.dataframe(df.head(20), use_container_width=True)

        with tab2:
            st.subheader("Validation sémantique des colonnes")
            semantic_df = pd.DataFrame.from_dict(
                results["semantic_validation"], orient="index"
            )
            st.dataframe(semantic_df, use_container_width=True)

        with tab3:
            st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
            st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
            st.plotly_chart(create_column_quality_bar(df), use_container_width=True)

            missing_fig = create_missing_data_chart(results, df)
            if missing_fig:
                st.plotly_chart(missing_fig, use_container_width=True)

        with tab4:
            if results["duplicates"]["count"] > 0:
                st.warning("Doublons détectés")
                st.dataframe(results["duplicates"]["data"], use_container_width=True)
            else:
                st.success("Aucun doublon détecté")

    except Exception as e:
        st.error("❌ Erreur lors de l’analyse")
        st.code(str(e))

else:
    st.info("👆 Uploadez un fichier pour commencer l’analyse")
