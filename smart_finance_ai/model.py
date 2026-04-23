import re
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


# ─── Keyword-based categorizer ────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Food & Dining": [
        "restaurant", "cafe", "coffee", "pizza", "burger", "sushi", "food",
        "dining", "eat", "lunch", "dinner", "breakfast", "grocery", "supermarket",
        "zomato", "swiggy", "mcdonald", "kfc", "dominos", "subway", "bakery",
        "hotel", "dhaba", "canteen", "snack", "juice", "milk", "fruits", "vegetables",
    ],
    "Transport": [
        "uber", "ola", "taxi", "cab", "auto", "bus", "train", "metro", "fuel",
        "petrol", "diesel", "parking", "toll", "flight", "airline", "travel",
        "transport", "rapido", "bike", "rickshaw",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "mall", "store",
        "shop", "clothes", "shirt", "shoes", "fashion", "apparell", "purchase",
        "buy", "order", "delivery", "market", "bazaar",
    ],
    "Entertainment": [
        "netflix", "prime", "hotstar", "spotify", "youtube", "movie", "cinema",
        "pvr", "inox", "concert", "game", "gaming", "streaming", "subscription",
        "music", "theatre", "show", "event", "ticket",
    ],
    "Health & Medical": [
        "hospital", "doctor", "clinic", "pharmacy", "medicine", "medical",
        "health", "gym", "fitness", "yoga", "diagnostic", "lab", "test",
        "chemist", "drug", "dental", "optician",
    ],
    "Utilities & Bills": [
        "electricity", "water", "gas", "internet", "wifi", "broadband",
        "mobile", "recharge", "bill", "utility", "maintenance", "rent",
        "insurance", "emi", "loan", "credit", "debit",
    ],
    "Education": [
        "school", "college", "university", "course", "udemy", "coursera",
        "book", "stationery", "tuition", "fees", "exam", "library", "study",
    ],
    "Personal Care": [
        "salon", "spa", "haircut", "beauty", "cosmetic", "parlour", "barber",
        "skin", "care", "hygiene", "soap", "shampoo",
    ],
}

FALLBACK_CATEGORY = "Others"


def normalize_text(text: str) -> str:
    """Lowercase and strip noise from a string."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def categorize(description: str) -> str:
    """Return a category string for a transaction description."""
    clean = normalize_text(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in clean:
                return category
    return FALLBACK_CATEGORY


# ─── Analysis helpers ─────────────────────────────────────────────────────────

def compute_dashboard(transactions: list[dict]) -> dict:
    """
    Given a list of transaction dicts (id, date, description, amount, category),
    return a dashboard summary dict ready for JSON serialisation.
    """
    if not transactions:
        return {
            "total_spending": 0,
            "category_breakdown": {},
            "monthly_trend": {},
            "prediction": None,
            "recommendations": [],
        }

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Only consider expenses (negative or positive depending on convention).
    # We treat ALL amounts as spending (absolute values).
    df["amount"] = df["amount"].abs()

    total = float(df["amount"].sum())

    # Category breakdown
    cat_df = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    category_breakdown = {k: round(float(v), 2) for k, v in cat_df.items()}

    # Monthly trend  (YYYY-MM → total)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().sort_index()
    monthly_trend = {k: round(float(v), 2) for k, v in monthly.items()}

    # Prediction (linear regression on month index → spending)
    prediction = predict_next_month(monthly_trend)

    # Recommendations
    recommendations = generate_recommendations(category_breakdown, total)

    return {
        "total_spending": round(total, 2),
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "prediction": prediction,
        "recommendations": recommendations,
    }


# ─── Prediction ───────────────────────────────────────────────────────────────

def predict_next_month(monthly_trend: dict) -> float | None:
    """Predict next month's spending with Linear Regression."""
    if len(monthly_trend) < 2:
        return None
    values = list(monthly_trend.values())
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(X, y)
    next_idx = np.array([[len(values)]])
    pred = float(model.predict(next_idx)[0])
    return round(max(pred, 0), 2)


# ─── Recommendations ─────────────────────────────────────────────────────────

def generate_recommendations(category_breakdown: dict, total: float) -> list[str]:
    recs = []
    if total == 0:
        return recs

    pct = {cat: (amt / total * 100) for cat, amt in category_breakdown.items()}

    food_pct = pct.get("Food & Dining", 0)
    if food_pct > 40:
        recs.append(
            f"🍔 Food & Dining takes {food_pct:.1f}% of your budget. "
            "Consider cooking at home more often to cut this below 30%."
        )

    entertainment_pct = pct.get("Entertainment", 0)
    if entertainment_pct > 15:
        recs.append(
            f"🎬 Entertainment is {entertainment_pct:.1f}% of spending. "
            "Review your streaming subscriptions and cancel unused ones."
        )

    transport_pct = pct.get("Transport", 0)
    if transport_pct > 20:
        recs.append(
            f"🚗 Transport costs {transport_pct:.1f}% of your total. "
            "Try carpooling, public transport, or a monthly pass to save."
        )

    shopping_pct = pct.get("Shopping", 0)
    if shopping_pct > 25:
        recs.append(
            f"🛍️ Shopping is {shopping_pct:.1f}% of expenses. "
            "Make a wish-list and wait 48 hours before buying non-essentials."
        )

    if not recs:
        recs.append("✅ Great job! Your spending looks well balanced across categories.")

    return recs
