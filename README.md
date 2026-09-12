# 💳 PhonePe Expense Tracker - Desktop & CLI App

An industry-grade personal finance application and statement analytics engine for PhonePe users. Built with a decoupled desktop architecture powered by **PyWebView (Windows WebView2)** and a **modular Python backend**.

---

## 📸 Key Features & UI/UX Capabilities

- **🚀 Dual Mode Support:**
  - **Desktop Application (`desktop_app.py`):** Sleek, native Windows desktop application with a signature PhonePe violet (`#5F259F`) FinTech dark theme.
  - **CLI Mode (`main.py`):** High-speed terminal-based report generator.
- **📁 Statement Ingestion:**
  - Native Windows Open File Dialog (`Choose Statement (.txt)`).
  - Drag-and-drop file ingestion zone.
  - One-click sample dataset loader.
- **📊 Real-time Visual Analytics:**
  - **Interactive Category Donut Chart:** Shows spend distribution with click-to-filter mechanics.
  - **Daily Spending Trend Area Chart:** Visualizes daily outflows alongside cumulative spend.
  - **Dynamic Budget Gauge:** Live progress bar that turns red and alerts when budget is exceeded.
- **🔍 Data Quality Diagnostics:**
  - Automatically isolates and flags malformed/skipped statement lines (e.g. missing commas) without failing the entire statement.
  - Interactive inspector drawer detailing line numbers, raw contents, and error reasons.
- **📋 Transaction Explorer:**
  - Instant search across merchant name, date, category, and amount.
  - Category filter pills (`Food`, `Travel`, `Shopping`, `Bills`, `Health`, `Other`).
  - Column sorting and pagination.
  - One-click **Export to CSV**.

---

## 🏛️ Project Architecture

```
phonepe_expense_tracker/
│
├── desktop_app.py              # Main Desktop Launcher & Window Manager
├── main.py                     # CLI Entrypoint (Terminal report)
├── pyproject.toml              # Dependencies & project configuration
├── .env                        # Budget limit and file paths
│
├── backend/                    # 100% PYTHON BACKEND
│   ├── api/
│   │   └── desktop_api.py      # PyWebView JS-Python IPC Bridge
│   ├── config/
│   │   └── setting.py          # .env loader & runtime settings
│   ├── models/
│   │   ├── expense.py          # Transaction, ExpenseSummary, SkippedLine
│   │   └── dto.py              # Strongly typed JSON contracts (DTOs)
│   ├── services/
│   │   ├── tracker.py          # Parsing, validation & summary engine
│   │   ├── categorizer.py      # Merchant keyword categorization
│   │   ├── analytics.py        # Trend analysis, daily aggregations & rankings
│   │   └── dialog_service.py   # Windows native file dialog integration
│   └── utils/
│       ├── decorators.py       # Performance timers
│       ├── file_handler.py     # Safe file I/O
│       └── logger.py           # Centralized UTF-8 logging
│
├── frontend/                   # 100% FRONTEND (HTML / CSS / JS)
│   ├── index.html              # Desktop UI shell
│   ├── assets/
│   │   └── vendor/             # Local offline Chart.js bundle
│   ├── css/
│   │   ├── variables.css       # Design tokens (PhonePe brand colors, dark theme)
│   │   ├── base.css            # Scaffolding & typography
│   │   ├── components.css      # Cards, charts container, data tables, modals
│   │   └── animations.css      # Number counters, glowing alerts, transitions
│   └── js/
│       ├── app.js              # Application coordinator
│       ├── bridge.js           # PyWebView IPC client with browser fallback
│       ├── charts.js           # Chart.js Donut & Area visualizer
│       ├── table.js            # Search, filter, sort & pagination
│       ├── state.js            # Frontend local state
│       └── ui.js               # KPI rendering, toasts & modals
│
├── data/
│   ├── transactions.txt        # Default PhonePe statement file
│   └── summary.json            # Generated analysis export
│
└── tests/
    └── test_tracker.py         # Automated unit and integration test suite
```

---

## 🚀 How to Run & Share
 
### 1. Share & Run Single-File Executable (.exe) ⭐
You can share the compiled `.exe` with anyone. They don't need Python, Node.js, or any setup installed:
- **Executable Location:** [`dist/PhonePe_Expense_Tracker.exe`](file:///d:/phonepe_expense_tracker/dist/PhonePe_Expense_Tracker.exe)
- **Size:** ~12.8 MB
- Simply double-click `PhonePe_Expense_Tracker.exe` to run on any 64-bit Windows PC!

To rebuild the `.exe` at any time:
```powershell
uv run python build_exe.py
```

### 2. Launch from Source (Desktop App)
```powershell
uv run python desktop_app.py
```

### 3. Run the CLI Report
```powershell
uv run python main.py
```

### 4. Run Unit Test Suite
```powershell
uv run python -m unittest discover tests
```

---

## 📝 Statement Format Specification
The tracker ingests plain text files where each line follows this format:
```text
YYYY-MM-DD, Merchant Name, Amount
```

**Example (`data/transactions.txt`):**
```text
2026-08-01, Swiggy, 350
2026-08-02, Uber Ride, 180
2026-08-03, DMart Supermarket, 1450
2026-08-08, Mobile Recharge Jio, 299
```
Lines missing fields or containing invalid numbers are safely captured and viewable in the **Statement Diagnostics** drawer.
