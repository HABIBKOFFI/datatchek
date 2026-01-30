# 🎯 DataTchek v2.0 - Style Dataiku DSS

## 📋 Résumé des Améliorations

Transformation de DataTchek pour adopter une approche **Dataiku DSS** :

### ❌ Ce qui a été RETIRÉ
- ✅ Validation spécifique téléphones (format +225)
- ✅ Validation spécifique emails
- ✅ Validation spécifique comptes bancaires BCEAO
- ✅ Validation spécifique devises FCFA

### ✅ Ce qui a été AJOUTÉ
- ✅ **Validation sémantique intelligente** (type attendu vs type réel)
- ✅ **Nommage intelligent** basé sur le fichier source
- ✅ **Nettoyage automatique** (style Dataiku Prepare)
- ✅ **Gestion données professionnelle**
- ✅ **Recommandations priorisées** (HAUTE/MOYENNE/BASSE)

---

## 🧠 1. Validation Sémantique (Cœur du Système)

### Concept

Au lieu de valider des formats spécifiques (téléphone, email), DataTchek analyse maintenant :

```
Nom de colonne → Type attendu
     ↓
Contenu réel → Type détecté
     ↓
Comparaison → Score de conformité
```

### Exemples Concrets

| Nom Colonne | Type Attendu | Type Détecté | Conformité | Analyse |
|-------------|--------------|--------------|------------|---------|
| `age` | numeric | numeric | 100% | ✅ Parfait |
| `date_naissance` | date | text | 45% | ⚠️ Problème format |
| `montant` | numeric | numeric | 98% | ✅ Bon (quelques nulls) |
| `statut` | categorical | categorical | 100% | ✅ Parfait |
| `id_client` | identifier | numeric | 100% | ✅ Parfait |

### Code

```python
# column_detector.py
def infer_expected_type(column_name: str) -> str:
    """
    Devine le type attendu basé sur le nom
    """
    name_lower = column_name.lower()
    
    # Règles sémantiques
    if any(kw in name_lower for kw in ['age', 'montant', 'prix', 'total']):
        return 'numeric'
    
    if any(kw in name_lower for kw in ['date', 'dt', 'naissance']):
        return 'date'
    
    if any(kw in name_lower for kw in ['id', 'code', 'ref']):
        return 'identifier'
    
    # ... etc
    return 'text'

def detect_actual_type(series: pd.Series) -> str:
    """
    Détecte le type réel en analysant le contenu
    """
    # Analyse échantillon
    # Retourne: numeric, date, boolean, categorical, text, etc.
```

---

## 📛 2. Nommage Intelligent des Fichiers

### Principe

Tous les fichiers générés (nettoyés, rapports, analyses) portent un nom **basé sur le fichier source** + timestamp.

### Module `file_naming.py`

```python
from file_naming import FileNamingManager

# Fichier source
manager = FileNamingManager("donnees_clients_2024.csv")

# Génération automatique des noms
manager.generate_cleaned_filename()
# → "donnees_clients_2024_cleaned_20260130_151234.csv"

manager.generate_report_filename('pdf')
# → "rapport_donnees_clients_2024_20260130_151234.pdf"

manager.generate_analysis_filename()
# → "analyse_donnees_clients_2024_20260130_151234.json"
```

### Avantages

✅ **Traçabilité** : Lien clair avec le fichier source  
✅ **Pas de collision** : Timestamp garantit unicité  
✅ **Organisation** : Facile de retrouver les fichiers liés  
✅ **Professionnel** : Nommage cohérent  

### Exemples Complets

| Fichier Source | Fichier Nettoyé | Rapport PDF |
|----------------|-----------------|-------------|
| `clients_janvier.csv` | `clients_janvier_cleaned_20260130_143022.csv` | `rapport_clients_janvier_20260130_143022.pdf` |
| `Ventes 2024.xlsx` | `ventes_2024_cleaned_20260130_150145.csv` | `rapport_ventes_2024_20260130_150145.pdf` |
| `DATA-EXPORT.csv` | `data_export_cleaned_20260130_152233.csv` | `rapport_data_export_20260130_152233.pdf` |

