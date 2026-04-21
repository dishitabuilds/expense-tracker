"""
=============================================================================
Flask Prediction API — AI Expense Category Predictor
=============================================================================
Loads the trained ML model and provides REST API endpoints for:
1. Predicting expense category from description + amount
2. Generating smart spending insights
3. Health check

Run: python predict_api.py
Server: http://localhost:5000
=============================================================================
"""

import os
import sys
import pickle
import json
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.sparse import hstack, csr_matrix

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smart_insights import SmartInsightsEngine

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from PHP frontend

# ── Load Trained Model ────────────────────────────────────────────────────────
print("🔧 Loading trained models...")

try:
    with open(os.path.join(MODELS_DIR, 'category_model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'), 'rb') as f:
        tfidf = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'label_encoder.pkl'), 'rb') as f:
        label_encoder = pickle.load(f)
    print("✅ All models loaded successfully!")
    print(f"   Categories: {list(label_encoder.classes_)}")
except FileNotFoundError as e:
    print(f"❌ Model file not found: {e}")
    print("   Run 'python expense_ai.py' first to train the model.")
    sys.exit(1)


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        'status': 'healthy',
        'model': 'Logistic Regression',
        'categories': list(label_encoder.classes_),
        'version': '1.0.0'
    })


@app.route('/predict', methods=['POST'])
def predict_category():
    """
    Predict expense category from description and amount.
    
    Request JSON:
        {
            "description": "swiggy lunch",
            "amount": 350
        }
    
    Response JSON:
        {
            "predicted_category": "Food",
            "confidence": 0.92,
            "all_probabilities": {
                "Food": 0.92,
                "Transport": 0.03,
                ...
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        description = data.get('description', '').strip()
        amount = data.get('amount', 0)
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0
        
        # Transform text using TF-IDF
        text_features = tfidf.transform([description.lower()])
        
        # Transform amount using scaler
        amount_features = csr_matrix(scaler.transform([[amount]]))
        
        # Combine features
        features = hstack([text_features, amount_features])
        
        # Predict
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get category name
        predicted_category = label_encoder.inverse_transform([prediction])[0]
        confidence = float(probabilities.max())
        
        # Build probability map for all categories
        all_probs = {}
        for i, cls in enumerate(label_encoder.classes_):
            all_probs[cls] = round(float(probabilities[i]), 4)
        
        # Sort by probability
        all_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True))
        
        return jsonify({
            'predicted_category': predicted_category,
            'confidence': round(confidence, 4),
            'all_probabilities': all_probs
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch predict categories for multiple expenses.
    
    Request JSON:
        {
            "expenses": [
                {"description": "swiggy lunch", "amount": 350},
                {"description": "uber ride", "amount": 250}
            ]
        }
    """
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses:
            return jsonify({'error': 'No expenses provided'}), 400
        
        results = []
        for expense in expenses:
            desc = expense.get('description', '').strip().lower()
            amt = float(expense.get('amount', 0))
            
            text_features = tfidf.transform([desc])
            amount_features = csr_matrix(scaler.transform([[amt]]))
            features = hstack([text_features, amount_features])
            
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            category = label_encoder.inverse_transform([prediction])[0]
            confidence = float(probabilities.max())
            
            results.append({
                'description': expense.get('description', ''),
                'amount': amt,
                'predicted_category': category,
                'confidence': round(confidence, 4)
            })
        
        return jsonify({'predictions': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/insights', methods=['GET', 'POST'])
def get_insights():
    """
    Generate smart spending insights.
    
    GET: Uses the training dataset for demo insights
    POST: Accepts custom expense data in JSON format
    
    POST Request JSON:
        {
            "expenses": [
                {"date": "2026-01-05", "description": "swiggy lunch", "amount": 350, "category": "Food"},
                ...
            ]
        }
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            expenses = data.get('expenses', [])
            if expenses:
                df = pd.DataFrame(expenses)
            else:
                return jsonify({'error': 'No expense data provided'}), 400
        else:
            # Use training dataset for demo
            df1 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset1.csv'))
            df2 = pd.read_csv(os.path.join(DATASET_DIR, 'expense_dataset2.csv'))
            df = pd.concat([df1, df2], ignore_index=True)
        
        engine = SmartInsightsEngine(df)
        insights = engine.analyze_all()
        
        return jsonify({
            'insights': insights,
            'total': len(insights),
            'summary': {
                'critical': len([i for i in insights if i['severity'] == 'critical']),
                'warning': len([i for i in insights if i['severity'] == 'warning']),
                'info': len([i for i in insights if i['severity'] == 'info']),
                'success': len([i for i in insights if i['severity'] == 'success'])
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Run Server ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  AI Expense Predictor API")
    print("=" * 50)
    print(f"  Server:     http://localhost:5000")
    print(f"  Endpoints:")
    print(f"    GET  /health         → Health check")
    print(f"    POST /predict        → Predict category")
    print(f"    POST /predict/batch  → Batch predictions")
    print(f"    GET  /insights       → Smart insights (demo)")
    print(f"    POST /insights       → Smart insights (custom data)")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
