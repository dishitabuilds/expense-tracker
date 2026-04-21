/**
 * Personal Expense Tracker - Dashboard JavaScript (Refactored v2)
 * - Stats: current month only + avg monthly spending (last 6mo)
 * - Monthly Budget card with progress bar
 * - Charts: Week/Month/Year filter toggles
 * - AI insights: 2 max (1 behavioral + 1 predictive)
 * - Recommendations: 2 max (priority-aware)
 * - AI auto-predict category preserved
 */

let expensesChart = null;
let categoryChart = null;

const dashboardState = {
    expenses: [],
    categories: [],
    currentFilter: 'all',
    trendChartFilter: 'week',
    categoryChartFilter: 'week',
    currentExpense: null,
    mlSuggestions: null,
    budgetData: null
};

// ============================================================================
// INITIALIZATION
// ============================================================================

async function initDashboard() {
    try {
        await Promise.all([
            loadExpenses(),
            loadCategories()
        ]);

        const now = new Date();
        const monthLabel = now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        const el = document.getElementById('currentMonthLabel');
        if (el) el.textContent = `Showing stats for ${monthLabel}`;

        renderExpenses();
        updateStats();
        initCharts();
        setupEventListeners();
        loadBudgetData();
        loadMLSuggestions();
    } catch (error) {
        console.error('Dashboard init error:', error);
        utils.showAlert('Failed to load dashboard data', 'error');
    }
}

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadExpenses() {
    const data = await utils.apiRequest('/personal_expense/api/expenses.php');
    dashboardState.expenses = data.expenses || [];
}

async function loadCategories() {
    const data = await utils.apiRequest('/personal_expense/api/categories.php');
    dashboardState.categories = data.categories || [];
    renderCategoryOptions();
}

async function loadBudgetData() {
    try {
        const data = await utils.apiRequest('/personal_expense/api/budget.php');
        if (data.success) {
            dashboardState.budgetData = data.budget;
            renderBudgetCard(data.budget);
        }
    } catch (e) {
        console.log('Budget API not available yet');
    }
}

// ============================================================================
// UI RENDERING
// ============================================================================

function renderCategoryOptions() {
    document.querySelectorAll('.category-select').forEach(select => {
        select.innerHTML = '<option value="">Select category</option>';
        dashboardState.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            select.appendChild(option);
        });
    });
}

function renderExpenses() {
    const list = document.getElementById('expenseList');
    if (!list) return;

    const filtered = filterExpenses();

    if (filtered.length === 0) {
        list.innerHTML = `<div class="text-center p-4 text-muted"><p>${
            dashboardState.expenses.length === 0
                ? 'No expenses found. Add your first expense!'
                : 'No expenses for the selected period.'
        }</p></div>`;
        return;
    }

    list.innerHTML = filtered.map(expense => {
        const cat = dashboardState.categories.find(c => c.id == expense.category_id);
        const color = cat?.color || '#6366f1';
        return `
            <div class="expense-item">
                <div class="expense-info">
                    <div class="expense-icon" style="background:${color}20;color:${color};">
                        ${getCategoryIcon(cat?.icon || 'tag')}
                    </div>
                    <div class="expense-details">
                        <div class="expense-description">${expense.description || 'No description'}</div>
                        <div class="expense-meta">
                            <span class="badge badge-outline">${cat?.name || 'Uncategorized'}</span>
                            <span class="text-muted">• ${utils.formatDate(expense.expense_date)}</span>
                        </div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:1rem;">
                    <div class="expense-amount">${utils.formatCurrency(expense.amount)}</div>
                    <div class="expense-actions">
                        <button class="btn btn-sm btn-ghost" onclick="editExpense(${expense.id})">Edit</button>
                        <button class="btn btn-sm btn-ghost text-destructive" onclick="deleteExpense(${expense.id})">Delete</button>
                    </div>
                </div>
            </div>`;
    }).join('');
}

// ============================================================================
// FILTERING
// ============================================================================

