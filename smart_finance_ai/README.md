<<<<<<< HEAD
# Smart-Finance-AI-
=======
# Smart Finance AI — MVP

A web-based personal finance analyser built with **Flask**, **pandas**, **scikit-learn**, and **Chart.js**.

---

## 📁 Project Structure

```
smart_finance_ai/
├── app.py                  ← Flask app & REST APIs
├── model.py                ← Categorisation, analysis, prediction, recommendations
├── database.py             ← SQLite helpers
├── requirements.txt
├── sample_transactions.csv ← CSV template (add your data here)
├── instance/
│   └── finance.db          ← SQLite database (auto-created)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   └── dashboard.html
└── static/
    └── css/
        └── style.css
```

---

## 🚀 Quick Start

```bash
# 1. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 📊 CSV Format

Your CSV must have **exactly these three columns** (case-insensitive):

| date       | description          | amount |
|------------|----------------------|--------|
| 2024-01-05 | Zomato dinner        | 450    |
| 2024-01-07 | Uber ride            | 120    |
| 2024-01-10 | Netflix subscription | 649    |

- **date** — Any standard date format (`YYYY-MM-DD`, `DD/MM/YYYY`, etc.)
- **description** — Free text; used for auto-categorisation
- **amount** — Numeric value (positive = expense)

---

## 🔌 REST API Reference

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/api/upload`             | Upload CSV file                    |
| POST   | `/api/transactions`       | Add a single transaction (JSON)    |
| GET    | `/api/transactions`       | List all transactions              |
| GET    | `/api/dashboard`          | Get computed analytics             |
| DELETE | `/api/transactions/clear` | Delete all transactions            |

### Add transaction (JSON body)
```json
{
  "date": "2024-03-15",
  "description": "coffee shop",
  "amount": 180,
  "category": ""
}
```

---

## 🗂️ Categories

Auto-detected from description keywords:

- Food & Dining
- Transport
- Shopping
- Entertainment
- Health & Medical
- Utilities & Bills
- Education
- Personal Care
- Others (fallback)

---

## 🔮 Prediction

Uses **scikit-learn LinearRegression** on monthly spending totals to forecast next month's expenses. Requires at least **2 months** of data.

---

## 💡 Recommendations (rule-based)

| Rule | Threshold |
|------|-----------|
| Food & Dining | > 40% of total → suggest cooking at home |
| Entertainment | > 15% → review subscriptions |
| Transport | > 20% → try public transport |
| Shopping | > 25% → apply 48-hour rule |
>>>>>>> 49c962e (Intial commit : Smart Finance AI project)
