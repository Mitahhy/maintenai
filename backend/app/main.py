from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .db import Base, engine, get_db

STATUSES = ["to_plan", "planned", "in_progress", "done"]
TYPES = ["corrective", "preventive", "predictive"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # remplacé par Alembic dès le premier jalon
    yield


app = FastAPI(title="Maintenance | IA", lifespan=lifespan)

# Autorise le frontend local (Vite) à appeler l'API depuis le navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Autorise l'interface web de développement (React, port 5173) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EquipmentIn(BaseModel):
    code: str
    designation: str
    criticality: str = "standard"
    site_id: int | None = None
    parent_id: int | None = None


class EquipmentOut(EquipmentIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class WorkOrderIn(BaseModel):
    title: str
    wo_type: str
    equipment_id: int
    priority: str = "normal"
    assignee: str | None = None


class WorkOrderOut(WorkOrderIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: str | None
    status: str


class AlertIn(BaseModel):
    equipment_id: int
    signal: str
    confidence: float


class AlertOut(AlertIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    work_order_id: int | None


def new_work_order(db: Session, data: WorkOrderIn) -> m.WorkOrder:
    if data.wo_type not in TYPES:
        raise HTTPException(422, f"wo_type doit être l'un de {TYPES}")
    if not db.get(m.Equipment, data.equipment_id):
        raise HTTPException(404, "Équipement introuvable")
    wo = m.WorkOrder(**data.model_dump())
    db.add(wo)
    db.flush()
    wo.number = f"OT-{wo.id:06d}"
    return wo


@app.get("/health")
def health():
    return {"status": "ok"}


class SiteIn(BaseModel):
    name: str


@app.post("/sites", status_code=201)
def create_site(data: SiteIn, db: Session = Depends(get_db)):
    if db.scalar(select(m.Site).where(m.Site.name == data.name)):
        raise HTTPException(409, f"Le site {data.name} existe déjà")
    site = m.Site(name=data.name)
    db.add(site)
    db.commit()
    return {"id": site.id, "name": site.name}


@app.post("/equipment", response_model=EquipmentOut, status_code=201)
def create_equipment(data: EquipmentIn, db: Session = Depends(get_db)):
    values = data.model_dump()
    # Swagger pré-remplit les nombres avec 0 : on le traite comme « pas de valeur »
    values["site_id"] = values["site_id"] or None
    values["parent_id"] = values["parent_id"] or None
    if values["site_id"] and not db.get(m.Site, values["site_id"]):
        raise HTTPException(404, "Site introuvable : créez-le d'abord avec POST /sites")
    if values["parent_id"] and not db.get(m.Equipment, values["parent_id"]):
        raise HTTPException(404, "Équipement parent introuvable")
    if db.scalar(select(m.Equipment).where(m.Equipment.code == values["code"])):
        raise HTTPException(409, f"Le code {values['code']} existe déjà")
    eq = m.Equipment(**values)
    db.add(eq)
    db.commit()
    return eq


@app.get("/equipment", response_model=list[EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    return db.scalars(select(m.Equipment).order_by(m.Equipment.code)).all()


@app.post("/work-orders", response_model=WorkOrderOut, status_code=201)
def create_work_order(data: WorkOrderIn, db: Session = Depends(get_db)):
    wo = new_work_order(db, data)
    db.commit()
    return wo


@app.get("/work-orders", response_model=list[WorkOrderOut])
def list_work_orders(status: str | None = None, db: Session = Depends(get_db)):
    q = select(m.WorkOrder).order_by(m.WorkOrder.id.desc())
    if status:
        q = q.where(m.WorkOrder.status == status)
    return db.scalars(q).all()


@app.patch("/work-orders/{wo_id}/status", response_model=WorkOrderOut)
def set_status(wo_id: int, status: str, db: Session = Depends(get_db)):
    wo = db.get(m.WorkOrder, wo_id)
    if not wo:
        raise HTTPException(404, "OT introuvable")
    if status not in STATUSES:
        raise HTTPException(422, f"status doit être l'un de {STATUSES}")
    wo.status = status
    wo.closed_at = datetime.now(timezone.utc) if status == "done" else None
    db.commit()
    return wo


@app.post("/alerts", response_model=AlertOut, status_code=201)
def create_alert(data: AlertIn, db: Session = Depends(get_db)):
    """Point d'entrée pour la plateforme ML : une alerte prédictive."""
    if not db.get(m.Equipment, data.equipment_id):
        raise HTTPException(404, "Équipement introuvable")
    alert = m.PredictiveAlert(**data.model_dump())
    db.add(alert)
    db.commit()
    return alert


@app.post("/alerts/{alert_id}/work-order", response_model=WorkOrderOut, status_code=201)
def alert_to_work_order(alert_id: int, db: Session = Depends(get_db)):
    """Validation humaine : le planificateur transforme l'alerte en OT."""
    alert = db.get(m.PredictiveAlert, alert_id)
    if not alert:
        raise HTTPException(404, "Alerte introuvable")
    wo = new_work_order(
        db,
        WorkOrderIn(title=alert.signal, wo_type="predictive", equipment_id=alert.equipment_id),
    )
    alert.status, alert.work_order_id = "accepted", wo.id
    db.commit()
    return wo


@app.get("/parts/low-stock")
def low_stock(db: Session = Depends(get_db)):
    parts = db.scalars(select(m.Part).where(m.Part.stock_qty <= m.Part.min_qty)).all()
    return [{"reference": p.reference, "label": p.label, "stock": p.stock_qty, "min": p.min_qty} for p in parts]


@app.get("/kpi")
def kpi(db: Session = Depends(get_db)):
    wos = db.scalars(select(m.WorkOrder)).all()
    closed = [w for w in wos if w.wo_type == "corrective" and w.closed_at]
    hours = [(w.closed_at - w.created_at).total_seconds() / 3600 for w in closed]
    return {
        "open_work_orders": sum(1 for w in wos if w.status != "done"),
        "preventive_share": (sum(1 for w in wos if w.wo_type == "preventive") / len(wos)) if wos else None,
        # Délai moyen création -> clôture des correctifs ; le MTTR exact exigera les heures d'intervention réelles.
        "mean_time_to_close_corrective_h": (sum(hours) / len(hours)) if hours else None,
    }
