# Application de Gestion RH

Une application web de gestion des ressources humaines développée avec Django.

## Fonctionnalités

- Gestion des employés (CRUD)
- Suivi des présences
- Gestion des absences
- Interface d'administration
- Interface employé
- Export de données (CSV/PDF)
- Statistiques et graphiques

## Prérequis

- Python 3.8+
- MySQL (pour la production)
- pip (gestionnaire de paquets Python)

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd pfa_web
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
- En développement : SQLite est utilisé par défaut
- En production : Configurer MySQL dans settings.py

5. Appliquer les migrations :
```bash
python manage.py migrate
```

6. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

7. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Structure du Projet

- `rh_app/` : Application principale
  - `models.py` : Modèles de données
  - `views.py` : Vues et logique métier
  - `urls.py` : Routes de l'application
  - `templates/` : Templates HTML
  - `static/` : Fichiers statiques (CSS, JS, images)
  - `forms.py` : Formulaires
  - `admin.py` : Configuration de l'interface admin

## Utilisation

1. Accéder à l'interface d'administration :
   - URL : http://localhost:8000/admin/
   - Utiliser les identifiants du superutilisateur

2. Interface employé :
   - URL : http://localhost:8000/
   - Se connecter avec les identifiants fournis

## Déploiement en Production

1. Configurer les variables d'environnement :
   - `DEBUG=False`
   - `SECRET_KEY`
   - `DATABASE_URL`

2. Configurer le serveur web (Apache/Nginx)

3. Configurer la base de données MySQL

## Sécurité

- Utiliser HTTPS en production
- Mettre à jour régulièrement les dépendances
- Sauvegarder régulièrement la base de données

## Licence

MIT 