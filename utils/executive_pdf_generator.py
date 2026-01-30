# utils/executive_pdf_generator.py
"""
Générateur de rapport PDF Executive pour DataTchek
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import io


def create_executive_pdf(df, results, filename, lang='fr'):
    """
    Génère un rapport PDF Executive Summary
    
    Args:
        df: DataFrame analysé
        results: Résultats de l'analyse
        filename: Nom du fichier source
        lang: Langue ('fr' ou 'en')
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
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#334155'),
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16
    )
    
    # ====================
    # PAGE DE GARDE
    # ====================
    elements.append(Spacer(1, 3*cm))
    
    elements.append(Paragraph("🎯 DATATCHEK", title_style))
    elements.append(Paragraph("Rapport d'Analyse de Qualité des Données" if lang == 'fr' else "Data Quality Analysis Report", subtitle_style))
    
    elements.append(Spacer(1, 2*cm))
    
    # Informations principales
    info_data = [
        ["Fichier analysé", filename],
        ["Date d'analyse", datetime.now().strftime('%d/%m/%Y %H:%M')],
        ["Volume", f"{len(df):,} lignes × {len(df.columns)} colonnes"],
        ["Score de qualité", f"{results['quality_score']}/100"]
    ]
    
    info_table = Table(info_data, colWidths=[6*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 2*cm))
    
    # Badge de qualité
    score = results['quality_score']
    if score >= 90:
        badge_text = "💎 QUALITÉ PLATINUM" if lang == 'fr' else "💎 PLATINUM QUALITY"
        badge_color = colors.HexColor('#C7D2FE')
    elif score >= 75:
        badge_text = "🏆 QUALITÉ GOLD" if lang == 'fr' else "🏆 GOLD QUALITY"
        badge_color = colors.HexColor('#FDE68A')
    elif score >= 60:
        badge_text = "🥈 QUALITÉ SILVER" if lang == 'fr' else "🥈 SILVER QUALITY"
        badge_color = colors.HexColor('#E5E7EB')
    else:
        badge_text = "🥉 QUALITÉ BRONZE" if lang == 'fr' else "🥉 BRONZE QUALITY"
        badge_color = colors.HexColor('#FDBA74')
    
    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=badge_color,
        borderPadding=15,
        borderRadius=10
    )
    
    elements.append(Paragraph(badge_text, badge_style))
    
    elements.append(PageBreak())
    
    # ====================
    # RÉSUMÉ EXÉCUTIF
    # ====================
    elements.append(Paragraph("📋 RÉSUMÉ EXÉCUTIF" if lang == 'fr' else "📋 EXECUTIVE SUMMARY", subtitle_style))
    
    # Générer résumé intelligent
    summary_text = generate_executive_summary(df, results, lang)
    elements.append(Paragraph(summary_text, body_style))
    
    elements.append(Spacer(1, 1*cm))
    
    # ====================
    # IMPACT MÉTIER
    # ====================
    elements.append(Paragraph("💼 IMPACT MÉTIER" if lang == 'fr' else "💼 BUSINESS IMPACT", subtitle_style))
    
    impact_text = generate_business_impact(results, lang)
    elements.append(Paragraph(impact_text, body_style))
    
    elements.append(Spacer(1, 1*cm))
    
    # ====================
    # PROBLÈMES MAJEURS
    # ====================
    elements.append(Paragraph("⚠️ PROBLÈMES MAJEURS" if lang == 'fr' else "⚠️ MAJOR ISSUES", subtitle_style))
    
    issues = identify_major_issues(results, lang)
    
    for idx, issue in enumerate(issues[:5], 1):
        issue_style = ParagraphStyle(
            'Issue',
            parent=body_style,
            leftIndent=20,
            bulletIndent=10,
            spaceBefore=6,
            spaceAfter=6
        )
        elements.append(Paragraph(f"<b>{idx}.</b> {issue}", issue_style))
    
    elements.append(Spacer(1, 1*cm))
    
    # ====================
    # RECOMMANDATIONS ACTIONNABLES
    # ====================
    elements.append(Paragraph("💡 RECOMMANDATIONS ACTIONNABLES" if lang == 'fr' else "💡 ACTIONABLE RECOMMENDATIONS", subtitle_style))
    
    recommendations = generate_actionable_recommendations(results, lang)
    
    for idx, reco in enumerate(recommendations[:5], 1):
        reco_style = ParagraphStyle(
            'Recommendation',
            parent=body_style,
            leftIndent=20,
            bulletIndent=10,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.HexColor('#0F766E')
        )
        elements.append(Paragraph(f"<b>{idx}.</b> {reco}", reco_style))
    
    elements.append(PageBreak())
    
    # ====================
    # NIVEAU DE MATURITÉ DATA
    # ====================
    elements.append(Paragraph("📊 NIVEAU DE MATURITÉ DATA" if lang == 'fr' else "📊 DATA MATURITY LEVEL", subtitle_style))
    
    maturity_text = assess_data_maturity(results, lang)
    elements.append(Paragraph(maturity_text, body_style))
    
    elements.append(Spacer(1, 2*cm))
    
    # ====================
    # FOOTER
    # ====================
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#94A3B8'),
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("─" * 80, footer_style))
    elements.append(Paragraph(
        "Rapport généré par DataTchek - Plateforme Professionnelle d'Analyse de Qualité<br/>"
        "© 2026 DataTchek by HABIB KOFFI - Tous droits réservés",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generate_executive_summary(df, results, lang='fr'):
    """Génère un résumé exécutif intelligent"""
    score = results['quality_score']
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_pct = results['missing_values']['percentage']
    duplicates = results['duplicates']['count']
    
    if lang == 'fr':
        if score >= 80:
            quality_adj = "excellente"
        elif score >= 60:
            quality_adj = "bonne"
        else:
            quality_adj = "insuffisante"
        
        summary = f"""
        Ce dataset contient <b>{total_rows:,} enregistrements</b> répartis sur <b>{total_cols} colonnes</b>. 
        L'analyse révèle une qualité globale <b>{quality_adj}</b> avec un score de <b>{score}/100</b>.
        <br/><br/>
        """
        
        if missing_pct > 20:
            summary += f"⚠️ <b>Point d'attention majeur</b> : {missing_pct:.1f}% des données sont manquantes, ce qui représente un risque significatif pour les analyses métier. "
        elif missing_pct > 5:
            summary += f"Les données manquantes représentent {missing_pct:.1f}% du volume total, un niveau acceptable mais nécessitant une surveillance. "
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            summary += f"<br/>{duplicates} doublons ont été identifiés ({dup_pct:.1f}%), suggérant des problèmes potentiels de collecte ou d'intégration. "
        
        summary += f"<br/><br/>Ce niveau de qualité permet {'une exploitation fiable des données pour la prise de décision.' if score >= 70 else 'une exploitation limitée et nécessite des actions correctives urgentes.'}"
    
    else:  # English
        quality_adj = "excellent" if score >= 80 else "good" if score >= 60 else "insufficient"
        
        summary = f"""
        This dataset contains <b>{total_rows:,} records</b> across <b>{total_cols} columns</b>.
        Analysis reveals <b>{quality_adj}</b> overall quality with a score of <b>{score}/100</b>.
        <br/><br/>
        """
        
        if missing_pct > 20:
            summary += f"⚠️ <b>Major concern</b>: {missing_pct:.1f}% of data is missing, representing significant risk for business analysis. "
        elif missing_pct > 5:
            summary += f"Missing data represents {missing_pct:.1f}% of total volume, an acceptable level requiring monitoring. "
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            summary += f"<br/>{duplicates} duplicates identified ({dup_pct:.1f}%), suggesting potential collection or integration issues. "
        
        summary += f"<br/><br/>This quality level allows {'reliable data exploitation for decision-making.' if score >= 70 else 'limited exploitation and requires urgent corrective actions.'}"
    
    return summary


def generate_business_impact(results, lang='fr'):
    """Traduit les métriques techniques en impact métier"""
    missing_pct = results['missing_values']['percentage']
    duplicates = results['duplicates']['count']
    total_rows = results['total_rows']
    
    if lang == 'fr':
        impact = "<b>Impacts identifiés sur l'activité :</b><br/><br/>"
        
        if missing_pct > 20:
            impact += "🔴 <b>Risque élevé</b> : Les données manquantes peuvent conduire à des décisions erronées et affecter la fiabilité des reportings.<br/>"
        elif missing_pct > 10:
            impact += "🟠 <b>Risque modéré</b> : Les analyses statistiques peuvent être biaisées par l'absence de certaines données.<br/>"
        else:
            impact += "🟢 <b>Risque faible</b> : Le taux de complétude permet des analyses fiables.<br/>"
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            if dup_pct > 5:
                impact += "<br/>🔴 <b>Surévaluation potentielle</b> : Les doublons peuvent fausser les indicateurs de volumétrie et de performance.<br/>"
            else:
                impact += "<br/>🟠 <b>Attention requise</b> : Présence de doublons pouvant affecter certains calculs.<br/>"
        
        impact += "<br/><b>Recommandation stratégique</b> : Prioriser le nettoyage des données avant toute prise de décision critique."
    
    else:  # English
        impact = "<b>Identified business impacts:</b><br/><br/>"
        
        if missing_pct > 20:
            impact += "🔴 <b>High risk</b>: Missing data may lead to incorrect decisions and affect reporting reliability.<br/>"
        elif missing_pct > 10:
            impact += "🟠 <b>Moderate risk</b>: Statistical analyses may be biased by missing data.<br/>"
        else:
            impact += "🟢 <b>Low risk</b>: Completeness rate allows for reliable analyses.<br/>"
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            if dup_pct > 5:
                impact += "<br/>🔴 <b>Potential overestimation</b>: Duplicates may distort volume and performance indicators.<br/>"
            else:
                impact += "<br/>🟠 <b>Attention required</b>: Presence of duplicates may affect some calculations.<br/>"
        
        impact += "<br/><b>Strategic recommendation</b>: Prioritize data cleaning before any critical decision-making."
    
    return impact


def identify_major_issues(results, lang='fr'):
    """Identifie les 5 problèmes majeurs"""
    issues = []
    
    missing_pct = results['missing_values']['percentage']
    duplicates = results['duplicates']['count']
    total_rows = results['total_rows']
    
    if lang == 'fr':
        if missing_pct > 20:
            issues.append(f"<b>Données manquantes critiques</b> : {missing_pct:.1f}% du volume total affecte la fiabilité des analyses")
        elif missing_pct > 5:
            issues.append(f"<b>Données manquantes modérées</b> : {missing_pct:.1f}% nécessite une attention")
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            issues.append(f"<b>Doublons détectés</b> : {duplicates} enregistrements ({dup_pct:.1f}%) nécessitent un dédoublonnage")
        
        # Analyser colonnes avec beaucoup de manquants
        for col, count in results['missing_values']['by_column'].items():
            if count > 0:
                col_pct = (count / total_rows * 100)
                if col_pct > 50:
                    issues.append(f"<b>Colonne '{col}' quasi-vide</b> : {col_pct:.1f}% manquant - Supprimer ou imputer")
                    if len(issues) >= 5:
                        break
    
    else:  # English
        if missing_pct > 20:
            issues.append(f"<b>Critical missing data</b>: {missing_pct:.1f}% of total volume affects analysis reliability")
        elif missing_pct > 5:
            issues.append(f"<b>Moderate missing data</b>: {missing_pct:.1f}% requires attention")
        
        if duplicates > 0:
            dup_pct = (duplicates / total_rows * 100)
            issues.append(f"<b>Duplicates detected</b>: {duplicates} records ({dup_pct:.1f}%) require deduplication")
        
        for col, count in results['missing_values']['by_column'].items():
            if count > 0:
                col_pct = (count / total_rows * 100)
                if col_pct > 50:
                    issues.append(f"<b>Column '{col}' nearly empty</b>: {col_pct:.1f}% missing - Remove or impute")
                    if len(issues) >= 5:
                        break
    
    return issues[:5]


def generate_actionable_recommendations(results, lang='fr'):
    """Génère des recommandations actionnables"""
    reco = []
    
    missing_pct = results['missing_values']['percentage']
    duplicates = results['duplicates']['count']
    
    if lang == 'fr':
        if missing_pct > 20:
            reco.append("Mettre en place un processus de collecte des données manquantes à la source")
        elif missing_pct > 5:
            reco.append("Documenter les raisons des données manquantes et définir une stratégie d'imputation")
        
        if duplicates > 0:
            reco.append("Exécuter un processus de dédoublonnage avec règles métier validées")
        
        reco.append("Établir des contrôles qualité automatisés à l'ingestion des données")
        reco.append("Former les équipes métier aux bonnes pratiques de saisie")
        reco.append("Mettre en place un tableau de bord de suivi de la qualité")
    
    else:  # English
        if missing_pct > 20:
            reco.append("Implement data collection process at source for missing data")
        elif missing_pct > 5:
            reco.append("Document reasons for missing data and define imputation strategy")
        
        if duplicates > 0:
            reco.append("Execute deduplication process with validated business rules")
        
        reco.append("Establish automated quality controls at data ingestion")
        reco.append("Train business teams on data entry best practices")
        reco.append("Implement quality monitoring dashboard")
    
    return reco[:5]


def assess_data_maturity(results, lang='fr'):
    """Évalue le niveau de maturité data"""
    score = results['quality_score']
    
    if lang == 'fr':
        if score >= 90:
            level = "🎓 <b>Niveau Expert</b>"
            desc = "Votre organisation démontre une excellente maîtrise de la qualité des données. Les processus de gouvernance sont en place et efficaces. Continuez à maintenir ce niveau d'excellence."
        elif score >= 75:
            level = "⭐ <b>Niveau Master</b>"
            desc = "Bonne maturité data avec des processus établis. Quelques optimisations permettraient d'atteindre l'excellence. Focalisez-vous sur l'automatisation des contrôles."
        elif score >= 60:
            level = "📊 <b>Niveau Avancé</b>"
            desc = "Niveau intermédiaire avec des bases solides. Des améliorations structurelles sont nécessaires pour fiabiliser les décisions métier. Priorisez la formation et les processus."
        else:
            level = "🌱 <b>Niveau Débutant</b>"
            desc = "La qualité des données nécessite une attention urgente. Mettez en place des processus de gouvernance et de contrôle avant d'utiliser ces données pour des décisions critiques."
        
        maturity = f"{level}<br/><br/>{desc}<br/><br/>"
        maturity += f"<b>Score actuel</b> : {score}/100<br/>"
        maturity += f"<b>Objectif recommandé</b> : {min(score + 15, 100)}/100 dans les 3 prochains mois"
    
    else:  # English
        if score >= 90:
            level = "🎓 <b>Expert Level</b>"
            desc = "Your organization demonstrates excellent data quality mastery. Governance processes are in place and effective. Continue maintaining this level of excellence."
        elif score >= 75:
            level = "⭐ <b>Master Level</b>"
            desc = "Good data maturity with established processes. Some optimizations would help achieve excellence. Focus on control automation."
        elif score >= 60:
            level = "📊 <b>Advanced Level</b>"
            desc = "Intermediate level with solid foundations. Structural improvements needed to ensure reliable business decisions. Prioritize training and processes."
        else:
            level = "🌱 <b>Beginner Level</b>"
            desc = "Data quality requires urgent attention. Implement governance and control processes before using this data for critical decisions."
        
        maturity = f"{level}<br/><br/>{desc}<br/><br/>"
        maturity += f"<b>Current score</b>: {score}/100<br/>"
        maturity += f"<b>Recommended target</b>: {min(score + 15, 100)}/100 within 3 months"
    
    return maturity