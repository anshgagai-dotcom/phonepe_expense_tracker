"""
Desktop IPC API exposed to Frontend JavaScript via PyWebView's js_api bridge.
"""
import logging
from pathlib import Path
from typing import Any, Optional

from backend.config.setting import get_budget_limit, set_budget_limit, DATA_FILE_PATH
from backend.services.tracker import ExpenseTrackerService
from backend.services.analytics import assemble_analytics_payload
from backend.services.dialog_service import DialogService
from backend.utils.file_handler import read_text_file

logger = logging.getLogger("PhonePeTracker")

class DesktopAPI:
    """
    Exposed API methods callable from frontend via `window.pywebview.api.<method>()`.
    """
    def __init__(self, window_getter: Optional[Any] = None):
        self.dialog_service = DialogService(window_getter)
        self.current_file_path: Path = DATA_FILE_PATH
        self.cached_transactions = []
        self.cached_skipped = []
        self.cached_summary = None

    def get_initial_data(self) -> dict[str, Any]:
        """Load default data upon desktop app initialization"""
        try:
            logger.info(f"Loading initial transaction dataset from: {self.current_file_path}")
            return self.parse_file_path(str(self.current_file_path))
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error loading initial transactions: {str(e)}"
            }

    def select_and_parse_file(self) -> dict[str, Any]:
        """Open native Windows file dialog, then parse selected file"""
        try:
            selected_path = self.dialog_service.select_txt_file()
            if not selected_path:
                return {
                    "success": False,
                    "cancelled": True,
                    "message": "File selection was cancelled."
                }
            return self.parse_file_path(selected_path)
        except Exception as e:
            logger.error(f"Error in select_and_parse_file: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to select/parse file: {str(e)}"
            }

    def parse_file_path(self, file_path_str: str) -> dict[str, Any]:
        """Parse transactions from a given local file path"""
        try:
            target_path = Path(file_path_str)
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path_str}"
                }

            self.current_file_path = target_path
            raw_lines = read_text_file(target_path)

            current_budget = get_budget_limit()
            service = ExpenseTrackerService(data_path=target_path, budget_limit=current_budget)
            transactions, skipped_lines = service.parse_transactions_from_lines(raw_lines)
            summary = service.generate_summary(transactions)

            # Auto-save summary
            service.save_summary(summary)

            self.cached_transactions = transactions
            self.cached_skipped = skipped_lines
            self.cached_summary = summary

            payload = assemble_analytics_payload(
                filename=target_path.name,
                total_raw_lines=len(raw_lines),
                transactions=transactions,
                skipped_lines=skipped_lines,
                summary=summary
            )
            return payload

        except Exception as e:
            logger.error(f"Error parsing file {file_path_str}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to parse file: {str(e)}"
            }

    def parse_raw_text(self, text_content: str, filename: str = "Uploaded_Statement.txt") -> dict[str, Any]:
        """Parse raw transaction string content (from drag-and-drop or clipboard)"""
        try:
            raw_lines = text_content.splitlines()
            current_budget = get_budget_limit()
            service = ExpenseTrackerService(budget_limit=current_budget)
            transactions, skipped_lines = service.parse_transactions_from_lines(raw_lines)
            summary = service.generate_summary(transactions)

            service.save_summary(summary)

            self.cached_transactions = transactions
            self.cached_skipped = skipped_lines
            self.cached_summary = summary

            payload = assemble_analytics_payload(
                filename=filename,
                total_raw_lines=len(raw_lines),
                transactions=transactions,
                skipped_lines=skipped_lines,
                summary=summary
            )
            return payload
        except Exception as e:
            logger.error(f"Error parsing raw text: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to process text content: {str(e)}"
            }

    def update_budget(self, new_limit: float) -> dict[str, Any]:
        """Update budget limit and recalculate analytics immediately"""
        try:
            float_limit = float(new_limit)
            if float_limit <= 0:
                return {"success": False, "error": "Budget limit must be greater than zero."}

            set_budget_limit(float_limit)

            service = ExpenseTrackerService(budget_limit=float_limit)
            summary = service.generate_summary(self.cached_transactions)
            service.save_summary(summary)
            self.cached_summary = summary

            return {
                "success": True,
                "budget_limit": summary.budget_limit,
                "is_over_budget": summary.is_over_budget,
                "total_spent": summary.total_spent,
                "over_budget_amount": summary.over_budget_amount,
                "budget_usage_percent": summary.budget_usage_percent,
                "message": f"Budget limit updated to ₹{float_limit:.2f}"
            }
        except Exception as e:
            logger.error(f"Error updating budget: {e}", exc_info=True)
            return {"success": False, "error": f"Failed to update budget: {str(e)}"}
