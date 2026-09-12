/**
 * Application Main Controller
 */
import { Bridge } from "./bridge.js";
import { State } from "./state.js";
import { UI } from "./ui.js";
import { Charts } from "./charts.js";
import { Table } from "./table.js";

// Sample Data Fallback (in case user opens frontend in standalone browser directly)
const FALLBACK_RAW_DATA = `2026-08-01, Swiggy, 350
2026-08-02, Uber Ride, 180
2026-08-03, DMart Supermarket, 1450
2026-08-04, Zomato Food, 220
2026-08-05, Petrol Pump HPCL, 600
2026-08-06, Amazon Purchase, 999
2026-08-07, Canteen Snacks, 60
2026-08-08, Mobile Recharge Jio, 299
2026-08-09, Invalid Line Without Comma
2026-08-10, Tea Stall, 40
2026-08-11, Flipkart Order, 1299
2026-08-12, Ola Mini Ride, 215
2026-08-13, Electricity Bill Bescom, 1850
2026-08-14, Restaurant Dinner, 850
2026-08-15, Broadband Wifi Bill Airtel, 799
2026-08-16, Metro Card Recharge, 500
2026-08-17, Myntra Fashion Shopping, 1750
2026-08-18, Rapido Bike Taxi, 75
2026-08-19, Swiggy Instamart, 420
2026-08-20, Cinema Movie Ticket, 350
2026-08-21, Petrol Pump BPCL, 750
2026-08-22, Pharmacy Medical Store, 240
2026-08-23, Zomato Delivery, 540
2026-08-24, Water Bill Payment, 310
2026-08-25, Gym Membership, 1200`;

document.addEventListener("DOMContentLoaded", async () => {
    Table.init();
    Charts.init((category) => {
        State.setCategory(category);
        const tableCard = document.querySelector(".table-card");
        if (tableCard) tableCard.scrollIntoView({ behavior: "smooth" });
    });

    // Subscribe table and charts to state updates
    State.subscribe(() => {
        Table.render();
    });

    bindUIActions();

    // Initialize Bridge
    const pywebviewReady = await Bridge.waitForPyWebView(1500);

    if (pywebviewReady) {
        try {
            const initialPayload = await Bridge.getInitialData();
            if (initialPayload && initialPayload.success) {
                applyDataPayload(initialPayload);
            }
        } catch (err) {
            console.error("Failed to load initial data via PyWebView:", err);
            UI.showToast("Failed to load initial data: " + err.message, "error");
        }
    } else {
        // Fallback for standalone browser testing: load sample data via direct parse
        console.log("Using browser fallback parsing.");
        parseAndApplyInBrowser(FALLBACK_RAW_DATA, "Sample_transactions.txt");
    }
});

function applyDataPayload(payload) {
    if (!payload || !payload.success) {
        UI.showToast(payload?.error || "Error parsing transaction statement", "error");
        return;
    }

    State.setData(payload);
    UI.renderKPIs(payload.summary);
    UI.renderBudgetBanner(payload.summary);
    UI.renderQualityStrip(payload.file_info, payload.skipped_lines);
    Charts.renderDonutChart(payload.category_breakdown);
    Charts.renderTrendChart(payload.daily_trend);
    Table.renderCategoryPills(payload.category_breakdown);
    Table.render();

    // Store skipped lines for modal
    window.__skippedLines = payload.skipped_lines || [];

    const statusMsg = payload.file_info.skipped_count > 0
        ? `Loaded ${payload.file_info.valid_count} transactions (${payload.file_info.skipped_count} skipped)`
        : `Loaded ${payload.file_info.valid_count} transactions`;
    UI.showToast(statusMsg, "success");
}

