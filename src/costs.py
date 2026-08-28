
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"

def calculate_delivery_penalties(schedule_file):
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["due_date"])
    schedule = pd.read_csv(schedule_file, parse_dates=["start", "end"])
    completed = schedule.groupby("order_id")["end"].max().reset_index(name="completion")
    merged = orders.merge(completed, on="order_id", how="left")

    rates = {"Tier 1":25000, "Tier 2":10000, "Tier 3":5000}
    merged["late_days"] = (
        merged["completion"].dt.normalize() - merged["due_date"].dt.normalize()
    ).dt.days.clip(lower=0)
    merged["penalty_inr"] = merged.apply(
        lambda r: r["late_days"] * rates[r["customer_tier"]], axis=1
    )
    return merged[["order_id","customer_tier","due_date","completion",
                   "late_days","penalty_inr"]]

if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "output" / "base_schedule.csv"
    if path.exists():
        result = calculate_delivery_penalties(path)
        print(result.to_string(index=False))
