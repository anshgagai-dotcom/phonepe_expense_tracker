"""
Comprehensive Unit and Integration Tests for PhonePe Expense Tracker Backend
"""
import unittest
from pathlib import Path
from backend.services.categorizer import get_category, CATEGORY_MAP, CATEGORY_COLORS
from backend.services.tracker import ExpenseTrackerService
from backend.services.analytics import build_category_breakdown, build_daily_trend, assemble_analytics_payload
from backend.api.desktop_api import DesktopAPI

SAMPLE_LINES = [
    "2026-08-01, Swiggy, 350",
    "2026-08-02, Uber Ride, 180",
    "2026-08-03, DMart Supermarket, 1450",
    "2026-08-04, Zomato Food, 220",
    "2026-08-05, Petrol Pump HPCL, 600",
    "2026-08-06, Amazon Purchase, 999",
    "2026-08-07, Canteen Snacks, 60",
    "2026-08-08, Mobile Recharge Jio, 299",
    "2026-08-09, Invalid Line Without Comma",
    "2026-08-10, Tea Stall, 40",
    "2026-08-11, Flipkart Order, 1299",
    "2026-08-12, Ola Mini Ride, 215",
    "2026-08-13, Electricity Bill Bescom, 1850",
    "2026-08-14, Restaurant Dinner, 850",
    "2026-08-15, Broadband Wifi Bill Airtel, 799",
    "2026-08-16, Metro Card Recharge, 500",
    "2026-08-17, Myntra Fashion Shopping, 1750",
    "2026-08-18, Rapido Bike Taxi, 75",
    "2026-08-19, Swiggy Instamart, 420",
    "2026-08-20, Cinema Movie Ticket, 350",
    "2026-08-21, Petrol Pump BPCL, 750",
    "2026-08-22, Pharmacy Medical Store, 240",
    "2026-08-23, Zomato Delivery, 540",
    "2026-08-24, Water Bill Payment, 310",
    "2026-08-25, Gym Membership, 1200",
]

class TestPhonePeTrackerBackend(unittest.TestCase):

    def setUp(self):
        self.service = ExpenseTrackerService(budget_limit=10000.0)

    def test_categorization(self):
        """Test merchant keyword categorization accuracy"""
        self.assertEqual(get_category("Swiggy Delivery"), "Food")
        self.assertEqual(get_category("Zomato"), "Food")
        self.assertEqual(get_category("Uber Ride"), "Travel")
        self.assertEqual(get_category("Ola Mini"), "Travel")
        self.assertEqual(get_category("DMart Supermarket"), "Shopping")
        self.assertEqual(get_category("Amazon Purchase"), "Shopping")
        self.assertEqual(get_category("Electricity Bill Bescom"), "Bills")
        self.assertEqual(get_category("Pharmacy Medical Store"), "Health")
        self.assertEqual(get_category("Gym Membership"), "Health")
        self.assertEqual(get_category("Unknown Vendor 123"), "Other")

    def test_line_parsing_accuracy(self):
        """Verify valid transaction counts and skipped line isolation"""
        txns, skipped = self.service.parse_transactions_from_lines(SAMPLE_LINES)
        self.assertEqual(len(txns), 24)
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0].line_number, 9)
        self.assertIn("Invalid Line Without Comma", skipped[0].raw_text)

    def test_summary_and_totals(self):
        """Verify exact totals matching the user CLI report"""
        txns, _ = self.service.parse_transactions_from_lines(SAMPLE_LINES)
        summary = self.service.generate_summary(txns)

        self.assertEqual(summary.total_spent, 15346.00)
        self.assertTrue(summary.is_over_budget)
        self.assertEqual(summary.over_budget_amount, 5346.00)
        self.assertAlmostEqual(summary.budget_usage_percent, 153.46, places=1)

        expected_cats = {
            "Food": 2480.00,
            "Travel": 2320.00,
            "Shopping": 5498.00,
            "Bills": 3608.00,
            "Health": 1440.00,
        }
        for cat, amt in expected_cats.items():
            self.assertEqual(summary.category_totals.get(cat), amt, f"Category mismatch for {cat}")

    def test_within_budget(self):
        """Verify budget calculations when within limit"""
        service_higher_budget = ExpenseTrackerService(budget_limit=20000.0)
        txns, _ = service_higher_budget.parse_transactions_from_lines(SAMPLE_LINES)
        summary = service_higher_budget.generate_summary(txns)

        self.assertFalse(summary.is_over_budget)
        self.assertEqual(summary.over_budget_amount, 0.0)
        self.assertLess(summary.budget_usage_percent, 100.0)

    def test_desktop_api_flow(self):
        """Verify Desktop API bridge contract and JSON serialization"""
        api = DesktopAPI()
        data = api.parse_raw_text("\n".join(SAMPLE_LINES), "test_statement.txt")

        self.assertTrue(data.get("success"))
        self.assertEqual(data["summary"]["total_spent"], 15346.00)
        self.assertEqual(data["file_info"]["valid_count"], 24)
        self.assertEqual(data["file_info"]["skipped_count"], 1)
        self.assertIsInstance(data["category_breakdown"], list)
        self.assertIsInstance(data["daily_trend"], list)
        self.assertIsInstance(data["transactions"], list)

        # Verify budget update
        budget_res = api.update_budget(25000.0)
        self.assertTrue(budget_res.get("success"))
        self.assertFalse(budget_res.get("is_over_budget"))
        self.assertEqual(budget_res.get("budget_limit"), 25000.0)

        # Restore budget limit back to 10000
        api.update_budget(10000.0)

if __name__ == "__main__":
    unittest.main()
