# Apache Spark Integration — Setup Guide

Complete step-by-step guide to install Apache Spark, connect to MySQL (XAMPP), and run the big data analytics pipeline for the Personal Expense Tracker.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install Java JDK](#2-install-java-jdk)
3. [Install Apache Spark](#3-install-apache-spark)
4. [Install Hadoop Winutils (Windows)](#4-install-hadoop-winutils-windows)
5. [Install MySQL JDBC Connector](#5-install-mysql-jdbc-connector)
6. [Install Python Dependencies](#6-install-python-dependencies)
7. [Create Summary Tables in MySQL](#7-create-summary-tables-in-mysql)
8. [Generate Sample Data (10K+ rows)](#8-generate-sample-data-10k-rows)
9. [Run Spark Analytics](#9-run-spark-analytics)
10. [Verify Results](#10-verify-results)
11. [Access the Dashboard](#11-access-the-dashboard)
12. [Troubleshooting](#12-troubleshooting)
13. [Project Folder Structure](#13-project-folder-structure)

---

## 1. Prerequisites

Before starting, ensure you have:

| Requirement       | Version           | Check Command              |
|-------------------|-------------------|----------------------------|
| XAMPP             | Any recent        | Open XAMPP Control Panel   |
| MySQL             | 5.7+ (via XAMPP)  | `mysql --version`          |
| Python            | 3.8+              | `python --version`         |
| pip               | Any recent        | `pip --version`            |
| Web Browser       | Chrome / Firefox  | —                          |

**Start XAMPP** → Make sure both **Apache** and **MySQL** are running.

---

## 2. Install Java JDK

Apache Spark requires Java. If you don't have it:

### Download

- Go to: https://adoptium.net/
- Download **JDK 17** (LTS) for Windows x64
- Run the installer

### Set Environment Variables

Open **System Properties** → **Environment Variables**:

1. **New System Variable:**
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Eclipse Adoptium\jdk-17.x.x-hotspot` (your actual path)

2. **Edit PATH** → Add:
   ```
   %JAVA_HOME%\bin
   ```

### Verify

```cmd
java -version
```

Expected output:
```
openjdk version "17.0.x" ...
```

---

## 3. Install Apache Spark

### Download

1. Go to: https://spark.apache.org/downloads.html
2. Choose:
   - Spark release: **3.5.1** (or latest 3.5.x)
   - Package type: **Pre-built for Apache Hadoop 3.3**
3. Download the `.tgz` file
4. Extract to `C:\spark` (use 7-Zip or WinRAR)

### Set Environment Variables

1. **New System Variable:**
   - Variable name: `SPARK_HOME`
   - Variable value: `C:\spark`

2. **Edit PATH** → Add:
   ```
   %SPARK_HOME%\bin
   ```

### Verify

```cmd
spark-submit --version
```

Expected output:
```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.5.1
      /_/
```

---

## 4. Install Hadoop Winutils (Windows)

Spark on Windows requires `winutils.exe`:

### Download

1. Go to: https://github.com/cdarlint/winutils
2. Download `winutils.exe` and `hadoop.dll` for **hadoop-3.3.x**

### Setup

1. Create folder: `C:\spark\hadoop\bin\`
2. Place `winutils.exe` and `hadoop.dll` inside

### Set Environment Variable

1. **New System Variable:**
   - Variable name: `HADOOP_HOME`
   - Variable value: `C:\spark\hadoop`

2. **Edit PATH** → Add:
   ```
   %HADOOP_HOME%\bin
   ```

---

## 5. Install MySQL JDBC Connector

Spark needs the MySQL JDBC driver to connect to your database.

### Download

1. Go to: https://dev.mysql.com/downloads/connector/j/
2. Select:
   - Operating System: **Platform Independent**
   - Download the `.zip` file
3. Extract and find `mysql-connector-j-8.x.x.jar`

### Install

Copy the JAR file to Spark's jars directory:

```cmd
copy mysql-connector-j-8.x.x.jar C:\spark\jars\
```

### Verify

```cmd
dir C:\spark\jars\mysql-connector-*.jar
```

You should see the connector JAR listed.

---

## 6. Install Python Dependencies

Open a terminal and run:

```cmd
cd C:\xampp\htdocs\personal_expense\spark
pip install -r requirements.txt
```

This installs:
- `pyspark==3.5.1` — Python Spark interface
- `mysql-connector-python==8.3.0` — For the data generator script

---

## 7. Create Summary Tables in MySQL

The Spark analytics pipeline writes results to 5 new MySQL tables. Create them first:

### Option A: phpMyAdmin

1. Open http://localhost/phpmyadmin
2. Select database: `personal_expense_tracker`
3. Go to **SQL** tab
4. Copy and paste the contents of `database/spark_tables.sql`
5. Click **Go**

### Option B: MySQL CLI

```cmd
cd C:\xampp\htdocs\personal_expense
C:\xampp\mysql\bin\mysql -u root < database\spark_tables.sql
```

### Tables Created

| Table | Purpose |
|-------|---------|
| `monthly_summary` | Monthly totals per user |
| `category_summary` | Category-wise spending per month |
| `trend_summary` | Weekly/Monthly/Yearly trends |
| `spark_insights` | AI spending insights (2 per user) |
| `spark_recommendations` | Smart recommendations (2 per user) |

---

## 8. Generate Sample Data (10K+ rows)

To demo Spark with a large dataset:

```cmd
cd C:\xampp\htdocs\personal_expense\spark
python generate_sample_data.py
```

This will:
- Create 3 test users (spark_user1, spark_user2, spark_user3)
- Generate 10,000 realistic expense records
- Distribute across 8 categories over 2 years
- Show a summary table when done

### Verify in phpMyAdmin

```sql
SELECT COUNT(*) FROM expenses;
-- Should show 10,000+ rows
```

---

## 9. Run Spark Analytics

### Option A: Using the batch file (recommended)

```cmd
cd C:\xampp\htdocs\personal_expense\spark
run_spark.bat
```

### Option B: Manual spark-submit

```cmd
cd C:\xampp\htdocs\personal_expense\spark
spark-submit --jars C:\spark\jars\mysql-connector-j-8.x.x.jar spark_analytics.py
```

### Expected Output

```
============================================================
  🚀 Expense Tracker — Spark Analytics Pipeline
============================================================
  Spark Session Created Successfully
  Spark Version: 3.5.1

📥 Reading data from MySQL...
  ✓ Loaded 'expenses': 10420 rows
  ✓ Loaded 'categories': 24 rows

📊 Computing Monthly Summary...
  → 72 monthly summary rows generated

📊 Computing Category Summary...
  → 412 category summary rows generated

📊 Computing Trend Summary...
  → 96 trend summary rows generated

🤖 Computing Smart Insights...
  → 6 insights generated

🤖 Computing Smart Recommendations...
  → 6 recommendations generated

📤 Writing results to MySQL...
  ✓ Written to 'monthly_summary' (mode=overwrite)
  ✓ Written to 'category_summary' (mode=overwrite)
  ✓ Written to 'trend_summary' (mode=overwrite)
  ✓ Written to 'spark_insights' (mode=overwrite)
  ✓ Written to 'spark_recommendations' (mode=overwrite)

============================================================
  ✅ Spark Analytics Pipeline Completed Successfully!
============================================================
```

---

## 10. Verify Results

### In phpMyAdmin

Run these queries to verify the data was written:

```sql
-- Monthly summary
SELECT * FROM monthly_summary ORDER BY year DESC, month DESC LIMIT 10;

-- Category breakdown
SELECT * FROM category_summary WHERE year = 2026 AND month = 4;

-- Trends
SELECT * FROM trend_summary WHERE period_type = 'monthly';

-- Insights
SELECT * FROM spark_insights;

-- Recommendations
SELECT * FROM spark_recommendations;
```

### Via PHP API

Test the API endpoints in your browser (must be logged in):

```
http://localhost/personal_expense/api/spark_summary.php?action=overview
http://localhost/personal_expense/api/spark_summary.php?action=monthly
http://localhost/personal_expense/api/spark_summary.php?action=category&year=2026&month=4
http://localhost/personal_expense/api/spark_summary.php?action=trends&period=monthly
http://localhost/personal_expense/api/spark_summary.php?action=insights
http://localhost/personal_expense/api/spark_summary.php?action=recommendations
```

---

## 11. Access the Dashboard

1. Open: http://localhost/personal_expense/
2. Log in with your account
3. Click **⚡ Spark Analytics** in the sidebar

### Dashboard Features

- **Summary Stats** — Total analyzed, avg monthly spending, top category
- **Spending Trend Chart** — Toggle between Week / Month / Year views
- **Category Pie Chart** — Doughnut chart with month selector
- **Smart Insights** — 2 AI-driven spending insights per user
- **Smart Recommendations** — 2 actionable saving suggestions
- **Monthly Breakdown Table** — Detailed monthly analysis

---

## 12. Troubleshooting

### "JAVA_HOME is not set"

Set the `JAVA_HOME` environment variable to your JDK installation folder.

### "SPARK_HOME is not set"

Set `SPARK_HOME=C:\spark` and add `%SPARK_HOME%\bin` to your PATH.

### "java.lang.ClassNotFoundException: com.mysql.cj.jdbc.Driver"

The MySQL JDBC JAR is not in Spark's classpath. Either:
- Copy `mysql-connector-j-8.x.x.jar` to `C:\spark\jars\`
- Or pass it with `--jars` flag: `spark-submit --jars path/to/mysql-connector-j.jar`

### "Connection refused" or "Cannot connect to MySQL"

- Make sure XAMPP MySQL is running (port 3306)
- Check credentials in `spark_analytics.py` — default is `root` with no password
- If you changed MySQL port, update `MYSQL_CONFIG` in `spark_analytics.py`

### "Table doesn't exist"

Run `database/spark_tables.sql` in phpMyAdmin to create the summary tables.

### "Spark Analytics Not Available" on dashboard

The Spark job hasn't been run yet. Execute `spark/run_spark.bat` first.

### winutils error on Windows

Download `winutils.exe` for your Hadoop version and place in `C:\spark\hadoop\bin\`.
Set `HADOOP_HOME=C:\spark\hadoop`.

### Python version mismatch

PySpark requires Python 3.8+. If you have multiple Python versions:
```cmd
set PYSPARK_PYTHON=python3
```

---

## 13. Project Folder Structure

```
personal_expense/
├── api/
│   ├── auth.php
│   ├── budget.php
│   ├── budget_alerts.php
│   ├── categories.php
│   ├── expenses.php
│   ├── ml_suggestions.php
│   ├── predict_category.php
│   └── spark_summary.php          ← NEW: Spark data API
├── assets/
│   ├── css/
│   │   ├── dashboard.css
│   │   ├── spark_analytics.css    ← NEW: Spark page styles
│   │   ├── style.css
│   │   └── theme.css
│   └── js/
│       ├── dashboard.js
│       ├── main.js
│       ├── spark_analytics.js     ← NEW: Spark page JS
│       └── theme.js
├── config/
│   ├── database.php
│   └── session.php
├── database/
│   ├── schema.sql
│   ├── spark_tables.sql           ← NEW: Summary table schema
│   └── ...
├── ml/
│   ├── expense_ai.py
│   ├── predict_api.py
│   └── smart_insights.py
├── spark/                          ← NEW: Spark analytics folder
│   ├── spark_analytics.py         ← Main PySpark engine
│   ├── generate_sample_data.py    ← 10K+ row generator
│   ├── requirements.txt           ← Python dependencies
│   └── run_spark.bat              ← One-click runner
├── dashboard.php                   (modified: sidebar nav)
├── expenses.php                    (modified: sidebar nav)
├── categories.php                  (modified: sidebar nav)
├── reports.php                     (modified: sidebar nav)
├── spark_analytics.php             ← NEW: Analytics dashboard page
├── SPARK_SETUP.md                  ← NEW: This file
└── ...
```

---

## Quick Start Summary

```
1. Install Java 17, Spark 3.5, winutils, MySQL JDBC JAR
2. pip install -r spark/requirements.txt
3. Run database/spark_tables.sql in phpMyAdmin
4. python spark/generate_sample_data.py     (optional: 10K+ rows)
5. spark/run_spark.bat                       (run analytics)
6. Open http://localhost/personal_expense/spark_analytics.php
```
