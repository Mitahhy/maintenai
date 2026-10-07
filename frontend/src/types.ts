export type WoStatus = "to_plan" | "planned" | "in_progress" | "done";
export type WoType = "corrective" | "preventive" | "predictive";

export interface WorkOrder {
  id: number;
  number: string | null;
  title: string;
  wo_type: WoType;
  status: WoStatus;
  priority: string;
  equipment_id: number;
  assignee: string | null;
}

export interface Equipment {
  id: number;
  code: string;
  designation: string;
  criticality: string;
}

export interface Kpi {
  open_work_orders: number;
  preventive_share: number | null;
  mean_time_to_close_corrective_h: number | null;
}
