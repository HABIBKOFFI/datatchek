from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io

def create_pdf_report(df, results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    title = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f77b4"),
        fontSize=24
    )

    elements.append(Paragraph("🎯 DATATCHEK", title))
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph(
        f"Rapport généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 0.6*cm))

    # SCORE
    elements.append(Paragraph("Score global de qualité", styles["Heading2"]))
    elements.append(Paragraph(f"{results['quality_score']} / 100", styles["Normal"]))

    # METRICS
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph("Métriques clés", styles["Heading2"]))

    metrics = [
        ["Lignes", results["total_rows"]],
        ["Colonnes", results["total_columns"]],
        ["Doublons", results["duplicates"]["count"]],
        ["Données manquantes", results["missing_values"]["total"]],
    ]

    table = Table(metrics, colWidths=[8*cm, 6*cm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(table)

    # SEMANTIC
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Cohérence des types de données", styles["Heading2"]))

    semantic_data = [["Colonne", "Type attendu", "Type réel", "Conformité (%)"]]
    for col, data in results["semantic_validation"].items():
        if data["conformity_rate"] < 100:
            semantic_data.append([
                col,
                data["expected_type"],
                data["actual_type"],
                data["conformity_rate"]
            ])

    semantic_table = Table(semantic_data, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])
    semantic_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f77b4")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white)
    ]))

    elements.append(semantic_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
