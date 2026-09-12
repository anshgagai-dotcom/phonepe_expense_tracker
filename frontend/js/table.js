/**
 * Transaction Data Table with search, sorting, filtering, and pagination
 */
import { State } from "./state.js";
import { UI } from "./ui.js";

const CATEGORY_COLORS = {
    "Shopping": "#8E44AD",
    "Bills": "#2980B9",
    "Food": "#E67E22",
    "Travel": "#16A085",
    "Health": "#27AE60",
    "Other": "#7F8C8D"
};

export const Table = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        const searchInput = document.getElementById("search-input");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                State.setSearchQuery(e.target.value);
            });
        }

        const sortDate = document.getElementById("sort-date");
        const sortMerchant = document.getElementById("sort-merchant");
        const sortAmount = document.getElementById("sort-amount");

        if (sortDate) sortDate.addEventListener("click", () => State.setSort("date"));
        if (sortMerchant) sortMerchant.addEventListener("click", () => State.setSort("merchant"));
        if (sortAmount) sortAmount.addEventListener("click", () => State.setSort("amount"));

        const prevBtn = document.getElementById("page-prev");
        const nextBtn = document.getElementById("page-next");

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (State.currentPage > 1) State.setPage(State.currentPage - 1);
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                const totalPages = Math.ceil(State.getFilteredTransactions().length / State.pageSize);
                if (State.currentPage < totalPages) State.setPage(State.currentPage + 1);
            });
        }

        const exportBtn = document.getElementById("btn-export-csv");
        if (exportBtn) {
            exportBtn.addEventListener("click", () => this.exportCurrentCSV());
        }
    },

    render() {
        const transactions = State.getFilteredTransactions();
        const tbody = document.getElementById("transactions-tbody");
        if (!tbody) return;

        tbody.innerHTML = "";

        if (transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align:center; padding: 32px; color: var(--text-muted);">
                        No transactions found matching the current search/filter.
                    </td>
                </tr>
            `;
            this.updatePagination(0, 0, 0);
            return;
        }

        const startIndex = (State.currentPage - 1) * State.pageSize;
        const pageItems = transactions.slice(startIndex, startIndex + State.pageSize);

        pageItems.forEach((txn, index) => {
            const tr = document.createElement("tr");
            const color = CATEGORY_COLORS[txn.category] || CATEGORY_COLORS["Other"];

            tr.innerHTML = `
                <td style="color: var(--text-muted); font-size: 13px;">${startIndex + index + 1}</td>
                <td class="font-mono" style="font-size: 13px;">${txn.date}</td>
                <td style="font-weight: 600;">${txn.merchant}</td>
                <td>
                    <span class="category-badge" style="background: ${color}20; color: ${color}; border: 1px solid ${color}40;">
                        <span style="width: 6px; height: 6px; border-radius: 50%; background: ${color};"></span>
                        ${txn.category}
                    </span>
                </td>
                <td class="font-mono" style="font-weight: 700; text-align: right; color: var(--text-primary);">
                    ${UI.formatCurrency(txn.amount)}
                </td>
            `;
            tbody.appendChild(tr);
        });

        this.updatePagination(startIndex + 1, Math.min(startIndex + State.pageSize, transactions.length), transactions.length);
        this.updateSortHeaders();
    },

    renderCategoryPills(categories) {
        const container = document.getElementById("category-pills");
        if (!container) return;

        container.innerHTML = "";

        const allPill = document.createElement("button");
        allPill.className = `cat-pill ${State.selectedCategory === "All" ? "active" : ""}`;
        allPill.textContent = "All Categories";
        allPill.addEventListener("click", () => State.setCategory("All"));
        container.appendChild(allPill);

        categories.forEach(item => {
            const pill = document.createElement("button");
            pill.className = `cat-pill ${State.selectedCategory === item.category ? "active" : ""}`;
            pill.textContent = `${item.category} (${item.count})`;
            pill.addEventListener("click", () => State.setCategory(item.category));
            container.appendChild(pill);
        });
    },

    updatePagination(start, end, total) {
        const info = document.getElementById("page-info");
        const prevBtn = document.getElementById("page-prev");
        const nextBtn = document.getElementById("page-next");

        if (info) {
            info.textContent = total > 0 ? `Showing ${start}-${end} of ${total} entries` : "0 entries";
        }
        if (prevBtn) prevBtn.disabled = State.currentPage <= 1;
        if (nextBtn) {
            const totalPages = Math.ceil(total / State.pageSize);
            nextBtn.disabled = State.currentPage >= totalPages || total === 0;
        }
    },

    updateSortHeaders() {
        const headers = ["date", "merchant", "amount"];
        headers.forEach(h => {
            const el = document.getElementById(`sort-${h}`);
            if (!el) return;
            const arrow = el.querySelector(".sort-arrow");
            if (arrow) {
                if (State.sortKey === h) {
                    arrow.textContent = State.sortDirection === "asc" ? " ↑" : " ↓";
                    arrow.style.color = "var(--brand-accent)";
                } else {
                    arrow.textContent = " ↕";
                    arrow.style.color = "var(--text-muted)";
                }
            }
        });
    },

    exportCurrentCSV() {
        const txns = State.getFilteredTransactions();
        if (txns.length === 0) {
            UI.showToast("No transactions to export.", "error");
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,Date,Merchant,Category,Amount\n";
        txns.forEach(t => {
            csvContent += `"${t.date}","${t.merchant.replace(/"/g, '""')}","${t.category}",${t.amount}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `phonepe_expenses_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        UI.showToast(`Exported ${txns.length} transactions as CSV!`, "success");
    }
};