function filterExpenses() {
    const now = new Date();
    return dashboardState.expenses.filter(exp => {
        const d = new Date(exp.expense_date);
        switch (dashboardState.currentFilter) {
            case 'week': return d >= new Date(now.getTime() - 7*86400000);
            case 'month': return d.getMonth()===now.getMonth() && d.getFullYear()===now.getFullYear();
            case 'year': return d.getFullYear()===now.getFullYear();
            default: return true;
        }
    });
}

function filterByPeriod(period) {
    const now = new Date();
    return dashboardState.expenses.filter(exp => {
        const d = new Date(exp.expense_date);
        switch (period) {
            case 'week': return d >= new Date(now.getTime() - 7*86400000);
            case 'month': return d.getMonth()===now.getMonth() && d.getFullYear()===now.getFullYear();
            case 'year': return d.getFullYear()===now.getFullYear();
            default: return true;
        }
    });
}

// ============================================================================
// STATS (current month + avg monthly spending)
// ============================================================================

function updateStats() {
    const now = new Date();
    const currentMonth = dashboardState.expenses.filter(exp => {
        const d = new Date(exp.expense_date);
        return d.getMonth()===now.getMonth() && d.getFullYear()===now.getFullYear();
    });

    const total = currentMonth.reduce((s,e) => s + parseFloat(e.amount), 0);
    const count = currentMonth.length;

    document.getElementById('totalExpense').textContent = utils.formatCurrency(total);
    document.getElementById('expenseCount').textContent = count;

    // Average Monthly Spending (last 6 months, excluding current)
    const monthlyTotals = {};
    dashboardState.expenses.forEach(exp => {
        const d = new Date(exp.expense_date);
        const sixMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 6, 1);
        if (d >= sixMonthsAgo && !(d.getMonth()===now.getMonth() && d.getFullYear()===now.getFullYear())) {
            const key = `${d.getFullYear()}-${d.getMonth()}`;
            monthlyTotals[key] = (monthlyTotals[key] || 0) + parseFloat(exp.amount);
        }
    });

    const months = Object.keys(monthlyTotals);
    let avgMonthly = 0;
    if (months.length > 0) {
        avgMonthly = Object.values(monthlyTotals).reduce((s,v) => s+v, 0) / months.length;
    }

    document.getElementById('averageExpense').textContent = utils.formatCurrency(avgMonthly);
    const detail = document.getElementById('avgMonthlyDetail');
    if (detail) {
        detail.textContent = months.length > 0
            ? `Based on last ${months.length} month${months.length>1?'s':''}`
            : 'Not enough data yet';
    }
}

// ============================================================================
// BUDGET CARD
// ============================================================================

function renderBudgetCard(budget) {
    const valueEl = document.getElementById('budgetValue');
    const progressWrap = document.getElementById('budgetProgressWrap');
    const fill = document.getElementById('budgetProgressFill');
    const percentText = document.getElementById('budgetPercentText');
    const remainingText = document.getElementById('budgetRemainingText');

    if (!budget || budget.monthly_budget <= 0) {
        if (valueEl) valueEl.textContent = 'Not Set';
        if (progressWrap) progressWrap.style.display = 'none';
        return;
    }

    if (valueEl) valueEl.textContent = utils.formatCurrency(budget.monthly_budget);
    if (progressWrap) progressWrap.style.display = 'block';

    const pct = Math.min(budget.percent_used, 100);
    if (fill) {
        fill.style.width = pct + '%';
        fill.className = 'budget-progress-fill';
        if (budget.percent_used > 90) fill.classList.add('danger');
        else if (budget.percent_used > 70) fill.classList.add('warning');
        else fill.classList.add('safe');
    }

    if (percentText) percentText.textContent = budget.percent_used + '%';
    if (remainingText) {
        if (budget.remaining >= 0) {
            remainingText.textContent = `• ₹${budget.remaining.toLocaleString('en-IN')} left`;
            remainingText.style.color = '';
        } else {
            remainingText.textContent = `• ₹${Math.abs(budget.remaining).toLocaleString('en-IN')} over`;
            remainingText.style.color = 'var(--error-color)';
        }
    }
}

