"""
Domain models for transactions, summaries, and parsing errors.
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Transaction:
    id: int
    date: str
    merchant: str
    amount: float
    category: str = "Uncategorized"

@dataclass
class SkippedLine:
    line_number: int
    raw_text: str
    reason: str

@dataclass
class ExpenseSummary:
    total_spent: float
    category_totals: dict[str, float]
    is_over_budget: bool
    budget_limit: float = 10000.0
    budget_usage_percent: float = 0.0
    over_budget_amount: float = 0.0
    daily_average: float = 0.0
    top_category: str = "None"
    top_category_amount: float = 0.0
    total_transactions: int = 0
