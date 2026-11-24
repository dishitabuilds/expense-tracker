# Expense Tracker

**Live app:** [expenses-tracker.kesug.com](https://expenses-tracker.kesug.com/)

> **Repository availability:** This repository currently contains only this README.
> The PHP application, database SQL, Python/Flask ML code, Spark jobs and screenshots
> described below are not included in a fresh clone. The following technical
> documentation describes the full project; its setup steps require the separate
> application source and assets. A live deployment does not supply those files.

<p align="center">
  <img src="https://img.shields.io/badge/PHP-8.x-777BB4?style=for-the-badge&logo=php&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache%20Spark-3.5-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white" />
  <img src="https://img.shields.io/badge/scikit--learn-1.3-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" />

</p>

<h1 align="center">💰 AI-Powered Personal Expense Tracker</h1>

<p align="center">
  <strong>A full-stack, intelligent expense management system that combines a modern PHP web application with machine learning–driven category prediction, smart spending insights, and Apache Spark–powered big data analytics.</strong>
</p>

<p align="center">
  <a href="https://expenses-tracker.kesug.com/">🌐 Live Demo</a> &nbsp;·&nbsp;
  <a href="#-quick-start">🚀 Quick Start</a> &nbsp;·&nbsp;
  <a href="#-ml-pipeline">🤖 ML Pipeline</a> &nbsp;·&nbsp;
  <a href="#-apache-spark-analytics">⚡ Spark Analytics</a>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [ML Pipeline](#-ml-pipeline)
- [Apache Spark Analytics](#-apache-spark-analytics)
- [Authentication System](#-authentication-system)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Screenshots](#-screenshots)
- [License](#-license)

---

## 🔍 Overview

The **AI-Powered Personal Expense Tracker** is a comprehensive financial management application built as a major academic project. It goes far beyond basic CRUD operations, integrating a complete machine learning pipeline for automatic expense categorization and a distributed Apache Spark engine for large-scale spending analytics.

### What Makes This Different?

| Traditional Trackers | This Project |
|---|---|
| Manual category selection | **AI auto-predicts** category from description |
| Static reports | **Spark-powered** real-time analytics & trend detection |
| Basic password login | **OTP-based authentication** with rate limiting |
| No spending intelligence | **Smart Insights Engine** with anomaly detection |
| Single-table summaries | **Multi-dimensional** weekly/monthly/yearly trend analysis |

---

## ✨ Key Features

### 🧠 AI & Machine Learning
- **Automatic Category Prediction** — TF-IDF + Logistic Regression model predicts expense categories from text descriptions with high accuracy
- **Smart Spending Insights** — Statistical anomaly detection using IQR method, trend analysis, and savings recommendations
- **Confidence Scoring** — Each prediction returns probability scores across all 8 categories
- **Batch Prediction API** — Process multiple expenses in a single API call

### ⚡ Big Data Analytics (Apache Spark)
- **Monthly Summary Aggregation** — Per-user monthly totals, averages, min/max breakdowns
- **Category-wise Analysis** — Spending distribution with percentage calculations using Spark window functions
- **Trend Detection** — Weekly (ISO 8601), monthly, and yearly trend computation with daily burn rates
- **Spike Detection** — Month-over-month spending surge alerts (>25% threshold)
- **End-of-Month Projections** — Predictive spending forecasts based on current daily rate vs. last month
- **Weekend vs. Weekday Patterns** — Spending habit analysis with actionable savings recommendations

### 📊 Financial Dashboard
- **Real-time Metrics** — Total spending, average monthly, transaction count, top category
- **Interactive Charts** — 7-day expense trends and category distribution (Chart.js)
- **Recent Transactions** — Live feed with category badges and timestamps
- **Monthly Budget Tracking** — Set per-category budgets with visual progress bars and overspend alerts

### 🔐 Authentication & Security
- **Dual Login Modes** — Traditional password + Email OTP (one-time password)
- **Guest Mode** — Try the app without registration (localStorage-based)
- **Rate Limiting** — Account lockout after 5 failed attempts (15-minute cooldown)
- **OTP Rate Limiting** — Max 3 OTP requests per 10-minute window
- **Remember Me** — Secure 30-day persistent sessions with hashed tokens
- **CSRF Protection** — Token-based protection on all forms

### 💼 Expense Management
- Full **CRUD operations** — Add, edit, delete, search expenses
- **Advanced Filtering** — By category, date range (today, week, month, year, custom), and search text
- **Sortable Columns** — Click headers to sort by date or amount
- **Custom Categories** — Create, edit, and color-code your own categories with icons
- **Notes Field** — Add optional notes to any transaction

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **PHP 8.x** | Server-side logic, RESTful API |
| **MySQL 8.0** | Relational database (XAMPP) |
| **Python 3.11** | ML pipeline & Spark analytics |
| **Flask 3.0** | ML prediction REST API server |
| **Apache Spark 3.5** | Distributed data processing |
| **PySpark** | Spark's Python API |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / CSS3** | Semantic markup, modern styling |
| **Vanilla JavaScript** | Dashboard interactivity, AJAX calls |
| **Chart.js** | Financial data visualization |
| **Lucide Icons** | Consistent iconography |

### ML & Data Science
| Library | Purpose |
|---|---|
| **scikit-learn** | Logistic Regression, TF-IDF, model evaluation |
| **pandas / NumPy** | Data manipulation & analysis |
| **matplotlib / seaborn** | EDA visualizations |
| **WordCloud** | Text feature visualization |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Browser)                          │
│   Dashboard  │  Expenses  │  Categories  │  Reports  │  Spark UI  │
└──────┬───────┴─────┬──────┴──────┬───────┴─────┬─────┴──────┬─────┘
       │             │            │             │            │
       ▼             ▼            ▼             ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PHP REST API Layer                          │
│  auth.php │ expenses.php │ categories.php │ budget.php │ spark_.php│
└──────┬────┴──────┬───────┴───────┬────────┴─────┬──────┴─────┬────┘
       │           │               │              │            │
       ▼           ▼               ▼              ▼            ▼
┌──────────────┐ ┌────────────────────┐ ┌──────────────────────────┐
│   MySQL DB   │ │  Flask ML API      │ │  Apache Spark Engine     │
│              │ │  (:5000)           │ │  (PySpark + JDBC)        │
│  • users     │ │  • /predict        │ │  • Monthly Summary       │
│  • expenses  │ │  • /predict/batch  │ │  • Category Summary      │
│  • categories│ │  • /insights       │ │  • Trend Analysis        │
│  • budgets   │ │  • /health         │ │  • Smart Insights        │
│  • spark_*   │ │                    │ │  • Recommendations       │
└──────────────┘ └────────────────────┘ └──────────────────────────┘
                          │                         │
                          ▼                         │
                 ┌─────────────────┐                │
                 │  Trained Models │                 │
                 │  (.pkl files)   │◄────────────────┘
                 │  • category_model│        (reads MySQL via JDBC,
                 │  • tfidf_vectorizer│       writes summaries back)
                 │  • scaler        │
                 │  • label_encoder │
                 └─────────────────┘
```

---

## 🚀 Full application setup (source required)

### Prerequisites

- [XAMPP](https://www.apachefriends.org/) (Apache + MySQL + PHP)
- [Python 3.11+](https://www.python.org/downloads/)
- [Apache Spark 3.5](https://spark.apache.org/downloads.html) *(optional, for analytics)*
- [Java 11+](https://adoptium.net/) *(required for Spark)*

### 1. Clone & Setup

```bash
git clone https://github.com/dishitabuilds/expense-tracker.git
# Place in your XAMPP htdocs directory as 'personal_expense'
```

### 2. Database Setup

Open **phpMyAdmin** (`http://localhost/phpmyadmin`) and run:

```sql
-- Create database and tables
SOURCE C:/xampp/htdocs/personal_expense/database/schema.sql;

-- Run auth migration (adds OTP + rate limiting columns)
SOURCE C:/xampp/htdocs/personal_expense/database/migrate_auth.sql;

-- Add Spark analytics tables
SOURCE C:/xampp/htdocs/personal_expense/database/spark_tables.sql;
```

Or import each SQL file via phpMyAdmin's Import tab.

### 3. Configure Database

Edit `config/database.php` if your MySQL credentials differ:

```php
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');  // Your MySQL password
define('DB_NAME', 'personal_expense_tracker');
```

### 4. Install ML Dependencies

```bash
cd ml
pip install -r requirements.txt
```

### 5. Train the ML Model

```bash
python expense_ai.py
```

This will:
- Load and merge the 602-record training dataset
- Perform exploratory data analysis with 8 visualizations
- Train a Logistic Regression model with TF-IDF features
- Run 5-fold cross-validation and regularization analysis
- Save 4 `.pkl` model files to `ml/models/`

### 6. Start the Prediction API

```bash
python predict_api.py
# Server starts at http://localhost:5000
```

### 7. Launch the App

1. Start **Apache** and **MySQL** from XAMPP Control Panel
2. Navigate to: **`http://localhost/personal_expense`**

---

## 🤖 ML Pipeline

### Model Architecture

```
Input: (description: str, amount: float)
  │
  ├── Text Branch ──► TF-IDF Vectorizer (500 features, 1-2 ngrams)
  │                    └── Sublinear TF scaling, English stop words removed
  │
  └── Numeric Branch ► StandardScaler (z-score normalization)
  │
  ▼
scipy.sparse.hstack → Combined Feature Matrix (501 features)
  │
  ▼
Logistic Regression (multinomial, L-BFGS solver, C=1.0)
  │
  ▼
Output: Predicted Category + Confidence Scores (8 classes)
```

### Training Details

| Parameter | Value |
|---|---|
| **Dataset** | 602 expense records across 8 categories |
| **Features** | TF-IDF text (500) + normalized amount (1) |
| **Model** | Logistic Regression (multinomial) |
| **Train/Test Split** | 80% / 20% (stratified) |
| **Solver** | L-BFGS with max 1000 iterations |
| **Cross-Validation** | 5-fold Stratified K-Fold |
| **Regularization** | C=1.0 (analyzed across [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]) |

### Categories Predicted

| # | Category | Description |
|---|---|---|
| 1 | 🍽️ Food & Dining | Restaurants, groceries, food delivery |
| 2 | 🚗 Transportation | Uber, fuel, public transit |
| 3 | 🛍️ Shopping | Clothing, electronics, online orders |
| 4 | 🎬 Entertainment | Movies, subscriptions, events |
| 5 | 📄 Bills & Utilities | Electricity, internet, phone bills |
| 6 | 🏥 Healthcare | Pharmacy, doctor visits, insurance |
| 7 | 📚 Education | Tuition, books, courses |
| 8 | 🏷️ Other | Miscellaneous expenses |

### EDA Visualizations Generated

The pipeline generates **8 publication-quality visualizations** during training:

| Visualization | Description |
|---|---|
| `class_distribution.png` | Bar chart of expense category distribution |
| `word_cloud.png` | Word cloud from expense descriptions |
| `amount_distribution.png` | Box plot of amounts per category |
| `monthly_spending.png` | Monthly spending trend with area fill |
| `spending_trends.png` | Stacked bar — monthly spending by category |
| `category_pie.png` | Donut chart of total spending distribution |
| `confusion_matrix.png` | Heatmap of model prediction performance |
| `cross_validation.png` | CV scores + regularization analysis |

### Model Artifacts

After training, 4 serialized model files are saved to `ml/models/`:

| File | Purpose |
|---|---|
| `category_model.pkl` | Trained Logistic Regression classifier |
| `tfidf_vectorizer.pkl` | Fitted TF-IDF vectorizer (vocabulary) |
| `scaler.pkl` | Fitted StandardScaler (mean, std) |
| `label_encoder.pkl` | Category label ↔ integer mapping |

### Smart Insights Engine

The `SmartInsightsEngine` class (`ml/smart_insights.py`) performs 7 types of statistical analysis:

1. **High Spending Alerts** — Flags categories >1.5σ above mean
2. **Unusual Transaction Detection** — IQR-based outlier detection per category
3. **Monthly Trend Analysis** — Detects rising/falling spending patterns
4. **Category Dominance** — Alerts when a single category exceeds 30% of total
5. **Weekend vs. Weekday Patterns** — Compares average daily spending
6. **Savings Recommendations** — Suggests 10–20% reductions on discretionary categories
7. **Spending Velocity** — Monitors transaction frequency for impulse detection

---

## ⚡ Apache Spark Analytics

### Overview

The Spark module (`spark/spark_analytics.py`) connects to the MySQL database via JDBC, ingests raw expense data into distributed DataFrames, and computes 5 types of analytics which are written back to dedicated summary tables.

### Setup

1. **Install PySpark:**
   ```bash
   cd spark
   pip install -r requirements.txt
   ```

2. **Download MySQL JDBC driver:**
   - Get `mysql-connector-j-8.x.x.jar` from [MySQL Downloads](https://dev.mysql.com/downloads/connector/j/)
   - Place in Spark's `jars/` directory or specify via `--jars` flag

3. **Run the pipeline:**
   ```bash
   spark-submit --jars <path-to-mysql-connector-j.jar> spark_analytics.py
   ```
   
   Or use the convenience script:
   ```bash
   run_spark.bat
   ```

### Analytics Computed

#### 1. Monthly Summary (`monthly_summary` table)
- Per-user monthly aggregation: total, average, min, max, transaction count
- Uses Spark UDFs for month name mapping

#### 2. Category Summary (`category_summary` table)
- Category-wise spending per user per month
- Window functions calculate percentage share within each user-month

#### 3. Trend Summary (`trend_summary` table)
- **Weekly:** ISO 8601 week-based trends (last 12 weeks) with date range labels
- **Monthly:** Calendar month trends (last 12 months)
- **Yearly:** Full calendar year comparisons
- Includes average daily burn rate at each granularity

#### 4. Smart Insights (`spark_insights` table)
- **Spending Spike Detection** — Compares current month vs. previous month per category; alerts on >25% increases with severity levels (`warning` at 25%+, `critical` at 75%+)
- **End-of-Month Projection** — Projects total spending from daily burn rate and compares against last month's actual total

#### 5. Smart Recommendations (`spark_recommendations` table)
- **Category Optimization** — Identifies highest growth category and suggests capped budgets (110% of last month)
- **Weekend vs. Weekday Pattern** — Analyzes spending ratio and estimates monthly savings potential

### Spark Architecture

```
MySQL (XAMPP)                Apache Spark (local[*])
┌────────────┐    JDBC     ┌───────────────────────────┐
│  expenses  │────────────►│  DataFrame: expenses_df   │
│  categories│────────────►│  DataFrame: categories_df │
└────────────┘             └───────────┬───────────────┘
                                       │
                           ┌───────────▼───────────────┐
                           │   Spark Transformations   │
                           │   • groupBy / agg         │
                           │   • Window functions      │
                           │   • UDFs                  │
                           │   • Joins                 │
                           └───────────┬───────────────┘
                                       │
                           ┌───────────▼───────────────┐
MySQL (XAMPP)    JDBC       │   Computed DataFrames     │
┌────────────────┐◄────────│   • monthly_summary       │
│ monthly_summary│         │   • category_summary      │
│ category_summary│        │   • trend_summary         │
│ trend_summary  │         │   • spark_insights        │
│ spark_insights │         │   • spark_recommendations │
│ spark_recommen.│         └───────────────────────────┘
└────────────────┘
```

---

## 🔐 Authentication System

The application supports **three authentication modes**:

### 1. Password Login
Traditional email + password authentication with:
- **bcrypt** password hashing (`PASSWORD_DEFAULT`)
- **Brute-force protection** — 5 failed attempts → 15-minute lockout
- **Remember Me** — 30-day persistent session using SHA-256 hashed tokens

### 2. Email OTP Login
Passwordless authentication flow:
1. User enters email → system generates 6-digit OTP
2. OTP is hashed with bcrypt and stored in the database
3. OTP expires after a configurable window (default: 10 minutes)
4. Rate limited to 3 sends per 10-minute window

### 3. Guest Mode
- No registration required
- Data stored in **localStorage** (browser-only)
- Full dashboard access with limited features
- Seamless upgrade path to registered account

---

## 📡 API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth.php?action=signup` | Register new user |
| `POST` | `/api/auth.php?action=login` | Password login |
| `POST` | `/api/auth.php?action=send_otp` | Send OTP to email |
| `POST` | `/api/auth.php?action=verify_otp` | Verify OTP & login |
| `POST` | `/api/auth.php?action=resend_otp` | Resend OTP |
| `GET` | `/api/auth.php?action=logout` | Logout & clear session |
| `GET` | `/api/auth.php?action=guest` | Activate guest mode |

### Expense Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/expenses.php` | Get all expenses (with filters) |
| `POST` | `/api/expenses.php` | Create new expense |
| `PUT` | `/api/expenses.php?id={id}` | Update expense |
| `DELETE` | `/api/expenses.php?id={id}` | Delete expense |

### Category Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/categories.php` | List all categories |
| `POST` | `/api/categories.php` | Create category |
| `PUT` | `/api/categories.php?id={id}` | Update category |
| `DELETE` | `/api/categories.php?id={id}` | Delete category |

### Budget Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/budget.php` | Get budget data |
| `POST` | `/api/budget.php` | Set / update budget |

### ML Prediction API (Flask — Port 5000)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check & model info |
| `POST` | `/predict` | Predict category (single) |
| `POST` | `/predict/batch` | Batch category prediction |
| `GET` | `/insights` | Demo insights (training data) |
| `POST` | `/insights` | Custom data insights |

#### Example: Predict Category

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"description": "swiggy lunch", "amount": 350}'
```

```json
{
  "predicted_category": "Food",
  "confidence": 0.9234,
  "all_probabilities": {
    "Food": 0.9234,
    "Shopping": 0.0312,
    "Entertainment": 0.0198,
    "...": "..."
  }
}
```

### Spark Analytics Endpoints (PHP)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/spark_summary.php?type=monthly` | Monthly aggregated data |
| `GET` | `/api/spark_summary.php?type=category` | Category breakdown |
| `GET` | `/api/spark_summary.php?type=trends` | Spending trends |
| `GET` | `/api/spark_summary.php?type=insights` | Spark-generated insights |
| `GET` | `/api/spark_summary.php?type=recommendations` | Smart recommendations |

---

## 🗄 Database Schema

### Core Tables

```sql
users           — User accounts with OTP & rate-limit fields
├── id, username, email, password
├── otp_code, otp_expires_at, otp_attempts, otp_last_sent_at
├── login_attempts, login_locked_until
└── remember_token, remember_expires_at

categories      — User-defined expense categories
├── id, user_id (FK), name, color, icon
└── budget (per-category monthly budget)

expenses        — Individual expense transactions
├── id, user_id (FK), category_id (FK)
├── amount, description, notes
└── expense_date, created_at, updated_at
```

### Spark-Generated Tables

```sql
monthly_summary       — Monthly totals per user
category_summary      — Category-wise spending per user/month
trend_summary         — Weekly/monthly/yearly trends
spark_insights        — AI-generated spending insights
spark_recommendations — Personalized savings recommendations
```

---

## 📂 Project Structure

```
expense-tracker/
│
├── api/                          # RESTful API endpoints (PHP)
│   ├── auth.php                  # Authentication (signup, login, OTP, guest)
│   ├── expenses.php              # Expense CRUD operations
│   ├── categories.php            # Category management
│   ├── budget.php                # Budget management
│   ├── budget_alerts.php         # Budget overspend alerts
│   ├── ml_suggestions.php        # ML-powered suggestions (PHP → Flask bridge)
│   ├── predict_category.php      # Category prediction proxy
│   └── spark_summary.php         # Spark analytics data API
│
├── assets/
│   ├── css/                      # Stylesheets
│   │   ├── style.css             # Global styles (Shadcn-inspired design system)
│   │   ├── auth.css              # Authentication pages
│   │   ├── dashboard.css         # Dashboard layout
│   │   ├── expenses.css          # Expense management
│   │   ├── categories.css        # Category management
│   │   ├── reports.css           # Reports page
│   │   └── spark_analytics.css   # Spark analytics UI
│   └── js/                       # Client-side JavaScript
│       ├── dashboard.js          # Dashboard logic & charts
│       ├── expenses.js           # Expense CRUD & filtering
│       ├── categories.js         # Category management
│       ├── reports.js            # Reports & visualizations
│       ├── guest.js              # Guest mode (localStorage)
│       ├── spark_analytics.js    # Spark analytics UI
│       ├── main.js               # Shared utilities
│       └── theme.js              # Dark/light theme toggle
│
├── config/                       # Server configuration
│   ├── database.php              # MySQL connection (PDO)
│   ├── session.php               # Session management & auth helpers
│   ├── mail.php                  # Email (OTP delivery) configuration
│   └── sidebar.php               # Shared navigation sidebar component
│
├── database/                     # SQL schema & migrations
│   ├── schema.sql                # Base schema (users, categories, expenses)
│   ├── migrate_auth.sql          # OTP & rate-limiting columns
│   ├── spark_tables.sql          # Spark analytics summary tables
│   ├── add_budget_column.sql     # Budget field migration
│   ├── add_budget_alerts.sql     # Alert tables
│   ├── add_notes_column.sql      # Notes field migration
│   ├── complete_update.sql       # Consolidated migration
│   └── import_csv_data.sql       # Sample data import
│
├── ml/                           # Machine Learning module
│   ├── expense_ai.py             # Full ML pipeline (EDA → Train → Evaluate → Save)
│   ├── predict_api.py            # Flask REST API for predictions
│   ├── smart_insights.py         # Statistical insights engine (7 analysis types)
│   ├── requirements.txt          # Python dependencies
│   ├── dataset/                  # Training data
│   │   ├── expense_dataset1.csv  # 302 records
│   │   └── expense_dataset2.csv  # 300 records
│   ├── models/                   # Serialized trained models
│   │   ├── category_model.pkl
│   │   ├── tfidf_vectorizer.pkl
│   │   ├── scaler.pkl
│   │   └── label_encoder.pkl
│   └── visualizations/           # Generated EDA charts (8 plots)
│
├── spark/                        # Apache Spark analytics module
│   ├── spark_analytics.py        # Main Spark pipeline (5 analytics)
│   ├── generate_sample_data.py   # Test data generator
│   ├── run_spark.bat             # Windows launch script
│   └── requirements.txt          # PySpark dependencies
│
├── index.php                     # Login page (split-screen UI)
├── signup.php                    # Registration page
├── dashboard.php                 # Main dashboard
├── expenses.php                  # Expense management page
├── categories.php                # Category management page
├── reports.php                   # Reports & analytics page
├── spark_analytics.php           # Spark analytics dashboard
├── migrate_account.php           # Account migration utility
│
├── Dockerfile                    # Docker deployment config
├── .htaccess                     # Apache URL rewriting
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## 🔒 Security

| Feature | Implementation |
|---|---|
| **Password Hashing** | bcrypt via `password_hash()` (cost factor 10) |
| **SQL Injection Prevention** | Prepared statements on all queries |
| **XSS Protection** | Output escaping with `htmlspecialchars()` |
| **CSRF Protection** | Token-based validation on forms |
| **Session Security** | Secure session configuration, regeneration on login |
| **Rate Limiting** | Login (5 attempts / 15-min lock), OTP (3 sends / 10-min window) |
| **OTP Security** | Hashed storage (bcrypt), configurable expiry, auto-invalidation |
| **Remember Me** | SHA-256 hashed tokens with 30-day expiry |
| **Input Validation** | Server-side + client-side validation on all inputs |

---

## 📸 Screenshots

> The application features a modern, dark-themed UI inspired by Shadcn design principles with glassmorphism effects, smooth animations, and responsive layouts.

### Pages

| Page | Description |
|---|---|
| **Login** | Split-screen layout with password + OTP tabs |
| **Dashboard** | Financial overview with charts, metrics, and AI insights |
| **Expenses** | Searchable, filterable transaction table with inline editing |
| **Categories** | Color-coded category cards with budget progress bars |
| **Reports** | Date-range reports with exportable charts |
| **Spark Analytics** | Big data insights dashboard with trend visualizations |

---

## 🛣️ Roadmap

- [x] Core expense CRUD with categories
- [x] Interactive dashboard with Chart.js
- [x] ML-based category prediction
- [x] Smart spending insights engine
- [x] Apache Spark analytics pipeline
- [x] OTP-based authentication
- [x] Guest mode with localStorage
- [x] Monthly budget management
- [x] Dark/light theme toggle
- [ ] Recurring expenses
- [ ] Export to CSV / PDF
- [ ] Multi-currency support
- [ ] Mobile-responsive PWA
- [ ] Receipt OCR scanning

---

## 📄 License

No license file is currently committed in this repository. Confirm the intended
license before redistributing the project source.

## 👨‍💻 Author

Built with ❤️ as a major academic project — combining full-stack web development, machine learning, and big data analytics.

<p align="center">
  <sub>If you found this useful, consider giving it a ⭐</sub>
</p>
