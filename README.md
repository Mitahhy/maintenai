# MaintenIA : socle de développement (MVP)

API FastAPI + PostgreSQL, conçue pour tourner sur votre infrastructure (conteneurs).

## Lancer

    docker compose up --build

API : http://localhost:8000 — documentation interactive : http://localhost:8000/docs
Sans `DATABASE_URL`, l'API utilise SQLite (développement local : `pip install -r backend/requirements.txt` puis `uvicorn app.main:app --reload` depuis `backend/`).

## Déjà en place

- Équipements avec arborescence (`parent_id`), criticité, compteur, garantie
- Ordres de travail correctifs, préventifs et prédictifs, numérotation OT, cycle de statuts
- Alertes prédictives (`POST /alerts`) et transformation en OT après validation humaine
- Stock de pièces avec alerte de seuil, KPI de base

## Prochains jalons

1. Authentification SSO (OIDC) et droits par site et par profil
2. Migrations Alembic, jeu de données de test, tests automatisés
3. Frontend web (écrans de la maquette) et application mobile hors ligne (PWA)
4. Plans de maintenance préventive et génération automatique des OT
5. Import Excel, connecteur ERP via le bus d'intégration
6. Ingestion des données capteurs (MQTT, OPC UA) et pipeline ML