---

## 🧹 3. Nettoyage Automatique (Style Dataiku Prepare)

### Module `data_cleaner.py`

Classe `DataCleaner` qui permet de :

```python
from data_cleaner import DataCleaner

# Créer nettoyeur
cleaner = DataCleaner(df, filename="donnees_clients_2024.csv")

# Nettoyage complet automatique
cleaner.auto_clean(aggressive=False)

# Récupérer le DataFrame nettoyé
df_cleaned = cleaner.get_cleaned_dataframe()

# Récupérer le rapport de nettoyage
report = cleaner.get_cleaning_report()
```

### Opérations Disponibles

| Opération | Description | Mode |
|-----------|-------------|------|
| `remove_empty_columns()` | Supprime colonnes 100% vides | Auto |
| `remove_high_missing_columns(threshold=0.8)` | Supprime colonnes >80% manquants | Auto |
| `remove_duplicates()` | Supprime lignes dupliquées | Auto |
| `remove_constant_columns()` | Supprime colonnes avec 1 seule valeur | Agressif |
| `fill_missing_numeric(strategy='median')` | Impute valeurs manquantes numériques | Auto |
| `fill_missing_categorical(strategy='mode')` | Impute valeurs manquantes catégorielles | Auto |
| `standardize_column_names()` | Standardise noms (snake_case) | Auto |
| `convert_to_numeric(columns)` | Convertit en numérique | Agressif |
| `convert_to_datetime(columns)` | Convertit en datetime | Agressif |
| `remove_whitespace()` | Supprime espaces inutiles | Auto |

### Exemple Complet

```python
# Fichier source
df = pd.read_csv("donnees_clients_2024.csv")

# Créer nettoyeur
cleaner = DataCleaner(df, "donnees_clients_2024.csv")

# Nettoyage automatique
cleaner.auto_clean(aggressive=True)

# Récupérer résultats
df_cleaned = cleaner.get_cleaned_dataframe()
report = cleaner.get_cleaning_report()

# Sauvegarder avec nom intelligent
cleaned_filename = cleaner.generate_cleaned_filename()
df_cleaned.to_csv(cleaned_filename, index=False)

print(report)
# {
#   'source_file': 'donnees_clients_2024.csv',
#   'original_shape': (1000, 25),
#   'cleaned_shape': (987, 20),
#   'rows_removed': 13,
#   'columns_removed': 5,
#   'operations': [
#       {'operation': 'remove_empty_columns', 'columns': ['col1', 'col2'], 'count': 2},
#       {'operation': 'remove_duplicates', 'rows_removed': 13},
#       ...
#   ]
# }
```

---

## 📊 4. Recommandations Priorisées

### Système de Priorités

Les recommandations sont maintenant **priorisées** comme dans Dataiku :

```python
recommendations = [
    {
        "priority": "HAUTE",        # 🔴
        "category": "Doublons",
        "message": "⚠️ 150 doublons détectés (15% des données)",
        "action": "Supprimer ou fusionner les lignes dupliquées"
    },
    {
        "priority": "MOYENNE",      # 🟠
        "category": "Cohérence sémantique",
        "message": "⚡ Colonne 'age' : Conformité 65%",
        "action": "Vérifier et nettoyer les 350 valeurs suspectes"
    },
    {
        "priority": "BASSE",        # ℹ️
        "category": "Optimisation",
        "message": "ℹ️ Colonne 'statut' : Très faible diversité (3 valeurs)",
        "action": "Convertir en type catégoriel pour optimiser"
    }
]
```

### Dans le Rapport PDF

