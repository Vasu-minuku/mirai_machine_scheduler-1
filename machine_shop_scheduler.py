"""Main entry point for the Mirai Labs Machine Shop Scheduler."""
from src.scheduler import schedule

if __name__ == "__main__":
    result = schedule()
    print("=" * 72)
    print("MIRAI LABS - MACHINE SHOP SCHEDULER")
    print("=" * 72)
    print(f"Scheduled operations : {len(result)}")
    print(f"Orders scheduled     : {result['order_id'].nunique()}")
    print(f"Machines used        : {result['machine_id'].nunique()}")
    print("\nFirst scheduled operations:")
    print(result.head(20).to_string(index=False))
    print("\nSchedule saved to: output/base_schedule.csv")
    print("=" * 72)
