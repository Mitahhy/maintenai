import { useCallback, useEffect, useState } from "react";
import { getEquipment, getKpi, getWorkOrders, setStatus } from "./api";
import type { Equipment, Kpi, WoStatus, WoType, WorkOrder } from "./types";

const COLUMNS: { status: WoStatus; label: string }[] = [
  { status: "to_plan", label: "À planifier" },
  { status: "planned", label: "Planifié" },
  { status: "in_progress", label: "En cours" },
  { status: "done", label: "Terminé" },
];

const TYPE_LABEL: Record<WoType, string> = {
  corrective: "Correctif",
  preventive: "Préventif",
  predictive: "Prédictif",
};

const TYPE_STYLE: Record<WoType, string> = {
  corrective: "bg-red-100 text-red-800",
  preventive: "bg-teal-100 text-teal-800",
  predictive: "bg-amber-100 text-amber-800",
};

function nextStatus(status: WoStatus): WoStatus | null {
  const i = COLUMNS.findIndex((c) => c.status === status);
  return COLUMNS[i + 1]?.status ?? null;
}

function labelOf(status: WoStatus): string {
  return COLUMNS.find((c) => c.status === status)?.label ?? status;
}

function KpiCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-300 bg-white p-4">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

export default function App() {
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [kpi, setKpi] = useState<Kpi | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [o, e, k] = await Promise.all([
        getWorkOrders(),
        getEquipment(),
        getKpi(),
      ]);
      setOrders(o);
      setEquipment(e);
      setKpi(k);
      setError(null);
    } catch {
      setError(
        "Impossible de joindre l'API. Vérifiez que « docker compose up » tourne.",
      );
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const codeOf = (id: number) =>
    equipment.find((e) => e.id === id)?.code ?? `#${id}`;

  async function advance(wo: WorkOrder) {
    const next = nextStatus(wo.status);
    if (!next) return;
    try {
      await setStatus(wo.id, next);
      await load();
    } catch {
      setError("Le changement de statut a échoué.");
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="bg-slate-900 px-8 py-4 text-white">
        <h1 className="text-xl font-semibold">MaintenAI · Anticipez la panne avant qu'elle arrive.</h1>
      </header>

      <main className="p-8">
        {error && (
          <p role="alert" className="mb-4 rounded bg-red-100 p-3 text-red-800">
            {error}
          </p>
        )}

        <section className="mb-6 grid gap-4 sm:grid-cols-3">
          <KpiCard
            label="OT ouverts"
            value={kpi ? String(kpi.open_work_orders) : "—"}
          />
          <KpiCard
            label="Part du préventif"
            value={
              kpi?.preventive_share != null
                ? `${Math.round(kpi.preventive_share * 100)} %`
                : "—"
            }
          />
          <KpiCard
            label="Délai moyen de clôture (correctifs)"
            value={
              kpi?.mean_time_to_close_corrective_h != null
                ? `${kpi.mean_time_to_close_corrective_h.toFixed(1)} h`
                : "—"
            }
          />
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {COLUMNS.map((col) => {
            const items = orders.filter((o) => o.status === col.status);
            return (
              <div key={col.status} className="rounded-lg bg-slate-200 p-3">
                <h2 className="mb-3 font-semibold">
                  {col.label}{" "}
                  <span className="text-sm font-normal text-slate-600">
                    ({items.length})
                  </span>
                </h2>
                <div className="space-y-3">
                  {items.map((wo) => {
                    const next = nextStatus(wo.status);
                    return (
                      <article
                        key={wo.id}
                        className="rounded-lg border border-slate-300 bg-white p-3 text-sm"
                      >
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs ${TYPE_STYLE[wo.wo_type]}`}
                        >
                          {TYPE_LABEL[wo.wo_type]}
                        </span>
                        <h3 className="mt-2 font-semibold">
                          {wo.number} · {wo.title}
                        </h3>
                        <p className="text-slate-600">
                          {codeOf(wo.equipment_id)} · priorité {wo.priority}
                        </p>
                        {next && (
                          <button
                            type="button"
                            onClick={() => void advance(wo)}
                            className="mt-3 min-h-11 w-full rounded border border-teal-700 px-3 font-semibold text-teal-800 hover:bg-teal-50"
                          >
                            Passer à « {labelOf(next)} »
                          </button>
                        )}
                      </article>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </section>
      </main>
    </div>
  );
}
