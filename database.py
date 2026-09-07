import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("chantiers.db")

def init_db():
    """Initialiser la base de données"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table Chantiers
    c.execute('''CREATE TABLE IF NOT EXISTS chantiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        lieu TEXT,
        chef_chantier TEXT,
        date_debut TEXT,
        date_fin TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')
    
    # Table Unités d'Œuvre
    c.execute('''CREATE TABLE IF NOT EXISTS unites_oeuvre (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chantier_id INTEGER NOT NULL,
        nom TEXT NOT NULL,
        date_debut TEXT,
        date_fin TEXT,
        budget REAL DEFAULT 0,
        depenses REAL DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (chantier_id) REFERENCES chantiers(id)
    )''')
    
    # Table Tâches
    c.execute('''CREATE TABLE IF NOT EXISTS taches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uo_id INTEGER NOT NULL,
        nom TEXT NOT NULL,
        unite TEXT,
        qte_prevue REAL DEFAULT 0,
        qte_realisee REAL DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (uo_id) REFERENCES unites_oeuvre(id)
    )''')

    # Migrations : colonne duree_jours pour les Unités d'Œuvre
    cols = [r[1] for r in c.execute("PRAGMA table_info(unites_oeuvre)").fetchall()]
    if 'duree_jours' not in cols:
        c.execute("ALTER TABLE unites_oeuvre ADD COLUMN duree_jours INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

def get_connection():
    """Obtenir une connexion à la DB"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== CHANTIERS ====================

def add_chantier(nom, lieu="", chef_chantier="", date_debut="", date_fin="", with_template=True):
    """Ajouter un chantier. Si with_template, crée la structure BTP par défaut."""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute('''INSERT INTO chantiers
                 (nom, lieu, chef_chantier, date_debut, date_fin, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (nom, lieu, chef_chantier, date_debut, date_fin, now, now))
    conn.commit()
    chantier_id = c.lastrowid
    conn.close()

    if with_template:
        seed_chantier_template(chantier_id)

    return chantier_id

def seed_chantier_template(chantier_id):
    """Créer la structure BTP par défaut (Unités d'Œuvre + Tâches) d'un chantier.
    Les quantités prévue/réalisée démarrent à 0."""
    from chantier_template import CHANTIER_TEMPLATE

    chantier = get_chantier(chantier_id)
    date_debut_defaut = (chantier['date_debut'] if chantier else '') or ''

    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()

    for uo_nom, taches in CHANTIER_TEMPLATE:
        c.execute('''INSERT INTO unites_oeuvre
                     (chantier_id, nom, date_debut, date_fin, budget, depenses, duree_jours, created_at)
                     VALUES (?, ?, ?, '', 0, 0, 0, ?)''',
                  (chantier_id, uo_nom, date_debut_defaut, now))
        uo_id = c.lastrowid
        c.executemany('''INSERT INTO taches
                         (uo_id, nom, unite, qte_prevue, qte_realisee, created_at)
                         VALUES (?, ?, ?, 0, 0, ?)''',
                      [(uo_id, nom, unite, now) for nom, unite in taches])

    conn.commit()
    conn.close()

def get_all_chantiers():
    """Récupérer tous les chantiers"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM chantiers ORDER BY created_at DESC')
    chantiers = [dict(row) for row in c.fetchall()]
    conn.close()
    return chantiers

def get_chantier(chantier_id):
    """Récupérer un chantier par ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM chantiers WHERE id = ?', (chantier_id,))
    row = c.fetchone()
    chantier = dict(row) if row else None
    conn.close()
    return chantier

def update_chantier(chantier_id, nom, lieu, chef_chantier, date_debut, date_fin):
    """Mettre à jour un chantier"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    c.execute('''UPDATE chantiers 
                 SET nom=?, lieu=?, chef_chantier=?, date_debut=?, date_fin=?, updated_at=?
                 WHERE id=?''',
              (nom, lieu, chef_chantier, date_debut, date_fin, now, chantier_id))
    conn.commit()
    conn.close()

def delete_chantier(chantier_id):
    """Supprimer un chantier et ses données"""
    conn = get_connection()
    c = conn.cursor()
    
    # Supprimer les tâches
    c.execute('DELETE FROM taches WHERE uo_id IN (SELECT id FROM unites_oeuvre WHERE chantier_id=?)',
              (chantier_id,))
    # Supprimer les UO
    c.execute('DELETE FROM unites_oeuvre WHERE chantier_id=?', (chantier_id,))
    # Supprimer le chantier
    c.execute('DELETE FROM chantiers WHERE id=?', (chantier_id,))
    
    conn.commit()
    conn.close()

# ==================== UNITÉS D'ŒUVRE ====================

def add_uo(chantier_id, nom, date_debut="", date_fin="", budget=0, depenses=0, duree_jours=0):
    """Ajouter une UO"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute('''INSERT INTO unites_oeuvre
                 (chantier_id, nom, date_debut, date_fin, budget, depenses, duree_jours, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (chantier_id, nom, date_debut, date_fin, budget, depenses, duree_jours, now))
    conn.commit()
    uo_id = c.lastrowid
    conn.close()
    return uo_id

def get_uos_by_chantier(chantier_id):
    """Récupérer les UO d'un chantier"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM unites_oeuvre WHERE chantier_id=? ORDER BY id',
              (chantier_id,))
    uos = [dict(row) for row in c.fetchall()]
    conn.close()
    return uos

def update_uo(uo_id, nom, date_debut, date_fin, budget, depenses, duree_jours=0):
    """Mettre à jour une UO"""
    conn = get_connection()
    c = conn.cursor()

    c.execute('''UPDATE unites_oeuvre
                 SET nom=?, date_debut=?, date_fin=?, budget=?, depenses=?, duree_jours=?
                 WHERE id=?''',
              (nom, date_debut, date_fin, budget, depenses, duree_jours, uo_id))
    conn.commit()
    conn.close()

def delete_uo(uo_id):
    """Supprimer une UO et ses tâches"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM taches WHERE uo_id=?', (uo_id,))
    c.execute('DELETE FROM unites_oeuvre WHERE id=?', (uo_id,))
    conn.commit()
    conn.close()

# ==================== TÂCHES ====================

def add_tache(uo_id, nom, unite="", qte_prevue=0, qte_realisee=0):
    """Ajouter une tâche"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    c.execute('''INSERT INTO taches 
                 (uo_id, nom, unite, qte_prevue, qte_realisee, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (uo_id, nom, unite, qte_prevue, qte_realisee, now))
    conn.commit()
    tache_id = c.lastrowid
    conn.close()
    return tache_id

def get_taches_by_uo(uo_id):
    """Récupérer les tâches d'une UO"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM taches WHERE uo_id=? ORDER BY created_at',
              (uo_id,))
    taches = [dict(row) for row in c.fetchall()]
    conn.close()
    return taches

def update_tache(tache_id, nom, unite, qte_prevue, qte_realisee):
    """Mettre à jour une tâche"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''UPDATE taches 
                 SET nom=?, unite=?, qte_prevue=?, qte_realisee=?
                 WHERE id=?''',
              (nom, unite, qte_prevue, qte_realisee, tache_id))
    conn.commit()
    conn.close()

def delete_tache(tache_id):
    """Supprimer une tâche"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM taches WHERE id=?', (tache_id,))
    conn.commit()
    conn.close()

# Initialiser la DB au démarrage
init_db()
