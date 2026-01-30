from .column_detector import analyze_columns
import pandas as pd

def detect_duplicates(df):
    duplicates = df[df.duplicated(keep=False)]
    return {
        "count": len(duplicates),
        "rows": duplicates.index.tolist(),
        "data": duplicates
    }

def detect_missing_values(df):
    missing = df.isnull().sum()
    total_cells = len(df) * len(df.columns)
    total_missing = missing.sum()
    return {
        "total": int(total_missing),
        "percentage": round((total_missing / total_cells) * 100, 2),
        "by_column": missing.to_dict()
    }

def validate_dataframe(df):
    semantic = analyze_columns(df)

    results = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicates": detect_duplicates(df),
        "missing_values": detect_missing_values(df),
        "semantic_validation": semantic
    }

    results["quality_score"] = calculate_quality_score(results)

    return results

def calculate_quality_score(results):
    score = 100

    # Doublons
    score -= min(20, results["duplicates"]["count"])

    # Missing
    score -= min(30, results["missing_values"]["percentage"])

    # Cohérence sémantique
    semantic_penalty = 0
    for col, data in results["semantic_validation"].items():
        if data["conformity_rate"] < 70:
            semantic_penalty += (70 - data["conformity_rate"]) * 0.2

    score -= min(30, semantic_penalty)

    return max(0, round(score, 1))
