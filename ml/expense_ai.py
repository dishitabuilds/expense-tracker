"""
=============================================================================
AI-Powered Personal Expense Tracker — ML Pipeline
=============================================================================
Title   : Developing a Custom AI-based Solution for a Real-World Problem
Purpose : Train a machine learning model to predict expense categories from
          text descriptions and amounts, with full EDA, evaluation, and
          overfitting analysis.

Model   : TF-IDF Vectorizer + Logistic Regression (Multi-class Classification)
Dataset : 602 expense records across 8 categories

Author  : Personal Expense Tracker Team
Date    : April 2026
=============================================================================
"""

import os
import sys
import warnings
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)
from scipy.sparse import hstack

warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
VISUALS_DIR = os.path.join(BASE_DIR, 'visualizations')

# Ensure output directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

# ── Style Configuration ──────────────────────────────────────────────────────
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e',
           '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4']
sns.set_palette(COLORS)

print("=" * 70)
print("  AI-Powered Personal Expense Tracker — ML Pipeline")
print("=" * 70)

# =============================================================================
# SECTION 1: DATA LOADING & MERGING
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 1: DATA LOADING & MERGING")
print("━" * 70)

# Load both CSV datasets
df1 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset1.csv'))
df2 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset2.csv'))

print(f"\n✅ Dataset 1 loaded: {df1.shape[0]} rows × {df1.shape[1]} columns")
print(f"✅ Dataset 2 loaded: {df2.shape[0]} rows × {df2.shape[1]} columns")

