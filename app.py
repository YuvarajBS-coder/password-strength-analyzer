from flask import Flask, render_template, request, jsonify
import re
import secrets
import string
import sqlite3
import hashlib
import hmac
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("password_history.db")

COMMON_PASSWORDS = {
    "password", "password123", "123456", "12345678", "123456789",
    "qwerty", "qwerty123", "admin", "admin123", "letmein",
    "welcome", "welcome123", "abc123", "iloveyou", "monkey",
    "football", "login", "user", "test", "passw0rd"
}

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()

def password_digest(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 150_000
    )

def is_reused(user_id, password):
    if not user_id or not password:
        return False
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(
            "SELECT salt, password_hash FROM password_history WHERE user_id = ?",
            (user_id,)
        ).fetchall()
    for salt, stored_hash in rows:
        if hmac.compare_digest(password_digest(password, salt), stored_hash):
            return True
    return False

def save_password(user_id, password):
    salt = secrets.token_bytes(16)
    digest = password_digest(password, salt)
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO password_history (user_id, salt, password_hash) VALUES (?, ?, ?)",
            (user_id, salt, digest)
        )
        con.commit()

def analyze_password(password):
    length = len(password)
    lower = bool(re.search(r"[a-z]", password))
    upper = bool(re.search(r"[A-Z]", password))
    digit = bool(re.search(r"\d", password))
    special = bool(re.search(r"[^A-Za-z0-9]", password))
    unique = len(set(password))
    score = 0
    feedback = []

    if length >= 16:
        score += 3
    elif length >= 12:
        score += 2
    elif length >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters; 12–16+ is preferable.")

    for ok, msg in [
        (lower, "Add lowercase letters."),
        (upper, "Add uppercase letters."),
        (digit, "Add numbers."),
        (special, "Add special characters such as !, @, #, or $.")
    ]:
        score += int(ok)
        if not ok:
            feedback.append(msg)

    p = password.lower()
    if p in COMMON_PASSWORDS:
        score = 0
        feedback.append("This is a commonly used password. Choose something unique.")

    if re.search(r"(.)\1\1", password):
        score = max(0, score - 2)
        feedback.append("Avoid repeating the same character three or more times.")

    if re.search(r"(0123|1234|2345|3456|4567|5678|6789|abcd|qwer)", p):
        score = max(0, score - 1)
        feedback.append("Avoid obvious sequences such as 1234 or qwer.")

    if length >= 8 and unique < length * 0.55:
        score = max(0, score - 1)
        feedback.append("Use a wider variety of characters.")

    if score <= 2:
        strength, level = "Very Weak", 1
    elif score <= 4:
        strength, level = "Weak", 2
    elif score <= 6:
        strength, level = "Moderate", 3
    elif score <= 8:
        strength, level = "Strong", 4
    else:
        strength, level = "Very Strong", 5

    if not feedback:
        feedback.append("Good structure. Keep the password unique and do not reuse it.")

    return {
        "length": length, "lowercase": lower, "uppercase": upper,
        "number": digit, "special": special, "unique_characters": unique,
        "strength": strength, "level": level, "score": score, "feedback": feedback
    }

def generate_password(length=16):
    length = max(12, min(int(length), 64))
    groups = [string.ascii_lowercase, string.ascii_uppercase,
              string.digits, "!@#$%^&*()-_=+"]
    chars = [secrets.choice(g) for g in groups]
    all_chars = "".join(groups)
    chars += [secrets.choice(all_chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password", "")
    result = analyze_password(password)
    result["reused"] = is_reused(user_id, password)
    if result["reused"]:
        result["feedback"].insert(0, "Password reuse detected for this User ID. Choose a new password.")
    return jsonify(result)

@app.post("/save")
def save():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password", "")
    if not user_id or not password:
        return jsonify({"ok": False, "message": "Enter both User ID and password."}), 400
    if is_reused(user_id, password):
        return jsonify({"ok": False, "message": "This password was already used for this User ID."}), 409
    save_password(user_id, password)
    return jsonify({"ok": True, "message": "Password hash saved to history. Plaintext password is not stored."})

@app.get("/generate")
def generate():
    length = request.args.get("length", 16, type=int)
    return jsonify({"password": generate_password(length)})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
