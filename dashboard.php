<?php
require_once 'config/session.php';
allowGuestAccess();

$user = getCurrentUser();
$isGuest = isGuest();
$activePage = 'dashboard';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Personal Expense Tracker</title>
    <link rel="stylesheet" href="assets/css/theme.css">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
    <link rel="stylesheet" href="assets/css/auth.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body data-guest-mode="<?php echo $isGuest ? 'true' : 'false'; ?>">
    <div class="dashboard-layout">
        <!-- Sidebar -->
        <?php include 'config/sidebar.php'; ?>

        <!-- Main Content -->
        <main class="main-content">
            <header class="dashboard-header">
                <div>
                    <h1 class="dashboard-title">Dashboard</h1>
                    <p class="dashboard-subtitle text-muted text-sm" id="currentMonthLabel"></p>
                </div>
                <div class="user-menu">
                    <button class="theme-toggle" role="button" tabindex="0" aria-label="Toggle theme" title="Toggle theme">
                        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                    </button>
                    <button id="addExpenseBtn" class="btn btn-primary">
                        + Add Expense
                    </button>
                </div>
            </header>

            <div class="dashboard-body">
                <?php if ($isGuest): ?>
                <div class="guest-banner">
                    <div class="guest-banner-text">
                        👤 <strong>Guest Mode</strong> — Your data is stored locally. Sign in to save permanently and access reports.
                    </div>
                    <a href="index.php" class="btn-guest-login">Sign In</a>
                </div>
                <?php endif; ?>

                <!-- Stats Cards -->
                <div class="stats-grid stats-grid-4">
                    <div class="stat-card">
                        <div class="stat-label">This Month's Expenses</div>
                        <div class="stat-value" id="totalExpense">₹0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Transactions This Month</div>
                        <div class="stat-value" id="expenseCount">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg. Monthly Spending</div>
                        <div class="stat-value" id="averageExpense">₹0.00</div>
                        <div class="stat-detail text-muted text-sm" id="avgMonthlyDetail"></div>
                    </div>
                    <div class="stat-card budget-card" id="budgetStatCard">
                        <div class="stat-label">
                            Monthly Budget
                            <button class="btn-edit-budget" id="editBudgetBtn" title="Set budget">✏️</button>
                        </div>
                        <div class="stat-value" id="budgetValue">Not Set</div>
                        <div class="budget-progress-wrap" id="budgetProgressWrap" style="display:none;">
                            <div class="budget-progress-bar">
                                <div class="budget-progress-fill" id="budgetProgressFill"></div>
                            </div>
                            <div class="budget-progress-text">
                                <span id="budgetPercentText">0%</span> used
                                <span class="budget-remaining" id="budgetRemainingText"></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Budget Modal -->
                <div id="budgetModal" class="modal-overlay hidden">
                    <div class="modal" style="max-width:380px;">
                        <div class="modal-header">
                            <h2 class="modal-title">Set Monthly Budget</h2>
                            <button type="button" class="modal-close">✕</button>
                        </div>
                        <form id="budgetForm">
                            <div class="modal-body">
                                <div class="form-group">
                                    <label for="monthlyBudgetInput" class="label">Total Monthly Budget (₹)</label>
                                    <input type="number" id="monthlyBudgetInput" class="input" placeholder="e.g. 50000" min="0" step="100" required>
                                    <div class="form-help">Set your total spending limit for each month</div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-outline modal-close">Cancel</button>
                                <button type="submit" class="btn btn-primary">Save Budget</button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Charts with filter toggle -->
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="card-title">Expense Trend</h3>
                                    <p class="card-description" id="trendChartLabel">Last 7 days</p>
                                </div>
                                <div class="chart-filter-toggle" id="trendFilterBtns">
                                    <button class="filter-btn active" data-chart-filter="week">Week</button>
                                    <button class="filter-btn" data-chart-filter="month">Month</button>
                                    <button class="filter-btn" data-chart-filter="year">Year</button>
                                </div>
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="chart-container">
                                <canvas id="expenseChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="card-title">Expenses by Category</h3>
                                    <p class="card-description" id="categoryChartLabel">This week</p>
                                </div>
                                <div class="chart-filter-toggle" id="categoryFilterBtns">
                                    <button class="filter-btn active" data-chart-filter="week">Week</button>
                                    <button class="filter-btn" data-chart-filter="month">Month</button>
                                    <button class="filter-btn" data-chart-filter="year">Year</button>
                                </div>
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="chart-container">
                                <canvas id="categoryChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Spending Insights (limited to 2 insights + 2 recommendations) -->
                <div id="mlSuggestionsCard" class="card ml-suggestions-card mb-4" style="display: none;">
                    <div class="card-header">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="card-title">
                                    <span class="ml-badge">🤖 AI</span>
                                    Smart Spending Insights
                                </h3>
                                <p class="card-description">Top insights based on your spending patterns</p>
                            </div>
                            <button id="refreshSuggestions" class="btn btn-sm btn-outline" title="Refresh insights">
                                🔄 Refresh
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div id="mlSuggestionsContent">
                            <div class="text-center p-4">
                                <div class="spinner" style="margin: 0 auto;"></div>
                                <p class="mt-2 text-muted">Analyzing your spending patterns...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Expenses -->
                <div class="card">
                    <div class="card-header">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="card-title">Recent Expenses</h3>
                                <p class="card-description">Your latest transactions</p>
                            </div>
                            <div class="flex gap-2">
                                <button class="btn btn-sm btn-outline active" data-filter="all">All</button>
                                <button class="btn btn-sm btn-outline" data-filter="week">Week</button>
                                <button class="btn btn-sm btn-outline" data-filter="month">Month</button>
                                <button class="btn btn-sm btn-outline" data-filter="year">Year</button>
                            </div>
                        </div>
                    </div>
                    <div class="card-content p-0">
                        <div id="expenseList" class="expense-list">
                            <!-- Expenses will be loaded here by JavaScript -->
                            <div class="text-center p-4">
                                <div class="spinner" style="margin: 0 auto;"></div>
                                <p class="mt-2 text-muted">Loading expenses...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Add/Edit Expense Modal -->
    <div id="expenseModal" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title" id="expenseModalTitle">Add Expense</h2>
                <button type="button" class="modal-close">✕</button>
            </div>
            <form id="expenseForm">
                <div class="modal-body">
                    <div class="form-group">
                        <label for="amount" class="label">Amount</label>
                        <input 
                            type="number" 
                            id="amount" 
                            name="amount" 
                            class="input" 
                            placeholder="0.00"
                            step="0.01"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label for="category_id" class="label">Category</label>
                        <select id="category_id" name="category_id" class="input category-select" required>
                            <option value="">Select category</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="description" class="label">Description</label>
                        <input 
                            type="text" 
                            id="description" 
                            name="description" 
                            class="input" 
                            placeholder="What did you spend on?"
                        >
                    </div>

                    <div class="form-group">
                        <label for="expense_date" class="label">Date</label>
                        <input 
                            type="date" 
                            id="expense_date" 
                            name="expense_date" 
                            class="input" 
                            required
                            value="<?php echo date('Y-m-d'); ?>"
                        >
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline modal-close">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Expense</button>
                </div>
            </form>
        </div>
    </div>

    <script src="assets/js/theme.js"></script>
    <script src="assets/js/main.js"></script>
    <script src="assets/js/guest.js"></script>
    <script src="assets/js/dashboard.js"></script>
</body>
</html>
