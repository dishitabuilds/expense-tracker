"""
Generate Project Report: Personal Expense Tracker with Smart Insights and Recommendations
Output: project_report.docx
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ── Page Setup ──
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

# ── Style helpers ──
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)

def set_cell_shading(cell, color):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)

def add_heading_styled(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Times New Roman'
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h

def add_para(text, bold=False, italic=False, size=12, align=None, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_screenshot_placeholder():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ADD SCREENSHOT!")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(24)
    run.bold = True
    run.font.color.rgb = RGBColor(255, 0, 0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
        set_cell_shading(cell, "D9E2F3")
    # Data rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
    doc.add_paragraph()  # spacing
    return table

def add_code_block(code_text):
    p = doc.add_paragraph()
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    # Light gray background via shading
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), 'F2F2F2')
    shd.set(qn('w:val'), 'clear')
    pPr.append(shd)

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 1.27)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    return p

# ══════════════════════════════════════════════════════════════
#                        TITLE PAGE
# ══════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

add_para("MAJOR PROJECT REPORT", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
add_para("on", size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
add_para("Personal Expense Tracker\nwith Smart Insights and Recommendations", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)

add_para("Submitted in partial fulfillment of the requirements\nfor the award of the degree of", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_para("Bachelor of Technology", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_para("in", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_para("Computer Science & Engineering", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)

add_para("Submitted By:", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
add_para("[Student Name 1]  —  [Roll No.]\n[Student Name 2]  —  [Roll No.]\n[Student Name 3]  —  [Roll No.]\n[Student Name 4]  —  [Roll No.]", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

add_para("Under the Guidance of", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
add_para("[Guide Name], [Designation]", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)

add_para("[Department Name]\n[College/University Name]\n[City, Year]", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                        ABSTRACT
# ══════════════════════════════════════════════════════════════

add_heading_styled("Abstract", level=1)

doc.add_paragraph(
    "Managing personal finances effectively remains a critical challenge for individuals across all demographics. "
    "Traditional expense tracking methods — spreadsheets, manual ledgers, and basic mobile apps — often fail to "
    "provide actionable insights that empower users to make informed financial decisions. This project presents an "
    "AI-Powered Personal Expense Tracker with Smart Insights and Recommendations, a full-stack web application "
    "that leverages Apache Spark for big data analytics to transform raw financial transactions into meaningful, "
    "data-driven intelligence."
)
doc.add_paragraph(
    "The system is built on a multi-layered architecture: a PHP/MySQL backend for data management, an Apache Spark "
    "(PySpark) analytics engine connected via JDBC for distributed data processing, and an interactive JavaScript "
    "frontend powered by Chart.js for real-time visualization. The Spark analytics pipeline processes over 10,000 "
    "expense records across multiple users, performing five key computations — monthly aggregation, category-wise "
    "breakdown with window functions, multi-granularity trend analysis (weekly, monthly, yearly), month-over-month "
    "spike detection, and end-of-month spending projections."
)
doc.add_paragraph(
    "The system generates smart insights such as spending spike alerts (flagging categories with >25% month-over-month "
    "increases), predictive end-of-month projections with last-month comparisons, and actionable savings recommendations "
    "based on spending patterns. All analytics are presented through an intuitive dashboard featuring interactive "
    "doughnut charts, trend line charts, stat cards, and data tables. The project demonstrates practical application "
    "of big data technologies (addressing all 5 V's of Big Data) in personal finance management, bridging the gap "
    "between raw transaction data and actionable financial intelligence."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                     1. INTRODUCTION
# ══════════════════════════════════════════════════════════════

add_heading_styled("1. Introduction", level=1)

add_heading_styled("1.1 Motivation", level=2)
doc.add_paragraph(
    "In today's fast-paced digital economy, individuals generate dozens of financial transactions daily — from UPI "
    "payments and online shopping to subscriptions and utility bills. Despite the availability of digital payment "
    "platforms, most users lack a consolidated view of their spending patterns. They cannot easily answer fundamental "
    "questions such as: 'How much did I spend on food last month compared to this month?', 'Am I on track to stay "
    "within my budget?', or 'Which spending category is growing the fastest?'"
)
doc.add_paragraph(
    "Existing expense trackers provide basic recording and categorization features but fall short in delivering "
    "predictive analytics, intelligent alerts, and actionable recommendations. Furthermore, as transaction volumes "
    "grow (a single user can accumulate thousands of records over a few years), traditional SQL-based approaches "
    "struggle to perform complex, multi-dimensional analytics efficiently."
)
doc.add_paragraph(
    "This project was motivated by the need to bridge this gap — to create a system that not only records expenses "
    "but also thinks about them. By integrating Apache Spark, a distributed big data processing engine, the system "
    "can perform sophisticated analytics that scale effortlessly from hundreds to millions of records, demonstrating "
    "real-world application of big data technologies in personal finance."
)

add_heading_styled("1.2 Objectives", level=2)
add_bullet("Develop a full-stack web application for personal expense tracking with user authentication, category management, and budget monitoring.")
add_bullet("Integrate Apache Spark (PySpark) with MySQL via JDBC to perform distributed analytics on expense data.")
add_bullet("Implement five core analytics computations: monthly summary, category breakdown, multi-granularity trends, spike detection, and spending projections.")
add_bullet("Generate smart, dynamic insights using rule-based analysis — including month-over-month comparisons, spending spike alerts, and savings recommendations.")
add_bullet("Build an interactive analytics dashboard with Chart.js visualizations (doughnut charts, trend lines, data tables).")
add_bullet("Demonstrate practical application of all 5 V's of Big Data (Volume, Velocity, Variety, Veracity, Value) within a personal finance context.")

add_heading_styled("1.3 Contributions", level=2)
add_bullet("A complete Spark analytics pipeline (spark_analytics.py) that reads raw MySQL data, performs 5 computations, and writes structured results back to MySQL.")
add_bullet("Dynamic insight generation engine that performs month-over-month comparisons instead of static templates — detecting spending spikes (>25% increase) and projecting end-of-month totals against last month's actuals.")
add_bullet("A PHP REST API layer (7 endpoints) that bridges Spark output tables with the frontend dashboard, serving pre-computed analytics as JSON.")
add_bullet("An interactive Spark Analytics Dashboard with switchable chart granularities (weekly/monthly/yearly), category month selectors, and severity-coded insight cards.")
add_bullet("ISO 8601 week-based trend analysis with human-readable date range labels for clear weekly pattern visualization.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                    2. PROPOSED WORK
# ══════════════════════════════════════════════════════════════

add_heading_styled("2. Proposed Work", level=1)

add_heading_styled("2.1 Key Features Implemented", level=2)

add_para("The Personal Expense Tracker with Smart Insights and Recommendations implements the following key features:", space_after=8)

add_para("A. User Management", bold=True)
add_bullet("Secure registration and login with bcrypt password hashing")
add_bullet("Session-based authentication with PHP session management")
add_bullet("Multi-user support — each user has isolated data and analytics")

add_para("B. Expense Management", bold=True)
add_bullet("Full CRUD (Create, Read, Update, Delete) operations for expense records")
add_bullet("Category assignment with custom colors and icons")
add_bullet("Date-based filtering, searching, and pagination")

add_para("C. Category & Budget Management", bold=True)
add_bullet("User-defined categories with priority levels (essential, moderate, discretionary)")
add_bullet("Monthly budget limits per category with alert thresholds (default: 80%)")
add_bullet("Budget utilization tracking with visual progress indicators")

add_para("D. Apache Spark Analytics Engine", bold=True)
add_bullet("JDBC-based integration reading 10,344+ records from MySQL into Spark DataFrames")
add_bullet("Five analytics computations: monthly summary, category breakdown (with Window functions), multi-granularity trends, smart insights, and savings recommendations")
add_bullet("Overwrite mode for fresh analytics on every Spark run")

add_para("E. Smart Insights & Recommendations", bold=True)
add_bullet("Month-over-month spike detection: flags categories with >25% spending increase")
add_bullet("End-of-month projection: daily burn rate extrapolation compared against last month's actual total")
add_bullet("Category growth ranking: identifies fastest-growing expense categories")
add_bullet("Weekend vs weekday spending pattern analysis")
add_bullet("Actionable savings recommendations with potential savings amount")

add_para("F. Interactive Dashboard & Visualization", bold=True)
add_bullet("Spending trend chart (line/bar) with weekly, monthly, and yearly toggle")
add_bullet("Category breakdown doughnut chart with month selector")
add_bullet("Monthly breakdown data table with Total, Count, Average, Max, Min columns")
add_bullet("Stat cards (grand total, avg monthly, top category, last Spark run)")
add_bullet("Severity-coded insight cards (critical/warning/info/success)")

add_heading_styled("2.2 Workflow", level=2)

doc.add_paragraph(
    "The system follows a five-stage workflow that transforms raw user input into actionable analytics:"
)

add_para("Stage 1: Data Entry", bold=True)
doc.add_paragraph(
    "The user logs into the web application and adds expense records through an intuitive form interface. "
    "Each expense includes an amount (DECIMAL), description (VARCHAR), date (DATE), and optional category. "
    "JavaScript validates inputs client-side, then sends a POST request to the PHP API, which inserts the "
    "record into the MySQL 'expenses' table using prepared statements."
)

add_para("Stage 2: Data Accumulation", bold=True)
doc.add_paragraph(
    "Over time, the MySQL database accumulates thousands of expense records. The current dataset contains "
    "10,344 records across 4 users spanning May 2024 to April 2026 (~2 years). The 'expenses' table is "
    "indexed on user_id, category_id, and expense_date for efficient querying."
)

add_para("Stage 3: Spark Analytics Processing", bold=True)
doc.add_paragraph(
    "The user triggers the Spark analytics pipeline via spark-submit (or a batch file). The pipeline follows "
    "a READ → TRANSFORM → WRITE pattern:"
)
add_bullet("READ: Spark reads 'expenses' (10,344 rows) and 'categories' (34 rows) from MySQL via JDBC into in-memory DataFrames.")
add_bullet("TRANSFORM: Five computations execute — monthly aggregation (groupBy + agg), category breakdown (JOIN + Window), "
           "trend analysis (filter + groupBy + UNION), smart insights (collect + Python logic), and recommendations (collect + pattern detection).")
add_bullet("WRITE: Results (850 total rows) are written back to 5 MySQL summary tables using JDBC in overwrite mode.")

add_para("Stage 4: API Serving", bold=True)
doc.add_paragraph(
    "The PHP API layer (api/spark_summary.php) provides 7 RESTful endpoints that read the Spark-generated "
    "summary tables and return JSON responses. The frontend calls these endpoints using the JavaScript Fetch API."
)

add_para("Stage 5: Dashboard Visualization", bold=True)
doc.add_paragraph(
    "JavaScript receives the JSON data and renders interactive visualizations using Chart.js — including "
    "trend line charts, category doughnut charts, stat cards, insight cards, recommendation cards, and "
    "monthly data tables. Users can interact with period toggles and month selectors to explore their data."
)

add_screenshot_placeholder()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                 3. IMPLEMENTATION DETAILS
# ══════════════════════════════════════════════════════════════

add_heading_styled("3. Implementation Details", level=1)

add_heading_styled("3.1 Dataset and Its Type", level=2)

add_para("3.1.1 Database Overview", bold=True)

add_table(
    ["Property", "Value"],
    [
        ["Database Name", "personal_expense_tracker"],
        ["Engine", "MySQL 8.0 / MariaDB (via XAMPP)"],
        ["Total Records", "10,344 expense transactions"],
        ["Users", "4 (1 real + 3 synthetic test users)"],
        ["Date Range", "May 2024 – April 2026 (~2 years)"],
        ["Categories", "8 per user (Food, Transport, Shopping, etc.)"],
        ["Source Tables", "3 (users, categories, expenses)"],
        ["Spark Output Tables", "5 (monthly_summary, category_summary, trend_summary, spark_insights, spark_recommendations)"],
        ["Total Tables", "8"],
    ]
)

add_para("3.1.2 Source Tables", bold=True)

add_para("Table: users", bold=True, italic=True)
add_table(
    ["Column", "Data Type", "Constraints", "Description"],
    [
        ["id", "INT(11)", "PK, AUTO_INCREMENT", "Unique user ID"],
        ["username", "VARCHAR(50)", "NOT NULL, UNIQUE", "Login username"],
        ["email", "VARCHAR(100)", "NOT NULL, UNIQUE", "User email address"],
        ["password", "VARCHAR(255)", "NOT NULL", "Bcrypt hashed password"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Account creation time"],
        ["updated_at", "TIMESTAMP", "ON UPDATE CURRENT_TIMESTAMP", "Last modification time"],
    ]
)

add_para("Table: categories", bold=True, italic=True)
add_table(
    ["Column", "Data Type", "Constraints", "Description"],
    [
        ["id", "INT(11)", "PK, AUTO_INCREMENT", "Unique category ID"],
        ["user_id", "INT(11)", "NOT NULL, FK→users.id", "Owner of the category"],
        ["name", "VARCHAR(50)", "NOT NULL", "Category display name"],
        ["color", "VARCHAR(7)", "DEFAULT '#6366f1'", "Hex color code for charts"],
        ["icon", "VARCHAR(50)", "DEFAULT 'tag'", "Icon identifier"],
        ["budget", "DECIMAL(10,2)", "NULLABLE", "Monthly budget limit (₹)"],
        ["priority", "ENUM", "DEFAULT 'moderate'", "essential / moderate / discretionary"],
        ["alert_threshold", "INT(11)", "DEFAULT 80", "Budget alert trigger (%)"],
        ["alert_enabled", "TINYINT(1)", "DEFAULT 1", "Whether alerts are on"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Creation time"],
    ]
)

add_para("Table: expenses (Primary Dataset — 10,344 rows)", bold=True, italic=True)
add_table(
    ["Column", "Data Type", "Constraints", "Description"],
    [
        ["id", "INT(11)", "PK, AUTO_INCREMENT", "Unique expense ID"],
        ["user_id", "INT(11)", "NOT NULL, FK→users.id", "Who made the expense"],
        ["category_id", "INT(11)", "NULLABLE, FK→categories.id", "Category (NULL = uncategorized)"],
        ["amount", "DECIMAL(10,2)", "NOT NULL", "Expense amount in ₹ (INR)"],
        ["description", "VARCHAR(255)", "NULLABLE", "Short description text"],
        ["notes", "TEXT", "NULLABLE", "Optional detailed notes"],
        ["expense_date", "DATE", "NOT NULL, INDEXED", "When the expense occurred"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Record creation time"],
        ["updated_at", "TIMESTAMP", "ON UPDATE CURRENT_TIMESTAMP", "Last modification time"],
    ]
)

add_para("Example Records:", bold=True)
add_table(
    ["id", "user_id", "category_id", "amount", "description", "expense_date"],
    [
        ["345", "1", "23", "23.00", "grocery", "2026-04-20"],
        ["343", "1", "23", "330.00", "grocery", "2026-04-20"],
        ["341", "1", "18", "300.00", "auto", "2026-04-17"],
        ["338", "1", "4", "1000.00", "food", "2026-04-17"],
        ["337", "1", "NULL", "500.00", "gift", "2026-04-15"],
    ]
)

add_para("Dataset Characteristics:", bold=True)
add_bullet("Amount range: ₹23 to ₹16,827")
add_bullet("Null category_id: Some expenses are uncategorized (handled via LEFT JOIN)")
add_bullet("Distribution: ~3,334 records per synthetic user, ~344 for real user")
add_bullet("Temporal spread: 2 years of data with realistic seasonal patterns")
add_bullet("Data type: Structured (relational tables with defined schemas)")

add_para("3.1.3 Spark Output Tables", bold=True)

add_table(
    ["Table Name", "Rows", "Key Columns", "Purpose"],
    [
        ["monthly_summary", "86", "user_id, year, month, total_amount, max_amount, min_amount", "Monthly spending aggregation"],
        ["category_summary", "641", "user_id, year, month, category_name, percentage", "Category-wise breakdown with %"],
        ["trend_summary", "107", "user_id, period_type, period_label, total_amount", "Weekly/monthly/yearly trends"],
        ["spark_insights", "8", "user_id, insight_type, message, severity", "Spike detection + projections"],
        ["spark_recommendations", "8", "user_id, rec_type, message, potential_savings", "Savings recommendations"],
    ]
)

add_screenshot_placeholder()

add_heading_styled("3.2 Tools and Technologies", level=2)

# XAMPP
add_para("3.2.1 XAMPP (Cross-platform Apache MySQL PHP Perl)", bold=True)
add_table(
    ["Property", "Detail"],
    [
        ["Version", "8.2.x"],
        ["Type", "Local development server stack"],
        ["License", "GNU General Public License (Free)"],
    ]
)
doc.add_paragraph(
    "XAMPP is a free, open-source, cross-platform web server solution stack package developed by Apache Friends. "
    "It bundles Apache HTTP Server, MariaDB/MySQL, and PHP into a single installer. In this project, XAMPP provides: "
    "Apache as the HTTP server (port 80), MySQL/MariaDB as the relational database (port 3306), PHP as the server-side "
    "scripting engine, and phpMyAdmin as the database administration GUI."
)

# MySQL
add_para("3.2.2 MySQL (MariaDB)", bold=True)
add_table(
    ["Property", "Detail"],
    [
        ["Version", "10.4.x (MariaDB, MySQL-compatible)"],
        ["Type", "Relational Database Management System (RDBMS)"],
        ["Storage Engine", "InnoDB (transactions + foreign keys)"],
        ["Query Language", "SQL (Structured Query Language)"],
    ]
)
doc.add_paragraph(
    "MySQL serves as both the primary data store and the Spark I/O layer. It stores all raw expense transactions, "
    "serves as the JDBC read source for Spark (spark.read.jdbc()), and receives Spark's processed analytics via "
    "JDBC write (df.write.jdbc()). Key features used include AUTO_INCREMENT primary keys, FOREIGN KEY constraints, "
    "INDEXES for fast lookups, DECIMAL(10,2) for precise currency values, and ENUM types for category priorities."
)

# Apache Spark
add_para("3.2.3 Apache Spark (PySpark)", bold=True)
add_table(
    ["Property", "Detail"],
    [
        ["Version", "4.1.1"],
        ["API Used", "PySpark (Python interface)"],
        ["Execution Mode", "Local (local[*] — all CPU cores)"],
        ["JVM", "Java HotSpot 17.0.10 (LTS)"],
        ["JDBC Driver", "mysql-connector-j-8.3.0.jar"],
        ["License", "Apache License 2.0"],
    ]
)
doc.add_paragraph(
    "Apache Spark is a unified analytics engine for large-scale data processing, originally developed at UC Berkeley's "
    "AMPLab. It is designed for speed (100× faster than Hadoop MapReduce for in-memory processing), ease of use, and "
    "sophisticated analytics. In this project, Spark reads raw expense data from MySQL via JDBC, performs five analytical "
    "computations using the DataFrame API (groupBy, agg, join, Window functions, UDFs), and writes structured results "
    "back to MySQL. PySpark communicates with the Spark JVM through the Py4J bridge."
)

add_para("Key Spark Components Used:", bold=True)
add_table(
    ["Component", "Purpose"],
    [
        ["SparkSession", "Entry point — creates driver program, manages configuration"],
        ["DataFrame API", "Distributed table abstraction — groupBy(), agg(), join(), filter()"],
        ["Spark SQL Functions", "Built-in: F.sum(), F.avg(), F.weekofyear(), F.dayofweek()"],
        ["Window Functions", "Analytic: percentage calculation using Window.partitionBy().over()"],
        ["UDF", "Custom Python function — month number to name mapping"],
        ["JDBC Connector", "Read/write MySQL — spark.read.jdbc(), df.write.jdbc()"],
    ]
)

# PHP
add_para("3.2.4 PHP (Hypertext Preprocessor)", bold=True)
add_table(
    ["Property", "Detail"],
    [
        ["Version", "8.2.x"],
        ["Type", "Server-side scripting language"],
        ["Database Driver", "MySQLi (MySQL Improved Extension)"],
    ]
)
doc.add_paragraph(
    "PHP serves as the backend API layer, providing 7 RESTful endpoints that read Spark-generated summary tables "
    "and return JSON responses. It also handles user authentication (session-based login with bcrypt), page rendering, "
    "and database connectivity using MySQLi prepared statements (preventing SQL injection). Key files include "
    "api/spark_summary.php (7 analytics endpoints), api/expenses.php (CRUD), and config/database.php (connection)."
)

# JavaScript
add_para("3.2.5 JavaScript (ES6+) with Chart.js", bold=True)
add_table(
    ["Property", "Detail"],
    [
        ["Version", "ES6+ (ECMAScript 2015+)"],
        ["Runtime", "Browser (client-side)"],
        ["Charting Library", "Chart.js 4.4.0"],
        ["HTTP Client", "Fetch API (native browser API)"],
    ]
)
doc.add_paragraph(
    "JavaScript powers the frontend interactivity — fetching analytics data from the PHP API via the Fetch API, "
    "rendering interactive charts using Chart.js (trend lines, doughnut charts), populating stat cards and insight "
    "cards with dynamic HTML, and handling user interactions (period toggles, month selectors, theme switching). "
    "Chart.js provides smooth animations, hover tooltips, responsive resizing, and gradient fills."
)

add_screenshot_placeholder()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                       4. RESULTS
# ══════════════════════════════════════════════════════════════

add_heading_styled("4. Results", level=1)

add_heading_styled("4.1 Prominent Queries of the System", level=2)

doc.add_paragraph(
    "The following are the key SQL and Spark queries used in the expense tracker analytics system. "
    "Each query is presented in both PySpark DataFrame API syntax and its equivalent SQL form."
)

# Query 1
add_para("Query 1: Monthly Expense Aggregation", bold=True)
doc.add_paragraph(
    "Purpose: Calculate total spending, count, average, maximum, and minimum per user per month. "
    "Powers the monthly summary table and stat cards."
)
add_code_block(
    "PySpark:\n"
    "monthly = expenses_df \\\n"
    "    .withColumn(\"year\", F.year(\"expense_date\")) \\\n"
    "    .withColumn(\"month\", F.month(\"expense_date\")) \\\n"
    "    .groupBy(\"user_id\", \"year\", \"month\") \\\n"
    "    .agg(\n"
    "        F.round(F.sum(\"amount\"), 2).alias(\"total_amount\"),\n"
    "        F.count(\"*\").alias(\"transaction_count\"),\n"
    "        F.round(F.avg(\"amount\"), 2).alias(\"avg_amount\"),\n"
    "        F.round(F.max(\"amount\"), 2).alias(\"max_amount\"),\n"
    "        F.round(F.min(\"amount\"), 2).alias(\"min_amount\")\n"
    "    )"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT user_id, YEAR(expense_date) AS year, MONTH(expense_date) AS month,\n"
    "       ROUND(SUM(amount), 2) AS total_amount, COUNT(*) AS transaction_count,\n"
    "       ROUND(AVG(amount), 2) AS avg_amount, ROUND(MAX(amount), 2) AS max_amount,\n"
    "       ROUND(MIN(amount), 2) AS min_amount\n"
    "FROM expenses GROUP BY user_id, YEAR(expense_date), MONTH(expense_date);"
)
add_para("Output: 86 rows  |  Spark Concepts: withColumn, groupBy, agg, F.sum, F.max, F.min", italic=True, size=10)

# Query 2
add_para("Query 2: Category-wise Spending with JOIN", bold=True)
doc.add_paragraph(
    "Purpose: Join expenses with categories to get category names and colors, then aggregate spending per "
    "category per month. Powers the doughnut chart."
)
add_code_block(
    "PySpark:\n"
    "joined = expenses_df.join(\n"
    "    categories_df.select(F.col(\"id\").alias(\"cat_id\"),\n"
    "        F.col(\"name\").alias(\"category_name\"),\n"
    "        F.col(\"color\").alias(\"category_color\")),\n"
    "    expenses_df[\"category_id\"] == F.col(\"cat_id\"), \"left\"\n"
    ").fillna({\"category_name\": \"Uncategorized\", \"category_color\": \"#6b7280\"})\n\n"
    "cat_totals = joined.withColumn(\"year\", F.year(\"expense_date\")) \\\n"
    "    .withColumn(\"month\", F.month(\"expense_date\")) \\\n"
    "    .groupBy(\"user_id\",\"year\",\"month\",\"category_name\",\"category_color\") \\\n"
    "    .agg(F.round(F.sum(\"amount\"), 2).alias(\"total_amount\"),\n"
    "         F.count(\"*\").alias(\"transaction_count\"))"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT e.user_id, YEAR(e.expense_date) AS year, MONTH(e.expense_date) AS month,\n"
    "       COALESCE(c.name, 'Uncategorized') AS category_name,\n"
    "       ROUND(SUM(e.amount), 2) AS total_amount, COUNT(*) AS transaction_count\n"
    "FROM expenses e LEFT JOIN categories c ON e.category_id = c.id\n"
    "GROUP BY e.user_id, year, month, category_name;"
)
add_para("Spark Concepts: join (LEFT), select, alias, fillna", italic=True, size=10)

# Query 3
add_para("Query 3: Percentage Calculation with Window Function", bold=True)
doc.add_paragraph(
    "Purpose: Calculate what percentage each category represents within a user's monthly total. "
    "E.g., 'Food = 35% of April spending'."
)
add_code_block(
    "PySpark:\n"
    "window = Window.partitionBy(\"user_id\", \"year\", \"month\")\n"
    "cat_summary = cat_totals.withColumn(\"percentage\",\n"
    "    F.round((F.col(\"total_amount\") / F.sum(\"total_amount\").over(window)) * 100, 2))"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT *, ROUND(total_amount / SUM(total_amount)\n"
    "    OVER (PARTITION BY user_id, year, month) * 100, 2) AS percentage\n"
    "FROM category_totals;"
)
add_para("Spark Concepts: Window.partitionBy, .over(window), analytic function", italic=True, size=10)

# Query 4
add_para("Query 4: ISO Weekly Trend Analysis", bold=True)
doc.add_paragraph(
    "Purpose: Group expenses into ISO 8601 weeks (Monday–Sunday) for the last 12 weeks with "
    "human-readable date range labels. Powers the weekly trend line chart."
)
add_code_block(
    "PySpark:\n"
    "weekly = expenses_df.filter(F.col(\"expense_date\") >= F.lit(twelve_weeks_ago)) \\\n"
    "    .withColumn(\"iso_week\", F.weekofyear(\"expense_date\")) \\\n"
    "    .groupBy(\"user_id\", \"iso_year\", \"iso_week\") \\\n"
    "    .agg(F.round(F.sum(\"amount\"),2).alias(\"total_amount\"),\n"
    "         F.min(\"expense_date\").alias(\"period_start\"),\n"
    "         F.max(\"expense_date\").alias(\"period_end\")) \\\n"
    "    .withColumn(\"period_label\", F.concat(\n"
    "         F.date_format(\"period_start\",\"MMM d\"), F.lit(\" - \"),\n"
    "         F.date_format(\"period_end\",\"MMM d\")))"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT user_id, YEARWEEK(expense_date, 3) AS iso_yearweek,\n"
    "       ROUND(SUM(amount), 2) AS total_amount,\n"
    "       CONCAT(DATE_FORMAT(MIN(expense_date),'%b %e'), ' - ',\n"
    "              DATE_FORMAT(MAX(expense_date),'%b %e')) AS period_label\n"
    "FROM expenses WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL 12 WEEK)\n"
    "GROUP BY user_id, iso_yearweek ORDER BY period_start;"
)
add_para("Spark Concepts: filter, F.weekofyear, F.date_format, F.concat", italic=True, size=10)

# Query 5
add_para("Query 5: Month-over-Month Spike Detection", bold=True)
doc.add_paragraph(
    "Purpose: Compare each category's spending this month vs last month. Detect any category with "
    ">25% increase and flag it as a spending spike."
)
add_code_block(
    "PySpark:\n"
    "current_month_cat = user_expenses.filter(\n"
    "    (F.year(\"expense_date\") == 2026) & (F.month(\"expense_date\") == 4)\n"
    ").groupBy(\"category_name\").agg(F.sum(\"amount\").alias(\"current_total\")).collect()\n\n"
    "last_month_cat = user_expenses.filter(\n"
    "    (F.year(\"expense_date\") == 2026) & (F.month(\"expense_date\") == 3)\n"
    ").groupBy(\"category_name\").agg(F.sum(\"amount\").alias(\"last_total\")).collect()\n\n"
    "# Python logic: detect spike\n"
    "for row in current_month_cat:\n"
    "    change_pct = ((current - last_val) / last_val) * 100\n"
    "    if change_pct > 25:  # SPIKE DETECTED"
)
add_para("Spark Concepts: collect() (brings data to driver), Python-side rule logic", italic=True, size=10)

# Query 6
add_para("Query 6: End-of-Month Spending Projection", bold=True)
doc.add_paragraph(
    "Purpose: Based on daily burn rate so far, project total spending by month end. Compare projection "
    "against last month's actual total."
)
add_code_block(
    "Python Logic:\n"
    "total_spent = SUM(current_month_expenses)     # e.g., Rs.12,723\n"
    "daily_rate = total_spent / day_of_month        # e.g., Rs.636/day\n"
    "projected = daily_rate * days_in_month         # e.g., Rs.19,084\n"
    "proj_vs_last = ((projected - last_total) / last_total) * 100  # -23.6%"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT SUM(amount) AS spent_so_far,\n"
    "       SUM(amount) / DAY(CURDATE()) AS daily_rate,\n"
    "       SUM(amount) / DAY(CURDATE()) * DAY(LAST_DAY(CURDATE())) AS projected\n"
    "FROM expenses WHERE user_id=1 AND YEAR(expense_date)=YEAR(CURDATE())\n"
    "  AND MONTH(expense_date)=MONTH(CURDATE());"
)

# Query 7
add_para("Query 7: Weekend vs Weekday Spending Pattern", bold=True)
doc.add_paragraph(
    "Purpose: Compare average daily spending on weekends vs weekdays in last 30 days."
)
add_code_block(
    "PySpark:\n"
    "recent = user_expenses.filter(F.col(\"expense_date\") >= thirty_days_ago) \\\n"
    "    .withColumn(\"day_of_week\", F.dayofweek(\"expense_date\"))\n"
    "weekend = recent.filter(F.col(\"day_of_week\").isin(1, 7)).agg(\n"
    "    F.sum(\"amount\").alias(\"total\"), F.countDistinct(\"expense_date\").alias(\"days\")).collect()\n"
    "weekday = recent.filter(~F.col(\"day_of_week\").isin(1, 7)).agg(...).collect()\n"
    "ratio = weekend_avg / weekday_avg  # e.g., 1.8x more on weekends"
)
add_para("Spark Concepts: F.dayofweek, F.countDistinct, isin(), ~ (NOT)", italic=True, size=10)

# Query 8
add_para("Query 8: Category Growth Ranking", bold=True)
doc.add_paragraph(
    "Purpose: Rank all categories by month-over-month spending growth. Find highest-growth category for recommendations."
)
add_code_block(
    "Python Logic:\n"
    "for each category:\n"
    "    growth_pct = ((current_total - prev_total) / prev_total) * 100\n"
    "    track the category with highest growth_pct\n"
    "    suggest capping at 110% of last month's total"
)

# Query 9
add_para("Query 9: UNION of Multi-Granularity Trends", bold=True)
doc.add_paragraph(
    "Purpose: Combine weekly, monthly, and yearly trend DataFrames into a single table using UNION ALL."
)
add_code_block(
    "PySpark:\n"
    "all_trends = weekly.select(cols).union(monthly.select(cols)).union(yearly.select(cols)) \\\n"
    "    .withColumn(\"generated_at\", F.current_timestamp())"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT 'weekly' AS period_type, ... FROM weekly_trends\n"
    "UNION ALL\n"
    "SELECT 'monthly' AS period_type, ... FROM monthly_trends\n"
    "UNION ALL\n"
    "SELECT 'yearly' AS period_type, ... FROM yearly_trends;"
)
add_para("Spark Concepts: union(), select() (column reordering), F.current_timestamp()", italic=True, size=10)

# Query 10
add_para("Query 10: Year-over-Year Comparison", bold=True)
doc.add_paragraph(
    "Purpose: Compare total spending across years per user. Shows long-term financial trajectory."
)
add_code_block(
    "PySpark:\n"
    "yearly = expenses_df.withColumn(\"year\", F.year(\"expense_date\")) \\\n"
    "    .groupBy(\"user_id\", \"year\").agg(\n"
    "        F.round(F.sum(\"amount\"), 2).alias(\"total_amount\"),\n"
    "        F.count(\"*\").alias(\"transaction_count\")) \\\n"
    "    .withColumn(\"avg_daily\", F.round(F.col(\"total_amount\") / 365, 2))"
)
add_code_block(
    "Equivalent SQL:\n"
    "SELECT user_id, YEAR(expense_date) AS year,\n"
    "       ROUND(SUM(amount), 2), COUNT(*), ROUND(SUM(amount) / 365, 2) AS avg_daily\n"
    "FROM expenses GROUP BY user_id, YEAR(expense_date) ORDER BY year;"
)

# Query 11
add_para("Query 11: Budget Utilization Check (PHP API)", bold=True)
doc.add_paragraph("Purpose: Check how much of the monthly budget has been used per category.")
add_code_block(
    "SQL (PHP API):\n"
    "SELECT c.name, c.budget, COALESCE(SUM(e.amount), 0) AS spent,\n"
    "       ROUND(COALESCE(SUM(e.amount),0) / c.budget * 100, 1) AS utilization_pct,\n"
    "       c.budget - COALESCE(SUM(e.amount), 0) AS remaining\n"
    "FROM categories c LEFT JOIN expenses e ON c.id = e.category_id\n"
    "    AND YEAR(e.expense_date) = YEAR(CURDATE()) AND MONTH(e.expense_date) = MONTH(CURDATE())\n"
    "WHERE c.user_id = 1 AND c.budget IS NOT NULL AND c.budget > 0\n"
    "GROUP BY c.id ORDER BY utilization_pct DESC;"
)

# Query 12
add_para("Query 12: Spark Overview API (Combined Dashboard Query)", bold=True)
doc.add_paragraph("Purpose: Single API call fetching monthly, category, insights, and recommendations together.")
add_code_block(
    "SQL (PHP getOverview):\n"
    "-- Query A: Last 12 months summary\n"
    "SELECT year, month, month_name, total_amount, max_amount, min_amount\n"
    "FROM monthly_summary WHERE user_id = ? ORDER BY year DESC, month DESC LIMIT 12;\n\n"
    "-- Query B: Current month categories\n"
    "SELECT category_name, category_color, total_amount, percentage\n"
    "FROM category_summary WHERE user_id=? AND year=YEAR(CURDATE()) AND month=MONTH(CURDATE());\n\n"
    "-- Query C: Smart insights (2 per user)\n"
    "SELECT insight_type, message, severity FROM spark_insights WHERE user_id=? LIMIT 2;\n\n"
    "-- Query D: Recommendations (2 per user)\n"
    "SELECT rec_type, message, priority, potential_savings\n"
    "FROM spark_recommendations WHERE user_id=? ORDER BY potential_savings DESC LIMIT 2;"
)

add_para("Queries Summary:", bold=True)
add_table(
    ["#", "Query", "Key Spark Concepts", "Purpose"],
    [
        ["1", "Monthly Aggregation", "groupBy, agg, sum/avg/max/min", "Monthly totals per user"],
        ["2", "Category JOIN", "join(\"left\"), fillna", "Category-wise breakdown"],
        ["3", "Percentage Window", "Window.partitionBy, .over()", "Category % of total"],
        ["4", "ISO Weekly Trends", "weekofyear, filter, date_format", "Weekly chart data"],
        ["5", "Spike Detection", "collect(), Python logic", "Month-over-month alerts"],
        ["6", "Month Projection", "collect(), arithmetic", "End-of-month forecast"],
        ["7", "Weekend Pattern", "dayofweek, isin, countDistinct", "Spending pattern analysis"],
        ["8", "Growth Ranking", "collect(), comparison loop", "Highest-growth category"],
        ["9", "Trend UNION", "union(), select()", "Combine W/M/Y trends"],
        ["10", "Year-over-Year", "cast(StringType), F.lit", "Annual comparison"],
        ["11", "Budget Utilization", "SQL LEFT JOIN, COALESCE", "Budget alerts"],
        ["12", "Overview API", "5 parameterized SQL queries", "Dashboard load"],
    ]
)

add_screenshot_placeholder()

add_heading_styled("4.2 Data Visualization", level=2)

# Doughnut
add_para("4.2.1 Category Doughnut Chart", bold=True)
doc.add_paragraph(
    "Chart Type: Doughnut (a pie chart with a 60% hollow center), rendered using Chart.js 4.4.0. "
    "This chart shows the proportional distribution of spending across categories for a selected month. "
    "Each segment's color is fetched from the category_color field in the database, ensuring consistency. "
    "Interactive features include a month selector dropdown, hover tooltips showing category name, amount, "
    "and percentage, and a clickable legend to toggle individual segments."
)
doc.add_paragraph(
    "Data Pipeline: Spark JOIN (expenses × categories) → groupBy(category) → agg(SUM) → "
    "Window function (percentage) → MySQL category_summary → PHP API (JSON) → Chart.js rendering."
)
add_screenshot_placeholder()

# Trend Line
add_para("4.2.2 Spending Trend Line Chart", bold=True)
doc.add_paragraph(
    "Chart Type: Line chart with gradient area fill (weekly/monthly view) and bar chart (yearly view), "
    "rendered using Chart.js 4.4.0. This chart visualizes spending patterns over time, helping users identify "
    "upward/downward trends, seasonal patterns, and unusual spikes. It supports three granularities:"
)
add_table(
    ["Mode", "Time Range", "Label Format", "Example", "Chart Type"],
    [
        ["Weekly", "Last 12 ISO weeks", "Date range", "Apr 7 - Apr 12", "Line + area fill"],
        ["Monthly", "Last 12 months", "Month Year", "Apr 2026", "Line + area fill"],
        ["Yearly", "All years", "Year", "2024, 2025, 2026", "Bar chart"],
    ]
)
doc.add_paragraph(
    "Design choices: Bezier curve smoothing (tension: 0.4) for readable trends, gradient fill from "
    "indigo (30% opacity) to transparent for visual weight, and responsive resizing on window changes."
)
add_screenshot_placeholder()

# Monthly Table
add_para("4.2.3 Monthly Breakdown Data Table", bold=True)
doc.add_paragraph(
    "A dynamic HTML table rendered via JavaScript showing detailed monthly metrics. Unlike charts, tables "
    "allow precise value comparison across months. Columns: Month Name, Total Amount (SUM), Transaction Count, "
    "Average Amount (AVG), Maximum Expense (MAX), Minimum Expense (MIN). Data is sorted most recent first."
)
add_table(
    ["Month", "Total", "Count", "Average", "Max", "Min"],
    [
        ["April 2026", "₹12,723", "15", "₹848.20", "₹8,000", "₹23"],
        ["March 2026", "₹24,990", "4", "₹6,247.50", "₹10,000", "₹4,990"],
        ["February 2026", "₹11,080", "5", "₹2,216.00", "₹7,000", "₹200"],
    ]
)
add_screenshot_placeholder()

# Stat Cards + Insight Cards
add_para("4.2.4 Stat Cards and Insight Cards", bold=True)
doc.add_paragraph(
    "Stat Cards: Four KPI cards at the top — Grand Total (SUM of all months), Average Monthly Spending "
    "(grand_total ÷ months_covered), Top Category (highest spending category), and Last Spark Run timestamp."
)
doc.add_paragraph(
    "Insight Cards: Dynamic severity-coded cards displaying AI-driven findings. Severity levels: "
    "critical (red, >75% spike), warning (amber, 25-75% spike), info (blue, neutral), success (green, "
    "spending below last month). Each card shows the insight type, related category, and a detailed message "
    "with exact amounts and percentages."
)
add_screenshot_placeholder()

add_heading_styled("4.3 Which V's of Big Data Are Targeted", level=2)

doc.add_paragraph(
    "Big Data is characterized by the 5 V's — a framework describing the dimensions of large-scale data "
    "processing. The following table explains how each V is addressed in this project:"
)

add_table(
    ["V", "Definition", "How This Project Addresses It"],
    [
        ["Volume", "Amount of data", "10,344 expense records processed in-memory by Spark. The same code scales to millions of rows by switching from local[*] to a multi-node cluster — zero code changes needed."],
        ["Velocity", "Speed of data generation/processing", "Currently uses batch processing via spark-submit (~30 seconds for 10K rows). Upgradeable to Spark Structured Streaming for real-time processing of each new expense."],
        ["Variety", "Different data formats", "Handles structured data (MySQL tables), semi-structured data (JSON metadata column in spark_insights), and multiple data types (DECIMAL, DATE, ENUM, VARCHAR, TEXT)."],
        ["Veracity", "Data quality & accuracy", "Ensured via NULL handling (fillna, COALESCE), DECIMAL(10,2) precision, prepared statements (SQL injection prevention), generated_at timestamps, and overwrite mode for data freshness."],
        ["Value", "Business insights extracted", "Raw transactions transformed into: spike detection, spending projections, savings recommendations, category breakdowns, and trend visualizations — enabling data-driven financial decisions."],
    ]
)

add_para("Detailed Explanation of Each V:", bold=True)

add_para("Volume:", bold=True)
doc.add_paragraph(
    "The system currently processes 10,344 expense records (~500 KB) in local[*] mode. Spark's DataFrame API "
    "distributes data across partitions processed in parallel across all CPU cores. The same spark_analytics.py "
    "code works at enterprise scale (millions of rows) by simply changing the master URL from 'local[*]' to "
    "'spark://cluster:7077'. At 10M rows (~500 MB), a 3-node cluster processes in approximately 5 minutes."
)

add_para("Velocity:", bold=True)
doc.add_paragraph(
    "Data is generated at low velocity (users manually enter a few transactions per day). The Spark job runs "
    "in batch mode — triggered manually via spark-submit, processing ALL accumulated data at once. This is "
    "appropriate since expense analytics don't require sub-second latency. For real-time scenarios, Spark "
    "Structured Streaming could incrementally update summary tables as each new expense is added."
)

add_para("Variety:", bold=True)
doc.add_paragraph(
    "The project primarily handles structured relational data from MySQL (3 tables with defined schemas). "
    "Additionally, the spark_insights table contains a 'metadata' column storing semi-structured JSON objects "
    "with variable structure. The categories table uses ENUM types for priority classification. In production, "
    "the pipeline could extend to ingest CSV bank statements, REST API webhooks, and OCR-processed receipt images."
)

add_para("Veracity:", bold=True)
doc.add_paragraph(
    "Data quality is ensured through multiple layers: database constraints (FOREIGN KEY, NOT NULL, UNIQUE), "
    "application validation (PHP checks for positive amounts, valid dates), Spark-level handling (fillna for "
    "NULL categories, F.round for DECIMAL precision), and freshness guarantees (overwrite mode, generated_at "
    "timestamps). The system uses DECIMAL(10,2) instead of FLOAT to prevent floating-point currency errors."
)

add_para("Value:", bold=True)
doc.add_paragraph(
    "This is the most critical V. The Spark pipeline transforms 10,344 raw transaction rows — which individually "
    "have zero analytical value — into 850 rows of structured intelligence across 5 output tables. Users receive "
    "spike alerts ('Education surged 45% vs March'), spending projections ('Projected ₹19,084 — 23% LESS than "
    "March'), savings recommendations ('Cap Education at ₹13,200 to save ₹4,224/month'), and visual trend "
    "patterns. This enables data-driven financial decisions that were impossible from raw data alone."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                      5. TAKE AWAY
# ══════════════════════════════════════════════════════════════

add_heading_styled("5. Take Away", level=1)

doc.add_paragraph(
    "This project provided hands-on experience with full-stack web development and big data analytics integration. "
    "The key takeaways are:"
)

add_bullet("Successfully integrated Apache Spark with a PHP/MySQL web application via JDBC, demonstrating that "
           "big data processing engines can enhance traditional web applications without replacing them.")
add_bullet("Learned the complete Spark data pipeline: JDBC read → in-memory DataFrame transformations (groupBy, "
           "join, Window functions, UDFs) → JDBC write — a pattern applicable to any database-backed analytics project.")
add_bullet("Implemented rule-based AI insights (spike detection, spending projections, pattern analysis) that provide "
           "genuinely actionable financial intelligence — moving beyond simple CRUD applications.")
add_bullet("Gained practical understanding of the 5 V's of Big Data and how they apply to real-world systems, "
           "including data quality handling (Veracity), mixed format support (Variety), and value generation.")
add_bullet("Understood the difference between batch and stream processing, and when each is appropriate — "
           "batch processing is ideal for periodic analytics, while streaming suits real-time dashboards.")
add_bullet("Developed proficiency in data visualization using Chart.js, including interactive chart design with "
           "tooltips, gradient fills, period switching, and responsive layouts.")
add_bullet("Practiced secure web development with prepared statements (SQL injection prevention), "
           "bcrypt password hashing, and session-based authentication.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                     6. FUTURE SCOPE
# ══════════════════════════════════════════════════════════════

add_heading_styled("6. Future Scope", level=1)

doc.add_paragraph(
    "The current system serves as a robust foundation that can be extended with the following enhancements:"
)

add_para("1. Spark Structured Streaming (Real-Time Analytics)", bold=True)
doc.add_paragraph(
    "Currently, the Spark job runs in batch mode. Implementing Spark Structured Streaming would allow the system "
    "to process each new expense in real-time (<1 second), keeping the dashboard always up-to-date without "
    "manual spark-submit runs."
)

add_para("2. Machine Learning — Spending Prediction (MLlib)", bold=True)
doc.add_paragraph(
    "Replace rule-based insights with Spark MLlib models. A Linear Regression or Time Series model trained on "
    "2 years of historical data could predict next month's spending with confidence intervals, providing more "
    "accurate projections than the current daily burn rate extrapolation."
)

add_para("3. Anomaly Detection (Z-Score / IQR)", bold=True)
doc.add_paragraph(
    "Use statistical methods to flag individual outlier transactions — not just category-level spikes. A Z-score "
    "approach using Spark Window functions could identify expenses that are 2+ standard deviations above the "
    "category average (e.g., 'Your ₹16,827 Healthcare expense is 3.2σ above your average of ₹2,500')."
)

add_para("4. Budget Forecasting with Seasonality", bold=True)
doc.add_paragraph(
    "Incorporate seasonal spending patterns (e.g., higher spending in December holidays, lower in January). "
    "Calculate monthly seasonal indices from historical data and apply them to projections for more accurate "
    "end-of-month forecasts."
)

add_para("5. CSV Bank Statement Import", bold=True)
doc.add_paragraph(
    "Allow users to upload CSV bank statements or credit card statements. Spark's CSV reader could parse and "
    "map bank columns to the expense schema, with keyword-based auto-categorization (e.g., 'SWIGGY' → Food, "
    "'UBER' → Transport). This would enable bulk import of hundreds of transactions."
)

add_para("6. NLP-Based Auto-Categorization", bold=True)
doc.add_paragraph(
    "Use Spark MLlib's NLP pipeline (Tokenizer → HashingTF → IDF → NaiveBayes) to train a text classifier on "
    "expense descriptions. The model would automatically suggest categories for new expenses based on their "
    "description text (e.g., typing 'uber ride' auto-suggests 'Transport')."
)

add_para("7. Multi-User Comparative Analytics", bold=True)
doc.add_paragraph(
    "Implement anonymous benchmarking — compare a user's spending against aggregated community averages without "
    "revealing individual data. This provides context (e.g., 'Your Food spending is 15% above the community "
    "average of ₹4,350')."
)

add_para("8. Cloud Deployment (AWS EMR / Databricks)", bold=True)
doc.add_paragraph(
    "Migrate from local mode to a cloud Spark cluster (AWS EMR, Azure HDInsight, or Databricks). This enables "
    "handling millions of users, scheduled cron-based Spark jobs (e.g., daily at midnight), auto-scaling, "
    "and production-grade reliability."
)

add_para("9. Receipt OCR Integration", bold=True)
doc.add_paragraph(
    "Integrate Optical Character Recognition (Tesseract or Google Vision API) to allow users to photograph "
    "paper receipts. The OCR engine would extract amount, date, and merchant name, auto-creating expense records."
)

add_para("10. Predictive Alerts and Goal Tracking", bold=True)
doc.add_paragraph(
    "Allow users to set savings goals (e.g., 'Save ₹10,000 this month') and receive predictive alerts when "
    "spending patterns indicate the goal won't be met. The system would calculate when budget breach will occur "
    "and suggest daily spending limits to stay on track."
)

add_para("Future Improvements Summary:", bold=True)
add_table(
    ["#", "Improvement", "Technology", "V Addressed", "Complexity"],
    [
        ["1", "Real-time Streaming", "Spark Structured Streaming", "Velocity", "Medium"],
        ["2", "Spending Prediction", "Spark MLlib (Linear Regression)", "Value", "Medium"],
        ["3", "Anomaly Detection", "Z-score / IQR statistics", "Veracity, Value", "Low"],
        ["4", "Seasonal Forecasting", "Moving averages + seasonal index", "Value", "Low"],
        ["5", "CSV Bank Import", "Spark CSV reader", "Variety, Volume", "Low"],
        ["6", "NLP Auto-Categorization", "Spark MLlib (NaiveBayes NLP)", "Variety, Value", "High"],
        ["7", "Comparative Analytics", "Aggregate benchmarking", "Value", "Medium"],
        ["8", "Cloud Deployment", "AWS EMR / Databricks", "Volume, Velocity", "High"],
        ["9", "Receipt OCR", "Tesseract / Google Vision", "Variety", "High"],
        ["10", "Predictive Alerts", "Goal tracking + projections", "Value", "Medium"],
    ]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
#                7. TEAM MEMBERS CONTRIBUTION
# ══════════════════════════════════════════════════════════════

add_heading_styled("7. Team Members Contribution", level=1)

add_table(
    ["Team Member", "Roll No.", "Contribution Area", "Key Tasks"],
    [
        ["[Student Name 1]", "[Roll No.]", "Frontend Development & UI/UX", "Dashboard design, Chart.js integration, responsive layouts, CSS styling, theme system"],
        ["[Student Name 2]", "[Roll No.]", "Backend Development & API", "PHP REST APIs, MySQL schema design, authentication system, session management"],
        ["[Student Name 3]", "[Roll No.]", "Spark Analytics Engine", "PySpark pipeline, JDBC integration, 5 analytics computations, insight generation"],
        ["[Student Name 4]", "[Roll No.]", "Testing & Documentation", "Test data generation, system testing, project report, environment setup documentation"],
    ]
)

doc.add_paragraph()
doc.add_paragraph(
    "Note: All team members collaborated on system integration, debugging, and presentation preparation. "
    "The contribution areas listed above represent the primary responsibilities of each member."
)

# ══════════════════════════════════════════════════════════════
#                       SAVE
# ══════════════════════════════════════════════════════════════

output_path = r"c:\xampp\htdocs\personal_expense\Project_Report.docx"
doc.save(output_path)
print(f"✅ Report generated successfully: {output_path}")
print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")
