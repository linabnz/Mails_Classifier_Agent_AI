#  Agent de Classification de Tickets Email

Un agent automatisé qui lit des emails Gmail, les classifie par catégorie et niveau d'urgence grâce à un LLM (Groq), et exporte les résultats directement dans un **Google Sheet**.

---

## Structure du projet

```
Classification_mails_agents_IA/
├── app/
│   ├── __init__.py
│   ├── config.py              # Chargement des variables d'environnement
│   ├── gmail_client.py        # Connexion et lecture des emails Gmail
│   ├── groq_client.py         # Classification via Groq LLM
│   ├── sheets_client.py       # Écriture des résultats dans Google Sheets
│   ├── csv_writer.py          # Écriture des résultats en CSV (mode alternatif)
│   ├── models.py              # Modèles Pydantic
│   └── main.py                # API FastAPI (point d'entrée)
├── credentials/               # ⚠️ Ne pas push (dans .gitignore)
│   ├── credentials.json       # Credentials OAuth2 Gmail
│   └── service_account.json   # Compte de service Google Sheets
├── comparaison.py             # Script d'évaluation vs vérité terrain
├── ground_truth.csv           # Vérité terrain pour évaluation
├── token.pickle               # Token Gmail (généré automatiquement)
├── .env                       # Variables d'environnement (à créer)
├── .gitignore
├── requirements.txt
└── README.md
```

---

##  Architecture

```
Gmail API → gmail_client.py → groq_client.py (LLM) → sheets_client.py → Google Sheets
```

Le projet est exposé via une **API FastAPI** avec deux endpoints :
- `GET /health` — vérifie que le serveur tourne
- `POST /process_all_emails` — lance le traitement complet des 549 emails

---

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer le fichier `.env`

Crée un fichier `.env` à la racine du projet :

```
GROQ_API_KEY=ta_clé_groq_ici
GMAIL_USER=ticketsdata5@gmail.com
GOOGLE_SHEET_ID=l_id_de_ton_google_sheet
```


---

##  Configuration Google Cloud

### Gmail API (lecture des emails)
1. Va sur [console.cloud.google.com](https://console.cloud.google.com)
2. Crée un projet
3. Active **Gmail API**
4. Crée des credentials **OAuth 2.0** (type : Application de bureau)
5. Télécharge le JSON → place-le dans `credentials/credentials.json`
6. Dans **Écran de consentement OAuth** → ajoute ton email comme utilisateur test

### Google Sheets API (écriture des résultats)
1. Active **Google Sheets API** et **Google Drive API**
2. Crée un **Compte de service** → télécharge le JSON → place-le dans `credentials/service_account.json`
3. Partage ton Google Sheet avec l'email du compte de service (rôle : **Éditeur**)

---

##  Structure du Google Sheet

Le Google Sheet contient **5 onglets**, un par catégorie :

| Onglet | Catégorie |
|--------|-----------|
| Problème technique informatique | Pannes, bugs matériels |
| Demande administrative | Congés, mises à jour RH |
| Problème d'accès / authentification | VPN, mots de passe, accès refusé |
| Demande de support utilisateur | Aide logiciel, configuration |
| Bug ou dysfonctionnement d'un service | Erreurs applicatives |

Chaque onglet contient 3 colonnes :

| Sujet | Urgence | Synthèse |
|-------|---------|----------|
| Objet de l'email | Anodine → Critique | Résumé en 1-3 phrases |

---

##  Niveaux d'urgence

| Niveau | Description |
|--------|-------------|
| 🔴 Critique | Impact majeur, intervention immédiate requise |
| 🟠 Élevée | Impact important, traitement prioritaire |
| 🟡 Modérée | Gêne notable mais non bloquante |
| 🟢 Faible | Problème mineur |
| ⚪ Anodine | Demande simple, aucun enjeu d'urgence |

---

##  Lancement

### Terminal 1 — Démarrer le serveur

```bash
uvicorn app.main:app --reload
```

### Terminal 2 — Lancer le traitement

via l'interface Swagger :
```
http://localhost:8000/docs
```
Clique sur **POST /process_all_emails** → **Try it out** → **Execute**



---

##  Évaluation des résultats

Une fois le traitement terminé, compare avec la vérité terrain :

```bash
python comparaison.py
```

Ce script génère :
- La **précision de classification** par catégorie
- La **précision des niveaux d'urgence**
- `erreurs_categories.csv` — détail des erreurs de catégories
- `erreurs_urgences.csv` — détail des erreurs d'urgences

### Résultats obtenus

| Métrique | Score |
|----------|-------|
| ✅ Précision catégories | **76%** |
| ✅ Précision urgences | **85.6%** |

---

##  Technologies utilisées h

| Technologie | Usage |
|-------------|-------|
| Python 3.11 | Langage principal |
| FastAPI | API REST |
| Groq — llama-3.3-70b-versatile | Classification LLM |
| Gmail API | Lecture des 549 emails |
| Google Sheets API | Écriture des résultats |
| google-auth-oauthlib | Authentification OAuth2 |
| pandas + scikit-learn | Évaluation des résultats |

---