function bindUIActions() {
    // 1. Choose File Button (triggers Windows native dialog)
    const btnSelectFile = document.getElementById("btn-select-file");
    const dropzone = document.getElementById("upload-dropzone");

    const triggerFilePicker = async () => {
        if (Bridge.isPyWebViewAvailable()) {
            try {
                const res = await Bridge.selectAndParseFile();
                if (res && res.success) {
                    applyDataPayload(res);
                } else if (res && !res.cancelled) {
                    UI.showToast(res.error || "Could not parse file.", "error");
                }
            } catch (err) {
                UI.showToast(err.message, "error");
            }
        } else {
            // Web fallback: standard file input
            const input = document.createElement("input");
            input.type = "file";
            input.accept = ".txt,.csv";
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        parseAndApplyInBrowser(event.target.result, file.name);
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        }
    };

    if (btnSelectFile) btnSelectFile.addEventListener("click", triggerFilePicker);
    if (dropzone) dropzone.addEventListener("click", triggerFilePicker);

    // 2. Drag and Drop Support
    if (dropzone) {
        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("drag-active");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("drag-active");
            });
        });

        dropzone.addEventListener("drop", (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                const reader = new FileReader();
                reader.onload = async (event) => {
                    const content = event.target.result;
                    if (Bridge.isPyWebViewAvailable()) {
                        const res = await Bridge.parseRawText(content, file.name);
                        applyDataPayload(res);
                    } else {
                        parseAndApplyInBrowser(content, file.name);
                    }
                };
                reader.readAsText(file);
            }
        });
    }

    // 3. Reset to Sample Data button
    const btnSample = document.getElementById("btn-load-sample");
    if (btnSample) {
        btnSample.addEventListener("click", async () => {
            if (Bridge.isPyWebViewAvailable()) {
                const res = await Bridge.parseRawText(FALLBACK_RAW_DATA, "transactions.txt");
                applyDataPayload(res);
            } else {
                parseAndApplyInBrowser(FALLBACK_RAW_DATA, "transactions.txt");
            }
        });
    }

    // 4. Budget Modal triggers
    const btnEditBudget = document.getElementById("btn-edit-budget");
    const modalBudget = document.getElementById("budget-modal");
    const btnCloseBudget = document.getElementById("btn-close-budget");
    const btnSaveBudget = document.getElementById("btn-save-budget");
    const inputBudget = document.getElementById("input-budget-limit");

    if (btnEditBudget) {
        btnEditBudget.addEventListener("click", () => {
            const currentLimit = State.data?.summary?.budget_limit || 10000;
            if (inputBudget) inputBudget.value = currentLimit;
            UI.openModal("budget-modal");
        });
    }

    if (btnCloseBudget) {
        btnCloseBudget.addEventListener("click", () => UI.closeModal("budget-modal"));
    }

    if (btnSaveBudget && inputBudget) {
        btnSaveBudget.addEventListener("click", async () => {
            const newLimit = parseFloat(inputBudget.value);
            if (isNaN(newLimit) || newLimit <= 0) {
                UI.showToast("Please enter a valid positive budget number.", "error");
                return;
            }

            if (Bridge.isPyWebViewAvailable()) {
                const res = await Bridge.updateBudget(newLimit);
                if (res && res.success) {
                    if (State.data && State.data.summary) {
                        State.data.summary.budget_limit = res.budget_limit;
                        State.data.summary.is_over_budget = res.is_over_budget;
                        State.data.summary.over_budget_amount = res.over_budget_amount;
                        State.data.summary.budget_usage_percent = res.budget_usage_percent;
                        UI.renderKPIs(State.data.summary);
                        UI.renderBudgetBanner(State.data.summary);
                    }
                    UI.closeModal("budget-modal");
                    UI.showToast(res.message, "success");
                } else {
                    UI.showToast(res.error || "Failed to update budget.", "error");
                }
            } else {
                // Browser fallback
                if (State.data && State.data.summary) {
                    State.data.summary.budget_limit = newLimit;
                    State.data.summary.is_over_budget = State.data.summary.total_spent > newLimit;
                    State.data.summary.over_budget_amount = Math.max(0, State.data.summary.total_spent - newLimit);
                    State.data.summary.budget_usage_percent = (State.data.summary.total_spent / newLimit) * 100;
                    UI.renderKPIs(State.data.summary);
                    UI.renderBudgetBanner(State.data.summary);
                }
                UI.closeModal("budget-modal");
                UI.showToast(`Budget limit updated to ₹${newLimit}`, "success");
            }
        });
    }

    // 5. Diagnostics Modal trigger
    const skippedBadge = document.getElementById("quality-skipped-badge");
    const modalDiag = document.getElementById("diag-modal");
    const btnCloseDiag = document.getElementById("btn-close-diag");

    if (skippedBadge) {
        skippedBadge.addEventListener("click", () => {
            const listEl = document.getElementById("diag-skipped-list");
            if (listEl && window.__skippedLines) {
                if (window.__skippedLines.length === 0) {
                    listEl.innerHTML = `<p style="color:var(--text-secondary); text-align:center;">No skipped rows found.</p>`;
                } else {
                    listEl.innerHTML = window.__skippedLines.map(item => `
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="font-weight: 700; color: #FCA5A5; font-size: 13px;">Line ${item.line_number}</div>
                            <div class="font-mono" style="background: rgba(0,0,0,0.4); padding: 6px 10px; border-radius: 4px; margin: 6px 0; font-size: 12px; color: #E2E8F0;">
                                ${escapeHtml(item.raw_text)}
                            </div>
                            <div style="color: #CBD5E1; font-size: 12px;">Reason: ${escapeHtml(item.reason)}</div>
                        </div>
                    `).join("");
                }
            }
            UI.openModal("diag-modal");
        });
    }

    if (btnCloseDiag) {
        btnCloseDiag.addEventListener("click", () => UI.closeModal("diag-modal"));
    }

    // 6. About Dr. ARG Company Modal triggers
    const btnAbout = document.getElementById("btn-about");
    const btnFooterAbout = document.getElementById("btn-footer-about");
    const btnCloseAbout = document.getElementById("btn-close-about");

    if (btnAbout) {
        btnAbout.addEventListener("click", () => UI.openModal("about-modal"));
    }
    if (btnFooterAbout) {
        btnFooterAbout.addEventListener("click", () => UI.openModal("about-modal"));
    }
    if (btnCloseAbout) {
        btnCloseAbout.addEventListener("click", () => UI.closeModal("about-modal"));
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Client-side fallback parser for standalone browser preview
function parseAndApplyInBrowser(rawText, filename) {
    const lines = rawText.split(/\r?\n/);
    const transactions = [];
    const skipped = [];
    let id = 1;

    const CATEGORY_MAP = {
        "Food": ["swiggy", "zomato", "canteen", "tea", "restaurant"],
        "Travel": ["ola", "uber", "rapido", "metro", "petrol"],
        "Shopping": ["dmart", "amazon", "flipkart", "myntra"],
        "Bills": ["recharge", "electricity", "wifi", "ticket", "bill"],
        "Health": ["pharmacy", "gym"]
    };
    const COLORS = {
        "Shopping": "#8E44AD",
        "Bills": "#2980B9",
        "Food": "#E67E22",
        "Travel": "#16A085",
        "Health": "#27AE60",
        "Other": "#7F8C8D"
    };

    lines.forEach((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return;
        const parts = trimmed.split(",").map(s => s.trim());
        if (parts.length !== 3) {
            skipped.push({ line_number: idx + 1, raw_text: trimmed, reason: "Expected 3 comma-separated values (Date, Merchant, Amount), found " + parts.length });
            return;
        }
        const [date, merchant, amountStr] = parts;
        const amount = parseFloat(amountStr.replace(/[₹$,]/g, ""));
        if (isNaN(amount)) {
            skipped.push({ line_number: idx + 1, raw_text: trimmed, reason: `Cannot parse '${amountStr}' into a valid number` });
            return;
        }

        let cat = "Other";
        const mLower = merchant.toLowerCase();
        for (const [c, kws] of Object.entries(CATEGORY_MAP)) {
            if (kws.some(k => mLower.includes(k))) {
                cat = c;
                break;
            }
        }
        transactions.push({ id: id++, date, merchant, amount, category: cat });
    });

    const budgetLimit = 10000;
    const catTotals = {};
    const catCounts = {};
    let totalSpent = 0;
    const dailySums = {};

    transactions.forEach(t => {
        totalSpent += t.amount;
        catTotals[t.category] = (catTotals[t.category] || 0) + t.amount;
        catCounts[t.category] = (catCounts[t.category] || 0) + 1;
        dailySums[t.date] = (dailySums[t.date] || 0) + t.amount;
    });

    const categoryBreakdown = Object.entries(catTotals).map(([cat, amt]) => ({
        category: cat,
        amount: amt,
        percentage: Number(((amt / totalSpent) * 100).toFixed(2)),
        color: COLORS[cat] || COLORS["Other"],
        count: catCounts[cat]
    })).sort((a, b) => b.amount - a.amount);

    const sortedDates = Object.keys(dailySums).sort();
    let cumulative = 0;
    const dailyTrend = sortedDates.map(d => {
        cumulative += dailySums[d];
        return { date: d, daily_total: dailySums[d], cumulative: cumulative, count: 1 };
    });

    const topCat = categoryBreakdown.length > 0 ? categoryBreakdown[0].category : "None";
    const topCatAmt = categoryBreakdown.length > 0 ? categoryBreakdown[0].amount : 0;
    const uniqueDates = sortedDates.length || 1;

    const payload = {
        success: true,
        file_info: {
            filename: filename,
            total_lines: lines.length,
            valid_count: transactions.length,
            skipped_count: skipped.length
        },
        summary: {
            total_spent: totalSpent,
            budget_limit: budgetLimit,
            is_over_budget: totalSpent > budgetLimit,
            budget_usage_percent: (totalSpent / budgetLimit) * 100,
            over_budget_amount: Math.max(0, totalSpent - budgetLimit),
            daily_average: Number((totalSpent / uniqueDates).toFixed(2)),
            top_category: topCat,
            top_category_amount: topCatAmt,
            total_transactions: transactions.length
        },
        category_breakdown: categoryBreakdown,
        daily_trend: dailyTrend,
        transactions: transactions,
        skipped_lines: skipped
    };

    applyDataPayload(payload);
}
