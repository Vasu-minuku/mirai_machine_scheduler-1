# Mirai Labs Machine Shop Scheduler — Dynamic Web Dashboard

A Python-based machine-shop scheduling project with an interactive Streamlit web dashboard.

## 1. Requirements

- Windows 10/11
- Python 3.10+ recommended
- VS Code (optional but recommended)

## 2. Open in VS Code

1. Extract the ZIP file.
2. Open VS Code.
3. Select **File → Open Folder**.
4. Select the `mirai_machine_scheduler` folder.

## 3. Install dependencies

Open **Terminal → New Terminal** and run:

```bash
pip install -r requirements.txt
```

## 4. Start the dynamic website

### Easiest method
Double-click:

`run_dashboard.bat`

### Or from VS Code terminal

```bash
python -m streamlit run dashboard.py
```

A browser window will open with the dashboard.

## 5. Dashboard features

- Live/recalculated production schedule
- KPI cards for orders, machines, operations, late orders and load
- Machine processing-hours chart
- On-time vs late order chart
- Interactive machine timeline
- Machine and customer-tier filters
- Operations, orders and machine data tables
- CSV download buttons
- Run/Recalculate Scheduler button

## 6. Run the scheduler from terminal

```bash
python machine_shop_scheduler.py
```

The generated schedule is saved to:

`output/base_schedule.csv`

## 7. Project structure

```text
mirai_machine_scheduler/
├── dashboard.py
├── machine_shop_scheduler.py
├── run_dashboard.bat
├── run_scheduler.bat
├── requirements.txt
├── README.md
├── src/
│   ├── generate_data.py
│   ├── scheduler.py
│   └── costs.py
├── data/
│   ├── machines.csv
│   ├── orders.csv
│   ├── operations.csv
│   ├── operators.csv
│   ├── shift_roster.csv
│   ├── cost_parameters.csv
│   ├── changeovers.csv
│   ├── disruption_scenarios.csv
│   └── breakdowns.csv
└── output/
    └── base_schedule.csv
```

## 8. Sharing

Share the complete ZIP. The recipient only needs Python installed, then they can extract the ZIP, open the folder in VS Code, run `pip install -r requirements.txt`, and launch `run_dashboard.bat`.
