import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_score_gauge(score):
    """Crée une jauge pour le score de qualité"""
    
    # Couleur selon le score
    if score >= 80:
        color = "green"
    elif score >= 60:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Score de Qualité", 'font': {'size': 24}},
        delta = {'reference': 100, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#ffcccc'},
                {'range': [60, 80], 'color': '#ffffcc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_problems_bar_chart(results):
    """Crée un graphique en barres des problèmes détectés"""
    
    problems = {
        'Doublons': results['duplicates']['count'],
        'Données Manquantes': results['missing_values']['total']
    }
    
    # Ajouter les emails invalides
    if 'emails' in results:
        total_invalid_emails = sum(data['invalid'] for data in results['emails'].values())
        problems['Emails Invalides'] = total_invalid_emails
    
    # Ajouter les téléphones invalides
    if 'phones' in results:
        total_invalid_phones = sum(data['invalid'] for data in results['phones'].values())
        problems['Téléphones Invalides'] = total_invalid_phones
    
    # Créer le DataFrame
    df_problems = pd.DataFrame({
        'Type': list(problems.keys()),
        'Nombre': list(problems.values())
    })
    
    # Créer le graphique
    fig = px.bar(
        df_problems,
        x='Type',
        y='Nombre',
        title='Problèmes Détectés par Type',
        color='Nombre',
        color_continuous_scale='Reds',
        text='Nombre'
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Type de Problème",
        yaxis_title="Nombre d'Occurrences"
    )
    
    return fig


def create_missing_data_chart(results, df):
    """Crée un graphique des données manquantes par colonne"""
    
    missing_data = results['missing_values']['by_column']
    
    # Filtrer les colonnes avec des données manquantes
    missing_df = pd.DataFrame({
        'Colonne': list(missing_data.keys()),
        'Manquants': list(missing_data.values())
    })
    
    missing_df = missing_df[missing_df['Manquants'] > 0].sort_values('Manquants', ascending=True)
    
    if len(missing_df) == 0:
        return None
    
    # Calculer les pourcentages
    total_rows = len(df)
    missing_df['Pourcentage'] = (missing_df['Manquants'] / total_rows * 100).round(2)
    
    fig = px.bar(
        missing_df,
        y='Colonne',
        x='Manquants',
        orientation='h',
        title='Données Manquantes par Colonne',
        color='Pourcentage',
        color_continuous_scale='YlOrRd',
        text='Manquants',
        hover_data=['Pourcentage']
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=max(300, len(missing_df) * 50),
        xaxis_title="Nombre de Valeurs Manquantes",
        yaxis_title="Colonnes"
    )
    
    return fig


def create_quality_distribution_pie(results):
    """Crée un camembert de la distribution des problèmes"""
    
    total_cells = results['total_rows'] * results['total_columns']
    
    problems_count = results['duplicates']['count'] + results['missing_values']['total']
    
    if 'emails' in results:
        problems_count += sum(data['invalid'] for data in results['emails'].values())
    
    if 'phones' in results:
        problems_count += sum(data['invalid'] for data in results['phones'].values())
    
    clean_cells = max(0, total_cells - problems_count)
    
    labels = ['Données Propres', 'Problèmes Détectés']
    values = [clean_cells, problems_count]
    colors = ['#90EE90', '#FFB6C6']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Répartition Globale de la Qualité",
        height=400,
        showlegend=True
    )
    
    return fig


def create_column_quality_bar(df):
    """Crée un graphique de qualité par colonne"""
    
    quality_by_column = []
    
    for col in df.columns:
        total = len(df)
        missing = df[col].isnull().sum()
        valid = total - missing
        quality_pct = (valid / total * 100) if total > 0 else 0
        
        quality_by_column.append({
            'Colonne': col,
            'Qualité (%)': round(quality_pct, 1),
            'Valides': valid,
            'Manquants': missing
        })
    
    quality_df = pd.DataFrame(quality_by_column).sort_values('Qualité (%)', ascending=True)
    
    fig = px.bar(
        quality_df,
        y='Colonne',
        x='Qualité (%)',
        orientation='h',
        title='Score de Qualité par Colonne',
        color='Qualité (%)',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        text='Qualité (%)',
        hover_data=['Valides', 'Manquants']
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=max(300, len(quality_df) * 40),
        xaxis_title="Qualité (%)",
        yaxis_title="Colonnes",
        xaxis_range=[0, 105]
    )
    
    return fig