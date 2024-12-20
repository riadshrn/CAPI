<p align="center">
  <img src="App/static/images/logo.png" alt="Planning Poker">
</p>

# Planning Poker 🎴

Une application web interactive pour estimer collaborativement les tâches dans un environnement de développement Agile, utilisant Flask pour le backend et des technologies modernes pour l'interface utilisateur.

---


## 📁 Structure du Projet
```bash
planning_poker/
├── App/
│   ├── app.py              # Application principale
│   ├── backlog.json        # Backlog d'exemple
│   ├── partie_sauvegardee/ # Sauvegardes automatiques des parties
│   ├── resultats/          # Résultats des parties terminées
│   ├── templates/          # Templates HTML pour les pages
│   ├── static/
│   │   ├── images/         # Images (logo, icônes)
│   │   ├── cards/          # Images des cartes
│   │   └── style.css       # Styles CSS personnalisés
├── tests/                  # Tests unitaires
│   ├── test_basic.py
├── README.md               # Documentation du projet
└── requirements.txt        # Dépendances Python
```

--- 

## 🚀 Technologies Utilisées
#### Frontend
- ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5&logoColor=white) **HTML**
- ![CSS3](https://img.shields.io/badge/-CSS3-1572B6?logo=css3&logoColor=white) **CSS**
- ![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?logo=javascript&logoColor=black) **JavaScript**

#### Backend
- ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) **Python**
- ![Flask](https://img.shields.io/badge/-Flask-009688?logo=Flask&logoColor=white) **Flask**
#### Gestion des données
- ![JSON](https://img.shields.io/badge/-Json-009688?logo=Json&logoColor=white) **JSON**


---

## 📄 Instructions d'Installation

### Prérequis
- Python 3.10
- pip pour la gestion des dépendances

---

### Étapes d'installation

1.  Clonez le dépôt Git :

```bash
git clone https://github.com/riadshrn/CAPI.git
cd CAPI
```


2.  Créez et activez un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate  # Pour Unix
.\.venv\Scripts\activate   # Pour Windows
```


3. Installez les dépendances :

```bash
pip install -r requirements.txt
```


4. Lancez l'application :

```bash
python App/app.py
```
5. Ouvrez votre navigateur et accédez à l'application : 
<p align="center">
  <a href="http://127.0.0.1:5000/" target="_blank">http://127.0.0.1:5000/</a>
</p>

---

## 🔧 Tests Unitaires

### Commande pour exécuter les tests :
```bash
Copier le code
python -m unittest discover tests
```


### Les tests unitaires incluent :

- Envoi d'un message dans le chat
- Création d'une partie
- Vérification de la page d'accueil 
- Rejoindre une partie 
- Chargement d'une partie sauvegardée 
- Fin d'une partie
- Sauvegarde et chargement d'une partie
- Soumission d'un vote 

---

## 🎨 Interface Utilisateur

L'interface utilisateur se base sur des designs modernes :
- Cartes interactives pour le vote.
- Gestion en temps réel des interactions.
- Résultats affichés en direct.

---

## 📊 Améliorations Futures
- **Mode en temps réel** Synchronisation instantanée grâce à WebSockets.

- **Gestion des utilisateurs** Authentification et sauvegarde des profils.

- **Statistiques**  Analyse des performances de l'équipe sur plusieurs parties.

- **Support multilingue** Ajout de plusieurs langues (anglais, arabe, français).
## 👥 Collaborateurs

- [TABET Idir](https://github.com/idirtb1)
- [TABET Nassim ](https://github.com/nassim4881)