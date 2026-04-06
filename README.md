# EduShare - Plateforme de Partage de Cours PDF

**Développé par Marino ATOHOUN**

## Description

EduShare est une plateforme web complète de partage de documents PDF éducatifs. Elle permet aux utilisateurs de :

- 📚 Parcourir et télécharger des cours PDF gratuitement
- 📤 Partager leurs propres cours avec la communauté
- 👁️ Prévisualiser les documents avant téléchargement
- 🔍 Rechercher des cours par domaine et mots-clés
- 👤 Gérer leur profil et suivre leurs contributions

## Architecture

### Backend - Django Rest API
- **Framework** : Django 5.2.4 avec Django REST Framework
- **Base de données** : SQLite (peut être changée pour PostgreSQL en production)
- **Authentification** : JWT (JSON Web Tokens)
- **Upload de fichiers** : Support des fichiers PDF jusqu'à 10MB
- **CORS** : Configuré pour permettre les requêtes cross-origin

### Frontend - React
- **Framework** : React 19 avec Vite
- **UI** : Tailwind CSS + shadcn/ui
- **Routage** : React Router
- **État** : Context API pour l'authentification
- **Icônes** : Lucide React

## Fonctionnalités

### 🔐 Authentification
- Inscription et connexion sécurisées
- Gestion des profils utilisateurs
- Tokens JWT avec refresh automatique

### 📁 Gestion des Documents
- Upload de fichiers PDF avec validation
- Catégorisation par domaines de cours
- Métadonnées (titre, description, taille)
- Compteur de téléchargements

### 🔍 Recherche et Navigation
- Recherche par titre et description
- Filtrage par domaine de cours
- Tri par date, popularité, titre
- Interface responsive

### 👁️ Prévisualisation
- Visualisation des PDF dans le navigateur
- Ouverture en plein écran
- Téléchargement direct

## Structure du Projet

```
pdf_sharing_platform/
├── backend/                 # Configuration Django
│   ├── settings.py         # Configuration principale
│   └── urls.py            # URLs principales
├── courses/                # Application Django
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues API
│   ├── serializers.py     # Sérialiseurs
│   ├── urls.py            # URLs de l'API
│   └── admin.py           # Interface d'administration
├── frontend/               # Application React
│   ├── src/
│   │   ├── components/    # Composants React
│   │   ├── hooks/         # Hooks personnalisés
│   │   ├── lib/           # Utilitaires et API
│   │   └── App.jsx        # Composant principal
│   ├── dist/              # Build de production
│   └── package.json       # Dépendances frontend
├── media/                  # Fichiers uploadés
├── manage.py              # Script de gestion Django
├── populate_data.py       # Script de données de test
└── README.md              # Ce fichier
```

## Installation et Démarrage

### Prérequis
- Python 3.11+
- Node.js 20+
- npm ou pnpm

### Backend Django

1. **Installation des dépendances**
```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt pillow
```

2. **Configuration de la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Création d'un superutilisateur**
```bash
python manage.py createsuperuser
```

4. **Données de test (optionnel)**
```bash
python populate_data.py
```

5. **Démarrage du serveur**
```bash
python manage.py runserver 0.0.0.0:8000
```

### Frontend React

1. **Installation des dépendances**
```bash
cd frontend
npm install
```

2. **Configuration de l'API**
Modifier `src/lib/api.js` pour pointer vers votre backend :
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

3. **Démarrage du serveur de développement**
```bash
npm run dev
```

4. **Build de production**
```bash
npm run build
```

## API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/refresh/` - Refresh token

### Profil
- `GET /api/profile/` - Profil utilisateur
- `PATCH /api/profile/` - Mise à jour du profil

### Cours
- `GET /api/courses/` - Liste des domaines de cours
- `POST /api/courses/` - Création d'un domaine

### Documents
- `GET /api/documents/` - Liste des documents
- `POST /api/documents/` - Upload d'un document
- `GET /api/documents/{id}/` - Détails d'un document
- `GET /api/documents/{id}/download/` - Téléchargement
- `GET /api/documents/{id}/preview/` - Prévisualisation

### Statistiques
- `GET /api/stats/` - Statistiques de la plateforme

