import io
import json
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request

import database as db
from model import categorize, compute_dashboard, normalize_text

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Initialise DB on startup ─────────────────────────────────────────────────
with app.app_context():
    db.init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# HTML Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


# ═══════════════════════════════════════════════════════════════════════════════
# REST APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Upload a CSV file with columns: date, description, amount."""
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are allowed."}), 400

    try:
        content = file.read().decode("utf-8", errors="replace")
        df = pd.read_csv(io.StringIO(content))
    except Exception as exc:
        return jsonify({"error": f"Could not parse CSV: {exc}"}), 422

    # Normalise column names
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        return jsonify({"error": f"CSV is missing columns: {missing}"}), 422

    df = df[["date", "description", "amount"]].dropna()
    df["description"] = df["description"].astype(str).apply(normalize_text)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    inserted = 0
    for _, row in df.iterrows():
        category = categorize(row["description"])
        db.insert_transaction(
            date=str(row["date"]),
            description=row["description"],
            amount=float(row["amount"]),
            category=category,
        )
        inserted += 1

    return jsonify({"message": f"Successfully imported {inserted} transactions.", "count": inserted})


@app.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    """Add a single manual transaction via JSON body."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required."}), 400

    required_fields = ["date", "description", "amount"]
    for field in required_fields:
        if field not in data or str(data[field]).strip() == "":
            return jsonify({"error": f"Field '{field}' is required."}), 422

    try:
        amount = float(data["amount"])
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a number."}), 422

    description = normalize_text(str(data["description"]))
    category = data.get("category") or categorize(description)

    row_id = db.insert_transaction(
        date=str(data["date"]),
        description=description,
        amount=amount,
        category=category,
    )
    return jsonify({"message": "Transaction added.", "id": row_id}), 201


@app.route("/api/transactions", methods=["GET"])
def api_list_transactions():
    """Return all stored transactions."""
    transactions = db.fetch_all_transactions()
    return jsonify({"transactions": transactions, "count": len(transactions)})


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """Return computed dashboard analytics."""
    transactions = db.fetch_all_transactions()
    summary = compute_dashboard(transactions)
    return jsonify(summary)


@app.route("/api/transactions/clear", methods=["DELETE"])
def api_clear_transactions():
    """Delete all transactions (useful for testing)."""
    db.delete_all_transactions()
    return jsonify({"message": "All transactions cleared."})


# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)