// ============================================================================
// CHARTS
// ============================================================================

function initCharts() {
    initExpenseChart(dashboardState.trendChartFilter);
    initCategoryChart(dashboardState.categoryChartFilter);
}

function initExpenseChart(period) {
    const ctx = document.getElementById('expenseChart');
    if (!ctx) return;
    const now = new Date();
    let labels = [], data = [], labelText = '';

    if (period === 'week') {
        labelText = 'Last 7 days';
        for (let i = 6; i >= 0; i--) {
            const date = new Date(now); date.setDate(date.getDate() - i);
            const ds = date.toISOString().split('T')[0];
            labels.push(date.toLocaleDateString('en-US', { month:'short', day:'numeric' }));
            data.push(dashboardState.expenses.filter(e => e.expense_date===ds).reduce((s,e) => s+parseFloat(e.amount), 0));
        }
    } else if (period === 'month') {
        labelText = now.toLocaleDateString('en-US', { month:'long', year:'numeric' });
        const y = now.getFullYear(), m = now.getMonth(), dim = new Date(y, m+1, 0).getDate();
        for (let d = 1; d <= dim; d += 7) {
            const end = Math.min(d+6, dim);
            labels.push(`${d}-${end}`);
            data.push(dashboardState.expenses.filter(e => {
                const ed = new Date(e.expense_date);
                return ed.getMonth()===m && ed.getFullYear()===y && ed.getDate()>=d && ed.getDate()<=end;
            }).reduce((s,e) => s+parseFloat(e.amount), 0));
        }
    } else {
        labelText = `Year ${now.getFullYear()}`;
        const mn = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        for (let m = 0; m < 12; m++) {
            labels.push(mn[m]);
            data.push(dashboardState.expenses.filter(e => {
                const ed = new Date(e.expense_date);
                return ed.getMonth()===m && ed.getFullYear()===now.getFullYear();
            }).reduce((s,e) => s+parseFloat(e.amount), 0));
        }
    }

    const desc = document.getElementById('trendChartLabel');
    if (desc) desc.textContent = labelText;

    if (expensesChart) expensesChart.destroy();
    const tc = ThemeManager.getChartColors();

    expensesChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{
            label: 'Expenses', data,
            borderColor: tc.palette[0], backgroundColor: tc.palette[0]+'20',
            tension: 0.4, fill: true
        }]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 600, easing: 'easeOutQuart' },
            plugins: { legend: { display: false },
                tooltip: { backgroundColor: tc.tooltipBg, titleColor: tc.text, bodyColor: tc.text, borderColor: tc.tooltipBorder, borderWidth: 1 }
            },
            scales: {
                x: { grid: { color: tc.grid }, ticks: { color: tc.text } },
                y: { beginAtZero: true, grid: { color: tc.grid }, ticks: { color: tc.text, callback: v => '₹'+v.toLocaleString('en-IN') } }
            }
        }
    });
}