## API Développeurs (API Key + Abonnements)

EduShare expose une API “Data” pensée pour extraire des cours en volume (constitution d’une base de données éducation).

### Principe
- Les utilisateurs génèrent une **API Key** depuis l’interface “API (Développeurs)” ou via l’endpoint backend.
- Les requêtes “Data API” utilisent la clé via header `X-API-Key`.
- Des **quotas** (requêtes/téléchargements par jour) s’appliquent selon l’offre (Freemium / Starter / Pro).

### Endpoints développeurs (backend)
- `GET /api/developer/plans/` — Liste des offres
- `GET /api/developer/subscription/` — Offre courante (utilisateur connecté)
- `GET /api/developer/api-keys/` — Liste des clés (utilisateur connecté)
- `POST /api/developer/api-keys/` — Créer une clé (retourne la clé une seule fois)
- `POST /api/developer/api-keys/{id}/revoke/` — Révoquer une clé

### Data API (API key requise)
- `GET /api/data/documents/` — Liste paginée des documents (supporte `search`, `domain`, `study_level`, `study_sublevel`, `tag`, `page`, `page_size`)
- `GET /api/data/documents/{encrypted_id}/download/` — Télécharger un PDF (compte dans le quota “downloads/jour”)

### Exemple (curl)
```bash
curl -H "X-API-Key: <ton_api_key>" "http://localhost:8000/api/data/whoami/"
curl -H "X-API-Key: <ton_api_key>" "http://localhost:8000/api/data/documents/?search=python&page_size=100"
curl -L -H "X-API-Key: <ton_api_key>" "http://localhost:8000/api/data/documents/<encrypted_id>/download/" -o cours.pdf
```

Note: la valeur du header doit être la clé brute `edush_xxx.yyy` (ne pas préfixer par `apikey=`).

Documentation complète: `docs/API.md`

## Comptes de Démonstration

### Utilisateurs de test
- **marie_dupont** / password123
- **jean_martin** / password123
- **sophie_bernard** / password123

### Administrateur
- **admin** / admin123

## Déploiement

### Avec Docker (Recommandé)

1. **Cloner le projet et configurer l'environnement**
```bash
cp .env.example .env
# Modifier les variables dans .env si nécessaire
```

2. **Construire et démarrer les conteneurs**
```bash
docker compose up -d --build
```

3. **Accéder à l'application**
- Frontend: http://localhost
- Backend API: http://localhost:8000/api/
- Admin Django: http://localhost:8000/admin/

4. **Créer un superutilisateur (optionnel)**
```bash
docker compose exec backend python manage.py createsuperuser
```

5. **Arrêter les conteneurs**
```bash
docker compose down
```

### Sans Docker

#### Backend
1. Configurer les variables d'environnement
2. Utiliser une base de données PostgreSQL en production
3. Configurer les fichiers statiques avec `collectstatic`
4. Utiliser un serveur WSGI (Gunicorn + Nginx)

#### Frontend
1. Mettre à jour l'URL de l'API dans `src/lib/api.js`
2. Créer le build de production avec `npm run build`
3. Servir les fichiers statiques depuis le dossier `dist/`

## Fonctionnalités Avancées

### Sécurité
- Validation des fichiers PDF
- Limitation de taille (10MB)
- Protection CSRF
- Authentification JWT

### Performance
- Pagination des résultats
- Optimisation des requêtes
- Compression des assets
- Lazy loading des composants

### UX/UI
- Interface responsive
- Mode sombre/clair
- Animations fluides
- Feedback utilisateur

## Technologies Utilisées

### Backend
- Django 5.2.4
- Django REST Framework 3.16.0
- Django CORS Headers 4.7.0
- Django Simple JWT 5.5.1
- Pillow (traitement d'images)

### Frontend
- React 19.1.0
- Vite 6.3.5
- Tailwind CSS
- shadcn/ui
- React Router DOM
- Axios
- Lucide React

## Licence

Ce projet est développé par **Marino ATOHOUN** dans le cadre d'une démonstration de plateforme éducative.

## Support

Pour toute question ou suggestion, contactez le développeur.

---

**© 2025 Marino ATOHOUN - EduShare Platform**

# EduShare
