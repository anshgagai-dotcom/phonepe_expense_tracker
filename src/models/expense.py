"""
Data models for expense tracking
"""
from dataclasses import dataclass

@dataclass
class Transaction:
    date: str
    merchant: str
    amount: float
    category: str = "Uncategorized"

@dataclass
class ExpenseSummary:
    total_spent: float
    category_totals: dict[str, float]
    is_over_budget: bool

# if __name__ == "__main__":
#     print(Transaction(date="2026-01-01", merchant="Amazon", amount=100.00, category="Shopping"))
#     print(ExpenseSummary(total_spent=100.00, category_totals={"Shopping": 100.00}, is_over_budget=False))


