# MaintenAI

**Une plateforme de gestion de maintenance (GMAO) pour l'industrie et l'énergie, avec un point d'entrée intégré pour les alertes de maintenance prédictive.**

> 🇬🇧 [Read in English](README.md) · Statut : **en cours de développement (MVP)**

MaintenAI centralise les équipements, les ordres de travail et les indicateurs de maintenance. Elle est conçue pour qu'un service de machine learning puisse envoyer des alertes de panne, qu'un planificateur valide pour en faire des ordres de travail.

## Captures d'écran

| Tableau des ordres de travail | Documentation de l'API |
|---|---|
| ![Tableau des ordres de travail](docs/screenshots/board.png) | ![Documentation de l'API](docs/screenshots/api-docs.png) |

## Fonctionnalités

Déjà en place :

- **Registre des équipements** avec niveaux de criticité et arborescence (parent/enfant)
- **Ordres de travail** (correctifs, préventifs, prédictifs) avec numérotation automatique (`OT-000001`) et cycle de statuts : à planifier, planifié, en cours, terminé
- **Alertes prédictives** : un point d'entrée reçoit les alertes (par exemple d'un service ML) ; un planificateur en valide une et elle devient un OT prédictif
- **KPI** : OT ouverts, part du préventif, délai moyen de clôture des correctifs
- **Tableau kanban** (React) pour suivre et faire avancer les OT
- **Pièces de rechange** : modèle de données et requête de stock bas (création à venir)

Pas encore développés : l'authentification, le modèle prédictif lui-même (seul le point d'entrée des alertes existe) et l'application mobile. Voir la [feuille de route](#feuille-de-route).

## Technologies

| Couche | Technologie |
|---|---|
| API | Python, FastAPI, SQLAlchemy |
| Base de données | PostgreSQL 16 |
| Interface web | React, TypeScript, Tailwind CSS (Vite) |
| Déploiement | Docker Compose |

## Démarrage rapide

**Prérequis :** [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Node.js](https://nodejs.org/) (LTS) et Python 3 (facultatif, seulement pour le script de données de démonstration).

```bash
git clone https://github.com/VOTRE-NOM/maintenai.git
cd maintenai
```

1. **Configurer les identifiants de la base.** Copiez le fichier d'exemple et choisissez votre mot de passe :

   ```bash
   cp .env.example .env        # Windows : copy .env.example .env
   ```

2. **Démarrer l'API et la base de données :**

   ```bash
   docker compose up --build
   ```

   La documentation interactive de l'API est sur <http://localhost:8000/docs>.

3. **Démarrer l'interface web** (dans un deuxième terminal) :

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Ouvrez <http://localhost:5173>.

4. **Charger des données de démonstration** (facultatif, dans un troisième terminal) :

   ```bash
   python scripts/seed.py
   ```

Pour tout arrêter, tapez `Ctrl + C`. Pour effacer aussi le contenu de la base : `docker compose down -v`.

## Aperçu de l'API

| Méthode | Chemin | Rôle |
|---|---|---|
| `POST` / `GET` | `/equipment` | Créer et lister les équipements |
| `POST` | `/sites` | Créer un site |
| `POST` / `GET` | `/work-orders` | Créer et lister les ordres de travail |
| `PATCH` | `/work-orders/{id}/status` | Changer le statut d'un OT |
| `POST` | `/alerts` | Recevoir une alerte prédictive |
| `POST` | `/alerts/{id}/work-order` | Valider une alerte et créer l'OT |
| `GET` | `/parts/low-stock` | Pièces au niveau ou sous le stock minimum |
| `GET` | `/kpi` | Indicateurs de maintenance |

## Structure du projet

```
backend/          Application FastAPI (modèles, routes, Dockerfile)
frontend/         Application React + TypeScript + Tailwind
scripts/seed.py   Chargement des données de démonstration
docs/screenshots/ Images utilisées dans ce README
docker-compose.yml, .env.example
```

## Feuille de route

- [x] Équipements, ordres de travail, KPI, point d'entrée des alertes prédictives
- [x] Tableau kanban
- [ ] Formulaire « Nouvel OT »
- [ ] Page des équipements et écran des alertes prédictives
- [ ] Authentification (SSO) et droits par site
- [ ] Migrations de base de données (Alembic) et tests automatisés
- [ ] Application mobile du technicien (React Native) : mode hors ligne, scan de QR code, photos
- [ ] Plans de maintenance préventive avec génération automatique des OT
- [ ] Ingestion de données capteurs et premier modèle de détection d'anomalies
- [ ] Import Excel et connecteur ERP

## À propos

Réalisé par **MITAHY** comme projet pratique sur les logiciels de maintenance pour l'industrie et l'énergie. Les retours sont les bienvenus : [LinkedIn](www.linkedin.com/in/mitahy-1a0748224) · [GitHub](https://github.com/Mitahhy).
