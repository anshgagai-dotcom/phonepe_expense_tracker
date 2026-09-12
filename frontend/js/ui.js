/**
 * UI Utilities & DOM Updates for PhonePe Expense Tracker
 */

export const UI = {
    formatCurrency(amount) {
        if (typeof amount !== "number") amount = Number(amount) || 0;
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    showToast(message, type = "success") {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        const icon = type === "success" ? "✓" : "⚠️";
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 250);
        }, 3500);
    },

    openModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add("open");
    },

    closeModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove("open");
    },

    renderKPIs(summary) {
        if (!summary) return;

        // Total Spent
        const elTotalSpent = document.getElementById("kpi-total-spent");
        if (elTotalSpent) elTotalSpent.textContent = this.formatCurrency(summary.total_spent);

        // Budget Status Card
        const elBudgetCard = document.getElementById("kpi-budget-card");
        const elBudgetValue = document.getElementById("kpi-budget-value");
        const elBudgetSub = document.getElementById("kpi-budget-subtext");
        const elBudgetProgress = document.getElementById("kpi-budget-progress");

        if (elBudgetValue) {
            elBudgetValue.textContent = `${summary.budget_usage_percent.toFixed(1)}%`;
        }

        if (elBudgetProgress) {
            const cappedPercent = Math.min(summary.budget_usage_percent, 100);
            elBudgetProgress.style.width = `${cappedPercent}%`;

            if (summary.is_over_budget) {
                elBudgetProgress.className = "progress-bar danger";
                if (elBudgetCard) elBudgetCard.className = "kpi-card danger";
                if (elBudgetSub) elBudgetSub.innerHTML = `<span style="color:var(--status-danger)">⚠️ ${this.formatCurrency(summary.over_budget_amount)} over ₹${summary.budget_limit.toLocaleString('en-IN')} limit</span>`;
            } else {
                elBudgetProgress.className = "progress-bar success";
                if (elBudgetCard) elBudgetCard.className = "kpi-card success";
                const remaining = Math.max(0, summary.budget_limit - summary.total_spent);
                if (elBudgetSub) elBudgetSub.innerHTML = `<span style="color:var(--status-success)">✓ ${this.formatCurrency(remaining)} remaining of ₹${summary.budget_limit.toLocaleString('en-IN')}</span>`;
            }
        }

        // Top Category
        const elTopCatValue = document.getElementById("kpi-top-category");
        const elTopCatSub = document.getElementById("kpi-top-category-sub");
        if (elTopCatValue) elTopCatValue.textContent = summary.top_category;
        if (elTopCatSub) elTopCatSub.textContent = `${this.formatCurrency(summary.top_category_amount)} spent`;

        // Daily Average
        const elDailyAvg = document.getElementById("kpi-daily-avg");
        const elTotalTxns = document.getElementById("kpi-total-txns");
        if (elDailyAvg) elDailyAvg.textContent = this.formatCurrency(summary.daily_average);
        if (elTotalTxns) elTotalTxns.textContent = `${summary.total_transactions} verified transactions`;
    },

    renderBudgetBanner(summary) {
        const banner = document.getElementById("budget-alert-banner");
        if (!banner || !summary) return;

        if (summary.is_over_budget) {
            banner.className = "budget-banner danger";
            banner.style.display = "flex";
            banner.innerHTML = `
                <div class="banner-left">
                    <span class="banner-icon">⚠️</span>
                    <span><strong>WARNING:</strong> You have exceeded your monthly budget limit of <strong>₹${summary.budget_limit.toLocaleString('en-IN')}</strong> by <strong>${this.formatCurrency(summary.over_budget_amount)}</strong></span>
                </div>
                <span class="badge-pill" style="background:rgba(239,68,68,0.3); color:#FCA5A5;">${summary.budget_usage_percent.toFixed(1)}% Used</span>
            `;
        } else {
            banner.className = "budget-banner success";
            banner.style.display = "flex";
            banner.innerHTML = `
                <div class="banner-left">
                    <span class="banner-icon">🎉</span>
                    <span><strong>Congratulations!</strong> You are within your monthly budget limit of <strong>₹${summary.budget_limit.toLocaleString('en-IN')}</strong></span>
                </div>
                <span class="badge-pill" style="background:rgba(16,185,129,0.25); color:#86EFAC;">${summary.budget_usage_percent.toFixed(1)}% Used</span>
            `;
        }
    },

    renderQualityStrip(fileInfo, skippedLines) {
        const strip = document.getElementById("quality-strip");
        const validBadge = document.getElementById("quality-valid-badge");
        const skippedBadge = document.getElementById("quality-skipped-badge");
        const filenameLabel = document.getElementById("quality-filename");

        if (!strip || !fileInfo) return;

        if (filenameLabel) filenameLabel.textContent = `File: ${fileInfo.filename}`;
        if (validBadge) validBadge.textContent = `${fileInfo.valid_count} Valid Transactions`;

        if (skippedBadge) {
            if (fileInfo.skipped_count > 0) {
                skippedBadge.textContent = `⚠️ ${fileInfo.skipped_count} Skipped Row(s) - Click to Inspect`;
                skippedBadge.style.display = "inline-flex";
            } else {
                skippedBadge.style.display = "none";
            }
        }
    }
};
