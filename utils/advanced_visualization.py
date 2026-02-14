# utils/advanced_visualizations.py
"""
Visualisations avancées pour DataTchek
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats


def create_distribution_analysis(df, column, max_categories=20):
    """
    Analyse de distribution pour une colonne
    """
    if df[column].dtype in ['object', 'category']:
        # Catégoriel
        value_counts = df[column].value_counts().head(max_categories)
        
        fig = go.Figure(data=[
            go.Bar(
                x=value_counts.index.astype(str),
                y=value_counts.values,
                marker_color='lightblue',
                text=value_counts.values,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Distribution des valeurs - {column}",
            xaxis_title="Valeur",
            yaxis_title="Fréquence",
            height=400
        )
        
    else:
        # Numérique
        fig = go.Figure()
        
        # Histogramme
        fig.add_trace(go.Histogram(
            x=df[column].dropna(),
            name='Distribution',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Ligne de densité
        try:
            from scipy.stats import gaussian_kde
            data = df[column].dropna()
            if len(data) > 1:
                kde = gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 100)
                y_range = kde(x_range) * len(data) * (data.max() - data.min()) / 30
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_range,
                    mode='lines',
                    name='Densité',
                    line=dict(color='red', width=2)
                ))
        except:
            pass
        
        fig.update_layout(
            title=f"Distribution - {column}",
            xaxis_title="Valeur",
            yaxis_title="Fréquence",
            height=400,
            showlegend=True
        )
    
    return fig


def create_correlation_heatmap(df, max_cols=20):
    """
    Matrice de corrélation pour colonnes numériques
    """
    # Sélectionner colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return None
    
    # Limiter le nombre de colonnes
    if len(numeric_cols) > max_cols:
        numeric_cols = numeric_cols[:max_cols]
    
    # Calculer corrélation
    corr_matrix = df[numeric_cols].corr()
    
    # Créer heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Corrélation")
    ))
    
    fig.update_layout(
        title="Matrice de Corrélation",
        height=600,
        xaxis={'side': 'bottom'},
    )
    
    return fig


def detect_outliers_visualization(df, column):
    """
    Détection et visualisation des outliers (valeurs aberrantes)
    """
    if not pd.api.types.is_numeric_dtype(df[column]):
        return None
    
    data = df[column].dropna()
    
    if len(data) < 4:
        return None
    
    # Calcul IQR
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    normal = data[(data >= lower_bound) & (data <= upper_bound)]
    
    # Box plot avec outliers
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=data,
        name=column,
        boxmean='sd',
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title=f"Détection d'Anomalies - {column}",
        yaxis_title="Valeur",
        height=400,
        annotations=[
            dict(
                text=f"{len(outliers)} anomalies détectées ({len(outliers)/len(data)*100:.1f}%)",
                showarrow=False,
                x=0.5,
                y=1.1,
                xref='paper',
                yref='paper',
                xanchor='center',
                yanchor='bottom',
                font=dict(size=12, color='red')
            )
        ]
    )
    
    return fig


def create_data_freshness_timeline(df, date_columns):
    """
    Timeline de fraîcheur des données pour colonnes de dates
    """
    if not date_columns:
        return None
    
    fig = go.Figure()
    
    for col in date_columns[:5]:  # Limiter à 5 colonnes
        try:
            dates = pd.to_datetime(df[col], errors='coerce').dropna()
            
            if len(dates) > 0:
                # Distribution temporelle
                date_counts = dates.dt.date.value_counts().sort_index()
                
                fig.add_trace(go.Scatter(
                    x=date_counts.index,
                    y=date_counts.values,
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))
        except:
            continue
    
    fig.update_layout(
        title="Timeline - Fraîcheur des Données",
        xaxis_title="Date",
        yaxis_title="Nombre d'enregistrements",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_quality_score_breakdown(results):
    """
    Décomposition du score de qualité par dimension
    """
    categories = ['Complétude', 'Validité', 'Unicité', 'Cohérence']
    
    # Calculer scores par catégorie depuis les données réelles
    completeness = 100 - results['missing_values']['percentage']

    # Validité : basée sur conformité sémantique
    semantic = results.get('semantic_validation', {})
    if semantic:
        conformity_rates = [v.get('conformity_rate', 100) for v in semantic.values()]
        validity = sum(conformity_rates) / len(conformity_rates) if conformity_rates else 100
    else:
        validity = 100

    uniqueness = 100 - (results['duplicates']['count'] / results['total_rows'] * 100) if results['total_rows'] > 0 else 100

    # Cohérence : basée sur colonnes constantes et cardinalité
    total_cols = results.get('total_columns', 1)
    quality_metrics = results.get('quality_metrics', {})
    low_cardinality_count = sum(1 for m in quality_metrics.values() if m.get('unique_percentage', 100) < 5)
    consistency = max(0, 100 - (low_cardinality_count / total_cols * 100)) if total_cols > 0 else 100
    
    scores = [completeness, validity, uniqueness, consistency]
    
    fig = go.Figure()
    
    # Radar chart
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Score',
        line_color='rgb(102, 126, 234)',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Décomposition du Score de Qualité",
        height=400
    )
    
    return fig


def create_column_quality_heatmap(df):
    """
    Heatmap de qualité par colonne (complétude)
    """
    quality_data = []
    
    for col in df.columns[:30]:  # Limiter à 30 colonnes
        missing_pct = df[col].isnull().sum() / len(df) * 100
        quality_pct = 100 - missing_pct
        
        quality_data.append({
            'Colonne': col,
            'Qualité': quality_pct
        })
    
    quality_df = pd.DataFrame(quality_data)
    
    # Trier par qualité
    quality_df = quality_df.sort_values('Qualité')
    
    fig = go.Figure(data=go.Bar(
        x=quality_df['Qualité'],
        y=quality_df['Colonne'],
        orientation='h',
        marker=dict(
            color=quality_df['Qualité'],
            colorscale=[
                [0, 'rgb(239, 68, 68)'],      # Rouge
                [0.5, 'rgb(245, 158, 11)'],   # Orange
                [0.8, 'rgb(59, 130, 246)'],   # Bleu
                [1, 'rgb(16, 185, 129)']      # Vert
            ],
            colorbar=dict(title="Qualité (%)")
        ),
        text=quality_df['Qualité'].round(1),
        texttemplate='%{text}%',
        textposition='inside'
    ))
    
    fig.update_layout(
        title="Qualité par Colonne (Complétude)",
        xaxis_title="Score de Qualité (%)",
        yaxis_title="Colonne",
        height=max(400, len(quality_df) * 20),
        xaxis=dict(range=[0, 100])
    )
    
    return fig


def create_value_uniqueness_analysis(df, max_cols=10):
    """
    Analyse de l'unicité des valeurs par colonne
    """
    uniqueness_data = []
    
    for col in df.columns[:max_cols]:
        total = len(df)
        unique = df[col].nunique()
        uniqueness_pct = (unique / total * 100) if total > 0 else 0
        
        uniqueness_data.append({
            'Colonne': col,
            'Valeurs Uniques': unique,
            'Total': total,
            'Unicité (%)': uniqueness_pct
        })
    
    uniqueness_df = pd.DataFrame(uniqueness_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Valeurs Uniques',
        x=uniqueness_df['Colonne'],
        y=uniqueness_df['Valeurs Uniques'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Doublons',
        x=uniqueness_df['Colonne'],
        y=uniqueness_df['Total'] - uniqueness_df['Valeurs Uniques'],
        marker_color='lightcoral'
    ))
    
    fig.update_layout(
        title="Analyse d'Unicité des Valeurs",
        xaxis_title="Colonne",
        yaxis_title="Nombre de valeurs",
        barmode='stack',
        height=400
    )
    
    return fig


def create_pattern_detection(df, column, top_n=10):
    """
    Détection de patterns dans une colonne texte
    """
    if df[column].dtype != 'object':
        return None
    
    data = df[column].dropna().astype(str)
    
    if len(data) == 0:
        return None
    
    # Analyser longueurs
    lengths = data.str.len()
    
    # Patterns de longueur
    length_counts = lengths.value_counts().head(top_n)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=length_counts.index,
        y=length_counts.values,
        marker_color='lightgreen',
        text=length_counts.values,
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f"Distribution des Longueurs - {column}",
        xaxis_title="Nombre de caractères",
        yaxis_title="Fréquence",
        height=400
    )
    
    return fig


def create_missing_data_patterns(df):
    """
    Patterns de données manquantes (combinaisons fréquentes)
    """
    # Créer une matrice binaire (1 = manquant, 0 = présent)
    missing_matrix = df.isnull().astype(int)
    
    # Limiter aux colonnes avec au moins 1 valeur manquante
    cols_with_missing = missing_matrix.sum()[missing_matrix.sum() > 0].index.tolist()
    
    if not cols_with_missing:
        return None
    
    # Limiter à 15 colonnes
    cols_with_missing = cols_with_missing[:15]
    missing_matrix = missing_matrix[cols_with_missing]
    
    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=missing_matrix.T.values,
        y=cols_with_missing,
        x=list(range(len(missing_matrix))),
        colorscale=[[0, 'lightgreen'], [1, 'red']],
        showscale=True,
        colorbar=dict(
            title="Statut",
            tickvals=[0, 1],
            ticktext=['Présent', 'Manquant']
        )
    ))
    
    fig.update_layout(
        title="Patterns de Données Manquantes",
        xaxis_title="Index de ligne (échantillon)",
        yaxis_title="Colonne",
        height=max(400, len(cols_with_missing) * 25),
        xaxis=dict(showticklabels=False)
    )
    
    return fig