# app.py
"""
DataTchek - Application Streamlit d'analyse de qualité des données
Version améliorée avec validateurs CI robustes
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
    page_title="DataTchek - Analyse de Qualité",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ======================
# CSS PERSONNALISÉ
# ======================
st.markdown("""
<style>
.big-metric {
    font-size: 3rem;
    font-weight: bold;
}
.metric-label {
    font-size: 1.2rem;
    color: #666;
    margin-top: 0.5rem;
}
.quality-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: bold;
    font-size: 1.1rem;
}
.badge-excellent {
    background-color: #10B981;
    color: white;
}
.badge-bon {
    background-color: #3B82F6;
    color: white;
}
.badge-moyen {
    background-color: #F59E0B;
    color: white;
}
.badge-faible {
    background-color: #EF4444;
    color: white;
}
.recommendation-box {
    background-color: #F3F4F6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #3B82F6;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.header("📊 À propos de DataTchek")
    st.write("""
    **DataTchek** analyse automatiquement la qualité de vos fichiers de données 
    avec une attention particulière aux standards de la Côte d'Ivoire.
    
    ### Fonctionnalités :
    - ✅ Détection intelligente des colonnes
    - ✅ Validation téléphones CI (+225)
    - ✅ Validation emails
    - ✅ Détection de doublons
    - ✅ Analyse données manquantes
    - ✅ Score global de qualité
    - ✅ Graphiques interactifs
    - ✅ Rapports PDF professionnels
    
    ### Validations spécifiques CI :
    - 📱 Téléphones : +225 XX XX XX XX XX
    - 🏦 Comptes BCEAO : CI93A...
    - 💰 Devise : FCFA/XOF
    """)
    
    st.divider()
    
    st.caption("🚀 Version 2.0")
    st.caption("Développé par HABIB KOFFI")
    st.caption("©️ 2026 - Tous droits réservés")


# ======================
# EN-TÊTE
# ======================
st.title("🎯 DataTchek")
st.subheader("Analyse de la cohérence et de la qualité de vos données")
st.markdown("---")


# ======================
# UPLOAD FICHIER
# ======================
st.header("📤 Uploadez votre fichier")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choisissez un fichier CSV ou Excel",
        type=["csv", "xlsx", "xls"],
        help="Formats supportés : CSV (UTF-8, ISO-8859-1), Excel (.xlsx, .xls)"
    )

with col2:
    if uploaded_file:
        st.success(f"✅ Fichier chargé")
        st.info(f"📁 {uploaded_file.name}")


