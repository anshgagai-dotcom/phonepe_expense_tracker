"""
Core expense tracker service responsible for parsing transaction files,
validating lines, and calculating expense totals.
"""
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from backend.models.expense import Transaction, ExpenseSummary, SkippedLine
from backend.services.categorizer import get_category
from backend.utils.file_handler import read_text_file, write_json_file
from backend.utils.decorators import timer
from backend.config.setting import get_budget_limit, DATA_FILE_PATH, OUTPUT_JSON_PATH

logger = logging.getLogger("PhonePeTracker")

class ExpenseTrackerService:
    def __init__(self, data_path: Optional[Path | str] = None, budget_limit: Optional[float] = None):
        self.data_path = Path(data_path) if data_path else DATA_FILE_PATH
        self.budget_limit = budget_limit if budget_limit is not None else get_budget_limit()

    @timer
    def parse_transactions_from_lines(self, lines: list[str]) -> tuple[list[Transaction], list[SkippedLine]]:
        """
        Parse raw transaction lines, isolating valid transactions from skipped/invalid lines.
        Expected format: YYYY-MM-DD, Merchant Name, Amount
        """
        transactions: list[Transaction] = []
        skipped_lines: list[SkippedLine] = []
        txn_id = 1

        for line_idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str:
                continue

            parts = [p.strip() for p in line_str.split(",")]
            if len(parts) != 3:
                reason = f"Expected 3 comma-separated values (Date, Merchant, Amount), found {len(parts)}"
                logger.warning(f"Skipped line {line_idx}: {reason}")
                skipped_lines.append(SkippedLine(line_idx, line_str, reason))
                continue

            date_str, merchant_str, amount_str = parts

            # Validate date string length/presence
            if not date_str:
                reason = "Date field is empty"
                logger.warning(f"Skipped line {line_idx}: {reason}")
                skipped_lines.append(SkippedLine(line_idx, line_str, reason))
                continue

            # Validate merchant
            if not merchant_str:
                reason = "Merchant field is empty"
                logger.warning(f"Skipped line {line_idx}: {reason}")
                skipped_lines.append(SkippedLine(line_idx, line_str, reason))
                continue

            # Validate and parse amount
            try:
                # Strip rupee symbols or spaces if user added them
                clean_amount = amount_str.replace("₹", "").replace("$", "").replace(",", "").strip()
                amount = float(clean_amount)
                if amount < 0:
                    reason = f"Negative amount ({amount}) is not permitted"
                    skipped_lines.append(SkippedLine(line_idx, line_str, reason))
                    continue
            except ValueError:
                reason = f"Cannot parse amount '{amount_str}' into a valid number"
                logger.warning(f"Skipped line {line_idx}: {reason}")
                skipped_lines.append(SkippedLine(line_idx, line_str, reason))
                continue

            category = get_category(merchant_str)
            transactions.append(Transaction(
                id=txn_id,
                date=date_str,
                merchant=merchant_str,
                amount=round(amount, 2),
                category=category
            ))
            txn_id += 1

        return transactions, skipped_lines

    @timer
    def parse_transactions(self, file_path: Optional[Path | str] = None) -> tuple[list[Transaction], list[SkippedLine]]:
        """Parse transactions from file on disk"""
        target_path = Path(file_path) if file_path else self.data_path
        lines = read_text_file(target_path)
        return self.parse_transactions_from_lines(lines)

    @timer
    def generate_summary(self, transactions: Optional[list[Transaction]] = None) -> ExpenseSummary:
        """Calculate aggregate metrics and budget compliance"""
        if transactions is None:
            transactions, _ = self.parse_transactions()

        category_totals: dict[str, float] = {}
        total_spent: float = 0.0

        for txn in transactions:
            category_totals[txn.category] = category_totals.get(txn.category, 0.0) + txn.amount
            total_spent += txn.amount

        total_spent = round(total_spent, 2)
        formatted_totals = {k: round(v, 2) for k, v in category_totals.items()}
        is_over = total_spent > self.budget_limit
        over_budget_amount = round(max(0.0, total_spent - self.budget_limit), 2)
        usage_pct = round((total_spent / self.budget_limit * 100) if self.budget_limit > 0 else 0.0, 2)

        # Determine top category
        top_cat = "None"
        top_cat_amount = 0.0
        if formatted_totals:
            top_cat = max(formatted_totals, key=formatted_totals.get)
            top_cat_amount = formatted_totals[top_cat]

        # Calculate daily average across unique active dates
        unique_dates = len(set(t.date for t in transactions)) if transactions else 1
        daily_avg = round(total_spent / max(1, unique_dates), 2)

        return ExpenseSummary(
            total_spent=total_spent,
            category_totals=formatted_totals,
            is_over_budget=is_over,
            budget_limit=self.budget_limit,
            budget_usage_percent=usage_pct,
            over_budget_amount=over_budget_amount,
            daily_average=daily_avg,
            top_category=top_cat,
            top_category_amount=top_cat_amount,
            total_transactions=len(transactions)
        )

    def save_summary(self, summary: ExpenseSummary, output_path: Optional[Path | str] = None) -> None:
        """Save the summary to JSON output file"""
        target_path = Path(output_path) if output_path else OUTPUT_JSON_PATH
        # Write format compatible with original summary.json
        data_to_write = {
            "total_spent": summary.total_spent,
            "category_totals": summary.category_totals,
            "is_over_budget": summary.is_over_budget,
            "budget_limit": summary.budget_limit,
            "daily_average": summary.daily_average,
            "top_category": summary.top_category,
        }
        write_json_file(data_to_write, target_path)
