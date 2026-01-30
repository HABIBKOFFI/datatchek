import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_score_gauge(score):
    color = "green" if score >= 80 else "orange" if score >= 60 else "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 60], "color": "#ffcccc"},
                {"range": [60, 80], "color": "#fff3cd"},
                {"range": [80, 100], "color": "#d4edda"},
            ],
        },
        title={"text": "Score de Qualité"}
    ))
    fig.update_layout(height=300)
    return fig


def create_problems_bar_chart(results):
    problems = {
        "Doublons": results["duplicates"]["count"],
        "Données manquantes": results["missing_values"]["total"],
        "Colonnes incohérentes": sum(
            1 for c in results["semantic_validation"].values()
            if c["conformity_rate"] < 70
        )
    }

    df = pd.DataFrame(problems.items(), columns=["Type", "Nombre"])
    fig = px.bar(df, x="Type", y="Nombre", text="Nombre", title="Problèmes détectés")
    fig.update_traces(textposition="outside")
    return fig


def create_missing_data_chart(results, df):
    missing = results["missing_values"]["by_column"]
    df_missing = pd.DataFrame({
        "Colonne": list(missing.keys()),
        "Manquants": list(missing.values())
    }).query("Manquants > 0")

    if df_missing.empty:
        return None

    fig = px.bar(
        df_missing,
        y="Colonne",
        x="Manquants",
        orientation="h",
        title="Données manquantes par colonne"
    )
    return fig


def create_quality_distribution_pie(results):
    total_cells = results["total_rows"] * results["total_columns"]
    issues = (
        results["duplicates"]["count"]
        + results["missing_values"]["total"]
    )

    clean = max(0, total_cells - issues)
    fig = px.pie(
        values=[clean, issues],
        names=["Données propres", "Problèmes"],
        hole=0.4,
        title="Répartition globale de la qualité"
    )
    return fig


def create_column_quality_bar(df):
    data = []
    for col in df.columns:
        total = len(df)
        missing = df[col].isnull().sum()
        quality = round(((total - missing) / total) * 100, 1) if total else 0
        data.append({"Colonne": col, "Qualité (%)": quality})

    dfq = pd.DataFrame(data).sort_values("Qualité (%)")
    fig = px.bar(
        dfq,
        y="Colonne",
        x="Qualité (%)",
        orientation="h",
        title="Qualité par colonne",
        range_x=[0, 100]
    )
    return fig