# ======================
# ANALYSE
# ======================
if uploaded_file:
    try:
        # Chargement du fichier
        with st.spinner("📖 Lecture du fichier..."):
            if uploaded_file.name.endswith(".csv"):
                # Essayer différents encodages
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="iso-8859-1")
            else:
                df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Fichier chargé avec succès : **{len(df):,} lignes** × **{len(df.columns)} colonnes**")
        
        # Analyse des données
        with st.spinner("🔍 Analyse en cours... Cela peut prendre quelques instants."):
            results = validate_dataframe(df)
        
        st.success("✅ Analyse terminée !")
        
        st.markdown("---")
        
        # ======================
        # SCORE DE QUALITÉ
        # ======================
        st.header("📊 Score de Qualité Global")
        
        score = results["quality_score"]
        
        # Déterminer le statut
        if score >= 80:
            color = "green"
            emoji = "🎉"
            label = "EXCELLENT"
            badge_class = "badge-excellent"
        elif score >= 60:
            color = "blue"
            emoji = "👍"
            label = "BON"
            badge_class = "badge-bon"
        elif score >= 40:
            color = "orange"
            emoji = "⚠️"
            label = "MOYEN"
            badge_class = "badge-moyen"
        else:
            color = "red"
            emoji = "❌"
            label = "FAIBLE"
            badge_class = "badge-faible"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(
                f"<div class='big-metric' style='color:{color}'>{score}/100</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='quality-badge {badge_class}'>{emoji} {label}</div>",
                unsafe_allow_html=True
            )
        
        with col2:
            try:
                fig = create_score_gauge(score)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Impossible d'afficher la jauge : {e}")
        
        st.markdown("---")
        
        # ======================
        # MÉTRIQUES CLÉS
        # ======================
        st.header("📈 Métriques Clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Lignes totales",
                value=f"{results['total_rows']:,}"
            )
        
        with col2:
            st.metric(
                label="📊 Colonnes",
                value=results['total_columns']
            )
        
        with col3:
            duplicate_count = results['duplicates']['count']
            st.metric(
                label="🔄 Doublons",
                value=duplicate_count,
                delta=f"-{duplicate_count}" if duplicate_count > 0 else None,
                delta_color="inverse"
            )
        
        with col4:
            missing_count = results['missing_values']['total']
            missing_pct = results['missing_values']['percentage']
            st.metric(
                label="❌ Données manquantes",
                value=f"{missing_count:,}",
                delta=f"{missing_pct}%",
                delta_color="inverse"
            )
        
        # Métriques de validation spécifique
        if results.get('specific_validation'):
            st.subheader("🔍 Validations Spécifiques")
            
            cols = st.columns(min(4, len(results['specific_validation'])))
            
            for idx, (col_name, data) in enumerate(results['specific_validation'].items()):
                with cols[idx % 4]:
                    invalid_count = data['validation']['invalid_count']
                    col_type = data['type']
                    
                    type_emoji = {
                        'phone': '📱',
                        'email': '✉️',
                        'bank_account': '🏦',
                        'currency': '💰'
                    }.get(col_type, '🔍')
                    
                    st.metric(
                        label=f"{type_emoji} {col_name[:15]}",
                        value=f"{invalid_count} invalides",
                        delta=f"{data['validation']['validity_rate']:.1f}% valides",
                        delta_color="normal"
                    )
        
        st.markdown("---")
        
        # ======================
        # BOUTON GÉNÉRATION PDF
        # ======================
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📄 Générer le Rapport PDF", type="primary", use_container_width=True):
                with st.spinner("🔄 Génération du rapport PDF en cours..."):
                    try:
                        pdf_buffer = create_pdf_report(df, results)
                        
                        st.success("✅ Rapport PDF généré avec succès !")
                        
                        st.download_button(
                            label="⬇️ Télécharger le PDF",
                            data=pdf_buffer,
                            file_name=f"rapport_datatcheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la génération du PDF : {str(e)}")
        
        st.markdown("---")
        
        # ======================
        # RECOMMANDATIONS
        # ======================
        st.header("💡 Recommandations")
        
        recommendations = generate_recommendations(results)
        
        if recommendations:
            for rec in recommendations[:10]:  # Limiter à 10 recommandations
                st.markdown(
                    f"<div class='recommendation-box'>• {rec}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("🎉 Aucune recommandation - Vos données sont de qualité excellente !")
        
        st.markdown("---")
        
        # ======================
        # ANALYSE DÉTAILLÉE (TABS)
        # ======================
        st.header("🔬 Analyse Détaillée")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Aperçu Données",
            "🧠 Cohérence Types",
            "📈 Graphiques",
            "🔄 Doublons",
            "❌ Données Manquantes"
        ])
        
        # --- TAB 1 : APERÇU ---
        with tab1:
            st.subheader("Aperçu des premières lignes")
            st.dataframe(df.head(50), use_container_width=True, height=400)
            
            st.subheader("Statistiques descriptives")
            try:
                st.dataframe(df.describe(), use_container_width=True)
            except Exception as e:
                st.warning(f"Impossible de générer les statistiques : {e}")
        
        # --- TAB 2 : COHÉRENCE (CORRIGÉ) ---
        with tab2:
            st.subheader("Validation sémantique des colonnes")
            
            if 'semantic_validation' in results and results['semantic_validation']:
                try:
                    # Créer un DataFrame propre sans types mixtes
                    semantic_data = []
                    
                    for col_name, col_data in results["semantic_validation"].items():
                        semantic_data.append({
                            'Colonne': str(col_name),
                            'Type Attendu': str(col_data.get('expected_type', 'N/A')),
                            'Type Réel': str(col_data.get('actual_type', 'N/A')),
                            'Conformité (%)': float(col_data.get('conformity_rate', 0)),
                            'Invalides': int(col_data.get('invalid_count', 0)),
                            'Nulls': int(col_data.get('null_count', 0)) if 'null_count' in col_data else 0,
                            'Uniques': int(col_data.get('unique_count', 0)) if 'unique_count' in col_data else 0
                        })
                    
                    semantic_df = pd.DataFrame(semantic_data)
                    
                    # Fonction de coloration
                    def color_conformity(val):
                        try:
                            if isinstance(val, (int, float)):
                                if val >= 90:
                                    return 'background-color: #D4EDDA'
                                elif val >= 70:
                                    return 'background-color: #FFF3CD'
                                else:
                                    return 'background-color: #F8D7DA'
                        except:
                            pass
                        return ''
                    
                    # Afficher le DataFrame avec style
                    st.dataframe(
                        semantic_df.style.applymap(
                            color_conformity, 
                            subset=['Conformité (%)']
                        ),
                        use_container_width=True,
                        height=500
                    )
                    
                except Exception as e:
                    st.warning(f"⚠️ Impossible d'afficher le tableau de cohérence : {str(e)}")
                    
                    # Affichage alternatif simple
                    st.write("**Résumé de la validation sémantique :**")
                    for col_name, col_data in results["semantic_validation"].items():
                        conformity = col_data.get('conformity_rate', 0)
                        emoji = "✅" if conformity >= 90 else "⚠️" if conformity >= 70 else "❌"
                        st.write(f"{emoji} **{col_name}** : {conformity}% de conformité")
            else:
                st.info("ℹ️ Aucune validation sémantique disponible")
        
        # --- TAB 3 : GRAPHIQUES ---
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    st.plotly_chart(
                        create_problems_bar_chart(results), 
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"Graphique indisponible : {e}")
            
            with col2:
                try:
                    st.plotly_chart(
                        create_quality_distribution_pie(results), 
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"Graphique indisponible : {e}")
            
            try:
                st.plotly_chart(
                    create_column_quality_bar(df), 
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"Graphique indisponible : {e}")
            
            try:
                missing_fig = create_missing_data_chart(results, df)
                if missing_fig:
                    st.plotly_chart(missing_fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Graphique données manquantes indisponible : {e}")
        
        # --- TAB 4 : DOUBLONS ---
        with tab4:
            duplicate_count = results["duplicates"]["count"]
            
            if duplicate_count > 0:
                st.warning(f"⚠️ {duplicate_count} doublons détectés")
                
                st.subheader("Lignes dupliquées")
                st.dataframe(
                    results["duplicates"]["data"], 
                    use_container_width=True,
                    height=400
                )
                
                st.info("💡 **Recommandation** : Vérifiez si ces doublons sont intentionnels ou nécessitent un nettoyage.")
            else:
                st.success("✅ Aucun doublon détecté - Excellent !")
        
        # --- TAB 5 : DONNÉES MANQUANTES ---
        with tab5:
            missing_total = results["missing_values"]["total"]
            
            if missing_total > 0:
                st.warning(f"⚠️ {missing_total:,} valeurs manquantes ({results['missing_values']['percentage']}%)")
                
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
                
                st.info("💡 **Recommandation** : Traitez les colonnes avec > 20% de valeurs manquantes.")
            else:
                st.success("✅ Aucune donnée manquante - Parfait !")
    
    except Exception as e:
        st.error("❌ Erreur lors de l'analyse du fichier")
        st.code(str(e))
        
        with st.expander("🔍 Détails de l'erreur"):
            import traceback
            st.code(traceback.format_exc())

else:
    # ======================
    # ÉTAT INITIAL
    # ======================
    st.info("👆 Uploadez un fichier CSV ou Excel pour commencer l'analyse")
    
    st.markdown("### 📝 Guide d'utilisation")
    st.markdown("""
    1. **Uploadez votre fichier** CSV ou Excel
    2. **Attendez l'analyse** (quelques secondes)
    3. **Consultez les résultats** :
       - Score global de qualité
       - Métriques détaillées
       - Recommandations actionnables
    4. **Téléchargez le rapport PDF** pour partager avec votre équipe
    
    ### 🎯 Types de validations effectuées :
    - ✅ Structure et types de données
    - ✅ Téléphones au format ivoirien (+225)
    - ✅ Emails valides
    - ✅ Doublons
    - ✅ Données manquantes
    - ✅ Cohérence sémantique
    """)