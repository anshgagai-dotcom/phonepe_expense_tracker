/**
 * Bridge module connecting the frontend UI to Python backend via PyWebView IPC
 */

export const Bridge = {
    isPyWebViewAvailable() {
        return Boolean(window.pywebview && window.pywebview.api);
    },

    async waitForPyWebView(timeoutMs = 3000) {
        if (this.isPyWebViewAvailable()) return true;
        return new Promise((resolve) => {
            const timer = setTimeout(() => resolve(false), timeoutMs);
            window.addEventListener('pywebviewready', () => {
                clearTimeout(timer);
                resolve(true);
            }, { once: true });
        });
    },

    async getInitialData() {
        if (this.isPyWebViewAvailable()) {
            return await window.pywebview.api.get_initial_data();
        }
        console.warn("PyWebView API not detected, running in web browser preview mode.");
        return null;
    },

    async selectAndParseFile() {
        if (this.isPyWebViewAvailable()) {
            return await window.pywebview.api.select_and_parse_file();
        }
        throw new Error("Native file dialog is only available inside the Desktop app.");
    },

    async parseRawText(content, filename = "statement.txt") {
        if (this.isPyWebViewAvailable()) {
            return await window.pywebview.api.parse_raw_text(content, filename);
        }
        throw new Error("PyWebView API bridge not available.");
    },

    async updateBudget(newLimit) {
        if (this.isPyWebViewAvailable()) {
            return await window.pywebview.api.update_budget(Number(newLimit));
        }
        throw new Error("PyWebView API bridge not available.");
    }
};