function initCategoryChart(period) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    const filtered = filterByPeriod(period);
    const labelMap = { week:'This week', month:'This month', year:'This year' };
    const desc = document.getElementById('categoryChartLabel');
    if (desc) desc.textContent = labelMap[period] || period;

    const totals = {};
    filtered.forEach(e => { const k = e.category_id||'x'; totals[k] = (totals[k]||0)+parseFloat(e.amount); });

    const labels = [], data = [], colors = [];
    Object.entries(totals).forEach(([id, total]) => {
        const cat = dashboardState.categories.find(c => c.id==id);
        labels.push(cat?.name||'Other'); data.push(total); colors.push(cat?.color||'#6b7280');
    });

    if (categoryChart) categoryChart.destroy();
    const tc = ThemeManager.getChartColors();

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 2,
            borderColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg').trim()
        }]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 600, easing: 'easeOutQuart' },
            plugins: { legend: { position:'bottom', labels: { color: tc.text } },
                tooltip: { backgroundColor: tc.tooltipBg, titleColor: tc.text, bodyColor: tc.text, borderColor: tc.tooltipBorder, borderWidth: 1 }
            }
        }
    });
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    document.getElementById('addExpenseBtn')?.addEventListener('click', () => {
        dashboardState.currentExpense = null;
        document.getElementById('expenseForm').reset();
        document.getElementById('expenseModalTitle').textContent = 'Add Expense';
        modal.open('expenseModal');
    });

    document.getElementById('expenseForm')?.addEventListener('submit', handleExpenseSubmit);

    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', e => {
            dashboardState.currentFilter = e.target.dataset.filter;
            renderExpenses();
            document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
        });
    });

    document.getElementById('trendFilterBtns')?.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            dashboardState.trendChartFilter = e.target.dataset.chartFilter;
            document.getElementById('trendFilterBtns').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            initExpenseChart(dashboardState.trendChartFilter);
        });
    });

    document.getElementById('categoryFilterBtns')?.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            dashboardState.categoryChartFilter = e.target.dataset.chartFilter;
            document.getElementById('categoryFilterBtns').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            initCategoryChart(dashboardState.categoryChartFilter);
        });
    });

    // Budget edit button + form
    document.getElementById('editBudgetBtn')?.addEventListener('click', () => {
        const input = document.getElementById('monthlyBudgetInput');
        if (input && dashboardState.budgetData?.monthly_budget) {
            input.value = dashboardState.budgetData.monthly_budget;
        }
        modal.open('budgetModal');
    });

    document.getElementById('budgetForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const val = parseFloat(document.getElementById('monthlyBudgetInput').value);
        if (isNaN(val) || val < 0) return;
        try {
            await utils.apiRequest('/personal_expense/api/budget.php', {
                method: 'POST', body: JSON.stringify({ monthly_budget: val })
            });
            modal.close('budgetModal');
            await loadBudgetData();
            loadMLSuggestions();
            utils.showAlert('Monthly budget updated!', 'success');
        } catch (err) {
            utils.showAlert(err.message, 'error');
        }
    });

    // ML refresh
    document.getElementById('refreshSuggestions')?.addEventListener('click', async function() {
        this.disabled = true; this.innerHTML = '🔄 Analyzing...';
        await loadMLSuggestions();
        this.disabled = false; this.innerHTML = '🔄 Refresh';
        utils.showAlert('Insights refreshed', 'success');
    });
}

// ============================================================================
// EXPENSE CRUD
// ============================================================================

async function handleExpenseSubmit(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const data = { amount: fd.get('amount'), category_id: fd.get('category_id'),
        description: fd.get('description'), expense_date: fd.get('expense_date') };
    try {
        const url = dashboardState.currentExpense
            ? `/personal_expense/api/expenses.php?id=${dashboardState.currentExpense}`
            : '/personal_expense/api/expenses.php';
        await utils.apiRequest(url, { method: dashboardState.currentExpense?'PUT':'POST', body: JSON.stringify(data) });
        modal.close('expenseModal');
        await loadExpenses();
        renderExpenses(); updateStats(); initCharts(); loadBudgetData(); loadMLSuggestions();
        utils.showAlert(dashboardState.currentExpense ? 'Expense updated' : 'Expense added', 'success');
    } catch (err) { utils.showAlert(err.message, 'error'); }
}

async function editExpense(id) {
    const exp = dashboardState.expenses.find(e => e.id==id);
    if (!exp) return;
    dashboardState.currentExpense = id;
    document.getElementById('amount').value = exp.amount;
    document.getElementById('category_id').value = exp.category_id;
    document.getElementById('description').value = exp.description;
    document.getElementById('expense_date').value = exp.expense_date;
    document.getElementById('expenseModalTitle').textContent = 'Edit Expense';
    modal.open('expenseModal');
}

