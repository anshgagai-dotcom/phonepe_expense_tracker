"""
Data Transfer Objects (DTOs) defining the contract between Python backend and Frontend UI.
"""
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class FileInfoDTO:
    filename: str
    total_lines: int
    valid_count: int
    skipped_count: int

@dataclass
class SummaryKPIsDTO:
    total_spent: float
    budget_limit: float
    is_over_budget: bool
    budget_usage_percent: float
    over_budget_amount: float
    daily_average: float
    top_category: str
    top_category_amount: float
    total_transactions: int

@dataclass
class CategorySliceDTO:
    category: str
    amount: float
    percentage: float
    color: str
    count: int

@dataclass
class DailyTrendPointDTO:
    date: str
    daily_total: float
    cumulative: float
    count: int

@dataclass
class AnalyticsResponseDTO:
    success: bool
    message: str
    file_info: dict[str, Any]
    summary: dict[str, Any]
    category_breakdown: list[dict[str, Any]]
    daily_trend: list[dict[str, Any]]
    transactions: list[dict[str, Any]]
    skipped_lines: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class BudgetStatusDTO:
    success: bool
    budget_limit: float
    is_over_budget: bool
    total_spent: float
    over_budget_amount: float
    budget_usage_percent: float
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
