<?php
require_once 'config/session.php';
requireLoginForFeature('Spark Analytics');

$user = getCurrentUser();
$activePage = 'spark';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark Analytics - Personal Expense Tracker</title>
    <meta name="description" content="Big data analytics dashboard powered by Apache Spark for expense tracking">
    <link rel="stylesheet" href="assets/css/theme.css">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
    <link rel="stylesheet" href="assets/css/spark_analytics.css">
    <link rel="stylesheet" href="assets/css/auth.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="dashboard-layout">
        <!-- Sidebar -->
        <?php include 'config/sidebar.php'; ?>

        <!-- Main Content -->
        <main class="main-content">
            <header class="dashboard-header">
                <div>
                    <h1 class="dashboard-title">
                        <span class="spark-icon">⚡</span> Spark Analytics
                    </h1>
                    <p class="dashboard-subtitle text-muted text-sm">
                        Big Data insights powered by Apache Spark
                    </p>
                </div>
                <div class="user-menu">
                    <div class="spark-status" id="sparkStatus">
                        <span class="status-dot"></span>
                        <span class="status-text" id="sparkStatusText">Checking...</span>
                    </div>
                    <button class="theme-toggle" role="button" tabindex="0" aria-label="Toggle theme" title="Toggle theme">
                        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                    </button>
                </div>
            </header>

            <div class="dashboard-body">
                <!-- No Data State -->
                <div id="noDataState" class="no-data-state" style="display: none;">
                    <div class="no-data-icon">⚡</div>
                    <h2>Spark Analytics Not Available</h2>
                    <p>Run the Apache Spark analytics job to generate insights from your expense data.</p>
                    <div class="no-data-steps">
                        <div class="step-item">
                            <span class="step-num">1</span>
                            <span>Open terminal in <code>spark/</code> folder</span>
                        </div>
                        <div class="step-item">
                            <span class="step-num">2</span>
                            <span>Run <code>run_spark.bat</code></span>
                        </div>
                        <div class="step-item">
                            <span class="step-num">3</span>
                            <span>Refresh this page</span>
                        </div>
                    </div>
                    <button class="btn btn-primary mt-3" onclick="location.reload()">🔄 Refresh Page</button>
                </div>

                <!-- Analytics Content -->
                <div id="analyticsContent" style="display: none;">
                    <!-- Summary Stats -->
                    <div class="stats-grid stats-grid-4">
                        <div class="stat-card spark-stat">
                            <div class="stat-label">Total Analyzed</div>
                            <div class="stat-value" id="statGrandTotal">₹0</div>
                            <div class="stat-detail text-muted text-sm" id="statMonthsCovered">0 months</div>
                        </div>
                        <div class="stat-card spark-stat">
                            <div class="stat-label">Avg Monthly Spending</div>
                            <div class="stat-value" id="statAvgMonthly">₹0</div>
                            <div class="stat-detail text-muted text-sm">across all months</div>
                        </div>
                        <div class="stat-card spark-stat">
                            <div class="stat-label">Top Category</div>
                            <div class="stat-value" id="statTopCategory">—</div>
                            <div class="stat-detail text-muted text-sm" id="statTopCatPercent">—</div>
                        </div>
                        <div class="stat-card spark-stat">
                            <div class="stat-label">Last Spark Run</div>
                            <div class="stat-value stat-value-sm" id="statLastRun">—</div>
                            <div class="stat-detail text-muted text-sm">
                                <span class="spark-badge">⚡ Spark Processed</span>
                            </div>
                        </div>
                    </div>

                    <!-- Charts Row -->
                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <!-- Spending Trend Chart -->
                        <div class="card">
                            <div class="card-header">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="card-title">Spending Trend</h3>
                                        <p class="card-description" id="trendChartLabel">Monthly trend</p>
                                    </div>
                                    <div class="chart-filter-toggle" id="trendFilterBtns">
                                        <button class="filter-btn" data-period="weekly">Week</button>
                                        <button class="filter-btn active" data-period="monthly">Month</button>
                                        <button class="filter-btn" data-period="yearly">Year</button>
                                    </div>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="chart-container">
                                    <canvas id="sparkTrendChart"></canvas>
                                </div>
                            </div>
                        </div>

                        <!-- Category Pie Chart -->
                        <div class="card">
                            <div class="card-header">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="card-title">Category Breakdown</h3>
                                        <p class="card-description" id="categoryChartLabel">This month</p>
                                    </div>
                                    <div class="month-selector">
                                        <select id="categoryMonthSelect" class="input input-sm">
                                            <!-- Populated by JS -->
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="chart-container">
                                    <canvas id="sparkCategoryChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- AI Insights & Recommendations -->
                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <!-- Smart Insights -->
                        <div class="card spark-insights-card">
                            <div class="card-header">
                                <h3 class="card-title">
                                    <span class="spark-badge">🤖 AI</span>
                                    Smart Spending Insights
                                </h3>
                                <p class="card-description">Data-driven analysis via Spark</p>
                            </div>
                            <div class="card-content">
                                <div id="insightsContainer">
                                    <div class="text-center p-4 text-muted">Loading insights...</div>
                                </div>
                            </div>
                        </div>

                        <!-- Smart Recommendations -->
                        <div class="card spark-recommendations-card">
                            <div class="card-header">
                                <h3 class="card-title">
                                    <span class="spark-badge">💡 Smart</span>
                                    Recommendations
                                </h3>
                                <p class="card-description">Actionable suggestions to optimize spending</p>
                            </div>
                            <div class="card-content">
                                <div id="recommendationsContainer">
                                    <div class="text-center p-4 text-muted">Loading recommendations...</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Monthly Breakdown Table -->
                    <div class="card">
                        <div class="card-header">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="card-title">Monthly Breakdown</h3>
                                    <p class="card-description">Detailed monthly spending analysis</p>
                                </div>
                            </div>
                        </div>
                        <div class="card-content p-0">
                            <div class="table-responsive">
                                <table class="data-table" id="monthlyTable">
                                    <thead>
                                        <tr>
                                            <th>Month</th>
                                            <th>Total Spent</th>
                                            <th>Transactions</th>
                                            <th>Avg/Transaction</th>
                                            <th>Max</th>
                                            <th>Min</th>
                                        </tr>
                                    </thead>
                                    <tbody id="monthlyTableBody">
                                        <!-- Populated by JS -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script src="assets/js/theme.js"></script>
    <script src="assets/js/main.js"></script>
    <script src="assets/js/spark_analytics.js"></script>
</body>
</html>
