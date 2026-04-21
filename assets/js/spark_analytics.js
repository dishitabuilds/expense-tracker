/**
 * ============================================================
 * Spark Analytics Dashboard — JavaScript
 * ============================================================
 * Fetches Spark-processed data from api/spark_summary.php
 * Renders charts (Chart.js), insights, recommendations, table
 * ============================================================
 */

(function () {
    'use strict';

    // ── State ──
    let trendChart = null;
    let categoryChart = null;
    let overviewData = null;
    let currentTrendPeriod = 'monthly';

    // ── Format helpers ──
    function formatCurrency(amount) {
        return '₹' + Number(amount).toLocaleString('en-IN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    function formatCurrencyDecimal(amount) {
        return '₹' + Number(amount).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function formatDate(dateStr) {
        if (!dateStr) return '—';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    }

    // ── Chart color palette ──
    const CHART_COLORS = [
        '#ef4444', '#3b82f6', '#8b5cf6', '#ec4899',
        '#f59e0b', '#10b981', '#06b6d4', '#6b7280',
        '#f97316', '#14b8a6', '#a855f7', '#e11d48'
    ];

    const GRADIENT_COLORS = {
        line: { start: 'rgba(99, 102, 241, 0.3)', end: 'rgba(99, 102, 241, 0.02)' },
        bar: { start: 'rgba(245, 158, 11, 0.8)', end: 'rgba(239, 68, 68, 0.8)' }
    };

    // ── Initialize ──
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        loadOverviewData();
        setupTrendFilters();
        setupMonthSelector();
    }

    // ── Load Overview Data ──
    async function loadOverviewData() {
        try {
            const resp = await fetch('api/spark_summary.php?action=overview');
            const data = await resp.json();

            if (!data.success) {
                if (data.spark_not_run) {
                    showNoDataState();
                    return;
                }
                throw new Error(data.message || 'Failed to load data');
            }

            if (!data.has_data) {
                showNoDataState();
                return;
            }

            overviewData = data;
            showAnalyticsContent();
            renderStats(data);
            renderTrendChart('monthly');
            renderCategoryChart(data.categories);
            renderInsights(data.insights);
            renderRecommendations(data.recommendations);
            renderMonthlyTable(data.monthly);
            updateSparkStatus(data.last_run);
            populateMonthSelector(data.monthly);

        } catch (err) {
            console.error('Error loading Spark data:', err);
            showNoDataState();
        }
    }

    // ── Show/Hide States ──
    function showNoDataState() {
        const noData = document.getElementById('noDataState');
        const content = document.getElementById('analyticsContent');
        const status = document.getElementById('sparkStatus');

        if (noData) noData.style.display = 'flex';
        if (content) content.style.display = 'none';
        if (status) {
            status.classList.add('inactive');
            status.classList.remove('active');
            document.getElementById('sparkStatusText').textContent = 'Not Run';
        }
    }

    function showAnalyticsContent() {
        const noData = document.getElementById('noDataState');
        const content = document.getElementById('analyticsContent');
        if (noData) noData.style.display = 'none';
        if (content) content.style.display = 'block';
    }

    // ── Update Spark Status ──
    function updateSparkStatus(lastRun) {
        const status = document.getElementById('sparkStatus');
        const statusText = document.getElementById('sparkStatusText');

        if (lastRun) {
            status.classList.add('active');
            status.classList.remove('inactive');
            statusText.textContent = 'Data Ready';
        } else {
            status.classList.add('inactive');
            status.classList.remove('active');
            statusText.textContent = 'Not Run';
        }
    }

    // ── Render Stats Cards ──
    function renderStats(data) {
        const s = data.summary || {};

        // Grand total
        const totalEl = document.getElementById('statGrandTotal');
        if (totalEl) totalEl.textContent = formatCurrency(s.grand_total || 0);

        // Months covered
        const monthsEl = document.getElementById('statMonthsCovered');
        if (monthsEl) monthsEl.textContent = `${s.months_covered || 0} months analyzed`;

        // Avg monthly
        const avgEl = document.getElementById('statAvgMonthly');
        if (avgEl) avgEl.textContent = formatCurrency(s.avg_monthly || 0);

        // Top category
        const topCatEl = document.getElementById('statTopCategory');
        const topCatPctEl = document.getElementById('statTopCatPercent');
        if (data.categories && data.categories.length > 0) {
            const top = data.categories[0];
            if (topCatEl) topCatEl.textContent = top.category_name;
            if (topCatPctEl) topCatPctEl.textContent = `${top.percentage}% of spending`;
        }

        // Last run
        const lastRunEl = document.getElementById('statLastRun');
        if (lastRunEl && data.last_run) {
            lastRunEl.textContent = formatDate(data.last_run);
        }
    }

    // ── Trend Chart ──
    function setupTrendFilters() {
        const btns = document.querySelectorAll('#trendFilterBtns .filter-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', function () {
                btns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const period = this.dataset.period;
                currentTrendPeriod = period;
                loadTrendData(period);
            });
        });
    }

    async function loadTrendData(period) {
        try {
            const resp = await fetch(`api/spark_summary.php?action=trends&period=${period}`);
            const data = await resp.json();

            if (data.success) {
                renderTrendChart(period, data.data);
            }
        } catch (err) {
            console.error('Error loading trend data:', err);
        }
    }

    function renderTrendChart(period, data) {
        // On initial load, use overview data for monthly
        if (!data && overviewData && period === 'monthly') {
            // Convert monthly overview to trend format
            data = (overviewData.monthly || []).map(m => ({
                period_label: `${m.month_name} ${m.year}`,
                total_amount: m.total_amount,
                transaction_count: m.transaction_count
            })).reverse();
        }

        if (!data || data.length === 0) {
            return;
        }

        const labels = data.map(d => d.period_label);
        const amounts = data.map(d => d.total_amount);

        const ctx = document.getElementById('sparkTrendChart');
        if (!ctx) return;

        if (trendChart) {
            trendChart.destroy();
        }

        // Create gradient
        const context = ctx.getContext('2d');
        const gradient = context.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, GRADIENT_COLORS.line.start);
        gradient.addColorStop(1, GRADIENT_COLORS.line.end);

        trendChart = new Chart(ctx, {
            type: period === 'yearly' ? 'bar' : 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Spending',
                    data: amounts,
                    borderColor: '#6366f1',
                    backgroundColor: period === 'yearly'
                        ? CHART_COLORS.slice(0, amounts.length)
                        : gradient,
                    borderWidth: 2,
                    fill: period !== 'yearly',
                    tension: 0.4,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: period === 'weekly' ? 4 : 3,
                    pointHoverRadius: 6,
                    borderRadius: period === 'yearly' ? 6 : 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.85)',
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function (ctx) {
                                return ' ' + formatCurrency(ctx.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            maxRotation: 45
                        }
                    },
                    y: {
                        grid: { color: 'rgba(148, 163, 184, 0.08)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            callback: v => formatCurrency(v)
                        }
                    }
                }
            }
        });

        // Update label
        const labelMap = { weekly: 'Weekly trend', monthly: 'Monthly trend', yearly: 'Yearly trend' };
        const label = document.getElementById('trendChartLabel');
        if (label) label.textContent = labelMap[period] || 'Trend';
    }

    // ── Category Chart ──
    function renderCategoryChart(categories) {
        if (!categories || categories.length === 0) return;

        const labels = categories.map(c => c.category_name);
        const amounts = categories.map(c => c.total_amount);
        const colors = categories.map((c, i) => c.category_color || CHART_COLORS[i % CHART_COLORS.length]);

        const ctx = document.getElementById('sparkCategoryChart');
        if (!ctx) return;

        if (categoryChart) {
            categoryChart.destroy();
        }

        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: amounts,
                    backgroundColor: colors,
                    borderColor: 'rgba(0,0,0,0.3)',
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            padding: 12,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.85)',
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function (ctx) {
                                const pct = categories[ctx.dataIndex]?.percentage || 0;
                                return ` ${ctx.label}: ${formatCurrency(ctx.parsed)} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // ── Month Selector for Category Chart ──
    function setupMonthSelector() {
        const select = document.getElementById('categoryMonthSelect');
        if (!select) return;

        select.addEventListener('change', async function () {
            const [year, month] = this.value.split('-').map(Number);
            try {
                const resp = await fetch(`api/spark_summary.php?action=category&year=${year}&month=${month}`);
                const data = await resp.json();
                if (data.success) {
                    renderCategoryChart(data.data);
                    const label = document.getElementById('categoryChartLabel');
                    if (label) {
                        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                            'July', 'August', 'September', 'October', 'November', 'December'];
                        label.textContent = `${monthNames[month]} ${year}`;
                    }
                }
            } catch (err) {
                console.error('Error loading category data:', err);
            }
        });
    }

    function populateMonthSelector(monthlyData) {
        const select = document.getElementById('categoryMonthSelect');
        if (!select || !monthlyData) return;

        select.innerHTML = '';
        monthlyData.forEach((m, idx) => {
            const opt = document.createElement('option');
            opt.value = `${m.year}-${m.month}`;
            opt.textContent = `${m.month_name} ${m.year}`;
            if (idx === 0) opt.selected = true;
            select.appendChild(opt);
        });
    }

    // ── Render Insights ──
    function renderInsights(insights) {
        const container = document.getElementById('insightsContainer');
        if (!container) return;

        if (!insights || insights.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <p>No insights available. Run Spark analytics to generate insights.</p>
                </div>`;
            return;
        }

        const severityIcons = {
            warning: '⚠️',
            info: 'ℹ️',
            success: '✅',
            critical: '🚨'
        };

        let html = '';
        insights.forEach(insight => {
            const icon = severityIcons[insight.severity] || 'ℹ️';
            html += `
                <div class="insight-item">
                    <div class="insight-header">
                        <span class="insight-type-badge ${insight.severity}">${icon} ${(insight.insight_type || '').replace(/_/g, ' ')}</span>
                        <span class="insight-category">${insight.category || ''}</span>
                    </div>
                    <div class="insight-message">${escapeHtml(insight.message)}</div>
                </div>`;
        });

        container.innerHTML = html;
    }

    // ── Render Recommendations ──
    function renderRecommendations(recommendations) {
        const container = document.getElementById('recommendationsContainer');
        if (!container) return;

        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <p>No recommendations available. Run Spark analytics to generate recommendations.</p>
                </div>`;
            return;
        }

        const typeIcons = {
            category_optimization: '📊',
            weekend_pattern: '📅',
            budget_suggestion: '💰',
            consistent_spending: '✅'
        };

        let html = '';
        recommendations.forEach(rec => {
            const icon = typeIcons[rec.rec_type] || '💡';
            const savings = rec.potential_savings > 0
                ? `<div class="rec-savings">💰 Potential savings: ${formatCurrency(rec.potential_savings)}/month</div>`
                : '';

            html += `
                <div class="recommendation-item">
                    <div class="rec-header">
                        <span>${icon}</span>
                        <span class="rec-priority-badge ${rec.priority}">${rec.priority} priority</span>
                        <span class="insight-category">${rec.category || ''}</span>
                    </div>
                    <div class="rec-message">${escapeHtml(rec.message)}</div>
                    ${savings}
                </div>`;
        });

        container.innerHTML = html;
    }

    // ── Render Monthly Table ──
    function renderMonthlyTable(monthly) {
        const tbody = document.getElementById('monthlyTableBody');
        if (!tbody || !monthly) return;

        if (monthly.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center p-4 text-muted">No data available</td></tr>`;
            return;
        }

        let html = '';
        monthly.forEach(m => {
            html += `
                <tr>
                    <td><strong>${m.month_name} ${m.year}</strong></td>
                    <td class="table-amount">${formatCurrency(m.total_amount)}</td>
                    <td>${m.transaction_count}</td>
                    <td>${formatCurrencyDecimal(m.avg_amount)}</td>
                    <td>${formatCurrency(m.max_amount || 0)}</td>
                    <td>${formatCurrency(m.min_amount || 0)}</td>
                </tr>`;
        });

        tbody.innerHTML = html;
    }

    // ── Escape HTML ──
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

})();
