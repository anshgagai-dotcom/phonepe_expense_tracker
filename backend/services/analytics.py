"""
Analytics service computing chart breakdowns, daily trends, and DTO packages.
"""
from collections import defaultdict
from dataclasses import asdict
from typing import Any

from backend.models.expense import Transaction, ExpenseSummary, SkippedLine
from backend.models.dto import AnalyticsResponseDTO
from backend.services.categorizer import get_category_color

def build_category_breakdown(transactions: list[Transaction], total_spent: float) -> list[dict[str, Any]]:
    """Build sorted breakdown of categories with percentages and color palettes"""
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)

    for txn in transactions:
        totals[txn.category] += txn.amount
        counts[txn.category] += 1

    breakdown: list[dict[str, Any]] = []
    # Sort descending by spend amount
    for cat, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        pct = round((amount / total_spent * 100) if total_spent > 0 else 0.0, 2)
        breakdown.append({
            "category": cat,
            "amount": round(amount, 2),
            "percentage": pct,
            "color": get_category_color(cat),
            "count": counts[cat]
        })

    return breakdown

def build_daily_trend(transactions: list[Transaction]) -> list[dict[str, Any]]:
    """Build chronologically sorted daily and cumulative spend trajectory"""
    daily_sums: dict[str, float] = defaultdict(float)
    daily_counts: dict[str, int] = defaultdict(int)

    for txn in transactions:
        daily_sums[txn.date] += txn.amount
        daily_counts[txn.date] += 1

    sorted_dates = sorted(daily_sums.keys())
    trend: list[dict[str, Any]] = []
    running_total = 0.0

    for d in sorted_dates:
        amount = round(daily_sums[d], 2)
        running_total = round(running_total + amount, 2)
        trend.append({
            "date": d,
            "daily_total": amount,
            "cumulative": running_total,
            "count": daily_counts[d]
        })

    return trend

def assemble_analytics_payload(
    filename: str,
    total_raw_lines: int,
    transactions: list[Transaction],
    skipped_lines: list[SkippedLine],
    summary: ExpenseSummary
) -> dict[str, Any]:
    """Combine all analytics into the complete API contract"""
    category_breakdown = build_category_breakdown(transactions, summary.total_spent)
    daily_trend = build_daily_trend(transactions)

    file_info = {
        "filename": filename,
        "total_lines": total_raw_lines,
        "valid_count": len(transactions),
        "skipped_count": len(skipped_lines)
    }

    summary_dict = {
        "total_spent": summary.total_spent,
        "budget_limit": summary.budget_limit,
        "is_over_budget": summary.is_over_budget,
        "budget_usage_percent": summary.budget_usage_percent,
        "over_budget_amount": summary.over_budget_amount,
        "daily_average": summary.daily_average,
        "top_category": summary.top_category,
        "top_category_amount": summary.top_category_amount,
        "total_transactions": summary.total_transactions,
    }

    txns_list = [asdict(t) for t in transactions]
    skipped_list = [asdict(s) for s in skipped_lines]

    response = AnalyticsResponseDTO(
        success=True,
        message=f"Parsed {len(transactions)} transactions successfully.",
        file_info=file_info,
        summary=summary_dict,
        category_breakdown=category_breakdown,
        daily_trend=daily_trend,
        transactions=txns_list,
        skipped_lines=skipped_list
    )

    return response.to_dict()
