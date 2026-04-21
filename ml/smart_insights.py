"""
=============================================================================
Smart Spending Insights Engine
=============================================================================
Analyzes expense data and generates intelligent, actionable spending insights.
Uses statistical methods to detect anomalies, trends, and provide recommendations.
=============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime


class SmartInsightsEngine:
    """
    Generates AI-powered spending insights from expense data.
    
    Insight Types:
    1. High Spending Alerts        - Flag categories above average
    2. Unusual Transaction Detection - Identify outlier amounts (IQR method)
    3. Monthly Trend Analysis      - Detect spending increases/decreases
    4. Category Dominance          - Alert when one category dominates
    5. Weekend vs Weekday Patterns - Compare spending habits
    6. Savings Recommendations     - Suggest potential savings
    """
    
    def __init__(self, df):
        """
        Initialize with a pandas DataFrame containing:
        - date (datetime)
        - description (str)
        - amount (float/int)
        - category (str)
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        self.df['day_of_week'] = self.df['date'].dt.dayofweek
        self.df['is_weekend'] = self.df['day_of_week'].isin([5, 6])
        self.insights = []
    
    def analyze_all(self):
        """Run all analyses and return combined insights."""
        self.insights = []
        self._high_spending_alerts()
        self._unusual_transactions()
        self._monthly_trends()
        self._category_dominance()
        self._weekend_vs_weekday()
        self._savings_recommendations()
        self._spending_velocity()
        return self.insights
    
    def _add_insight(self, insight_type, severity, title, message, data=None):
        """Add a structured insight to the list."""
        self.insights.append({
            'type': insight_type,
            'severity': severity,        # critical, warning, info, success
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        })
    
    # ── 1. High Spending Alerts ──────────────────────────────────────────────
    def _high_spending_alerts(self):
        """Flag categories where spending exceeds average by >1.5 std dev."""
        cat_spending = self.df.groupby('category')['amount'].sum()
        mean_spending = cat_spending.mean()
        std_spending = cat_spending.std()
        threshold = mean_spending + (1.5 * std_spending)
        
        for category, total in cat_spending.items():
            if total > threshold:
                excess = total - mean_spending
                self._add_insight(
                    'high_spending', 'critical',
                    f'🚨 High {category} Spending',
                    f'{category} spending (₹{total:,.0f}) is significantly above average '
                    f'(₹{mean_spending:,.0f}). Exceeds by ₹{excess:,.0f}.',
                    {'category': category, 'total': total, 'average': mean_spending}
                )
    
    # ── 2. Unusual Transaction Detection ─────────────────────────────────────
    def _unusual_transactions(self):
        """Identify outlier transactions using IQR method per category."""
        for category in self.df['category'].unique():
            cat_data = self.df[self.df['category'] == category]['amount']
            Q1 = cat_data.quantile(0.25)
            Q3 = cat_data.quantile(0.75)
            IQR = Q3 - Q1
            upper_bound = Q3 + (1.5 * IQR)
            
            outliers = self.df[
                (self.df['category'] == category) & 
                (self.df['amount'] > upper_bound)
            ]
            
            if len(outliers) > 0:
                for _, row in outliers.iterrows():
                    self._add_insight(
                        'unusual_transaction', 'warning',
                        f'⚠️ Unusual {category} transaction detected',
                        f'"{row["description"]}" on {row["date"].strftime("%b %d, %Y")} '
                        f'for ₹{row["amount"]:,.0f} is unusually high '
                        f'(normal range: ₹{Q1:,.0f} - ₹{upper_bound:,.0f}).',
                        {'description': row['description'], 'amount': row['amount'],
                         'normal_upper': upper_bound}
                    )
    
    # ── 3. Monthly Trend Analysis ────────────────────────────────────────────
    def _monthly_trends(self):
        """Detect if spending is increasing or decreasing month-over-month."""
        monthly = self.df.groupby('month')['amount'].sum()
        
        if len(monthly) < 2:
            return
        
        # Overall trend
        values = monthly.values
        months = list(monthly.index.astype(str))
        
        if len(values) >= 3:
            recent_avg = np.mean(values[-2:])
            older_avg = np.mean(values[:-2])
            
            if recent_avg > older_avg * 1.15:
                pct_increase = ((recent_avg - older_avg) / older_avg) * 100
                self._add_insight(
                    'trend', 'warning',
                    '📈 Spending is Increasing',
                    f'Recent months average ₹{recent_avg:,.0f}/month, '
                    f'up {pct_increase:.1f}% from earlier average of ₹{older_avg:,.0f}/month.',
                    {'recent_avg': recent_avg, 'older_avg': older_avg, 'pct_change': pct_increase}
                )
            elif recent_avg < older_avg * 0.85:
                pct_decrease = ((older_avg - recent_avg) / older_avg) * 100
                self._add_insight(
                    'trend', 'success',
                    '📉 Spending is Decreasing — Great job!',
                    f'Recent months average ₹{recent_avg:,.0f}/month, '
                    f'down {pct_decrease:.1f}% from ₹{older_avg:,.0f}/month.',
                    {'recent_avg': recent_avg, 'older_avg': older_avg, 'pct_change': -pct_decrease}
                )
        
        # Month-over-month for most recent
        last_month = values[-1]
        prev_month = values[-2]
        
        if last_month > prev_month * 1.2:
            pct = ((last_month - prev_month) / prev_month) * 100
            self._add_insight(
                'trend', 'warning',
                f'📊 Spending up {pct:.0f}% this month',
                f'Current month: ₹{last_month:,.0f} vs previous: ₹{prev_month:,.0f}. '
                f'Consider reviewing your recent expenses.',
                {'current': last_month, 'previous': prev_month}
            )
    
    # ── 4. Category Dominance ────────────────────────────────────────────────
    def _category_dominance(self):
        """Alert when one category exceeds 30% of total spending."""
        total = self.df['amount'].sum()
        cat_totals = self.df.groupby('category')['amount'].sum()
        
        for category, amount in cat_totals.items():
            pct = (amount / total) * 100
            if pct > 30:
                self._add_insight(
                    'dominance', 'info',
                    f'📊 {category} dominates your spending ({pct:.1f}%)',
                    f'{category} accounts for ₹{amount:,.0f} out of ₹{total:,.0f} total. '
                    f'Consider diversifying or setting a budget for this category.',
                    {'category': category, 'percentage': pct, 'amount': amount}
                )
    
    # ── 5. Weekend vs Weekday Patterns ───────────────────────────────────────
    def _weekend_vs_weekday(self):
        """Compare spending patterns between weekdays and weekends."""
        weekday_avg = self.df[~self.df['is_weekend']]['amount'].mean()
        weekend_avg = self.df[self.df['is_weekend']]['amount'].mean()
        
        if pd.isna(weekend_avg) or pd.isna(weekday_avg):
            return
        
        if weekend_avg > weekday_avg * 1.3:
            pct_more = ((weekend_avg - weekday_avg) / weekday_avg) * 100
            self._add_insight(
                'pattern', 'info',
                f'🗓️ You spend {pct_more:.0f}% more on weekends',
                f'Weekend average: ₹{weekend_avg:,.0f} vs Weekday: ₹{weekday_avg:,.0f}. '
                f'Try planning weekend activities in advance to manage costs.',
                {'weekend_avg': weekend_avg, 'weekday_avg': weekday_avg}
            )
        elif weekday_avg > weekend_avg * 1.3:
            self._add_insight(
                'pattern', 'success',
                '✅ Your weekend spending is well-controlled',
                f'Weekend average: ₹{weekend_avg:,.0f} vs Weekday: ₹{weekday_avg:,.0f}. '
                f'Great job keeping weekend expenses in check!',
                {'weekend_avg': weekend_avg, 'weekday_avg': weekday_avg}
            )
    
    # ── 6. Savings Recommendations ───────────────────────────────────────────
    def _savings_recommendations(self):
        """Suggest potential savings based on reducible categories."""
        reducible_categories = ['Food', 'Entertainment', 'Shopping']
        cat_monthly = self.df.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
        
        for category in reducible_categories:
            if category in cat_monthly.columns:
                monthly_avg = cat_monthly[category].mean()
                if monthly_avg > 0:
                    savings_10 = monthly_avg * 0.10
                    savings_20 = monthly_avg * 0.20
                    self._add_insight(
                        'recommendation', 'info',
                        f'💰 Save ₹{savings_10:,.0f}-₹{savings_20:,.0f}/month on {category}',
                        f'Your average monthly {category} spending is ₹{monthly_avg:,.0f}. '
                        f'Reducing by 10-20% could save you ₹{savings_10:,.0f}-₹{savings_20:,.0f} per month '
                        f'(₹{savings_10*12:,.0f}-₹{savings_20*12:,.0f} per year).',
                        {'category': category, 'monthly_avg': monthly_avg,
                         'potential_savings': savings_10}
                    )
    
    # ── 7. Spending Velocity ─────────────────────────────────────────────────
    def _spending_velocity(self):
        """Check how fast money is being spent in the current period."""
        if len(self.df) < 10:
            return
        
        # Frequency analysis
        self.df_sorted = self.df.sort_values('date')
        recent = self.df_sorted.tail(30)
        
        if len(recent) >= 5:
            date_diffs = recent['date'].diff().dt.days.dropna()
            avg_gap = date_diffs.mean()
            
            if avg_gap < 1.5:
                self._add_insight(
                    'velocity', 'warning',
                    '⚡ High spending frequency detected',
                    f'You\'re making transactions every {avg_gap:.1f} days on average. '
                    f'Consider batching purchases to reduce impulse spending.',
                    {'avg_gap_days': avg_gap}
                )
    
    def get_summary(self):
        """Get a formatted text summary of all insights."""
        if not self.insights:
            self.analyze_all()
        
        summary = []
        summary.append("=" * 60)
        summary.append("  SMART SPENDING INSIGHTS")
        summary.append("=" * 60)
        
        severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'success': 3}
        sorted_insights = sorted(self.insights, key=lambda x: severity_order.get(x['severity'], 4))
        
        for insight in sorted_insights:
            severity_icon = {
                'critical': '🔴', 'warning': '🟡',
                'info': '🔵', 'success': '🟢'
            }.get(insight['severity'], '⚪')
            
            summary.append(f"\n{severity_icon} [{insight['severity'].upper()}] {insight['title']}")
            summary.append(f"   {insight['message']}")
        
        summary.append("\n" + "=" * 60)
        summary.append(f"  Total Insights: {len(self.insights)}")
        
        # Count by severity
        for sev in ['critical', 'warning', 'info', 'success']:
            count = len([i for i in self.insights if i['severity'] == sev])
            if count > 0:
                summary.append(f"  {sev.capitalize()}: {count}")
        
        summary.append("=" * 60)
        return "\n".join(summary)
    
    def to_json(self):
        """Return insights as a JSON-serializable list."""
        if not self.insights:
            self.analyze_all()
        return self.insights


# ── Standalone Execution ─────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    
    # Load datasets
    df1 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset1.csv'))
    df2 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset2.csv'))
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Generate insights
    engine = SmartInsightsEngine(df)
    engine.analyze_all()
    
    # Print formatted summary
    print(engine.get_summary())
    
    # Print JSON format
    print("\n📋 JSON Output (for API):")
    import json
    print(json.dumps(engine.to_json(), indent=2, default=str))