# Merge into a single DataFrame
df = pd.concat([df1, df2], ignore_index=True)
print(f"\n📊 Combined Dataset: {df.shape[0]} rows × {df.shape[1]} columns")

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Display basic info
print(f"\n📋 Columns: {list(df.columns)}")
print(f"📅 Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"💰 Amount Range: ₹{df['amount'].min()} to ₹{df['amount'].max()}")
print(f"🏷️ Categories: {df['category'].nunique()} unique categories")
print(f"\n🔍 First 5 rows:")
print(df.head().to_string(index=False))

# =============================================================================
# SECTION 2: EXPLORATORY DATA ANALYSIS (EDA)
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 2: EXPLORATORY DATA ANALYSIS")
print("━" * 70)

# ── 2.1 Check for Missing Values ─────────────────────────────────────────────
print("\n📊 Missing Values:")
missing = df.isnull().sum()
print(missing.to_string())
if missing.sum() == 0:
    print("✅ No missing values found!")
else:
    print(f"⚠️ Found {missing.sum()} missing values. Cleaning...")
    df = df.dropna()
    print(f"✅ After cleaning: {df.shape[0]} rows remaining")

# ── 2.2 Category Distribution ────────────────────────────────────────────────
print("\n📊 Category Distribution:")
cat_counts = df['category'].value_counts()
for cat, count in cat_counts.items():
    pct = count / len(df) * 100
    bar = "█" * int(pct / 2)
    print(f"  {cat:15s} │ {count:3d} ({pct:5.1f}%) {bar}")

# ── 2.3 Amount Statistics per Category ────────────────────────────────────────
print("\n💰 Amount Statistics per Category:")
amount_stats = df.groupby('category')['amount'].agg(['mean', 'median', 'std', 'min', 'max'])
amount_stats.columns = ['Mean', 'Median', 'Std Dev', 'Min', 'Max']
print(amount_stats.round(2).to_string())

# ── 2.4 Generate Visualization: Class Distribution ───────────────────────────
print("\n📈 Generating visualizations...")

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(cat_counts.index, cat_counts.values, color=COLORS[:len(cat_counts)],
              edgecolor='white', linewidth=1.5)
ax.set_title('Expense Category Distribution', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Number of Transactions', fontsize=12)
ax.set_xticklabels(cat_counts.index, rotation=45, ha='right')

# Add value labels on bars
for bar, val in zip(bars, cat_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
            str(val), ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'class_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: class_distribution.png")

# ── 2.5 Generate Visualization: Word Cloud ───────────────────────────────────
all_descriptions = ' '.join(df['description'].str.lower().values)
wordcloud = WordCloud(
    width=1200, height=600,
    background_color='#1a1a2e',
    colormap='cool',
    max_words=100,
    contour_width=2,
    contour_color='#6366f1',
    font_path=None,  # Uses default
    prefer_horizontal=0.7
).generate(all_descriptions)

fig, ax = plt.subplots(figsize=(14, 7))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
ax.set_title('Expense Description Word Cloud', fontsize=16, fontweight='bold',
             pad=15, color='#333333')
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'word_cloud.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: word_cloud.png")

# ── 2.6 Generate Visualization: Amount Box Plot ──────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
category_order = df.groupby('category')['amount'].median().sort_values(ascending=False).index
sns.boxplot(data=df, x='category', y='amount', order=category_order,
            palette=COLORS[:len(cat_counts)], ax=ax, fliersize=4)
ax.set_title('Amount Distribution by Category', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Amount (₹)', fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'amount_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: amount_distribution.png")

# ── 2.7 Generate Visualization: Monthly Spending Trends ──────────────────────
df['year_month'] = df['date'].dt.to_period('M')
monthly = df.groupby('year_month')['amount'].sum().reset_index()
monthly['year_month'] = monthly['year_month'].astype(str)

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(range(len(monthly)), monthly['amount'], alpha=0.3, color='#6366f1')
ax.plot(range(len(monthly)), monthly['amount'], color='#6366f1', linewidth=2.5,
        marker='o', markersize=8, markerfacecolor='white', markeredgecolor='#6366f1',
        markeredgewidth=2)
ax.set_title('Monthly Spending Trend', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Total Spending (₹)', fontsize=12)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['year_month'], rotation=45, ha='right')

# Add value labels
for i, val in enumerate(monthly['amount']):
    ax.text(i, val + max(monthly['amount'])*0.02, f'₹{val:,.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'monthly_spending.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: monthly_spending.png")

# ── 2.8 Generate Visualization: Spending by Category Over Time ───────────────
monthly_cat = df.groupby(['year_month', 'category'])['amount'].sum().unstack(fill_value=0)
monthly_cat.index = monthly_cat.index.astype(str)

fig, ax = plt.subplots(figsize=(14, 7))
monthly_cat.plot(kind='bar', stacked=True, ax=ax, color=COLORS[:len(cat_counts)],
                 edgecolor='white', linewidth=0.5)
ax.set_title('Monthly Spending by Category', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Amount (₹)', fontsize=12)
ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'spending_trends.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: spending_trends.png")

# ── 2.9 Generate Visualization: Category Pie Chart ───────────────────────────
fig, ax = plt.subplots(figsize=(10, 10))
cat_amounts = df.groupby('category')['amount'].sum().sort_values(ascending=False)
wedges, texts, autotexts = ax.pie(
    cat_amounts.values, labels=cat_amounts.index,
    autopct='%1.1f%%', colors=COLORS[:len(cat_amounts)],
    pctdistance=0.85, startangle=140, textprops={'fontsize': 11}
)
# Draw circle for donut style
centre_circle = plt.Circle((0, 0), 0.60, fc='white')
ax.add_artist(centre_circle)
ax.set_title('Total Spending by Category', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'category_pie.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: category_pie.png")


# =============================================================================
# SECTION 3: DATA PREPROCESSING
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 3: DATA PREPROCESSING")
print("━" * 70)

# ── 3.1 Text Preprocessing ───────────────────────────────────────────────────
print("\n🔧 Preprocessing text descriptions...")
df['description_clean'] = df['description'].str.lower().str.strip()

# Show unique descriptions
unique_desc = df['description_clean'].nunique()
print(f"  Unique descriptions: {unique_desc}")
print(f"  Sample cleaned descriptions: {list(df['description_clean'].head(5))}")

# ── 3.2 Encode Labels ────────────────────────────────────────────────────────
label_encoder = LabelEncoder()
df['category_encoded'] = label_encoder.fit_transform(df['category'])
print(f"\n🏷️ Label Encoding:")
for i, label in enumerate(label_encoder.classes_):
    print(f"  {i} → {label}")

# ── 3.3 TF-IDF Vectorization ─────────────────────────────────────────────────
print("\n📝 Applying TF-IDF Vectorization...")
tfidf = TfidfVectorizer(
    max_features=500,       # Limit vocabulary size
    ngram_range=(1, 2),     # Unigrams + Bigrams for better context
    stop_words='english',   # Remove common English words
    sublinear_tf=True       # Apply sublinear TF scaling
)
X_text = tfidf.fit_transform(df['description_clean'])
print(f"  TF-IDF Matrix Shape: {X_text.shape}")
print(f"  Vocabulary Size: {len(tfidf.vocabulary_)}")
print(f"  Top 10 Features: {list(sorted(tfidf.vocabulary_, key=tfidf.vocabulary_.get))[:10]}")

# ── 3.4 Normalize Amount Feature ─────────────────────────────────────────────
print("\n💰 Normalizing amount feature...")
scaler = StandardScaler()
X_amount = scaler.fit_transform(df[['amount']])
print(f"  Amount Mean: ₹{df['amount'].mean():.2f}")
print(f"  Amount Std:  ₹{df['amount'].std():.2f}")

# ── 3.5 Combine Features ─────────────────────────────────────────────────────
# Combine TF-IDF text features + normalized amount
from scipy.sparse import csr_matrix
X_amount_sparse = csr_matrix(X_amount)
X_combined = hstack([X_text, X_amount_sparse])
y = df['category_encoded']

print(f"\n✅ Final Feature Matrix: {X_combined.shape}")
print(f"  Text features: {X_text.shape[1]}")
print(f"  Amount feature: 1")
print(f"  Total features: {X_combined.shape[1]}")


# =============================================================================
# SECTION 4: MODEL TRAINING
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 4: MODEL TRAINING")
print("━" * 70)

# ── 4.1 Train/Test Split ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y,
    test_size=0.2,          # 80% train, 20% test
    random_state=42,        # Reproducibility
    stratify=y              # Maintain class distribution
)

print(f"\n📊 Dataset Split:")
print(f"  Training Set: {X_train.shape[0]} samples ({X_train.shape[0]/len(y)*100:.1f}%)")
print(f"  Test Set:     {X_test.shape[0]} samples ({X_test.shape[0]/len(y)*100:.1f}%)")

# ── 4.2 Train Logistic Regression ────────────────────────────────────────────
print("\n🤖 Training Logistic Regression model...")
model = LogisticRegression(
    max_iter=1000,          # Ensure convergence
    solver='lbfgs',         # Optimal solver for multinomial
    C=1.0,                  # Regularization strength (inverse)
    random_state=42
)
model.fit(X_train, y_train)
print("  ✅ Model trained successfully!")

# ── 4.3 Training vs Test Accuracy ────────────────────────────────────────────
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)
print(f"\n📊 Accuracy Comparison:")
print(f"  Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
print(f"  Test Accuracy:     {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
print(f"  Difference:        {abs(train_accuracy - test_accuracy):.4f}")

if abs(train_accuracy - test_accuracy) < 0.05:
    print("  ✅ Good generalization (train-test gap < 5%)")
elif abs(train_accuracy - test_accuracy) < 0.10:
    print("  ⚠️ Slight overfitting detected (train-test gap 5-10%)")
else:
    print("  ❌ Overfitting detected! (train-test gap > 10%)")


# =============================================================================
# SECTION 5: MODEL EVALUATION
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 5: MODEL EVALUATION")
print("━" * 70)

# ── 5.1 Predictions ──────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
y_pred_labels = label_encoder.inverse_transform(y_pred)
y_test_labels = label_encoder.inverse_transform(y_test)

# ── 5.2 Classification Metrics ───────────────────────────────────────────────
print("\n📊 Classification Report:")
print("─" * 65)
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
print(report)

# Overall metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print("─" * 65)
print(f"📈 Overall Metrics:")
print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1-Score:  {f1:.4f}")

# ── 5.3 Confusion Matrix ─────────────────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='RdPu',
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_,
            linewidths=0.5, linecolor='white',
            cbar_kws={'shrink': 0.8},
            ax=ax)
ax.set_title('Confusion Matrix — Logistic Regression', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Predicted Category', fontsize=12, labelpad=10)
ax.set_ylabel('Actual Category', fontsize=12, labelpad=10)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
plt.close()
print("\n  ✅ Saved: confusion_matrix.png")


# =============================================================================
# SECTION 6: OVERFITTING / UNDERFITTING ANALYSIS
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 6: OVERFITTING / UNDERFITTING ANALYSIS")
print("━" * 70)

# ── 6.1 K-Fold Cross Validation ──────────────────────────────────────────────
print("\n🔄 Running 5-Fold Stratified Cross-Validation...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_combined, y, cv=cv, scoring='accuracy')

print(f"\n  Fold Results:")
for i, score in enumerate(cv_scores, 1):
    bar = "█" * int(score * 50)
    print(f"    Fold {i}: {score:.4f} ({score*100:.2f}%) {bar}")

print(f"\n  Mean CV Accuracy:  {cv_scores.mean():.4f} ({cv_scores.mean()*100:.2f}%)")
print(f"  Std Dev:           {cv_scores.std():.4f}")
print(f"  Training Accuracy: {train_accuracy:.4f}")
print(f"  Gap (Train - CV):  {abs(train_accuracy - cv_scores.mean()):.4f}")

# ── 6.2 Verdict ──────────────────────────────────────────────────────────────
gap = abs(train_accuracy - cv_scores.mean())
if gap < 0.05 and cv_scores.std() < 0.05:
    print("\n  ✅ VERDICT: No overfitting detected!")
    print("     • Train-CV gap is small (<5%)")
    print("     • CV scores are consistent (low std dev)")
    print("     • Model generalizes well to unseen data")
elif gap < 0.10:
    print("\n  ⚠️ VERDICT: Mild overfitting detected")
    print("     • Consider increasing regularization (lower C value)")
    print("     • Consider getting more training data")
else:
    print("\n  ❌ VERDICT: Significant overfitting detected!")
    print("     • Model memorizes training data")
    print("     • Increase regularization or simplify model")

# ── 6.3 Regularization Analysis ──────────────────────────────────────────────
print("\n📊 Regularization (C parameter) Analysis:")
C_values = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
train_scores = []
cv_mean_scores = []

for C in C_values:
    temp_model = LogisticRegression(
        max_iter=1000, solver='lbfgs', C=C, random_state=42
    )
    temp_model.fit(X_train, y_train)
    t_score = temp_model.score(X_train, y_train)
    cv_s = cross_val_score(temp_model, X_combined, y, cv=cv, scoring='accuracy')
    train_scores.append(t_score)
    cv_mean_scores.append(cv_s.mean())
    print(f"  C={C:6.2f} │ Train: {t_score:.4f} │ CV Mean: {cv_s.mean():.4f} │ Gap: {abs(t_score - cv_s.mean()):.4f}")

# ── 6.4 Cross Validation Plot ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: CV Scores per Fold
axes[0].bar(range(1, 6), cv_scores, color=COLORS[:5], edgecolor='white', linewidth=1.5)
axes[0].axhline(y=cv_scores.mean(), color='#f43f5e', linestyle='--', linewidth=2,
                label=f'Mean: {cv_scores.mean():.4f}')
axes[0].set_title('5-Fold Cross-Validation Scores', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Fold', fontsize=12)
axes[0].set_ylabel('Accuracy', fontsize=12)
axes[0].set_ylim([max(0, cv_scores.min() - 0.1), 1.0])
axes[0].legend(fontsize=11)

# Add value labels
for i, score in enumerate(cv_scores):
    axes[0].text(i+1, score + 0.01, f'{score:.3f}', ha='center', fontweight='bold', fontsize=11)

# Plot 2: Regularization Analysis
axes[1].plot([str(c) for c in C_values], train_scores, 'o-', color='#6366f1',
             linewidth=2, markersize=8, label='Training Accuracy')
axes[1].plot([str(c) for c in C_values], cv_mean_scores, 's-', color='#f43f5e',
             linewidth=2, markersize=8, label='CV Mean Accuracy')
axes[1].set_title('Regularization (C) vs Accuracy', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Regularization Parameter (C)', fontsize=12)
axes[1].set_ylabel('Accuracy', fontsize=12)
axes[1].legend(fontsize=11)
axes[1].set_ylim([max(0, min(cv_mean_scores) - 0.1), 1.02])

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'cross_validation.png'), dpi=150, bbox_inches='tight')
plt.close()
print("\n  ✅ Saved: cross_validation.png")


# =============================================================================
# SECTION 7: SAVE MODEL
# =============================================================================
print("\n" + "━" * 70)
print("  SECTION 7: SAVE MODEL")
print("━" * 70)

# Save the trained model
model_path = os.path.join(MODELS_DIR, 'category_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\n  ✅ Saved: category_model.pkl ({os.path.getsize(model_path):,} bytes)")

# Save the TF-IDF vectorizer
vectorizer_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
with open(vectorizer_path, 'wb') as f:
    pickle.dump(tfidf, f)
print(f"  ✅ Saved: tfidf_vectorizer.pkl ({os.path.getsize(vectorizer_path):,} bytes)")

# Save the StandardScaler
scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"  ✅ Saved: scaler.pkl ({os.path.getsize(scaler_path):,} bytes)")

# Save the Label Encoder
encoder_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
with open(encoder_path, 'wb') as f:
    pickle.dump(label_encoder, f)
print(f"  ✅ Saved: label_encoder.pkl ({os.path.getsize(encoder_path):,} bytes)")

# ── Test the saved model ─────────────────────────────────────────────────────
print("\n🧪 Testing saved model with sample predictions:")
test_cases = [
    ("swiggy lunch", 350),
    ("uber ride", 250),
    ("electricity bill", 1500),
    ("netflix subscription", 499),
    ("pharmacy purchase", 800),
    ("flipkart order", 2000),
    ("tuition fee", 5000),
    ("vegetable market", 200),
]

# Load model to verify
with open(model_path, 'rb') as f:
    loaded_model = pickle.load(f)
with open(vectorizer_path, 'rb') as f:
    loaded_tfidf = pickle.load(f)
with open(scaler_path, 'rb') as f:
    loaded_scaler = pickle.load(f)
with open(encoder_path, 'rb') as f:
    loaded_encoder = pickle.load(f)

print(f"\n  {'Description':<25} {'Amount':>8} │ {'Predicted Category':<15} {'Confidence':>10}")
print("  " + "─" * 70)

for desc, amount in test_cases:
    # Transform text
    text_features = loaded_tfidf.transform([desc.lower()])
    # Transform amount
    amount_features = csr_matrix(loaded_scaler.transform([[amount]]))
    # Combine
    features = hstack([text_features, amount_features])
    # Predict
    prediction = loaded_model.predict(features)[0]
    probabilities = loaded_model.predict_proba(features)[0]
    confidence = probabilities.max()
    category = loaded_encoder.inverse_transform([prediction])[0]
    print(f"  {desc:<25} ₹{amount:>6,} │ {category:<15} {confidence:>9.1%}")


# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("  PIPELINE COMPLETE — SUMMARY")
print("=" * 70)
print(f"""
  📊 Dataset:      {len(df)} records, {df['category'].nunique()} categories
  🤖 Model:        Logistic Regression (TF-IDF + Amount)
  📈 Accuracy:     {accuracy*100:.2f}%
  📊 Precision:    {precision:.4f}
  📊 Recall:       {recall:.4f}
  📊 F1-Score:     {f1:.4f}
  🔄 CV Accuracy:  {cv_scores.mean()*100:.2f}% (±{cv_scores.std()*100:.2f}%)
  💾 Models saved: {MODELS_DIR}
  📈 Charts saved: {VISUALS_DIR}
""")

# List generated files
print("  📁 Generated Visualizations:")
for f in sorted(os.listdir(VISUALS_DIR)):
    size = os.path.getsize(os.path.join(VISUALS_DIR, f))
    print(f"     • {f} ({size:,} bytes)")

print("\n  📁 Saved Models:")
for f in sorted(os.listdir(MODELS_DIR)):
    size = os.path.getsize(os.path.join(MODELS_DIR, f))
    print(f"     • {f} ({size:,} bytes)")

print("\n" + "=" * 70)
print("  ✅ All done! Run predict_api.py to start the Flask prediction server.")
print("=" * 70)