async function deleteExpense(id) {
    if (!confirm('Delete this expense?')) return;
    try {
        await utils.apiRequest(`/personal_expense/api/expenses.php?id=${id}`, { method:'DELETE' });
        await loadExpenses();
        renderExpenses(); updateStats(); initCharts(); loadBudgetData(); loadMLSuggestions();
        utils.showAlert('Expense deleted', 'success');
    } catch (err) { utils.showAlert(err.message, 'error'); }
}

function getCategoryIcon(icon) {
    return { 'utensils':'🍴','car':'🚗','shopping-bag':'🛍️','film':'🎬','file-text':'📄','heart':'❤️','book':'📚','tag':'🏷️' }[icon] || '🏷️';
}

// ============================================================================
// ML SUGGESTIONS (2 insights + 2 recommendations, priority-aware)
// ============================================================================

async function loadMLSuggestions() {
    try {
        if (dashboardState.expenses.length === 0) return;
        const data = await utils.apiRequest('/personal_expense/api/ml_suggestions.php');
        if (data.success) { dashboardState.mlSuggestions = data; renderMLSuggestions(); }
    } catch (e) { console.error('ML load failed:', e); }
}

function renderMLSuggestions() {
    const card = document.getElementById('mlSuggestionsCard');
    const content = document.getElementById('mlSuggestionsContent');
    if (!card || !content || !dashboardState.mlSuggestions) return;

    const { insights, recommendations } = dashboardState.mlSuggestions;
    card.style.display = 'block';
    let html = '';

    // Insights section (max 2)
    if (insights && insights.length > 0) {
        html += `<div class="ml-section">
            <h4 class="ml-section-title"><span class="ml-section-icon">💡</span> Key Insights</h4>
            <div class="ml-suggestions-grid">${insights.map(renderInsightCard).join('')}</div>
        </div>`;
    }

    // Recommendations section (max 2)
    if (recommendations && recommendations.length > 0) {
        html += `<div class="ml-section">
            <h4 class="ml-section-title"><span class="ml-section-icon">🎯</span> Recommendations</h4>
            <div class="ml-suggestions-grid">${recommendations.map(renderRecommendation).join('')}</div>
        </div>`;
    }

    if (!html) {
        html = `<div class="ml-empty-state"><div class="ml-empty-state-icon">📊</div>
            <div class="ml-empty-state-message">Keep tracking! Insights appear once we have enough data.</div></div>`;
    }

    content.innerHTML = html;
}

function renderInsightCard(item) {
    const icons = { spending_pattern:'📈', trend_prediction:'📊', overall_prediction:'🔮' };
    const sev = item.severity || 'info';
    return `<div class="ml-insight-card">
        <div class="ml-insight-header">
            <div class="ml-insight-type">
                <span class="ml-insight-icon">${icons[item.type]||'💡'}</span>
                <span>${item.category}</span>
            </div>
            <span class="ml-insight-severity ${sev}">${sev}</span>
        </div>
        <div class="ml-insight-message">${item.message}</div>
    </div>`;
}

function renderRecommendation(rec) {
    const icons = { reduce_spending:'💰', set_budget:'🎯', positive_feedback:'✨' };
    const pri = rec.priority || 'medium';
    const priBadge = { high:'🔴', medium:'🟡', low:'🟢' };
    let details = '';
    if (rec.potential_savings) {
        details = `<div class="ml-insight-details">
            <div class="ml-metric"><span class="ml-metric-label">Overspend</span><span class="ml-metric-value">${rec.overspend_percent||0}%</span></div>
            <div class="ml-metric"><span class="ml-metric-label">Save up to</span><span class="ml-metric-value">₹${rec.potential_savings.toLocaleString('en-IN')}/mo</span></div>
        </div>`;
    } else if (rec.suggested_budget) {
        details = `<div class="ml-insight-details">
            <div class="ml-metric"><span class="ml-metric-label">Suggested Budget</span><span class="ml-metric-value">₹${rec.suggested_budget.toLocaleString('en-IN')}/mo</span></div>
        </div>`;
    }
    return `<div class="ml-recommendation">
        <div class="ml-recommendation-header">
            <div class="ml-insight-type">
                <span class="ml-insight-icon">${icons[rec.type]||'🎯'}</span>
                <span class="ml-recommendation-title">${rec.category}</span>
            </div>
            <span class="ml-recommendation-priority ${pri}">${priBadge[pri]||''} ${pri}</span>
        </div>
        <div class="ml-recommendation-message">${rec.message}</div>
        ${details}
    </div>`;
}

