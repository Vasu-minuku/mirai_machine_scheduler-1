
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(exist_ok=True)

SHIFT_HOURS = 8
SHIFT_STARTS = {1: 6, 2: 14}

def next_shift(dt):
    day = dt.replace(minute=0, second=0, microsecond=0)
    if day.hour <= 6:
        return day.replace(hour=6)
    if day.hour <= 14:
        return day.replace(hour=14)
    if day.hour <= 22:
        return day.replace(hour=22)
    return (day + timedelta(days=1)).replace(hour=6)

def schedule():
    machines = pd.read_csv(DATA / "machines.csv")
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["due_date"])
    ops = pd.read_csv(DATA / "operations.csv")

    machine_available = {m: datetime(2026, 8, 28, 6) for m in machines.machine_id}
    rows = []

    # Simple earliest-due-date heuristic.
    for _, order in orders.sort_values(["due_date", "customer_tier"]).iterrows():
        order_ops = ops[ops.order_id == order.order_id].sort_values("operation_no")
        prev_end = datetime(2026, 8, 28, 6)

        for _, op in order_ops.iterrows():
            candidates = op.eligible_machines.split("|")
            mid = min(candidates, key=lambda x: machine_available[x])
            start = max(prev_end, machine_available[mid])
            start = next_shift(start)

            hours = op.processing_hours_per_piece * op.quantity
            end = start + timedelta(hours=hours)
            rows.append([
                order.order_id, int(op.operation_no), mid, op.operation_type,
                start, end, float(hours)
            ])
            machine_available[mid] = end
            prev_end = end

    result = pd.DataFrame(rows, columns=[
        "order_id","operation_no","machine_id","operation_type",
        "start","end","processing_hours"
    ])
    result.to_csv(OUT / "base_schedule.csv", index=False)
    return result

if __name__ == "__main__":
    result = schedule()
    print(result.head(20).to_string(index=False))
    print(f"\nSaved: {OUT/'base_schedule.csv'}")
