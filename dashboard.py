from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
SCHEDULE_FILE = OUTPUT / "base_schedule.csv"

st.set_page_config(page_title="Mirai Machine Shop Scheduler", page_icon="⚙️", layout="wide")

# ---------- Helpers ----------
@st.cache_data(ttl=10)
def load_data():
    machines = pd.read_csv(DATA / "machines.csv")
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["due_date"])
    operations = pd.read_csv(DATA / "operations.csv")
    if SCHEDULE_FILE.exists():
        schedule = pd.read_csv(SCHEDULE_FILE, parse_dates=["start", "end"])
    else:
        schedule = pd.DataFrame(columns=["order_id", "operation_no", "machine_id", "operation_type", "start", "end", "processing_hours"])
    return machines, orders, operations, schedule


def run_scheduler():
    from src.scheduler import schedule
    schedule()
    load_data.clear()


def make_completion(orders, schedule):
    if schedule.empty:
        return pd.DataFrame()
    completion = schedule.groupby("order_id", as_index=False)["end"].max().rename(columns={"end": "completion"})
    result = orders[["order_id", "customer_name", "customer_tier", "due_date"]].merge(completion, on="order_id", how="left")
    result["late_days"] = ((result["completion"].dt.normalize() - result["due_date"].dt.normalize()).dt.days).clip(lower=0).fillna(0).astype(int)
    result["status"] = result.apply(lambda r: "Late" if r["late_days"] > 0 else "On Time", axis=1)
    return result

machines, orders, operations, schedule = load_data()

# ---------- Header ----------
st.title("⚙️ Mirai Labs — Machine Shop Scheduler")
st.caption("Interactive production scheduling dashboard • Sridhar Precision Works")

with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Run / Recalculate Schedule", use_container_width=True):
        with st.spinner("Calculating production schedule..."):
            run_scheduler()
        st.success("Schedule updated")
        st.rerun()

    st.divider()
    st.subheader("Filters")
    machine_options = ["All Machines"] + sorted(schedule["machine_id"].dropna().unique().tolist())
    selected_machine = st.selectbox("Machine", machine_options)
    tier_options = ["All Tiers"] + sorted(orders["customer_tier"].dropna().unique().tolist())
    selected_tier = st.selectbox("Customer Tier", tier_options)

    if st.button("🧹 Clear filters", use_container_width=True):
        st.rerun()

completion = make_completion(orders, schedule)

# Apply filters
filtered_schedule = schedule.copy()
if selected_machine != "All Machines":
    filtered_schedule = filtered_schedule[filtered_schedule["machine_id"] == selected_machine]
filtered_orders = orders.copy()
if selected_tier != "All Tiers":
    filtered_orders = filtered_orders[filtered_orders["customer_tier"] == selected_tier]

# ---------- KPI cards ----------
late_orders = int((completion["late_days"] > 0).sum()) if not completion.empty else 0
util_hours = schedule.groupby("machine_id")["processing_hours"].sum() if not schedule.empty else pd.Series(dtype=float)
avg_util = (util_hours.mean() / 8 * 100) if len(util_hours) else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Open Orders", len(filtered_orders))
c2.metric("Machines", len(machines))
c3.metric("Scheduled Ops", len(filtered_schedule))
c4.metric("Late Orders", late_orders, delta="Needs attention" if late_orders else "On track", delta_color="inverse")
c5.metric("Avg. Load", f"{avg_util:.0f}%")

if schedule.empty:
    st.warning("No schedule found. Click **Run / Recalculate Schedule** in the sidebar.")
    st.stop()

# ---------- Charts ----------
st.subheader("📊 Production Overview")
col1, col2 = st.columns(2)

with col1:
    machine_load = schedule.groupby("machine_id", as_index=False)["processing_hours"].sum().sort_values("processing_hours", ascending=False)
    fig = px.bar(machine_load, x="machine_id", y="processing_hours", title="Processing Hours by Machine", labels={"machine_id": "Machine", "processing_hours": "Hours"})
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if not completion.empty:
        status_counts = completion["status"].value_counts().rename_axis("status").reset_index(name="count")
        fig2 = px.pie(status_counts, names="status", values="count", hole=0.55, title="Order Completion Status")
        fig2.update_layout(height=360, margin=dict(l=20, r=20, t=55, b=20))
        st.plotly_chart(fig2, use_container_width=True)

# ---------- Schedule timeline ----------
st.subheader("🗓️ Interactive Machine Schedule")
timeline = filtered_schedule.copy()
if not timeline.empty:
    timeline["Job"] = timeline["order_id"].astype(str) + " • " + timeline["operation_type"]
    fig3 = px.timeline(
        timeline,
        x_start="start",
        x_end="end",
        y="machine_id",
        color="operation_type",
        hover_data=["order_id", "operation_no", "processing_hours"],
        title="Machine Timeline",
    )
    fig3.update_yaxes(autorange="reversed", title="Machine")
    fig3.update_xaxes(title="Time")
    fig3.update_layout(height=max(450, len(timeline["machine_id"].unique()) * 55), margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No scheduled operations match the selected machine filter.")

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📋 Operations", "📦 Orders", "🖥️ Machines"])

with tab1:
    st.dataframe(filtered_schedule.sort_values(["start", "machine_id"]), use_container_width=True, hide_index=True)
    csv = filtered_schedule.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Schedule CSV", csv, "filtered_schedule.csv", "text/csv")

with tab2:
    order_view = completion[completion["order_id"].isin(filtered_orders["order_id"])] if not completion.empty else completion
    if not order_view.empty:
        st.dataframe(order_view.sort_values("due_date"), use_container_width=True, hide_index=True)
        csv2 = order_view.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Order Status CSV", csv2, "order_status.csv", "text/csv")
    else:
        st.info("No order information available.")

with tab3:
    machine_view = machines.copy()
    if selected_machine != "All Machines":
        machine_view = machine_view[machine_view["machine_id"] == selected_machine]
    load = schedule.groupby("machine_id", as_index=False)["processing_hours"].sum().rename(columns={"processing_hours": "scheduled_hours"})
    machine_view = machine_view.merge(load, on="machine_id", how="left")
    machine_view["scheduled_hours"] = machine_view["scheduled_hours"].fillna(0)
    machine_view["estimated_utilization"] = (machine_view["scheduled_hours"] / 8 * 100).round(1)
    st.dataframe(machine_view, use_container_width=True, hide_index=True)

st.divider()
st.caption(f"Last dashboard load: {datetime.now().strftime('%d %b %Y, %I:%M %p')} • Data source: data/ • Output: output/base_schedule.csv")