```
5. RECOMMANDATIONS

🔴 Priorité HAUTE :
• ⚠️ 150 doublons détectés (15% des données)
  → Supprimer ou fusionner les lignes dupliquées

• ⚠️ Colonne 'email' : 85% de valeurs manquantes
  → Supprimer la colonne ou imputer les valeurs

🟠 Priorité MOYENNE :
• ⚡ Colonne 'age' : Type 'text' au lieu de 'numeric'
  → Convertir en numérique et corriger les 45 valeurs invalides

ℹ️ Priorité BASSE :
• Colonne 'statut' : Très faible diversité
  → Convertir en catégoriel pour optimiser mémoire
```

---

## 📈 5. Calcul du Score de Qualité

### Nouvelle Formule (style Dataiku)

```python
Score Global = 100 points

- Doublons (max -15 points)
  └─ Pénalité = min(15, % doublons × 1.5)

- Valeurs manquantes (max -25 points)
  └─ Pénalité = min(25, % manquants × 1.2)

- Incohérence sémantique (max -35 points)
  └─ Pour chaque colonne :
      • Conformité < 50% : -3 points
      • Conformité 50-70% : -2 points
      • Conformité 70-90% : -1 point

- Faible cardinalité sur clés (max -10 points)
  └─ Si colonne avec 'id'/'code' a <80% valeurs uniques : -2 points

+ Bonus qualité excellente (max +10 points)
  └─ Si 0 doublons ET <5% manquants : +10
```

### Exemple Calcul

```
Dataset : 1000 lignes, 20 colonnes

- Doublons : 2% → -3 points
- Manquants : 15% → -18 points
- Sémantique : 3 colonnes avec problèmes → -7 points
- Cardinalité : OK → 0 point
- Bonus : non applicable

Score final : 100 - 3 - 18 - 7 = 72/100 🟡 MOYEN
```

---

## 🔄 6. Workflow Complet

### Étape par Étape

```
1. UPLOAD
   User: Upload "donnees_clients_2024.csv"
   ↓
   App: Charge fichier + crée FileNamingManager

2. ANALYSE AUTOMATIQUE
   App: Analyse qualité via validate_dataframe()
   ↓
   Résultats:
   - Score global : 72/100
   - Doublons : 2%
   - Manquants : 15%
   - Sémantique : 3 colonnes incohérentes

3. AFFICHAGE RÉSULTATS
   App: Affiche score + métriques + recommandations
   ↓
   User: Consulte recommandations priorisées

4. NETTOYAGE AUTO (optionnel)
   User: Clic "Lancer nettoyage automatique"
   ↓
   App: DataCleaner.auto_clean(aggressive=True)
   ↓
   Résultats nettoyage:
   - 13 lignes supprimées (doublons)
   - 5 colonnes supprimées (>80% manquants)
   - Noms colonnes standardisés

5. TÉLÉCHARGEMENTS
   User: Télécharge fichiers
   ↓
   Fichiers générés:
   - donnees_clients_2024_cleaned_20260130_151234.csv
   - rapport_donnees_clients_2024_20260130_151234.pdf
```

---

## 📦 7. Structure des Fichiers

### Arborescence Projet

```
datatcheck/
├── utils/
│   ├── validators.py           # ← Validation sémantique (NOUVEAU)
│   ├── column_detector.py      # Détection types
│   ├── data_cleaner.py         # ← Nettoyage auto (NOUVEAU)
│   ├── file_naming.py          # ← Nommage intelligent (NOUVEAU)
│   ├── pdf_generator.py        # Génération PDF
│   └── visualizations.py       # Graphiques
├── app.py                       # ← Application Streamlit (MISE À JOUR)
├── requirements.txt
└── README.md
```

### Fichiers Principaux Modifiés

1. **`validators.py`** (v2.0)
   - ❌ Supprimé : CIValidators (téléphone, email, IBAN)
   - ✅ Ajouté : Validation sémantique type vs nom
   - ✅ Ajouté : Recommandations priorisées
   - ✅ Ajouté : Métriques qualité détaillées

2. **`file_naming.py`** (NOUVEAU)
   - Classe FileNamingManager
   - Génération noms intelligents
   - Standardisation noms datasets

