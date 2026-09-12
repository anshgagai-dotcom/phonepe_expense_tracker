"""
Service for launching native Windows file picker and save dialogs via PyWebView.
"""
import logging
from typing import Optional, Any

logger = logging.getLogger("PhonePeTracker")

class DialogService:
    def __init__(self, window_getter: Optional[Any] = None):
        self.window_getter = window_getter

    def select_txt_file(self) -> Optional[str]:
        """Launch Windows native Open File dialog filtered to text/statement files"""
        try:
            import webview
            window = self.window_getter() if callable(self.window_getter) else None
            if not window and webview.windows:
                window = webview.windows[0]

            if not window:
                logger.error("No active PyWebView window found to open file dialog")
                return None

            file_types = ('Text Files (*.txt;*.csv)', 'All Files (*.*)')
            result = window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=file_types
            )

            if result and len(result) > 0:
                selected_path = result[0]
                logger.info(f"User selected file via native dialog: {selected_path}")
                return str(selected_path)
            return None
        except Exception as e:
            logger.error(f"Error opening native file dialog: {e}")
            return None
