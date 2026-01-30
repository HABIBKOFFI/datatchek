# pdf_generator.py
"""
Générateur de rapports PDF pour DataTchek
Génère des rapports professionnels avec métriques et recommandations
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


def get_score_status(score: float) -> tuple:
    """
    Retourne le statut et l'emoji associé au score
    
    Args:
        score: Score de qualité (0-100)
        
    Returns:
        tuple: (status, emoji, color)
    """
    if score >= 80:
        return ("EXCELLENT", "✓", colors.HexColor("#10B981"))
    elif score >= 60:
        return ("BON", "●", colors.HexColor("#3B82F6"))
    elif score >= 40:
        return ("À AMÉLIORER", "■", colors.HexColor("#F59E0B"))
    else:
        return ("CRITIQUE", "▲", colors.HexColor("#EF4444"))


def create_pdf_report(df: pd.DataFrame, results: Dict[str, Any]) -> io.BytesIO:
    """
    Génère un rapport PDF complet
    
    Args:
        df: DataFrame analysé
        results: Résultats de l'analyse
        
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
    
    # Styles
    styles = getSampleStyleSheet()
    elements = []
    
    # Style titre principal
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f77b4"),
        fontSize=28,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Style sous-titre
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=24
    )
    
    # Style section
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=12,
        spaceBefore=18,
        fontName='Helvetica-Bold'
    )
    
    # ======================
    # EN-TÊTE
    # ======================
    elements.append(Paragraph("■ DATATCHEK", title_style))
    elements.append(Paragraph(
        "Rapport d'Analyse de Qualité des Données",
        subtitle_style
    ))
    elements.append(Paragraph(
        f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        subtitle_style
    ))
    
    elements.append(Spacer(1, 0.8*cm))
    
    # ======================
    # SCORE GLOBAL
    # ======================
    score = results['quality_score']
    status, emoji, score_color = get_score_status(score)
    
    elements.append(Paragraph("■ SCORE DE QUALITÉ GLOBAL", section_style))
    
    score_data = [
        ["Score Global", "Statut"],
        [f"{score}/100", f"{status} {emoji}"]
    ]
    
    score_table = Table(score_data, colWidths=[8*cm, 8*cm])
    score_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BACKGROUND', (1, 1), (1, 1), score_color),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # MÉTRIQUES CLÉS
    # ======================
    elements.append(Paragraph("■ MÉTRIQUES CLÉS", section_style))
    
    metrics_data = [
        ["Métrique", "Valeur"],
        ["Total de lignes", f"{results['total_rows']:,}"],
        ["Total de colonnes", f"{results['total_columns']}"],
        ["Doublons détectés", f"{results['duplicates']['count']}"],
        [
            "Données manquantes", 
            f"{results['missing_values']['total']:,} ({results['missing_values']['percentage']}%)"
        ]
    ]
    
    # Ajouter les validations spécifiques
    for col, data in results.get('specific_validation', {}).items():
        invalid_count = data['validation']['invalid_count']
        col_type = data['type']
        
        type_label = {
            'phone': 'Téléphones invalides',
            'email': 'Emails invalides',
            'bank_account': 'Comptes bancaires invalides',
            'currency': 'Devises invalides'
        }.get(col_type, 'Valeurs invalides')
        
        metrics_data.append([
            f"{type_label} ({col})",
            f"{invalid_count:,}"
        ])
    
    metrics_table = Table(metrics_data, colWidths=[11*cm, 5*cm])
    metrics_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # COLONNES DÉTECTÉES
    # ======================
    from .column_detector import detect_column_patterns
    patterns = detect_column_patterns(df)
    
    if patterns:
        elements.append(Paragraph("■ COLONNES DÉTECTÉES AUTOMATIQUEMENT", section_style))
        
        pattern_data = [["Type", "Colonnes"]]
        
        pattern_labels = {
            'identifiers': '■ Identifiants',
            'names': '■ Noms',
            'phones': '■ Téléphones',
            'emails': '■ Emails',
            'dates': '■ Dates',
            'amounts': '■ Montants',
            'categories': '■ Catégories'
        }
        
        for pattern_key, columns in patterns.items():
            if columns:
                pattern_data.append([
                    pattern_labels.get(pattern_key, pattern_key),
                    ", ".join(columns[:5])  # Max 5 colonnes par ligne
                ])
        
        if len(pattern_data) > 1:
            pattern_table = Table(pattern_data, colWidths=[5*cm, 11*cm])
            pattern_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(pattern_table)
            elements.append(Spacer(1, 0.6*cm))
    
    # ======================
    # RECOMMANDATIONS
    # ======================
    from .validators import generate_recommendations
    recommendations = generate_recommendations(results)
    
    if recommendations:
        elements.append(Paragraph("■ RECOMMANDATIONS", section_style))
        
        for i, rec in enumerate(recommendations[:20], 1):  # Max 20 recommandations
            # Nettoyer le texte pour éviter les problèmes d'encodage
            rec_clean = rec.replace('•', '-')
            elements.append(Paragraph(f"• {rec_clean}", styles["Normal"]))
            elements.append(Spacer(1, 0.2*cm))
    
    # ======================
    # PIED DE PAGE
    # ======================
    elements.append(Spacer(1, 1*cm))
    
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey
    )
    
    elements.append(Paragraph(
        "Rapport généré par Datatchek - Outil d'analyse de qualité de données",
        footer_style
    ))
    elements.append(Paragraph(
        "© 2026 HABIB KOFFI - Tous droits réservés",
        footer_style
    ))
    
    # Génération du PDF
    try:
        doc.build(elements)
    except Exception as e:
        print(f"Erreur génération PDF: {e}")
        # Fallback : PDF minimaliste
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = [
            Paragraph("DATATCHEK - Rapport d'Analyse", styles['Title']),
            Paragraph(f"Score: {score}/100", styles['Normal']),
            Paragraph(f"Erreur génération complète: {str(e)}", styles['Normal'])
        ]
        doc.build(elements)
    
    buffer.seek(0)
    return buffer


def create_detailed_semantic_table(results: Dict[str, Any]) -> Table:
    """
    Crée un tableau détaillé de validation sémantique
    (Fonction auxiliaire pour rapports avancés)
    
    Args:
        results: Résultats de l'analyse
        
    Returns:
        Table: Tableau ReportLab
    """
    semantic_data = [
        ["Colonne", "Type attendu", "Type réel", "Conformité (%)", "Invalides"]
    ]
    
    for col, data in results["semantic_validation"].items():
        conformity = data["conformity_rate"]
        
        # N'inclure que les colonnes avec problèmes
        if conformity < 100:
            semantic_data.append([
                col[:20],  # Tronquer si trop long
                data["expected_type"],
                data["actual_type"],
                f"{conformity}%",
                str(data["invalid_count"])
            ])
    
    if len(semantic_data) == 1:
        # Aucun problème
        return None
    
    table = Table(semantic_data, colWidths=[4*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    return table