3. **`data_cleaner.py`** (NOUVEAU)
   - Classe DataCleaner
   - 10+ opérations nettoyage
   - Mode auto vs agressif
   - Rapport détaillé

4. **`app.py`** (v2.0)
   - Interface style Dataiku
   - Workflow complet
   - Nettoyage intégré
   - Téléchargements multiples

---

## 🎯 8. Utilisation

### Installation

```bash
pip install streamlit pandas numpy plotly reportlab
```

### Lancement

```bash
streamlit run app.py
```

### Exemple d'Utilisation

```python
from utils.validators import validate_dataframe
from utils.data_cleaner import DataCleaner
from utils.file_naming import FileNamingManager

# 1. Charger données
df = pd.read_csv("donnees_clients_2024.csv")

# 2. Créer gestionnaire nommage
naming = FileNamingManager("donnees_clients_2024.csv")

# 3. Analyser qualité
results = validate_dataframe(df, filename="donnees_clients_2024.csv")

print(f"Score : {results['quality_score']}/100")
print(f"Doublons : {results['duplicates']['count']}")
print(f"Manquants : {results['missing_values']['percentage']}%")

# 4. Nettoyer (si nécessaire)
if results['quality_score'] < 80:
    cleaner = DataCleaner(df, "donnees_clients_2024.csv")
    cleaner.auto_clean(aggressive=True)
    
    df_cleaned = cleaner.get_cleaned_dataframe()
    report = cleaner.get_cleaning_report()
    
    # 5. Sauvegarder avec nom intelligent
    cleaned_filename = naming.generate_cleaned_filename()
    df_cleaned.to_csv(cleaned_filename, index=False)
    
    print(f"Fichier nettoyé : {cleaned_filename}")
```

---

## ✅ 9. Checklist Changements

### Ce qui FONCTIONNE maintenant

- ✅ Validation sémantique (type vs nom colonne)
- ✅ Nommage intelligent fichiers (basé sur source)
- ✅ Nettoyage automatique (10+ opérations)
- ✅ Recommandations priorisées (HAUTE/MOYENNE/BASSE)
- ✅ Rapport PDF avec nom intelligent
- ✅ Score qualité basé sur sémantique
- ✅ Gestion données style Dataiku DSS

### Ce qui a été RETIRÉ

- ❌ Validation téléphone CI (+225)
- ❌ Validation email spécifique
- ❌ Validation IBAN BCEAO
- ❌ Validation devise FCFA

### Pourquoi ces retraits ?

**Raison 1 : Focus sémantique**
- Plus générique et adaptable
- Fonctionne pour tous pays/contextes
- Basé sur la logique métier (nom → type)

**Raison 2 : Style Dataiku**
- Dataiku ne valide pas des formats spécifiques
- Il analyse la cohérence type vs nom
- Approche plus professionnelle

**Raison 3 : Extensibilité**
- Facile d'ajouter nouveaux types sémantiques
- Pas besoin de coder validateurs pour chaque format
- Règles sémantiques dans fichier config

---

## 🚀 10. Prochaines Étapes

### Pour améliorer encore

1. **Profiling avancé** (comme Dataiku Statistics)
   - Distribution des valeurs
   - Détection outliers
   - Corrélations entre colonnes

2. **Suggestions de transformations**
   - "Colonne X devrait être splittée en 2"
   - "Colonne Y devrait être en majuscules"

3. **Détection de patterns métier**
   - Détection emails automatique (même sans "email" dans nom)
   - Détection téléphones automatique
   - Détection codes postaux

4. **Export vers Dataiku**
   - Export au format Dataiku DSS
   - Génération de recipes

---

## 📞 Support

Pour toute question :
- **Version** : 2.0 - Style Dataiku DSS
- **Date** : 30 Janvier 2026
- **Auteur** : HABIB KOFFI

---

**🎉 DataTchek v2.0 est prêt !**

Focus sur la validation sémantique intelligente, le nommage professionnel et le nettoyage automatique, exactement comme Dataiku DSS.