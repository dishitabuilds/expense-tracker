"""
=============================================================
Apache Spark Analytics Engine for Personal Expense Tracker
=============================================================
Connects to MySQL (XAMPP) via JDBC, reads expense data,
performs aggregation analytics, smart insights & recommendations,
and writes results back to MySQL summary tables.

Usage:
    spark-submit --jars <path-to-mysql-connector-j.jar> spark_analytics.py

Requirements:
    - Apache Spark 3.5.x
    - MySQL Connector/J JAR in Spark's classpath
    - MySQL running on XAMPP (localhost:3306)
=============================================================
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, IntegerType, DoubleType
import json
from datetime import datetime, timedelta


# ============================================================
# Configuration
# ============================================================
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "personal_expense_tracker",
    "user": "root",
    "password": ""
}

JDBC_URL = f"jdbc:mysql://{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"

JDBC_PROPERTIES = {
    "user": MYSQL_CONFIG["user"],
    "password": MYSQL_CONFIG["password"],
    "driver": "com.mysql.cj.jdbc.Driver"
}


def create_spark_session():
    """Create and return a SparkSession with MySQL JDBC support."""
    spark = SparkSession.builder \
        .appName("ExpenseTracker_SparkAnalytics") \
        .master("local[*]") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .config("spark.sql.session.timeZone", "Asia/Kolkata") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print("=" * 60)
    print("  Spark Session Created Successfully")
    print(f"  Spark Version: {spark.version}")
    print("=" * 60)
    return spark


def read_table(spark, table_name):
    """Read a MySQL table into a Spark DataFrame."""
    df = spark.read.jdbc(
        url=JDBC_URL,
        table=table_name,
        properties=JDBC_PROPERTIES
    )
    count = df.count()
    print(f"  ✓ Loaded '{table_name}': {count} rows")
    return df


def write_table(df, table_name, mode="overwrite"):
    """Write a Spark DataFrame to a MySQL table."""
    df.write.jdbc(
        url=JDBC_URL,
        table=table_name,
        mode=mode,
        properties=JDBC_PROPERTIES
    )
    print(f"  ✓ Written to '{table_name}' (mode={mode})")


# ============================================================
# Analytics: Monthly Summary
# ============================================================
def compute_monthly_summary(expenses_df):
    """
    Aggregate monthly totals per user.
    Output columns: user_id, year, month, month_name, total_amount,
                    transaction_count, avg_amount, max_amount, min_amount
    """
    print("\n📊 Computing Monthly Summary...")

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    # Create a mapping UDF
    @F.udf(StringType())
    def get_month_name(m):
        return month_names.get(m, "Unknown")

    summary = expenses_df \
        .withColumn("year", F.year("expense_date")) \
        .withColumn("month", F.month("expense_date")) \
        .groupBy("user_id", "year", "month") \
        .agg(
            F.round(F.sum("amount"), 2).alias("total_amount"),
            F.count("*").alias("transaction_count"),
            F.round(F.avg("amount"), 2).alias("avg_amount"),
            F.round(F.max("amount"), 2).alias("max_amount"),
            F.round(F.min("amount"), 2).alias("min_amount")
        ) \
        .withColumn("month_name", get_month_name(F.col("month"))) \
        .withColumn("generated_at", F.current_timestamp()) \
        .orderBy("user_id", "year", "month")

    row_count = summary.count()
    print(f"  → {row_count} monthly summary rows generated")
    return summary


# ============================================================
# Analytics: Category Summary
# ============================================================
def compute_category_summary(expenses_df, categories_df):
    """
    Category-wise spending per user per month.
    Output columns: user_id, year, month, category_name, category_color,
                    total_amount, transaction_count, percentage, avg_amount
    """
    print("\n📊 Computing Category Summary...")

    # Join expenses with categories
    joined = expenses_df.join(
        categories_df.select(
            F.col("id").alias("cat_id"),
            F.col("name").alias("category_name"),
            F.col("color").alias("category_color")
        ),
        expenses_df["category_id"] == F.col("cat_id"),
        "left"
    ).fillna({"category_name": "Uncategorized", "category_color": "#6b7280"})

    # Aggregate by user, year, month, category
    cat_totals = joined \
        .withColumn("year", F.year("expense_date")) \
        .withColumn("month", F.month("expense_date")) \
        .groupBy("user_id", "year", "month", "category_name", "category_color") \
        .agg(
            F.round(F.sum("amount"), 2).alias("total_amount"),
            F.count("*").alias("transaction_count"),
            F.round(F.avg("amount"), 2).alias("avg_amount")
        )

    # Calculate percentage within each user-month
    window = Window.partitionBy("user_id", "year", "month")
    cat_summary = cat_totals \
        .withColumn(
            "percentage",
            F.round(
                (F.col("total_amount") / F.sum("total_amount").over(window)) * 100,
                2
            )
        ) \
        .withColumn("generated_at", F.current_timestamp()) \
        .orderBy("user_id", "year", "month", F.desc("total_amount"))

    row_count = cat_summary.count()
    print(f"  → {row_count} category summary rows generated")
    return cat_summary


# ============================================================
# Analytics: Trend Summary (Weekly / Monthly / Yearly)
# ============================================================
def compute_trend_summary(expenses_df):
    """
    Compute spending trends at three granularities.

    Weekly:  Based on ISO 8601 week numbers. Each week starts on Monday
             and ends on Sunday. Labels show actual date range, e.g.
             'Jan 6 - Jan 12' so data is unambiguous.
    Monthly: Calendar months, labeled 'MMM yyyy' (e.g. 'Apr 2026').
    Yearly:  Full calendar years.

    Output columns: user_id, period_type, period_label,
                    period_start, period_end, total_amount,
                    transaction_count, avg_daily
    """
    print("\n📊 Computing Trend Summary...")

    all_trends = None

    # --- Weekly Trends (last 12 ISO weeks) ---
    # ISO 8601: week starts Monday, ends Sunday. weekofyear() returns ISO week.
    twelve_weeks_ago = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")

    weekly = expenses_df \
        .filter(F.col("expense_date") >= F.lit(twelve_weeks_ago)) \
        .withColumn("iso_week", F.weekofyear("expense_date")) \
        .withColumn("iso_year", F.year("expense_date")) \
        .groupBy("user_id", "iso_year", "iso_week") \
        .agg(
            F.round(F.sum("amount"), 2).alias("total_amount"),
            F.count("*").alias("transaction_count"),
            F.min("expense_date").alias("period_start"),
            F.max("expense_date").alias("period_end")
        ) \
        .withColumn("period_type", F.lit("weekly")) \
        .withColumn("avg_daily", F.round(F.col("total_amount") / 7, 2)) \
        .withColumn(
            "period_label",
            F.concat(
                F.date_format("period_start", "MMM d"),
                F.lit(" - "),
                F.date_format("period_end", "MMM d")
            )
        ) \
        .drop("iso_year", "iso_week")

    # --- Monthly Trends (last 12 calendar months) ---
    twelve_months_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    monthly = expenses_df \
        .filter(F.col("expense_date") >= F.lit(twelve_months_ago)) \
        .withColumn("year", F.year("expense_date")) \
        .withColumn("month", F.month("expense_date")) \
        .withColumn("period_label",
                     F.date_format("expense_date", "MMM yyyy")) \
        .groupBy("user_id", "period_label") \
        .agg(
            F.round(F.sum("amount"), 2).alias("total_amount"),
            F.count("*").alias("transaction_count"),
            F.min("expense_date").alias("period_start"),
            F.max("expense_date").alias("period_end")
        ) \
        .withColumn("period_type", F.lit("monthly")) \
        .withColumn("avg_daily", F.round(F.col("total_amount") / 30, 2))

    # --- Yearly Trends ---
    yearly = expenses_df \
        .withColumn("year", F.year("expense_date")) \
        .withColumn("period_label", F.col("year").cast(StringType())) \
        .groupBy("user_id", "period_label") \
        .agg(
            F.round(F.sum("amount"), 2).alias("total_amount"),
            F.count("*").alias("transaction_count"),
            F.min("expense_date").alias("period_start"),
            F.max("expense_date").alias("period_end")
        ) \
        .withColumn("period_type", F.lit("yearly")) \
        .withColumn("avg_daily", F.round(F.col("total_amount") / 365, 2))

    # Union all trends
    select_cols = ["user_id", "period_type", "period_label",
                   "period_start", "period_end", "total_amount",
                   "transaction_count", "avg_daily"]

    all_trends = weekly.select(select_cols) \
        .union(monthly.select(select_cols)) \
        .union(yearly.select(select_cols)) \
        .withColumn("generated_at", F.current_timestamp())

    row_count = all_trends.count()
    print(f"  → {row_count} trend summary rows generated")
    return all_trends


# ============================================================
# Smart Insights (2 per user, rule-based)
# ============================================================
def compute_smart_insights(expenses_df, categories_df):
    """
    Generate 2 smart spending insights per user:
    1. Month-over-Month Spike Detection — compares THIS month vs LAST month
       per category. Detects any category with >25% increase and flags it
       with the exact change amount and percentage.
    2. End-of-Month Projection with Comparison — projects total spending
       based on daily burn rate AND compares against last month's final total
       to show whether the user is on track to spend more or less.
    """
    print("\n🤖 Computing Smart Insights...")

    from pyspark.sql import Row
    import calendar

    now = datetime.now()
    current_year = now.year
    current_month = now.month
    day_of_month = now.day
    days_in_month = calendar.monthrange(current_year, current_month)[1]

    # Previous month calculation
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    prev_month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    prev_month_name = prev_month_names[prev_month]

    # Join with category names
    joined = expenses_df.join(
        categories_df.select(
            F.col("id").alias("cat_id"),
            F.col("name").alias("category_name")
        ),
        expenses_df["category_id"] == F.col("cat_id"),
        "left"
    ).fillna({"category_name": "Uncategorized"})

    # Get list of user_ids
    user_ids = [row.user_id for row in expenses_df.select("user_id").distinct().collect()]

    insights_rows = []

    for uid in user_ids:
        user_expenses = joined.filter(F.col("user_id") == uid)

        # ---- Insight 1: Month-over-Month Spike Detection ----
        # Current month spending per category
        current_month_cat = user_expenses \
            .filter(
                (F.year("expense_date") == current_year) &
                (F.month("expense_date") == current_month)
            ) \
            .groupBy("category_name") \
            .agg(F.round(F.sum("amount"), 2).alias("current_total")) \
            .collect()

        # Last month spending per category (direct comparison)
        last_month_cat = user_expenses \
            .filter(
                (F.year("expense_date") == prev_year) &
                (F.month("expense_date") == prev_month)
            ) \
            .groupBy("category_name") \
            .agg(F.round(F.sum("amount"), 2).alias("last_total")) \
            .collect()

        last_dict = {row.category_name: float(row.last_total) for row in last_month_cat}

        biggest_spike = None
        biggest_spike_pct = 0

        for row in current_month_cat:
            cat_name = row.category_name
            current = float(row.current_total)
            last_val = last_dict.get(cat_name, 0)

            if last_val > 0:
                change_pct = ((current - last_val) / last_val) * 100
                # Detect spike: >25% increase vs last month
                if change_pct > biggest_spike_pct and change_pct > 25:
                    biggest_spike_pct = change_pct
                    biggest_spike = {
                        "category": cat_name,
                        "current": current,
                        "last_month": last_val,
                        "change_amount": round(current - last_val, 2),
                        "change_pct": round(change_pct, 1)
                    }

        if biggest_spike:
            severity = "critical" if biggest_spike["change_pct"] > 75 else "warning"
            insights_rows.append(Row(
                user_id=uid,
                insight_type="spending_spike",
                category=biggest_spike["category"],
                message=(
                    f"🔺 Spike Detected: {biggest_spike['category']} spending surged "
                    f"{biggest_spike['change_pct']}% vs {prev_month_name} "
                    f"(₹{biggest_spike['last_month']:,.0f} → ₹{biggest_spike['current']:,.0f}, "
                    f"+₹{biggest_spike['change_amount']:,.0f}). "
                    f"This is your biggest month-over-month increase."
                ),
                severity=severity,
                score=float(biggest_spike["change_pct"]),
                metadata=json.dumps(biggest_spike)
            ))
        else:
            # No spike — show top category with last-month comparison
            if current_month_cat:
                top = max(current_month_cat, key=lambda r: r.current_total)
                top_name = top.category_name
                top_current = float(top.current_total)
                top_last = last_dict.get(top_name, 0)

                if top_last > 0:
                    change_pct = ((top_current - top_last) / top_last) * 100
                    direction = "up" if change_pct > 0 else "down"
                    arrow = "↑" if change_pct > 0 else "↓"
                    msg = (
                        f"Top category: {top_name} at ₹{top_current:,.0f} this month "
                        f"({arrow} {abs(change_pct):.1f}% {direction} from ₹{top_last:,.0f} in {prev_month_name}). "
                        f"No major spending spikes detected — your spending is stable."
                    )
                else:
                    msg = (
                        f"Top category: {top_name} at ₹{top_current:,.0f} this month. "
                        f"This is a new category compared to {prev_month_name}."
                    )

                insights_rows.append(Row(
                    user_id=uid,
                    insight_type="top_category",
                    category=top_name,
                    message=msg,
                    severity="info",
                    score=top_current,
                    metadata=json.dumps({
                        "category": top_name,
                        "current": top_current,
                        "last_month": top_last
                    })
                ))

        # ---- Insight 2: End-of-Month Projection vs Last Month ----
        current_month_total = user_expenses \
            .filter(
                (F.year("expense_date") == current_year) &
                (F.month("expense_date") == current_month)
            ) \
            .agg(F.round(F.sum("amount"), 2).alias("total")) \
            .collect()

        last_month_total = user_expenses \
            .filter(
                (F.year("expense_date") == prev_year) &
                (F.month("expense_date") == prev_month)
            ) \
            .agg(F.round(F.sum("amount"), 2).alias("total")) \
            .collect()

        total_spent = float(current_month_total[0].total or 0)
        last_total = float(last_month_total[0].total or 0)

        if total_spent > 0 and day_of_month > 0:
            daily_rate = total_spent / day_of_month
            projected = daily_rate * days_in_month
            remaining_days = days_in_month - day_of_month

            # Compare projection with last month's actual
            if last_total > 0:
                proj_vs_last = ((projected - last_total) / last_total) * 100
                if proj_vs_last > 0:
                    comparison = f"That's {proj_vs_last:.1f}% MORE than {prev_month_name}'s total of ₹{last_total:,.0f}."
                    sev = "warning" if proj_vs_last > 20 else "info"
                else:
                    comparison = f"That's {abs(proj_vs_last):.1f}% LESS than {prev_month_name}'s total of ₹{last_total:,.0f}. Good job!"
                    sev = "success"
            else:
                comparison = f"No data from {prev_month_name} to compare."
                sev = "info"

            insights_rows.append(Row(
                user_id=uid,
                insight_type="monthly_projection",
                category="Overall",
                message=(
                    f"Spending ₹{daily_rate:,.0f}/day so far → projected ₹{projected:,.0f} by month end "
                    f"({remaining_days} days left, ₹{total_spent:,.0f} spent). {comparison}"
                ),
                severity=sev,
                score=float(projected),
                metadata=json.dumps({
                    "daily_rate": round(daily_rate, 2),
                    "projected": round(projected, 2),
                    "spent_so_far": round(total_spent, 2),
                    "remaining_days": remaining_days,
                    "last_month_total": round(last_total, 2),
                    "proj_vs_last_pct": round(proj_vs_last if last_total > 0 else 0, 1)
                })
            ))

    if insights_rows:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        insights_df = spark.createDataFrame(insights_rows) \
            .withColumn("generated_at", F.current_timestamp())
        print(f"  → {len(insights_rows)} insights generated")
        return insights_df
    else:
        print("  → No insights generated (insufficient data)")
        return None


# ============================================================
# Smart Recommendations (2 per user, rule-based)
# ============================================================
def compute_smart_recommendations(expenses_df, categories_df):
    """
    Generate 2 smart recommendations per user:
    1. Category Optimization — highest month-over-month growth category
    2. Weekend vs Weekday Pattern — spending pattern analysis
    """
    print("\n🤖 Computing Smart Recommendations...")

    from pyspark.sql import Row

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Join with category names
    joined = expenses_df.join(
        categories_df.select(
            F.col("id").alias("cat_id"),
            F.col("name").alias("category_name")
        ),
        expenses_df["category_id"] == F.col("cat_id"),
        "left"
    ).fillna({"category_name": "Uncategorized"})

    user_ids = [row.user_id for row in expenses_df.select("user_id").distinct().collect()]

    rec_rows = []

    for uid in user_ids:
        user_expenses = joined.filter(F.col("user_id") == uid)

        # ---- Recommendation 1: Category with highest growth ----
        # Compare current month vs previous month per category
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1

        current_cats = user_expenses \
            .filter(
                (F.year("expense_date") == current_year) &
                (F.month("expense_date") == current_month)
            ) \
            .groupBy("category_name") \
            .agg(F.round(F.sum("amount"), 2).alias("current_total")) \
            .collect()

        prev_cats = user_expenses \
            .filter(
                (F.year("expense_date") == prev_year) &
                (F.month("expense_date") == prev_month)
            ) \
            .groupBy("category_name") \
            .agg(F.round(F.sum("amount"), 2).alias("prev_total")) \
            .collect()

        prev_dict = {row.category_name: float(row.prev_total) for row in prev_cats}

        highest_growth = None
        highest_growth_pct = 0

        for row in current_cats:
            cat = row.category_name
            current = float(row.current_total)
            prev = prev_dict.get(cat, 0)

            if prev > 0:
                growth_pct = ((current - prev) / prev) * 100
                if growth_pct > highest_growth_pct and growth_pct > 20:
                    highest_growth_pct = growth_pct
                    highest_growth = {
                        "category": cat,
                        "current": current,
                        "previous": prev,
                        "growth_pct": round(growth_pct, 1),
                        "savings": round(current - prev, 2)
                    }

        if highest_growth:
            suggested_cap = round(highest_growth["previous"] * 1.1, 2)
            rec_rows.append(Row(
                user_id=uid,
                rec_type="category_optimization",
                category=highest_growth["category"],
                message=f"Your {highest_growth['category']} spending grew {highest_growth['growth_pct']}% from last month (₹{highest_growth['previous']:,.0f} → ₹{highest_growth['current']:,.0f}). Consider capping at ₹{suggested_cap:,.0f} to save ₹{highest_growth['savings']:,.0f}/month.",
                priority="high" if highest_growth_pct > 50 else "medium",
                potential_savings=float(highest_growth["savings"]),
                current_spending=float(highest_growth["current"]),
                metadata=json.dumps(highest_growth)
            ))
        else:
            # Fallback: suggest a budget for the top category
            if current_cats:
                top = max(current_cats, key=lambda r: r.current_total)
                suggested = round(float(top.current_total) * 0.9, 2)
                rec_rows.append(Row(
                    user_id=uid,
                    rec_type="budget_suggestion",
                    category=top.category_name,
                    message=f"Set a monthly budget of ₹{suggested:,.0f} for {top.category_name} (10% reduction from current ₹{float(top.current_total):,.0f}). Small reductions in your top category compound over time.",
                    priority="medium",
                    potential_savings=round(float(top.current_total) * 0.1, 2),
                    current_spending=float(top.current_total),
                    metadata=json.dumps({"category": top.category_name, "amount": float(top.current_total)})
                ))

        # ---- Recommendation 2: Weekend vs Weekday Pattern ----
        # Compare average daily spending: weekdays vs weekends
        thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

        recent = user_expenses \
            .filter(F.col("expense_date") >= F.lit(thirty_days_ago)) \
            .withColumn("day_of_week", F.dayofweek("expense_date"))

        # dayofweek: 1=Sunday, 7=Saturday in Spark
        weekend_spend = recent \
            .filter(F.col("day_of_week").isin(1, 7)) \
            .agg(
                F.round(F.sum("amount"), 2).alias("total"),
                F.countDistinct("expense_date").alias("days")
            ).collect()

        weekday_spend = recent \
            .filter(~F.col("day_of_week").isin(1, 7)) \
            .agg(
                F.round(F.sum("amount"), 2).alias("total"),
                F.countDistinct("expense_date").alias("days")
            ).collect()

        we_total = float(weekend_spend[0].total or 0)
        we_days = int(weekend_spend[0].days or 1)
        wd_total = float(weekday_spend[0].total or 0)
        wd_days = int(weekday_spend[0].days or 1)

        we_avg = we_total / max(we_days, 1)
        wd_avg = wd_total / max(wd_days, 1)

        if wd_avg > 0 and we_avg > 0:
            ratio = we_avg / wd_avg
            monthly_we_savings = round((we_avg - wd_avg) * 8, 2)  # ~8 weekend days/month

            if ratio > 1.5:
                rec_rows.append(Row(
                    user_id=uid,
                    rec_type="weekend_pattern",
                    category="Weekend Spending",
                    message=f"You spend {ratio:.1f}x more on weekends (₹{we_avg:,.0f}/day) vs weekdays (₹{wd_avg:,.0f}/day). Planning weekend activities in advance could save ₹{monthly_we_savings:,.0f}/month.",
                    priority="medium",
                    potential_savings=float(monthly_we_savings),
                    current_spending=float(we_total),
                    metadata=json.dumps({
                        "weekend_avg": round(we_avg, 2),
                        "weekday_avg": round(wd_avg, 2),
                        "ratio": round(ratio, 2)
                    })
                ))
            else:
                rec_rows.append(Row(
                    user_id=uid,
                    rec_type="consistent_spending",
                    category="Daily Pattern",
                    message=f"Your spending is fairly consistent across weekdays (₹{wd_avg:,.0f}/day) and weekends (₹{we_avg:,.0f}/day). Good discipline! Focus on reducing your top spending category for savings.",
                    priority="low",
                    potential_savings=0.0,
                    current_spending=float(we_total + wd_total),
                    metadata=json.dumps({
                        "weekend_avg": round(we_avg, 2),
                        "weekday_avg": round(wd_avg, 2)
                    })
                ))

    if rec_rows:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        rec_df = spark.createDataFrame(rec_rows) \
            .withColumn("generated_at", F.current_timestamp())
        print(f"  → {len(rec_rows)} recommendations generated")
        return rec_df
    else:
        print("  → No recommendations generated (insufficient data)")
        return None


# ============================================================
# Main Execution Pipeline
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("  🚀 Expense Tracker — Spark Analytics Pipeline")
    print("=" * 60)

    # 1. Create Spark session
    spark = create_spark_session()

    try:
        # 2. Read source data from MySQL
        print("\n📥 Reading data from MySQL...")
        expenses_df = read_table(spark, "expenses")
        categories_df = read_table(spark, "categories")

        if expenses_df.count() == 0:
            print("\n⚠️  No expense data found! Please add expenses first.")
            spark.stop()
            return

        # 3. Compute analytics
        monthly_df = compute_monthly_summary(expenses_df)
        category_df = compute_category_summary(expenses_df, categories_df)
        trend_df = compute_trend_summary(expenses_df)
        insights_df = compute_smart_insights(expenses_df, categories_df)
        recommendations_df = compute_smart_recommendations(expenses_df, categories_df)

        # 4. Write results back to MySQL
        print("\n📤 Writing results to MySQL...")
        write_table(monthly_df, "monthly_summary")
        write_table(category_df, "category_summary")
        write_table(trend_df, "trend_summary")

        if insights_df is not None:
            write_table(insights_df, "spark_insights")

        if recommendations_df is not None:
            write_table(recommendations_df, "spark_recommendations")

        # 5. Print summary
        print("\n" + "=" * 60)
        print("  ✅ Spark Analytics Pipeline Completed Successfully!")
        print("=" * 60)
        print(f"  Monthly Summary   : {monthly_df.count()} rows")
        print(f"  Category Summary  : {category_df.count()} rows")
        print(f"  Trend Summary     : {trend_df.count()} rows")
        if insights_df:
            print(f"  Smart Insights    : {insights_df.count()} rows")
        if recommendations_df:
            print(f"  Recommendations   : {recommendations_df.count()} rows")
        print(f"  Timestamp         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        spark.stop()
        print("\n🛑 Spark session stopped.")


if __name__ == "__main__":
    main()
