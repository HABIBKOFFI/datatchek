from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


def create_pdf_report(df, results, filename="rapport_qualite.pdf"):
    """
    Génère un rapport PDF complet de l'analyse de qualité
    
    Args:
        df: DataFrame analysé
        results: Résultats de l'analyse
        filename: Nom du fichier PDF
    
    Returns:
        BytesIO: Fichier PDF en mémoire
    """
    # Créer un buffer en mémoire
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Conteneur pour les éléments du PDF
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style sous-titre
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Style normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12
    )
    
    # EN-TÊTE
    elements.append(Paragraph("🎯 DATATCHEK", title_style))
    elements.append(Paragraph("Rapport d'Analyse de Qualité des Données", normal_style))
    elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Ligne de séparation
    elements.append(Spacer(1, 0.3*cm))
    
    # SCORE DE QUALITÉ
    elements.append(Paragraph("📊 SCORE DE QUALITÉ GLOBAL", subtitle_style))
    
    score = results['quality_score']
    
    # Déterminer le statut
    if score >= 80:
        statut = "EXCELLENT 🎉"
        couleur_score = colors.green
    elif score >= 60:
        statut = "BIEN 👍"
        couleur_score = colors.orange
    else:
        statut = "À AMÉLIORER ⚠️"
        couleur_score = colors.red
    
    # Tableau du score
    score_data = [
        ['Score Global', 'Statut'],
        [f'{score}/100', statut]
    ]
    
    score_table = Table(score_data, colWidths=[8*cm, 8*cm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, 1), couleur_score),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.white),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, 1), 16),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # MÉTRIQUES PRINCIPALES
    elements.append(Paragraph("📈 MÉTRIQUES CLÉS", subtitle_style))
    
    metrics_data = [
        ['Métrique', 'Valeur'],
        ['Total de lignes', f"{results['total_rows']:,}"],
        ['Total de colonnes', f"{results['total_columns']:,}"],
        ['Doublons détectés', f"{results['duplicates']['count']:,}"],
        ['Données manquantes', f"{results['missing_values']['total']:,} ({results['missing_values']['percentage']}%)"]
    ]
    
    # Ajouter emails si présents
    if 'emails' in results:
        for col, data in results['emails'].items():
            metrics_data.append([f'Emails invalides ({col})', f"{data['invalid']:,}"])
    
    # Ajouter téléphones si présents
    if 'phones' in results:
        for col, data in results['phones'].items():
            metrics_data.append([f'Téléphones invalides ({col})', f"{data['invalid']:,}"])
    
    metrics_table = Table(metrics_data, colWidths=[10*cm, 6*cm])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # COLONNES DÉTECTÉES
    if 'detected_columns' in results:
        detected = results['detected_columns']
        
        elements.append(Paragraph("🔍 COLONNES DÉTECTÉES AUTOMATIQUEMENT", subtitle_style))
        
        detection_data = [['Type', 'Colonnes']]
        
        if detected['email']:
            detection_data.append(['📧 Emails', ', '.join(detected['email'])])
        
        if detected['phone']:
            detection_data.append(['📱 Téléphones', ', '.join(detected['phone'])])
        
        if detected['name']:
            detection_data.append(['👤 Noms', ', '.join(detected['name'])])
        
        if len(detection_data) > 1:
            detection_table = Table(detection_data, colWidths=[4*cm, 12*cm])
            detection_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            elements.append(detection_table)
            elements.append(Spacer(1, 0.5*cm))
    
    # RECOMMANDATIONS
    elements.append(Paragraph("💡 RECOMMANDATIONS", subtitle_style))
    
    recommendations = []
    
    if results['duplicates']['count'] > 0:
        recommendations.append(f"• Supprimer les {results['duplicates']['count']} doublons détectés")
    
    if results['missing_values']['total'] > 0:
        recommendations.append(f"• Traiter les {results['missing_values']['total']} valeurs manquantes")
    
    if 'emails' in results:
        for col, data in results['emails'].items():
            if data['invalid'] > 0:
                recommendations.append(f"• Corriger les {data['invalid']} emails invalides dans '{col}'")
    
    if 'phones' in results:
        for col, data in results['phones'].items():
            if data['invalid'] > 0:
                recommendations.append(f"• Corriger les {data['invalid']} téléphones invalides dans '{col}'")
    
    if not recommendations:
        recommendations.append("• Vos données sont de bonne qualité ! Continuez ainsi.")
    
    for rec in recommendations:
        elements.append(Paragraph(rec, normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # FOOTER
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Rapport généré par Datatchek - Outil d'analyse de qualité de données", footer_style))
    elements.append(Paragraph(f"© {datetime.now().year} HABIB KOFFI - Tous droits réservés", footer_style))
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le PDF du buffer
    buffer.seek(0)
    return buffer