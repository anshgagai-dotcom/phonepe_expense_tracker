/**
 * Interactive Visualizations using Chart.js
 */

export const Charts = {
    donutChart: null,
    trendChart: null,

    init(onCategorySelect) {
        this.onCategorySelect = onCategorySelect;
    },

    renderDonutChart(categoryBreakdown) {
        const canvas = document.getElementById("donutChart");
        if (!canvas || !window.Chart) return;

        if (this.donutChart) {
            this.donutChart.destroy();
        }

        const labels = categoryBreakdown.map(c => c.category);
        const data = categoryBreakdown.map(c => c.amount);
        const colors = categoryBreakdown.map(c => c.color);

        const ctx = canvas.getContext("2d");
        this.donutChart = new window.Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: "#111827",
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#94A3B8",
                            boxWidth: 12,
                            padding: 16,
                            font: { size: 12, family: "'Plus Jakarta Sans', sans-serif" }
                        }
                    },
                    tooltip: {
                        backgroundColor: "#1F2937",
                        titleColor: "#F8FAFC",
                        bodyColor: "#CBD5E1",
                        borderColor: "rgba(255, 255, 255, 0.1)",
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6,
                        callbacks: {
                            label: function(context) {
                                const val = context.raw || 0;
                                const item = categoryBreakdown[context.dataIndex];
                                return ` ₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })} (${item.percentage}%)`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements && elements.length > 0) {
                        const index = elements[0].index;
                        const selectedCategory = labels[index];
                        if (this.onCategorySelect) {
                            this.onCategorySelect(selectedCategory);
                        }
                    }
                }
            }
        });
    },

    renderTrendChart(dailyTrend) {
        const canvas = document.getElementById("trendChart");
        if (!canvas || !window.Chart) return;

        if (this.trendChart) {
            this.trendChart.destroy();
        }

        const labels = dailyTrend.map(d => d.date);
        const dailyAmounts = dailyTrend.map(d => d.daily_total);
        const cumulativeAmounts = dailyTrend.map(d => d.cumulative);

        const ctx = canvas.getContext("2d");
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, "rgba(95, 37, 159, 0.45)");
        gradient.addColorStop(1, "rgba(95, 37, 159, 0.0)");

        this.trendChart = new window.Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Daily Spend (₹)",
                        data: dailyAmounts,
                        borderColor: "#9D4EDD",
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        pointBackgroundColor: "#9D4EDD"
                    },
                    {
                        label: "Cumulative Total (₹)",
                        data: cumulativeAmounts,
                        borderColor: "#38BDF8",
                        borderDash: [5, 5],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.2,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748B", maxTicksLimit: 8 }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: {
                            color: "#64748B",
                            callback: function(value) {
                                return "₹" + value.toLocaleString("en-IN");
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        align: "end",
                        labels: {
                            color: "#94A3B8",
                            boxWidth: 10,
                            padding: 12,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: "#1F2937",
                        titleColor: "#F8FAFC",
                        bodyColor: "#CBD5E1",
                        borderColor: "rgba(255, 255, 255, 0.1)",
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return ` ${context.dataset.label}: ₹${context.raw.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                            }
                        }
                    }
                }
            }
        });
    }
};
