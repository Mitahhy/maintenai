"""Load demo data into the MaintenAI API (the API must be running on localhost:8000).

Usage:  python scripts/seed.py
Uses only the Python standard library.
"""
import json
import urllib.error
import urllib.request

API = "http://localhost:8000"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as err:
        if err.code == 409:
            return None  # already exists
        raise SystemExit(f"Error {err.code} on {method} {path}: {err.read().decode()}")
    except urllib.error.URLError:
        raise SystemExit("API unreachable: start it first with 'docker compose up'.")


def main():
    if call("GET", "/equipment"):
        raise SystemExit("The database already contains data: nothing was added.")

    site = call("POST", "/sites", {"name": "Demo site"})
    site_id = site["id"] if site else None

    equipment = {}
    for code, name, criticality in [
        ("P-101", "Centrifugal pump", "critique"),
        ("T-02", "Transformer", "importante"),
        ("C-07", "Compressor", "standard"),
        ("V-12", "Isolation valve", "standard"),
    ]:
        created = call(
            "POST",
            "/equipment",
            {"code": code, "designation": name, "criticality": criticality, "site_id": site_id},
        )
        equipment[code] = created["id"]

    orders = [
        ("Gasket replacement", "corrective", "P-101", "high", "done"),
        ("Quarterly lubrication", "preventive", "P-101", "normal", "planned"),
        ("Compressor inspection", "preventive", "C-07", "normal", "in_progress"),
        ("Valve leak", "corrective", "V-12", "high", "to_plan"),
    ]
    for title, wo_type, code, priority, status in orders:
        wo = call(
            "POST",
            "/work-orders",
            {"title": title, "wo_type": wo_type, "equipment_id": equipment[code], "priority": priority},
        )
        if status != "to_plan":
            call("PATCH", f"/work-orders/{wo['id']}/status?status={status}")

    # Simulated predictive alerts: one is validated by a planner (creates a work order),
    # the other stays pending.
    alert = call(
        "POST", "/alerts",
        {"equipment_id": equipment["T-02"], "signal": "Abnormal temperature", "confidence": 0.87},
    )
    call("POST", f"/alerts/{alert['id']}/work-order")
    call(
        "POST", "/alerts",
        {"equipment_id": equipment["P-101"], "signal": "Rising vibration", "confidence": 0.74},
    )

    print("Demo data loaded: 1 site, 4 equipment, 5 work orders, 2 predictive alerts.")


if __name__ == "__main__":
    main()
