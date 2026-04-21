<?php
/**
 * Sidebar Include
 * Reusable sidebar component with avatar, guest mode support
 * 
 * Usage: include 'config/sidebar.php';
 * Requires: $activePage variable set before including (e.g., $activePage = 'dashboard')
 */

$_sidebarUser = isLoggedIn() ? getCurrentUser() : null;
$_sidebarInitial = getUserInitial();
$_sidebarDisplayName = getDisplayName();
$_sidebarIsGuest = isGuest();
?>
<aside class="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-logo">💰 ExpenseTracker</div>
    </div>

    <nav class="sidebar-nav">
        <a href="dashboard.php" class="nav-item <?php echo ($activePage ?? '') === 'dashboard' ? 'active' : ''; ?>">
            <span class="nav-icon">📊</span>
            Dashboard
        </a>
        <a href="expenses.php" class="nav-item <?php echo ($activePage ?? '') === 'expenses' ? 'active' : ''; ?>">
            <span class="nav-icon">💳</span>
            Expenses
        </a>
        <a href="categories.php" class="nav-item <?php echo ($activePage ?? '') === 'categories' ? 'active' : ''; ?>">
            <span class="nav-icon">📁</span>
            Categories
        </a>
        <a href="reports.php" class="nav-item <?php echo ($activePage ?? '') === 'reports' ? 'active' : ''; ?>">
            <span class="nav-icon">📈</span>
            Reports
            <?php if ($_sidebarIsGuest): ?>
                <span style="font-size: 0.6rem; margin-left: 4px;">🔒</span>
            <?php endif; ?>
        </a>
        <a href="spark_analytics.php" class="nav-item <?php echo ($activePage ?? '') === 'spark' ? 'active' : ''; ?>">
            <span class="nav-icon">⚡</span>
            Spark Analytics
            <?php if ($_sidebarIsGuest): ?>
                <span style="font-size: 0.6rem; margin-left: 4px;">🔒</span>
            <?php endif; ?>
        </a>
    </nav>

    <div class="sidebar-footer">
        <div style="display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.75rem;">
            <div class="user-avatar <?php echo $_sidebarIsGuest ? 'guest' : ''; ?>">
                <?php echo htmlspecialchars($_sidebarInitial); ?>
            </div>
            <div>
                <div style="font-size: 0.8125rem; font-weight: 600; color: var(--text-primary);">
                    <?php echo htmlspecialchars($_sidebarDisplayName); ?>
                </div>
                <?php if ($_sidebarIsGuest): ?>
                    <div style="font-size: 0.6875rem; color: var(--text-tertiary);">Guest Mode</div>
                <?php else: ?>
                    <div style="font-size: 0.6875rem; color: var(--text-tertiary);">
                        <?php echo htmlspecialchars($_sidebarUser['email'] ?? ''); ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>
        <?php if ($_sidebarIsGuest): ?>
            <a href="index.php" class="btn btn-primary w-full btn-sm" style="margin-bottom: 0.375rem; text-decoration: none;">
                Sign In
            </a>
        <?php else: ?>
            <a href="api/auth.php?action=logout" class="btn btn-outline w-full btn-sm">
                Logout
            </a>
        <?php endif; ?>
    </div>
</aside>
