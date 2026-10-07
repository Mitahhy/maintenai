# MaintenAI

**A maintenance management platform (CMMS) for industrial and energy companies, with a built-in entry point for predictive maintenance alerts.**

> 🇫🇷 [Lire en français](README.fr.md) · Status: **work in progress (MVP)**

MaintenAI centralizes equipment, work orders and maintenance indicators, and is designed so that a machine-learning service can send failure alerts that a planner validates and turns into work orders.

## Screenshots

| Work orders board | API documentation |
|---|---|
| ![Work orders board](docs/screenshots/board.png) | ![API documentation](docs/screenshots/api-docs.png) |

## Features

Working today:

- **Equipment registry** with criticality levels and parent/child hierarchy support
- **Work orders** (corrective, preventive, predictive) with automatic numbering (`OT-000001`) and a status workflow: to plan, planned, in progress, done
- **Predictive alerts**: an endpoint receives alerts (for example from an ML service); a planner validates one and it becomes a predictive work order
- **KPIs**: open work orders, preventive share, mean time to close corrective work orders
- **Kanban board** (React) to follow and advance work orders
- **Spare parts**: data model and low-stock query (creation endpoint planned)

Not built yet: authentication, the predictive model itself (only the alert entry point exists), the mobile app. See the [roadmap](#roadmap).

## Tech stack

| Layer | Technology |
|---|---|
| API | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL 16 |
| Web front end | React, TypeScript, Tailwind CSS (Vite) |
| Packaging | Docker Compose |

## Quick start

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Node.js](https://nodejs.org/) (LTS), and Python 3 (optional, only for the demo data script).

```bash
git clone https://github.com/YOUR-USERNAME/maintenai.git
cd maintenai
```

1. **Configure the database credentials.** Copy the example file and choose your own password:

   ```bash
   cp .env.example .env        # Windows: copy .env.example .env
   ```

2. **Start the API and the database:**

   ```bash
   docker compose up --build
   ```

   The interactive API documentation is at <http://localhost:8000/docs>.

3. **Start the web front end** (in a second terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open <http://localhost:5173>.

4. **Load demo data** (optional, in a third terminal):

   ```bash
   python scripts/seed.py
   ```

To stop everything, press `Ctrl + C`. To also delete the database content: `docker compose down -v`.

## API overview

| Method | Path | Purpose |
|---|---|---|
| `POST` / `GET` | `/equipment` | Create and list equipment |
| `POST` | `/sites` | Create a site |
| `POST` / `GET` | `/work-orders` | Create and list work orders |
| `PATCH` | `/work-orders/{id}/status` | Move a work order to another status |
| `POST` | `/alerts` | Receive a predictive alert |
| `POST` | `/alerts/{id}/work-order` | Validate an alert and create the work order |
| `GET` | `/parts/low-stock` | Parts at or below their minimum stock |
| `GET` | `/kpi` | Maintenance indicators |

## Project structure

```
backend/          FastAPI application (models, routes, Dockerfile)
frontend/         React + TypeScript + Tailwind application
scripts/seed.py   Demo data loader
docs/screenshots/ Images used in this README
docker-compose.yml, .env.example
```

## Roadmap

- [x] Equipment, work orders, KPIs, predictive alert entry point
- [x] Kanban board
- [ ] "New work order" form
- [ ] Equipment page and predictive alerts screen
- [ ] Authentication (SSO) and per-site permissions
- [ ] Database migrations (Alembic) and automated tests
- [ ] Technician mobile app (React Native): offline mode, QR code scanning, photos
- [ ] Preventive maintenance plans with automatic work order generation
- [ ] Sensor data ingestion and a first anomaly-detection model
- [ ] Excel import and ERP connector

## About

Built by **MITAHY** as a hands-on project on maintenance software for industry and energy. Feedback is welcome: [LinkedIn](www.linkedin.com/in/mitahy-1a0748224) · [GitHub](https://github.com/Mitahhy).
