import streamlit as st
import pandas as pd
from utils.validators import validate_dataframe

# Configuration
st.set_page_config(
    page_title="Datatchek - Analyse de Qualité",
    page_icon="🎯",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
    <style>
    .big-metric {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Titre
st.title("🎯 Datatchek")
st.subheader("Analyse de qualité de vos données")

# Sidebar
with st.sidebar:
    st.header("📊 À propos")
    st.write("""
    Datatchek analyse automatiquement la qualité de vos fichiers de données.
    
    **Fonctionnalités:**
    - Détection de doublons
    - Validation d'emails
    - Validation de téléphones
    - Données manquantes
    - Score de qualité
    """)
    
    st.divider()
    st.caption("Développé par HABIB KOFFI")

# Upload
st.header("📤 Uploadez votre fichier")
uploaded_file = st.file_uploader(
    "Choisissez un fichier CSV ou Excel",
    type=['csv', 'xlsx'],
    help="Formats acceptés: CSV, XLSX"
)

if uploaded_file:
    try:
        # Lire le fichier
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")
        
        # Analyser
        with st.spinner("🔍 Analyse en cours..."):
            results = validate_dataframe(df)
        
        # SCORE DE QUALITÉ
        st.header("📊 Score de Qualité")
        
        score = results['quality_score']
        
        # Couleur selon le score
        if score >= 80:
            color = "green"
            emoji = "🎉"
            message = "Excellent !"
        elif score >= 60:
            color = "orange"
            emoji = "👍"
            message = "Bien"
        else:
            color = "red"
            emoji = "⚠️"
            message = "À améliorer"
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"<div class='big-metric' style='color: {color};'>{score}/100 {emoji}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-label'>{message}</div>", unsafe_allow_html=True)
        
        # MÉTRIQUES CLÉS
        st.header("📈 Métriques Clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Total Lignes",
                value=results['total_rows']
            )
        
        with col2:
            st.metric(
                label="🔄 Doublons",
                value=results['duplicates']['count'],
                delta=f"-{results['duplicates']['count']}" if results['duplicates']['count'] > 0 else "Aucun",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="❌ Données Manquantes",
                value=results['missing_values']['total'],
                delta=f"{results['missing_values']['percentage']}%",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label="📊 Colonnes",
                value=results['total_columns']
            )
        
        # DÉTAILS
        st.header("🔍 Analyse Détaillée")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Aperçu", "🔄 Doublons", "✉️ Emails", "📱 Téléphones"])
        
        with tab1:
            st.subheader("Aperçu des données")
            st.dataframe(df.head(20), use_container_width=True)
            
            st.subheader("Données manquantes par colonne")
            missing_df = pd.DataFrame({
                'Colonne': results['missing_values']['by_column'].keys(),
                'Manquants': results['missing_values']['by_column'].values()
            })
            missing_df = missing_df[missing_df['Manquants'] > 0].sort_values('Manquants', ascending=False)
            
            if len(missing_df) > 0:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("✅ Aucune donnée manquante !")
        
        with tab2:
            st.subheader("Doublons détectés")
            if results['duplicates']['count'] > 0:
                st.warning(f"⚠️ {results['duplicates']['count']} lignes dupliquées trouvées")
                st.dataframe(results['duplicates']['data'], use_container_width=True)
            else:
                st.success("✅ Aucun doublon détecté !")
        
        with tab3:
            st.subheader("Validation des emails")
            if 'emails' in results:
                for col, data in results['emails'].items():
                    st.write(f"**Colonne : {col}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("✅ Valides", data['valid'])
                    with col2:
                        st.metric("❌ Invalides", data['invalid'])
                    
                    if data['invalid'] > 0:
                        with st.expander("Voir les emails invalides"):
                            invalid_df = df.iloc[data['invalid_rows']][[col]]
                            st.dataframe(invalid_df, use_container_width=True)
            else:
                st.info("ℹ️ Aucune colonne email détectée")
        
        with tab4:
            st.subheader("Validation des téléphones")
            if 'phones' in results:
                for col, data in results['phones'].items():
                    st.write(f"**Colonne : {col}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("✅ Valides", data['valid'])
                    with col2:
                        st.metric("❌ Invalides", data['invalid'])
                    
                    if data['invalid'] > 0:
                        with st.expander("Voir les téléphones invalides"):
                            invalid_df = df.iloc[data['invalid_rows']][[col]]
                            st.dataframe(invalid_df, use_container_width=True)
            else:
                st.info("ℹ️ Aucune colonne téléphone détectée")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
        st.info("💡 Vérifiez que votre fichier est bien formaté")

else:
    # Message d'accueil
    st.info("👆 Uploadez un fichier CSV ou Excel pour commencer l'analyse")
    
    st.divider()
    
    st.subheader("🎯 Pourquoi utiliser Datatchek ?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Détection Automatique")
        st.write("Identifie instantanément les problèmes dans vos données")
    
    with col2:
        st.markdown("### 📊 Score de Qualité")
        st.write("Évaluation globale de 0 à 100 pour vos fichiers")
    
    with col3:
        st.markdown("### ⚡ Rapide et Simple")
        st.write("Uploadez, analysez, téléchargez en quelques secondes")