
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"

def validate():
    files = [
        "machines.csv", "operators.csv", "orders.csv", "operations.csv",
        "changeovers.csv", "shift_roster.csv", "breakdowns.csv",
        "disruption_scenarios.csv", "cost_parameters.csv"
    ]
    for file in files:
        path = DATA / file
        if not path.exists():
            raise FileNotFoundError(path)

    machines = pd.read_csv(DATA / "machines.csv")
    operators = pd.read_csv(DATA / "operators.csv")
    orders = pd.read_csv(DATA / "orders.csv")
    operations = pd.read_csv(DATA / "operations.csv")
    changeovers = pd.read_csv(DATA / "changeovers.csv")

    assert len(machines) == 14, "Expected 14 machines"
    assert len(orders) == 25, "Expected 25 orders"
    assert len(operators) >= 20, "Expected at least 20 operators"
    assert len(changeovers) == 14 * 5 * 5, "Unexpected changeover matrix size"

    counts = operations.groupby("order_id").size()
    assert counts.between(3, 6).all(), "Every order must have 3-6 operations"

    print("DATA VALIDATION PASSED")
    print(f"Machines : {len(machines)}")
    print(f"Operators: {len(operators)}")
    print(f"Orders   : {len(orders)}")
    print(f"Operations: {len(operations)}")

if __name__ == "__main__":
    validate()
