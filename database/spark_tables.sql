-- ============================================================
-- Spark Analytics Summary Tables
-- Run this in phpMyAdmin or MySQL CLI before running Spark
-- Database: personal_expense_tracker
-- ============================================================

USE personal_expense_tracker;

-- -------------------------------------------------------
-- 1. Monthly Summary — aggregated monthly totals per user
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS monthly_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    avg_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_amount DECIMAL(10, 2) DEFAULT 0,
    min_amount DECIMAL(10, 2) DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_year_month (user_id, year, month),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 2. Category Summary — category-wise spending per user/month
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS category_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_color VARCHAR(7) DEFAULT '#6366f1',
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    percentage DECIMAL(5, 2) NOT NULL DEFAULT 0,
    avg_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_year_month (user_id, year, month),
    INDEX idx_category (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 3. Trend Summary — weekly / monthly / yearly trends
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS trend_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    period_type ENUM('weekly', 'monthly', 'yearly') NOT NULL,
    period_label VARCHAR(50) NOT NULL,
    period_start DATE DEFAULT NULL,
    period_end DATE DEFAULT NULL,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    avg_daily DECIMAL(10, 2) DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_period (user_id, period_type),
    INDEX idx_period_type (period_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 4. Spark Insights — smart spending insights (2 per user)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS spark_insights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) DEFAULT NULL,
    message TEXT NOT NULL,
    severity ENUM('info', 'warning', 'success', 'critical') DEFAULT 'info',
    score DECIMAL(8, 2) DEFAULT 0,
    metadata JSON DEFAULT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 5. Spark Recommendations — smart recommendations (2 per user)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS spark_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rec_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) DEFAULT NULL,
    message TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    potential_savings DECIMAL(10, 2) DEFAULT 0,
    current_spending DECIMAL(10, 2) DEFAULT 0,
    metadata JSON DEFAULT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- Verification: Show created tables
-- -------------------------------------------------------
SHOW TABLES LIKE '%summary%';
SHOW TABLES LIKE 'spark_%';
