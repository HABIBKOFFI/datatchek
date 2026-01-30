import pandas as pd
from datetime import datetime

SEMANTIC_RULES = {
    "numeric": ["age", "montant", "prix", "total", "score", "quantite", "nombre", "amount"],
    "date": ["date", "dt", "naissance", "created", "updated"],
    "boolean": ["is_", "has_", "flag", "actif", "enabled"],
    "categorical": ["type", "statut", "status", "niveau", "category"],
}

def infer_expected_type(column_name):
    name = column_name.lower()
    for expected_type, keywords in SEMANTIC_RULES.items():
        if any(k in name for k in keywords):
            return expected_type
    return "text"

def detect_actual_type(series):
    non_null = series.dropna()
    if non_null.empty:
        return "unknown"

    sample = non_null.head(min(100, len(non_null)))

    numeric, date, boolean = 0, 0, 0

    for val in sample:
        # Numeric
        try:
            float(str(val).replace(",", "").replace(" ", ""))
            numeric += 1
            continue
        except:
            pass

        # Date
        try:
            pd.to_datetime(val, errors="raise")
            date += 1
            continue
        except:
            pass

        # Boolean
        if str(val).lower() in ["true", "false", "yes", "no", "1", "0"]:
            boolean += 1

    total = len(sample)
    threshold = 0.7

    if numeric / total >= threshold:
        return "numeric"
    if date / total >= threshold:
        return "date"
    if boolean / total >= threshold:
        return "boolean"

    unique_ratio = sample.nunique() / total
    if unique_ratio < 0.3:
        return "categorical"

    return "text"

def analyze_columns(df):
    analysis = {}

    for col in df.columns:
        expected = infer_expected_type(col)
        actual = detect_actual_type(df[col])

        non_null = df[col].dropna()
        if non_null.empty:
            conformity = 0
        else:
            valid_count = sum(
                detect_actual_type(pd.Series([v])) == actual
                for v in non_null
            )
            conformity = round((valid_count / len(non_null)) * 100, 1)

        analysis[col] = {
            "expected_type": expected,
            "actual_type": actual,
            "conformity_rate": conformity,
            "invalid_count": len(non_null) - int(len(non_null) * conformity / 100)
        }

    return analysis
