# 🚀 Quick Start - BTP-Engineering Dashboard

## Installation (5 min)

### Étape 1 : Télécharger les fichiers
Télécharge tous les fichiers `.py`, `requirements.txt` et `README.md`

### Étape 2 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 3 : Lancer l'app
**Windows :**
```bash
run_app.bat
```

**Mac/Linux :**
```bash
bash run_app.sh
```

Ou directement :
```bash
streamlit run app.py
```

L'app ouvrira automatiquement sur : **http://localhost:8501**

---

## Utilisation (quick tour)

### 1️⃣ Créer un chantier
- Clic sur **➕ Nouveau Chantier**
- Remplis : Nom, Lieu, Chef de chantier, Dates
- Clique **Créer le chantier**

### 2️⃣ Ajouter une Unité d'Œuvre (UO)
- Va dans **🏢 Chantiers**
- Clique sur le chantier (expander)
- Tab "Unités d'Œuvre" → forme **➕ Ajouter UO**
- Remplis : Nom, Dates, Budget
- Valide

### 3️⃣ Ajouter des Tâches
- Dans l'UO, clique sur **🔧** pour développer
- Ajoute des tâches avec :
  - Nom (ex: "Reconnaissance du site")
  - Unité (ex: "m²", "ml", "jour")
  - Qté prévue (ex: 100)
  - Qté réalisée (ex: 85)

### 4️⃣ Voir le suivi
- Retour **📊 Tableau de Bord**
- L'avancement se calcule auto !
- Graphiques en temps réel

---

## 📊 Comment ça marche ?

```
Avancement TÂCHE = Qté réalisée ÷ Qté prévue
   ↓
Avancement UO = Moyenne des tâches
   ↓
Avancement CHANTIER = Moyenne des UO
```

**Statut UO :**
- 🟠 **Planifiée** : 0%
- 🟡 **En cours** : 1-99%
- 🟢 **Terminée** : 100%

---

## 🎯 Cas d'usage

### Exemple : Installation de chantier
```
Chantier : Résidence Prestige Cocody
└─ UO : Installation de chantier (Budget: 500k FCFA)
   ├─ Tâche 1 : Reconnaissance site (Qté prévue: 1, Réalisée: 1) ✅ 100%
   ├─ Tâche 2 : Base-vie (Qté prévue: 1, Réalisée: 0.8) 80%
   └─ Tâche 3 : Clôtures (Qté prévue: 200ml, Réalisée: 150ml) 75%
   
   → Avancement UO = (100 + 80 + 75) / 3 = 85%
```

---

## 💾 Où sont les données ?

La base de données `chantiers.db` se crée auto et stocke :
- ✅ Tous les chantiers
- ✅ Toutes les UO
- ✅ Toutes les tâches
- ✅ Tous les budgets

**Important** : La DB persiste entre les sessions. Pas besoin de tout refaire !

---

## ⚙️ Configuration avancée

### Changer le port
```bash
streamlit run app.py --server.port 8502
```

### Mode sombre
Settings → Paramètres des couleurs

### Reset complet
```bash
rm chantiers.db
streamlit run app.py
```

---

## 🐛 Problèmes courants

| Problème | Solution |
|----------|----------|
| **"Port 8501 déjà utilisé"** | Change le port : `--server.port 8502` |
| **"Module not found"** | Refais : `pip install -r requirements.txt` |
| **Pas d'update après modif** | Actualise : F5 ou bouton **Rerun** |
| **"chantiers.db" manquante** | L'app la crée auto au premier lancement |

---

## 📈 Prochaines étapes

- [ ] Ajouter plus de chantiers
- [ ] Remplir les quantités réalisées
- [ ] Mettre à jour les dépenses
- [ ] Regarder les graphiques se mettre à jour ! 📊

---

## 💬 Questions ?

Consulte le **README.md** pour plus de détails sur l'architecture et les calculs.

**Bon suivi de chantier ! 🏗️**
