# 🏗️ BTP-Engineering Dashboard

Dashboard Streamlit pour la gestion et le suivi de chantiers de construction.

## 📋 Structure de l'App

### Hiérarchie des données :
```
Chantier (nom, lieu, chef de chantier, dates)
├─ Unité d'Œuvre (budget, dépenses, dates)
│  └─ Tâche (qté prévue, qté réalisée)
```

### Logique de calcul :
- **Avancement tâche** = Qté réalisée / Qté prévue
- **Avancement UO** = Moyenne des avancements des tâches
- **Avancement Chantier** = Moyenne des avancements des UO
- **Statut UO** : Planifiée (0%), En cours (0-100%), Terminée (100%)

## 🚀 Installation & Lancement

### 1. Prérequis
```bash
pip install streamlit pandas plotly openpyxl
```

### 2. Lancer l'app
```bash
streamlit run app.py
```

L'app ouvrira automatiquement sur : `http://localhost:8501`

## 📊 Fonctionnalités

### 📊 Tableau de Bord Global
- KPIs globaux (nombre de chantiers, budgets totaux)
- Sélection d'un chantier
- Graphiques (pie chart statuts, bar chart budget vs dépenses)
- Tableau détaillé des UO

### 🏢 Gestion des Chantiers
- Vue de tous les chantiers
- Expander par chantier avec 4 tabs :
  - **Vue Globale** : KPIs du chantier
  - **Unités d'Œuvre** : Liste des UO avec détails et tâches
  - **Éditer** : Modifier les infos du chantier
  - **Supprimer** : Suppression avec confirmation
  
- Pour chaque UO :
  - Voir avancement, budget, dépenses
  - Voir détail des tâches
  - Ajouter une nouvelle UO (form inline)

### ➕ Créer un Chantier
- Form pour créer un nouveau chantier
- Champs : nom*, lieu, chef, date début/fin

## 📁 Structure des fichiers

```
/home/claude/
├── app.py              # Application principale Streamlit
├── database.py         # Gestion SQLite
├── utils.py           # Utilitaires et calculs
├── chantiers.db       # Base de données (auto-créée)
└── README.md          # Ce fichier
```

## 💾 Base de données

La DB SQLite `chantiers.db` se crée automatiquement et contient :
- **chantiers** : nom, lieu, chef, dates
- **unites_oeuvre** : nom, dates, budget, dépenses
- **taches** : nom, unité, qté prévue, qté réalisée

## 🎨 Interface

- **Couleurs** : 
  - 🔵 Bleu : En-têtes/KPIs
  - 🟠 Orange : Données éditables
  - 🟢 Vert : Statuts positifs
  - 🔴 Rouge : Statuts critiques

- **Navigation** : Sidebar avec 3 pages + radios

## 📈 Prochaines améliorations possibles

- [ ] Diagramme de Gantt par chantier
- [ ] Export Excel détaillé
- [ ] Graphiques de tendance
- [ ] Multi-utilisateurs
- [ ] Historique des modifications
- [ ] Notifications alertes
- [ ] Photos des chantiers

## 🐛 Troubleshooting

### "Port 8501 déjà utilisé"
```bash
streamlit run app.py --server.port 8502
```

### "chantiers.db not found"
La DB se crée automatiquement au premier lancement

### "Pas de chantier après création"
Actualiser la page (F5) ou relancer l'app

## 📞 Support

Pour toute question ou problème, vérifiez que :
1. Toutes les dépendances sont installées
2. Vous êtes dans le bon répertoire
3. Python 3.8+ est utilisé
