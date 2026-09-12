"""
PhonePe Expense Tracker - Desktop Application Launcher
Powered by PyWebView & Windows native WebView2
"""
import sys
import os
import argparse
from pathlib import Path

# Ensure project bundle directory is in sys.path
def get_bundle_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

BASE_DIR = get_bundle_dir()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Windows UTF-8 stdout fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.utils.logger import setup_logger
from backend.api.desktop_api import DesktopAPI

logger = setup_logger()

def run_headless_test() -> bool:
    """Run headless tests to verify backend, parsing, and API contracts"""
    logger.info("Running headless system verification...")
    try:
        api = DesktopAPI()
        data = api.get_initial_data()

        assert data.get("success") is True, f"Failed getting initial data: {data}"
        summary = data.get("summary", {})
        assert summary.get("total_spent") == 15346.0, f"Expected 15346.0, got {summary.get('total_spent')}"
        assert summary.get("is_over_budget") is True, "Expected over budget True"
        assert len(data.get("transactions", [])) == 24, f"Expected 24 valid transactions, got {len(data.get('transactions', []))}"
        assert len(data.get("skipped_lines", [])) == 1, f"Expected 1 skipped line, got {len(data.get('skipped_lines', []))}"

        categories = {c["category"]: c["amount"] for c in data.get("category_breakdown", [])}
        expected_cats = {
            "Shopping": 5498.0,
            "Bills": 3608.0,
            "Food": 2480.0,
            "Travel": 2320.0,
            "Health": 1440.0
        }
        for cat, expected_amt in expected_cats.items():
            assert categories.get(cat) == expected_amt, f"Mismatch in {cat}: expected {expected_amt}, got {categories.get(cat)}"

        logger.info("All headless automated verifications PASSED with 100% accuracy!")
        print("\n" + "="*60)
        print(" [PASSED] PHONEPE DESKTOP BACKEND VERIFICATION ")
        print(f" Total Spent     : ₹{summary.get('total_spent'):.2f}")
        print(f" Valid Txns      : {len(data.get('transactions', []))}")
        print(f" Skipped Lines   : {len(data.get('skipped_lines', []))}")
        print(f" Over Budget     : {summary.get('is_over_budget')}")
        print("="*60 + "\n")
        return True

    except Exception as e:
        logger.error(f"Verification test failed: {e}", exc_info=True)
        print(f"\n[FAILED] Verification error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="PhonePe Expense Tracker Desktop Application")
    parser.add_argument("--test", action="store_true", help="Run automated headless contract test")
    parser.add_argument("--debug", action="store_true", help="Enable developer inspection tools")
    args = parser.parse_args()

    if args.test:
        success = run_headless_test()
        sys.exit(0 if success else 1)

    import webview

    frontend_index = BASE_DIR / "frontend" / "index.html"
    if not frontend_index.exists():
        logger.error(f"Frontend entrypoint not found at: {frontend_index}")
        sys.exit(1)

    api = DesktopAPI()

    logger.info("Initializing PhonePe Desktop window...")
    window = webview.create_window(
        title="PhonePe Expense Tracker - Desktop Analytics",
        url=str(frontend_index),
        js_api=api,
        width=1280,
        height=850,
        min_size=(1000, 680),
        background_color="#0B0F19"
    )

    # Attach window reference to dialog service
    api.dialog_service.window_getter = lambda: window

    webview.start(http_server=True, debug=args.debug)

if __name__ == "__main__":
    main()
