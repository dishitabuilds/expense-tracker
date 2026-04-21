/**
 * Guest Mode — localStorage-based expense management
 * Used when users access the app without logging in
 */

const GuestStorage = {
    KEYS: {
        expenses: 'guest_expenses',
        categories: 'guest_categories',
        budget: 'guest_budget'
    },

    /**
     * Default categories for guest users
     */
    defaultCategories: [
        { id: 1, name: 'Food & Dining', color: '#ef4444', icon: 'utensils' },
        { id: 2, name: 'Transportation', color: '#3b82f6', icon: 'car' },
        { id: 3, name: 'Shopping', color: '#8b5cf6', icon: 'shopping-bag' },
        { id: 4, name: 'Entertainment', color: '#ec4899', icon: 'film' },
        { id: 5, name: 'Bills & Utilities', color: '#f59e0b', icon: 'file-text' },
        { id: 6, name: 'Healthcare', color: '#10b981', icon: 'heart' },
        { id: 7, name: 'Education', color: '#06b6d4', icon: 'book' },
        { id: 8, name: 'Other', color: '#6b7280', icon: 'tag' }
    ],

    /**
     * Initialize guest storage with defaults if empty
     */
    init() {
        if (!localStorage.getItem(this.KEYS.categories)) {
            localStorage.setItem(this.KEYS.categories, JSON.stringify(this.defaultCategories));
        }
        if (!localStorage.getItem(this.KEYS.expenses)) {
            localStorage.setItem(this.KEYS.expenses, JSON.stringify([]));
        }
    },

    // ============================================
    // CATEGORIES
    // ============================================

    getCategories() {
        this.init();
        return JSON.parse(localStorage.getItem(this.KEYS.categories) || '[]');
    },

    getCategoryById(id) {
        return this.getCategories().find(c => c.id === parseInt(id));
    },

    addCategory(category) {
        const categories = this.getCategories();
        const newId = categories.length > 0 ? Math.max(...categories.map(c => c.id)) + 1 : 1;
        const newCategory = { id: newId, ...category };
        categories.push(newCategory);
        localStorage.setItem(this.KEYS.categories, JSON.stringify(categories));
        return newCategory;
    },

    updateCategory(id, updates) {
        const categories = this.getCategories();
        const index = categories.findIndex(c => c.id === parseInt(id));
        if (index !== -1) {
            categories[index] = { ...categories[index], ...updates };
            localStorage.setItem(this.KEYS.categories, JSON.stringify(categories));
            return categories[index];
        }
        return null;
    },

    deleteCategory(id) {
        const categories = this.getCategories().filter(c => c.id !== parseInt(id));
        localStorage.setItem(this.KEYS.categories, JSON.stringify(categories));
    },

    // ============================================
    // EXPENSES
    // ============================================

    getExpenses() {
        this.init();
        return JSON.parse(localStorage.getItem(this.KEYS.expenses) || '[]');
    },

    getExpenseById(id) {
        return this.getExpenses().find(e => e.id === parseInt(id));
    },

    addExpense(expense) {
        const expenses = this.getExpenses();
        const newId = expenses.length > 0 ? Math.max(...expenses.map(e => e.id)) + 1 : 1;
        const now = new Date().toISOString();
        const newExpense = {
            id: newId,
            ...expense,
            category_id: parseInt(expense.category_id),
            amount: parseFloat(expense.amount),
            created_at: now,
            updated_at: now
        };
        expenses.push(newExpense);
        localStorage.setItem(this.KEYS.expenses, JSON.stringify(expenses));
        return newExpense;
    },

    updateExpense(id, updates) {
        const expenses = this.getExpenses();
        const index = expenses.findIndex(e => e.id === parseInt(id));
        if (index !== -1) {
            expenses[index] = {
                ...expenses[index],
                ...updates,
                updated_at: new Date().toISOString()
            };
            localStorage.setItem(this.KEYS.expenses, JSON.stringify(expenses));
            return expenses[index];
        }
        return null;
    },

    deleteExpense(id) {
        const expenses = this.getExpenses().filter(e => e.id !== parseInt(id));
        localStorage.setItem(this.KEYS.expenses, JSON.stringify(expenses));
    },

    // ============================================
    // QUERIES (mimic API responses)
    // ============================================

    /**
     * Get expenses with optional filters
     */
    queryExpenses(filters = {}) {
        let expenses = this.getExpenses();

        // Category filter
        if (filters.category_id) {
            expenses = expenses.filter(e => e.category_id === parseInt(filters.category_id));
        }

        // Date range filter
        if (filters.start_date) {
            expenses = expenses.filter(e => e.expense_date >= filters.start_date);
        }
        if (filters.end_date) {
            expenses = expenses.filter(e => e.expense_date <= filters.end_date);
        }

        // Search
        if (filters.search) {
            const term = filters.search.toLowerCase();
            expenses = expenses.filter(e =>
                (e.description || '').toLowerCase().includes(term) ||
                (e.notes || '').toLowerCase().includes(term)
            );
        }

        // Sort
        const sortBy = filters.sort || 'expense_date';
        const sortDir = filters.sort_dir || 'DESC';
        expenses.sort((a, b) => {
            let cmp = 0;
            if (sortBy === 'amount') {
                cmp = a.amount - b.amount;
            } else {
                cmp = (a[sortBy] || '').localeCompare(b[sortBy] || '');
            }
            return sortDir === 'DESC' ? -cmp : cmp;
        });

        // Enrich with category data
        const categories = this.getCategories();
        expenses = expenses.map(e => {
            const cat = categories.find(c => c.id === e.category_id);
            return {
                ...e,
                category_name: cat ? cat.name : 'Uncategorized',
                category_color: cat ? cat.color : '#6b7280'
            };
        });

        return expenses;
    },

    /**
     * Get dashboard summary for current month
     */
    getDashboardSummary() {
        const now = new Date();
        const year = now.getFullYear();
        const month = (now.getMonth() + 1).toString().padStart(2, '0');
        const startDate = `${year}-${month}-01`;
        const endDate = `${year}-${month}-31`;

        const expenses = this.queryExpenses({ start_date: startDate, end_date: endDate });
        const total = expenses.reduce((sum, e) => sum + e.amount, 0);
        const count = expenses.length;
        const average = count > 0 ? total / count : 0;

        return {
            total_expense: total,
            expense_count: count,
            average_expense: average,
            month_label: now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
        };
    },

    /**
     * Get category-wise breakdown
     */
    getCategoryBreakdown(startDate, endDate) {
        const expenses = this.queryExpenses({ start_date: startDate, end_date: endDate });
        const categories = this.getCategories();
        const breakdown = {};

        expenses.forEach(e => {
            if (!breakdown[e.category_id]) {
                const cat = categories.find(c => c.id === e.category_id);
                breakdown[e.category_id] = {
                    name: cat ? cat.name : 'Unknown',
                    color: cat ? cat.color : '#6b7280',
                    total: 0,
                    count: 0
                };
            }
            breakdown[e.category_id].total += e.amount;
            breakdown[e.category_id].count++;
        });

        return Object.values(breakdown);
    },

    // ============================================
    // BUDGET
    // ============================================

    getBudget() {
        return parseFloat(localStorage.getItem(this.KEYS.budget)) || 0;
    },

    setBudget(amount) {
        localStorage.setItem(this.KEYS.budget, amount.toString());
    },

    // ============================================
    // UTILITIES
    // ============================================

    getExpenseCount() {
        return this.getExpenses().length;
    },

    clearAll() {
        Object.values(this.KEYS).forEach(key => localStorage.removeItem(key));
    }
};

/**
 * Check if current page is in guest mode
 */
function isGuestMode() {
    // The page sets this data attribute based on PHP session
    return document.body.dataset.guestMode === 'true';
}

/**
 * Show login prompt when guest tries to access premium features
 */
function showLoginRequired(feature) {
    const overlay = document.createElement('div');
    overlay.className = 'login-required-overlay';
    overlay.innerHTML = `
        <div class="login-required-card">
            <div class="lock-icon">🔒</div>
            <h3>Login Required</h3>
            <p>${feature || 'This feature'} requires a free account. Your guest data will be preserved.</p>
            <a href="/personal_expense/index.php" class="btn-signin" style="display: inline-block; text-decoration: none; margin-bottom: 0.5rem;">
                Sign In / Create Account
            </a>
            <br>
            <button onclick="this.closest('.login-required-overlay').remove()" style="background:none; border:none; color:#64748b; cursor:pointer; font-size:0.875rem; margin-top:0.5rem;">
                Cancel
            </button>
        </div>
    `;
    document.body.appendChild(overlay);

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.remove();
    });
}

// Initialize guest storage on load
GuestStorage.init();

// Export
window.GuestStorage = GuestStorage;
window.isGuestMode = isGuestMode;
window.showLoginRequired = showLoginRequired;
