# 🏗️ Architecture Technique

## Structure de données

### Hiérarchie
```
CHANTIER
├── Lieu
├── Chef de chantier  
├── Date début / fin
└── UNITÉ D'ŒUVRE (UO)
    ├── Date début / fin
    ├── Budget
    ├── Dépenses
    ├── Avancement (calculé)
    ├── Statut (calculé)
    └── TÂCHE
        ├── Nom
        ├── Unité (m², ml, t, jour, etc.)
        ├── Qté prévue
        ├── Qté réalisée
        └── Avancement (calculé)
```

## Base de données SQLite

### Table: chantiers
```sql
CREATE TABLE chantiers (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    lieu TEXT,
    chef_chantier TEXT,
    date_debut TEXT,
    date_fin TEXT,
    created_at TEXT,
    updated_at TEXT
)
```

### Table: unites_oeuvre
```sql
CREATE TABLE unites_oeuvre (
    id INTEGER PRIMARY KEY,
    chantier_id INTEGER,
    nom TEXT,
    date_debut TEXT,
    date_fin TEXT,
    budget REAL,
    depenses REAL,
    created_at TEXT
)
```

### Table: taches
```sql
CREATE TABLE taches (
    id INTEGER PRIMARY KEY,
    uo_id INTEGER,
    nom TEXT,
    unite TEXT,
    qte_prevue REAL,
    qte_realisee REAL,
    created_at TEXT
)
```

## Formules de calcul

### Avancement d'une tâche
```python
avancement_tache = qte_realisee / qte_prevue  # min 0, max 100%
```

### Avancement d'une UO
```python
# Moyenne des avancements des tâches
avancement_uo = sum(avancement_tache) / nombre_taches
```

### Avancement d'un chantier
```python
# Moyenne des avancements des UO
avancement_chantier = sum(avancement_uo) / nombre_uos
```

### Statut d'une UO
```python
if avancement_uo == 0:
    statut = "Planifiée"
elif avancement_uo >= 1.0:
    statut = "Terminée"
else:
    statut = "En cours"
```

### Écart budgétaire
```python
ecart = budget - depenses
```

### Taux de dépense
```python
taux_depense = (depenses / budget) * 100
```

## Architecture de l'app

### Fichiers
```
app.py           → Interface Streamlit (pages, formulaires, graphiques)
database.py      → Opérations CRUD sur SQLite
utils.py         → Calculs, agrégations, exports
chantiers.db     → Base de données (auto-créée)
```

### Flux de données
```
USER INPUT (formulaires)
    ↓
database.py (INSERT/UPDATE/DELETE)
    ↓
chantiers.db (SQLite)
    ↓
utils.py (SELECT + CALCULS)
    ↓
app.py (AFFICHAGE + GRAPHIQUES)
```

## Modules Python utilisés

| Module | Usage |
|--------|-------|
| **streamlit** | Interface web |
| **sqlite3** | Base de données |
| **pandas** | DataFrames et exports |
| **plotly** | Graphiques interactifs |
| **openpyxl** | Export Excel |
| **datetime** | Gestion des dates |

## Fonctionnalités clés

### Dashboard
- ✅ KPIs globaux (nombre chantiers, budgets, écarts)
- ✅ Pie chart (distribution des statuts UO)
- ✅ Bar chart (budget vs dépenses)
- ✅ Tableau détaillé (UO avec métriques)

### Gestion chantiers
- ✅ CRUD complet (Create, Read, Update, Delete)
- ✅ Vue détaillée par chantier
- ✅ Gestion des UO (CRUD)
- ✅ Gestion des tâches (CRUD)
- ✅ Validation des données

### Calculs en temps réel
- ✅ Avancement auto mis à jour
- ✅ Écarts budgétaires
- ✅ Statuts dynamiques
- ✅ Totaux agrégés

### Futures améliorations
- 📋 Diagramme de Gantt
- 📊 Graphiques de tendance
- 💾 Export Excel détaillé
- 📸 Galerie photos
- 👥 Multi-utilisateurs
- 📧 Notifications/alertes

## Performance

- **DB** : Optimisée pour requêtes simples (indexes sur FK)
- **Calculs** : En mémoire (< 1ms pour 1000 tâches)
- **Affichage** : Streamlit rerend au clic (optimisé avec @st.cache)
- **Stockage** : SQLite suffisant pour 10k+ chantiers

## Sécurité

- ✅ SQL injection prevention (parameterized queries)
- ✅ Données locales (pas de cloud)
- ✅ Validations des entrées
- ⚠️ Pas d'authentification (ajoutable)
- ⚠️ Pas de chiffrement (DB locale)

## Déploiement possible

L'app peut être déployée sur :
- **Local** : `streamlit run app.py`
- **Streamlit Cloud** : Push sur GitHub + deploy
- **Docker** : Containerize + run anywhere
- **Serveur** : Python + Streamlit Server
