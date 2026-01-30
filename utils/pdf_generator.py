# pdf_generator.py
"""
Générateur de rapports PDF avec nommage intelligent
Style Dataiku DSS
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
from typing import Dict, Any
import pandas as pd


def create_pdf_report(df: pd.DataFrame, results: Dict[str, Any], filename: str = None) -> io.BytesIO:
    """
    Génère un rapport PDF professionnel
    
    Args:
        df: DataFrame analysé
        results: Résultats de l'analyse
        filename: Nom du fichier source (pour le titre)
        
    Returns:
        BytesIO: Buffer contenant le PDF
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2563EB"),
        fontSize=26,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=15,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # ======================
    # EN-TÊTE
    # ======================
    elements.append(Paragraph("DATATCHEK", title_style))
    elements.append(Paragraph("Rapport d'Analyse de Qualité des Données", subtitle_style))
    
    # Nom du fichier source
    if filename:
        elements.append(Paragraph(
            f"<b>Fichier analysé :</b> {filename}",
            styles["Normal"]
        ))
    
    elements.append(Paragraph(
        f"<b>Date du rapport :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles["Normal"]
    ))
    
    elements.append(Spacer(1, 0.8*cm))
    
    # ======================
    # SCORE GLOBAL
    # ======================
    score = results['quality_score']
    
    if score >= 80:
        status, color = "EXCELLENT", colors.HexColor("#10B981")
    elif score >= 60:
        status, color = "BON", colors.HexColor("#3B82F6")
    elif score >= 40:
        status, color = "MOYEN", colors.HexColor("#F59E0B")
    else:
        status, color = "FAIBLE", colors.HexColor("#EF4444")
    
    elements.append(Paragraph("1. SCORE DE QUALITÉ", section_style))
    
    score_data = [
        ["Score Global", "Statut"],
        [f"{score}/100", status]
    ]
    
    score_table = Table(score_data, colWidths=[8*cm, 8*cm])
    score_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 16),
        ('BACKGROUND', (1, 1), (1, 1), color),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # MÉTRIQUES CLÉS
    # ======================
    elements.append(Paragraph("2. MÉTRIQUES CLÉS", section_style))
    
    metrics_data = [
        ["Métrique", "Valeur"],
        ["Nombre total de lignes", f"{results['total_rows']:,}"],
        ["Nombre total de colonnes", f"{results['total_columns']}"],
        ["Doublons détectés", f"{results['duplicates']['count']:,} ({results['duplicates']['percentage']}%)"],
        ["Valeurs manquantes", f"{results['missing_values']['total']:,} ({results['missing_values']['percentage']}%)"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[10*cm, 6*cm])
    metrics_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # VALIDATION SÉMANTIQUE
    # ======================
    elements.append(Paragraph("3. VALIDATION SÉMANTIQUE", section_style))
    elements.append(Paragraph(
        "Cohérence entre le type de données attendu (basé sur le nom de la colonne) et le type réel détecté :",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.3*cm))
    
    semantic_data = [["Colonne", "Type Attendu", "Type Réel", "Conformité (%)"]]
    
    # Ajouter colonnes avec problèmes de conformité
    has_semantic_issues = False
    for col, data in results["semantic_validation"].items():
        if data["conformity_rate"] < 100:
            has_semantic_issues = True
            semantic_data.append([
                col[:25],  # Tronquer si trop long
                data["expected_type"],
                data["actual_type"],
                f"{data['conformity_rate']}%"
            ])
    
    if has_semantic_issues:
        semantic_table = Table(semantic_data, colWidths=[5*cm, 3.5*cm, 3.5*cm, 3*cm])
        semantic_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(semantic_table)
    else:
        elements.append(Paragraph(
            "✓ Toutes les colonnes ont un type cohérent avec leur nom",
            styles["Normal"]
        ))
    
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # COLONNES PAR TYPE
    # ======================
    elements.append(Paragraph("4. RÉPARTITION DES COLONNES PAR TYPE", section_style))
    
    # Grouper colonnes par type détecté
    type_groups = {}
    for col, data in results["semantic_validation"].items():
        actual_type = data["actual_type"]
        if actual_type not in type_groups:
            type_groups[actual_type] = []
        type_groups[actual_type].append(col)
    
    type_data = [["Type de Données", "Nombre", "Colonnes (exemples)"]]
    for dtype, cols in sorted(type_groups.items(), key=lambda x: len(x[1]), reverse=True):
        col_examples = ", ".join(cols[:5])  # Max 5 exemples
        if len(cols) > 5:
            col_examples += "..."
        type_data.append([
            dtype,
            str(len(cols)),
            col_examples
        ])
    
    type_table = Table(type_data, colWidths=[4*cm, 2*cm, 10*cm])
    type_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(type_table)
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # RECOMMANDATIONS
    # ======================
    elements.append(Paragraph("5. RECOMMANDATIONS", section_style))
    
    from .validators import generate_recommendations
    recommendations = generate_recommendations(results)
    
    if recommendations:
        # Grouper par priorité
        high_priority = [r for r in recommendations if r['priority'] == 'HAUTE']
        medium_priority = [r for r in recommendations if r['priority'] == 'MOYENNE']
        
        if high_priority:
            elements.append(Paragraph("<b>🔴 Priorité HAUTE :</b>", styles["Normal"]))
            for rec in high_priority[:5]:  # Max 5
                elements.append(Paragraph(f"• {rec['message']}", styles["Normal"]))
                elements.append(Paragraph(f"  → <i>{rec['action']}</i>", styles["Normal"]))
                elements.append(Spacer(1, 0.2*cm))
        
        if medium_priority:
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("<b>🟠 Priorité MOYENNE :</b>", styles["Normal"]))
            for rec in medium_priority[:5]:  # Max 5
                elements.append(Paragraph(f"• {rec['message']}", styles["Normal"]))
                elements.append(Paragraph(f"  → <i>{rec['action']}</i>", styles["Normal"]))
                elements.append(Spacer(1, 0.2*cm))
    else:
        elements.append(Paragraph(
            "✓ Aucune recommandation - Vos données sont de qualité excellente !",
            styles["Normal"]
        ))
    
    # ======================
    # PIED DE PAGE
    # ======================
    elements.append(Spacer(1, 1.5*cm))
    
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.grey
    )
    
    elements.append(Paragraph(
        "Rapport généré par DataTchek - Analyse automatique de la qualité des données",
        footer_style
    ))
    elements.append(Paragraph(
        f"© {datetime.now().year} HABIB KOFFI - Tous droits réservés",
        footer_style
    ))
    
    # Génération du PDF
    try:
        doc.build(elements)
    except Exception as e:
        print(f"Erreur génération PDF: {e}")
        # Fallback simple
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = [
            Paragraph("DATATCHEK - Rapport d'Analyse", styles['Title']),
            Paragraph(f"Fichier: {filename}", styles['Normal']),
            Paragraph(f"Score: {score}/100", styles['Normal']),
            Paragraph(f"Erreur génération complète: {str(e)}", styles['Normal'])
        ]
        doc.build(elements)
    
    buffer.seek(0)
    return buffer