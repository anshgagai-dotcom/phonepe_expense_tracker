/**
 * Central State Management for PhonePe Expense Tracker UI
 */

export const State = {
    data: null,
    selectedCategory: "All",
    searchQuery: "",
    sortKey: "date",
    sortDirection: "desc",
    currentPage: 1,
    pageSize: 8,
    listeners: new Set(),

    setData(newData) {
        this.data = newData;
        this.currentPage = 1;
        this.notify();
    },

    setCategory(category) {
        this.selectedCategory = category;
        this.currentPage = 1;
        this.notify();
    },

    setSearchQuery(query) {
        this.searchQuery = query.toLowerCase().trim();
        this.currentPage = 1;
        this.notify();
    },

    setSort(key) {
        if (this.sortKey === key) {
            this.sortDirection = this.sortDirection === "asc" ? "desc" : "asc";
        } else {
            this.sortKey = key;
            this.sortDirection = key === "amount" ? "desc" : "asc";
        }
        this.notify();
    },

    setPage(page) {
        this.currentPage = page;
        this.notify();
    },

    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    },

    notify() {
        for (const listener of this.listeners) {
            listener(this);
        }
    },

    getFilteredTransactions() {
        if (!this.data || !this.data.transactions) return [];

        let list = [...this.data.transactions];

        // Filter category
        if (this.selectedCategory !== "All") {
            list = list.filter(t => t.category.toLowerCase() === this.selectedCategory.toLowerCase());
        }

        // Filter search
        if (this.searchQuery) {
            list = list.filter(t =>
                t.merchant.toLowerCase().includes(this.searchQuery) ||
                t.date.toLowerCase().includes(this.searchQuery) ||
                t.category.toLowerCase().includes(this.searchQuery) ||
                t.amount.toString().includes(this.searchQuery)
            );
        }

        // Sort
        list.sort((a, b) => {
            let valA = a[this.sortKey];
            let valB = b[this.sortKey];

            if (this.sortKey === "amount") {
                valA = Number(valA);
                valB = Number(valB);
            }

            if (valA < valB) return this.sortDirection === "asc" ? -1 : 1;
            if (valA > valB) return this.sortDirection === "asc" ? 1 : -1;
            return 0;
        });

        return list;
    }
};
