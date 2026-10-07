import type { Equipment, Kpi, WoStatus, WorkOrder } from "./types";

const API = "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, init);
  if (!res.ok) throw new Error(`Erreur ${res.status} sur ${path}`);
  return res.json() as Promise<T>;
}

export const getWorkOrders = () => request<WorkOrder[]>("/work-orders");
export const getEquipment = () => request<Equipment[]>("/equipment");
export const getKpi = () => request<Kpi>("/kpi");
export const setStatus = (id: number, status: WoStatus) =>
  request<WorkOrder>(`/work-orders/${id}/status?status=${status}`, {
    method: "PATCH",
  });
