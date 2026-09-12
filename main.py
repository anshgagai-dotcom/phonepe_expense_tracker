import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.utils.logger import setup_logger
from backend.services.tracker import ExpenseTrackerService
from backend.config.setting import BUDGET_LIMIT


def main():
    logger = setup_logger()
    logger.info("Initializing PhonePe Expence Tracker....")

    service = ExpenseTrackerService()
    summary = service.generate_summary()
    service.save_summary(summary)

    print("\n" + "="*50)
    print(" PHONEPE EXPENSE ANALYSIS REPORT ")
    print("="*50 + "\n")
    print(f"Total Money Spent: ₹{summary.total_spent:.2f}")
    print(f"\nSpending Breakdown by Category:")

    for category, amount  in summary.category_totals.items():
        print(f"     {category:12s} : ₹{amount:.2f}")

    print("-"*50)

    if summary.is_over_budget:
        print(f"\n WARNING: You have exceeded your monthly budget limit of ₹{BUDGET_LIMIT}")
    else:
        print(f"\n Congratulations! You are within your budget limit of ₹{BUDGET_LIMIT}")

    print("="*50 + "\n")


if __name__=="__main__":
    main()





