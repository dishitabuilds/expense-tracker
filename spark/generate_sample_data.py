"""
=============================================================
Sample Data Generator for Expense Tracker
=============================================================
Generates 10,000+ synthetic expense records and inserts them
directly into the MySQL database (XAMPP) for demo/testing.

Usage:
    python generate_sample_data.py

This script:
  - Uses existing categories from the database
  - Creates 3-5 test users if needed
  - Generates realistic expenses over a 2-year period
  - Distributes amounts realistically per category
=============================================================
"""

import mysql.connector
import random
from datetime import datetime, timedelta
import hashlib


# ============================================================
# Configuration
# ============================================================
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "personal_expense_tracker"
}

# Number of records to generate
TARGET_ROWS = 10000

# Test users to create (username, email)
TEST_USERS = [
    ("spark_user1", "spark_user1@demo.com"),
    ("spark_user2", "spark_user2@demo.com"),
    ("spark_user3", "spark_user3@demo.com"),
]

# Category configurations: name -> (min_amount, max_amount, frequency_weight)
# frequency_weight controls how likely this category is to appear
CATEGORY_CONFIG = {
    "Food & Dining":     (50, 2000, 25),
    "Transportation":    (20, 1500, 15),
    "Shopping":          (100, 5000, 12),
    "Entertainment":     (50, 3000, 10),
    "Bills & Utilities": (200, 8000, 8),
    "Healthcare":        (100, 10000, 5),
    "Education":         (200, 15000, 5),
    "Other":             (50, 3000, 10),
    # Generic fallback for unknown categories
    "_default":          (100, 3000, 10),
}

# Sample descriptions per category
DESCRIPTIONS = {
    "Food & Dining": [
        "Lunch at restaurant", "Grocery shopping", "Coffee shop",
        "Dinner out", "Food delivery", "Bakery", "Street food",
        "Monthly groceries", "Snacks", "Ice cream", "Fast food",
        "Home cooking supplies", "Breakfast", "Fruits & vegetables"
    ],
    "Transportation": [
        "Uber ride", "Petrol", "Bus ticket", "Metro card recharge",
        "Ola cab", "Auto rickshaw", "Parking fee", "Car service",
        "Monthly bus pass", "Train ticket", "Toll fee", "Bike service"
    ],
    "Shopping": [
        "New clothes", "Electronics", "Amazon order", "Flipkart purchase",
        "Shoes", "Home decor", "Kitchen items", "Book purchase",
        "Gifts", "Personal care items", "Accessories", "Stationery"
    ],
    "Entertainment": [
        "Movie tickets", "Netflix subscription", "Gaming",
        "Concert tickets", "Spotify premium", "YouTube premium",
        "Amusement park", "Bowling", "Sports event", "Streaming service"
    ],
    "Bills & Utilities": [
        "Electricity bill", "Water bill", "Internet bill",
        "Phone bill", "Gas bill", "Society maintenance",
        "Insurance premium", "DTH recharge", "Rent", "EMI payment"
    ],
    "Healthcare": [
        "Doctor consultation", "Medicines", "Lab tests",
        "Dental checkup", "Eye checkup", "Health insurance",
        "Gym membership", "Fitness supplements", "Physiotherapy"
    ],
    "Education": [
        "Course fee", "Textbooks", "Online course", "Tuition fee",
        "Coaching class", "Certification exam", "Workshop fee",
        "Study materials", "Library membership"
    ],
    "Other": [
        "ATM withdrawal", "Donation", "Miscellaneous",
        "Gift to friend", "Pet supplies", "Home repair",
        "Laundry", "Courier charges", "Subscription"
    ],
}


def get_connection():
    """Create MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def hash_password(password):
    """Create a bcrypt-compatible hash (using PHP-compatible format)."""
    # Generate a simple hash for demo users
    # In production, PHP's password_hash() generates proper bcrypt
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def simple_hash(password):
    """Fallback simple hash if bcrypt not available."""
    return "$2y$10$" + hashlib.sha256(password.encode()).hexdigest()[:53]


def ensure_test_users(conn):
    """Create test users if they don't exist. Returns list of user IDs."""
    cursor = conn.cursor()
    user_ids = []

    for username, email in TEST_USERS:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            user_ids.append(result[0])
            print(f"  ✓ User '{username}' already exists (ID: {result[0]})")
        else:
            try:
                pwd_hash = simple_hash("password123")
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, pwd_hash)
                )
                conn.commit()
                user_ids.append(cursor.lastrowid)
                print(f"  ✓ Created user '{username}' (ID: {cursor.lastrowid})")
            except Exception as e:
                print(f"  ⚠ Could not create user '{username}': {e}")
                conn.rollback()

    cursor.close()
    return user_ids