// ============================================================================
// INIT + GLOBALS
// ============================================================================

document.addEventListener('DOMContentLoaded', initDashboard);
window.addEventListener('themeChanged', () => { if (expensesChart || categoryChart) initCharts(); });
window.editExpense = editExpense;
window.deleteExpense = deleteExpense;

// ============================================================================
// AI AUTO-PREDICT CATEGORY (preserved)
// ============================================================================

let predictDebounceTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    const descInput = document.getElementById('description');
    const amtInput = document.getElementById('amount');
    const catSelect = document.getElementById('category_id');
    if (!descInput || !catSelect) return;

    const badge = document.createElement('div');
    badge.id = 'aiPredictionBadge';
    badge.className = 'ai-prediction-badge';
    badge.style.display = 'none';
    const fg = catSelect.closest('.form-group');
    if (fg) { fg.style.position = 'relative'; fg.appendChild(badge); }

    descInput.addEventListener('input', () => {
        const desc = descInput.value.trim(), amt = parseFloat(amtInput?.value)||0;
        if (predictDebounceTimer) clearTimeout(predictDebounceTimer);
        if (desc.length < 3) { badge.style.display = 'none'; return; }
        predictDebounceTimer = setTimeout(() => predictCategory(desc, amt), 400);
    });

    if (amtInput) {
        amtInput.addEventListener('input', () => {
            const desc = descInput.value.trim();
            if (desc.length >= 3) {
                if (predictDebounceTimer) clearTimeout(predictDebounceTimer);
                predictDebounceTimer = setTimeout(() => predictCategory(desc, parseFloat(amtInput.value)||0), 400);
            }
        });
    }

    catSelect.addEventListener('change', () => { catSelect.dataset.userSelected = 'true'; });

    document.getElementById('addExpenseBtn')?.addEventListener('click', () => {
        delete catSelect.dataset.userSelected;
        badge.style.display = 'none';
    });
});

async function predictCategory(description, amount) {
    const badge = document.getElementById('aiPredictionBadge');
    const catSelect = document.getElementById('category_id');
    if (!badge || !catSelect) return;

    badge.style.display = 'flex';
    badge.innerHTML = '<span class="ai-badge-icon">🤖</span> <span class="ai-badge-text">Predicting...</span>';
    badge.className = 'ai-prediction-badge loading';

    try {
        const resp = await fetch('/personal_expense/api/predict_category.php', {
            method: 'POST', headers: { 'Content-Type':'application/json' },
            body: JSON.stringify({ description, amount })
        });
        const data = await resp.json();
        if (data.error) { badge.style.display = 'none'; return; }

        const predicted = data.predicted_category;
        const conf = (data.confidence * 100).toFixed(0);
        const match = Array.from(catSelect.options).find(o => o.textContent.toLowerCase().trim() === predicted.toLowerCase().trim());
        if (match && !catSelect.dataset.userSelected) catSelect.value = match.value;

        const cls = conf >= 80 ? 'high' : conf >= 60 ? 'medium' : 'low';
        badge.className = `ai-prediction-badge ${cls}`;
        badge.innerHTML = `<span class="ai-badge-icon">🤖</span><span class="ai-badge-text">AI suggests: <strong>${predicted}</strong> (${conf}% confident)</span>`;
        badge.style.display = 'flex';
    } catch (e) {
        badge.style.display = 'none';
    }
}