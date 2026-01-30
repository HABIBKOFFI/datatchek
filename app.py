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
    create_column_quality_bar
)
from utils.pdf_generator import create_pdf_report
from utils.data_cleaner import clean_dataframe, get_cleaning_preview

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
    - Détection intelligente des colonnes
    - Détection de doublons
    - Validation d'emails
    - Validation de téléphones
    - Données manquantes
    - Score de qualité
    - Graphiques interactifs
    - Génération de rapports PDF
    - Nettoyage automatique
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
        # Lire le fichier avec gestion d'encodage
        if uploaded_file.name.endswith('.csv'):
            # Essayer différents encodages
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)  # Retour au début du fichier
                try:
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='iso-8859-1', errors='ignore')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")
        
        # Analyser avec détection automatique
        with st.spinner("🔍 Analyse en cours..."):
            results = validate_dataframe(df)
        
        # Afficher les colonnes détectées automatiquement
        if 'detected_columns' in results:
            detected = results['detected_columns']
            
            if detected['email'] or detected['phone']:
                st.info("🔍 **Détection automatique des colonnes** (basée sur l'analyse du contenu)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if detected['email']:
                        st.success(f"📧 **Emails détectés :** `{', '.join(detected['email'])}`")
                    else:
                        st.warning("📧 Aucune colonne email détectée")
                
                with col2:
                    if detected['phone']:
                        st.success(f"📱 **Téléphones détectés :** `{', '.join(detected['phone'])}`")
                    else:
                        st.warning("📱 Aucune colonne téléphone détectée")
                
                st.divider()
        
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<div class='big-metric' style='color: {color};'>{score}/100 {emoji}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-label'>{message}</div>", unsafe_allow_html=True)
        
        with col2:
            gauge_fig = create_score_gauge(score)
            st.plotly_chart(gauge_fig, use_container_width=True)
        
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
        
        # BOUTON TÉLÉCHARGER RAPPORT PDF
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📄 Générer Rapport PDF", type="primary", use_container_width=True):
                with st.spinner("📝 Génération du rapport en cours..."):
                    pdf_buffer = create_pdf_report(df, results)
                    
                    st.download_button(
                        label="⬇️ Télécharger le Rapport PDF",
                        data=pdf_buffer,
                        file_name=f"rapport_datatchek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.success("✅ Rapport généré avec succès !")
        
        st.divider()
        
        # NETTOYAGE AUTOMATIQUE
        st.header("🧹 Nettoyage Automatique")
        
        with st.expander("⚙️ Options de nettoyage", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                remove_dupes = st.checkbox("Supprimer les doublons", value=True)
            
            with col2:
                clean_emails_opt = st.checkbox("Nettoyer les emails", value=True)
            
            with col3:
                clean_phones_opt = st.checkbox("Standardiser les téléphones", value=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🧹 Nettoyer les Données", type="secondary", use_container_width=True):
                with st.spinner("🔄 Nettoyage en cours..."):
                    detected = results.get('detected_columns', {})
                    df_clean, clean_stats = clean_dataframe(
                        df, 
                        detected_columns=detected,
                        remove_dupes=remove_dupes,
                        clean_emails=clean_emails_opt,
                        clean_phones=clean_phones_opt
                    )
                    
                    # Stocker dans session state
                    st.session_state['df_clean'] = df_clean
                    st.session_state['clean_stats'] = clean_stats
                    
                    st.success("✅ Nettoyage terminé !")
        
        # Afficher les résultats du nettoyage
        if 'df_clean' in st.session_state and 'clean_stats' in st.session_state:
            st.divider()
            
            clean_stats = st.session_state['clean_stats']
            df_clean = st.session_state['df_clean']
            
            st.subheader("📊 Résultats du Nettoyage")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📋 Lignes Initiales",
                    value=clean_stats['original_rows']
                )
            
            with col2:
                st.metric(
                    label="🔄 Doublons Supprimés",
                    value=clean_stats['duplicates_removed'],
                    delta=f"-{clean_stats['duplicates_removed']}",
                    delta_color="normal"
                )
            
            with col3:
                st.metric(
                    label="✉️ Emails Nettoyés",
                    value=clean_stats['emails_cleaned']
                )
            
            with col4:
                st.metric(
                    label="📱 Téléphones Nettoyés",
                    value=clean_stats['phones_cleaned']
                )
            
            # Aperçu des données nettoyées
            st.subheader("👀 Aperçu des Données Nettoyées")
            st.dataframe(df_clean.head(20), use_container_width=True)
            
            # Bouton de téléchargement
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Préparer le fichier pour téléchargement
                if uploaded_file.name.endswith('.csv'):
                    csv = df_clean.to_csv(index=False).encode('utf-8')
                    file_ext = 'csv'
                    mime_type = 'text/csv'
                    download_data = csv
                else:
                    # Pour Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_clean.to_excel(writer, index=False, sheet_name='Données Nettoyées')
                    download_data = output.getvalue()
                    file_ext = 'xlsx'
                    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                st.download_button(
                    label="⬇️ Télécharger les Données Nettoyées",
                    data=download_data,
                    file_name=f"donnees_nettoyees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                    mime=mime_type,
                    type="primary",
                    use_container_width=True
                )
        
        st.divider()
        
        # DÉTAILS
        st.header("🔍 Analyse Détaillée")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Aperçu", "📈 Graphiques", "🔄 Doublons", "✉️ Emails", "📱 Téléphones"])
        
        with tab1:
            st.subheader("Aperçu des données")
            st.dataframe(df.head(20), use_container_width=True)
            
            st.subheader("Statistiques")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Lignes totales", results['total_rows'])
                st.metric("Colonnes totales", results['total_columns'])
            
            with col2:
                st.metric("Cellules totales", results['total_rows'] * results['total_columns'])
                st.metric("Score de qualité", f"{score}/100")
            
            # Afficher les types de colonnes détectés
            if 'detected_columns' in results:
                st.subheader("Types de colonnes détectés")
                detected = results['detected_columns']
                types_df = pd.DataFrame({
                    'Colonne': list(detected['all_types'].keys()),
                    'Type Détecté': list(detected['all_types'].values())
                })
                st.dataframe(types_df, use_container_width=True)
        
        with tab2:
            st.subheader("📊 Visualisations")
            
            # Graphique des problèmes
            st.plotly_chart(create_problems_bar_chart(results), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Camembert de répartition
                st.plotly_chart(create_quality_distribution_pie(results), use_container_width=True)
            
            with col2:
                # Qualité par colonne
                st.plotly_chart(create_column_quality_bar(df), use_container_width=True)
            
            # Données manquantes
            missing_fig = create_missing_data_chart(results, df)
            if missing_fig:
                st.plotly_chart(missing_fig, use_container_width=True)
            else:
                st.success("✅ Aucune donnée manquante !")
        
        with tab3:
            st.subheader("Doublons détectés")
            if results['duplicates']['count'] > 0:
                st.warning(f"⚠️ {results['duplicates']['count']} lignes dupliquées trouvées")
                st.dataframe(results['duplicates']['data'], use_container_width=True)
            else:
                st.success("✅ Aucun doublon détecté !")
        
        with tab4:
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
        
        with tab5:
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
        st.code(str(e), language="python")

else:
    # Message d'accueil
    st.info("👆 Uploadez un fichier CSV ou Excel pour commencer l'analyse")
    
    st.divider()
    
    st.subheader("🎯 Pourquoi utiliser Datatchek ?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Détection Intelligente")
        st.write("Analyse automatique du contenu, pas besoin de nommer vos colonnes")
    
    with col2:
        st.markdown("### 📊 Score de Qualité")
        st.write("Évaluation globale de 0 à 100 pour vos fichiers")
    
    with col3:
        st.markdown("### ⚡ Rapide et Simple")
        st.write("Uploadez, analysez, téléchargez en quelques secondes")