def ensure_categories(conn, user_ids):
    """Ensure each user has categories. Returns {user_id: [{id, name, ...}]}."""
    cursor = conn.cursor(dictionary=True)
    user_categories = {}

    default_categories = [
        ("Food & Dining", "#ef4444", "utensils"),
        ("Transportation", "#3b82f6", "car"),
        ("Shopping", "#8b5cf6", "shopping-bag"),
        ("Entertainment", "#ec4899", "film"),
        ("Bills & Utilities", "#f59e0b", "file-text"),
        ("Healthcare", "#10b981", "heart"),
        ("Education", "#06b6d4", "book"),
        ("Other", "#6b7280", "tag"),
    ]

    for uid in user_ids:
        cursor.execute("SELECT id, name FROM categories WHERE user_id = %s", (uid,))
        cats = cursor.fetchall()

        if len(cats) >= 4:
            user_categories[uid] = cats
            print(f"  ✓ User {uid} has {len(cats)} categories")
        else:
            # Create default categories
            for name, color, icon in default_categories:
                try:
                    cursor.execute(
                        "INSERT INTO categories (user_id, name, color, icon) VALUES (%s, %s, %s, %s)",
                        (uid, name, color, icon)
                    )
                except:
                    pass
            conn.commit()
            cursor.execute("SELECT id, name FROM categories WHERE user_id = %s", (uid,))
            user_categories[uid] = cursor.fetchall()
            print(f"  ✓ Created categories for user {uid}")

    cursor.close()
    return user_categories


def generate_expenses(user_categories, total_rows):
    """Generate synthetic expense records."""
    records = []
    now = datetime.now()
    two_years_ago = now - timedelta(days=730)

    # Distribute rows across users
    user_ids = list(user_categories.keys())
    rows_per_user = total_rows // len(user_ids)
    remainder = total_rows % len(user_ids)

    for idx, uid in enumerate(user_ids):
        user_rows = rows_per_user + (1 if idx < remainder else 0)
        cats = user_categories[uid]

        # Build weighted category list
        weighted_cats = []
        for cat in cats:
            cat_name = cat["name"]
            config = CATEGORY_CONFIG.get(cat_name, CATEGORY_CONFIG["_default"])
            weight = config[2]
            weighted_cats.extend([(cat, config)] * weight)

        for _ in range(user_rows):
            # Pick random category (weighted)
            cat, (min_amt, max_amt, _) = random.choice(weighted_cats)

            # Generate realistic amount (log-normal-ish distribution)
            # Most expenses are small, a few are large
            amount = round(random.uniform(min_amt, max_amt) *
                           random.choice([0.3, 0.5, 0.7, 0.8, 1.0, 1.0, 1.2, 1.5]), 2)
            amount = max(amount, min_amt)
            amount = min(amount, max_amt * 1.5)

            # Random date in last 2 years (more recent dates weighted)
            days_ago = int(random.triangular(0, 730, 60))  # bias towards recent
            expense_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            # Pick description
            cat_name = cat["name"]
            desc_list = DESCRIPTIONS.get(cat_name, DESCRIPTIONS["Other"])
            description = random.choice(desc_list)

            records.append((uid, cat["id"], amount, description, expense_date))

    random.shuffle(records)
    return records


def insert_expenses(conn, records, batch_size=500):
    """Insert expense records in batches."""
    cursor = conn.cursor()
    total = len(records)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        cursor.executemany(
            "INSERT INTO expenses (user_id, category_id, amount, description, expense_date) "
            "VALUES (%s, %s, %s, %s, %s)",
            batch
        )
        conn.commit()
        inserted += len(batch)
        pct = (inserted / total) * 100
        print(f"  → Inserted {inserted}/{total} records ({pct:.1f}%)", end="\r")

    print(f"\n  ✓ All {total} records inserted successfully!")
    cursor.close()


def show_summary(conn):
    """Show summary statistics after generation."""
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM expenses")
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT u.username, COUNT(e.id) as expense_count,
               ROUND(SUM(e.amount), 2) as total_amount,
               ROUND(AVG(e.amount), 2) as avg_amount,
               MIN(e.expense_date) as earliest,
               MAX(e.expense_date) as latest
        FROM expenses e
        JOIN users u ON e.user_id = u.id
        GROUP BY u.id, u.username
        ORDER BY expense_count DESC
    """)
    users = cursor.fetchall()

    print("\n" + "=" * 70)
    print("  📊 Database Summary")
    print("=" * 70)
    print(f"  Total expenses in database: {total}")
    print(f"  {'User':<20} {'Count':<10} {'Total (₹)':<15} {'Avg (₹)':<12} {'Date Range'}")
    print("  " + "-" * 65)

    for u in users:
        print(f"  {u['username']:<20} {u['expense_count']:<10} "
              f"{u['total_amount']:>12,.2f} {u['avg_amount']:>10,.2f}   "
              f"{u['earliest']} → {u['latest']}")

    cursor.close()


def main():
    print("\n" + "=" * 60)
    print("  🔧 Expense Tracker — Sample Data Generator")
    print(f"  Target: {TARGET_ROWS:,} expense records")
    print("=" * 60)

    conn = get_connection()

    try:
        # 1. Ensure test users exist
        print("\n👤 Setting up test users...")
        user_ids = ensure_test_users(conn)

        if not user_ids:
            print("❌ No users available. Cannot generate data.")
            return

        # 2. Ensure categories exist
        print("\n📁 Setting up categories...")
        user_categories = ensure_categories(conn, user_ids)

        # 3. Generate expense data
        print(f"\n📝 Generating {TARGET_ROWS:,} expense records...")
        records = generate_expenses(user_categories, TARGET_ROWS)

        # 4. Insert into database
        print(f"\n💾 Inserting into MySQL...")
        insert_expenses(conn, records)

        # 5. Show summary
        show_summary(conn)

        print("\n✅ Data generation complete!")
        print("   You can now run spark_analytics.py to process this data.\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
