"""
Notes Management System
Flask + SQLite full-stack CRUD application with authentication.
"""

import os
import sqlite3
from datetime import timedelta, datetime
import random
from functools import wraps

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
app.permanent_session_lifetime = timedelta(days=1)

# ---------------------------------------------------------
# DATABASE CONFIGURATION (SQLite)
# Auto-configures: uses /tmp in serverless/Netlify, local file otherwise
# ---------------------------------------------------------
DB_PATH = os.environ.get(
    "SQLITE_DB_PATH",
    os.path.join(
        "/tmp" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("NETLIFY") else BASE_DIR,
        "notes.db"
    )
)


def init_sqlite_db():
    """Ensure SQLite tables are created automatically on startup."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[DB INIT ERROR] {e}")


# Initialize SQLite database and tables
init_sqlite_db()


def get_db_connection():
    """Create and return a new SQLite connection with dictionary-style row access."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None


# EMAIL / OTP CONFIGURATION
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "False").lower() in ("true", "1", "yes")

app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "aamid3666@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "vjnn baio lxcd mrgj")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

mail = Mail(app)

OTP_VALID_MINUTES = 5


# ---------------------------------------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for("register"))

        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")
        except sqlite3.Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------------------------------------------------
# FORGOT PASSWORD - STEP 1: Verify user and send OTP
# ---------------------------------------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for("forgot_password"))

        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND email = ?",
            (username, email)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            flash("No account found with that username and email.", "danger")
            return redirect(url_for("forgot_password"))

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP in session
        session["reset_user_id"] = user["id"]
        session["reset_otp"] = otp
        session["reset_email"] = user["email"]
        session["reset_otp_expiry"] = (
            datetime.utcnow().timestamp() + (OTP_VALID_MINUTES * 60)
        )

        try:
            msg = Message(
                subject="NotesVault - Password Reset OTP",
                recipients=[user["email"]],
                body=f"""Hello {user["username"]},

Your OTP for resetting your NotesVault password is:

{otp}

This OTP will expire in {OTP_VALID_MINUTES} minutes.

If you did not request a password reset, please ignore this email.

Regards,
NotesVault Team
"""
            )
            mail.send(msg)
            flash("OTP has been sent to your registered email.", "success")
            return redirect(url_for("verify_otp"))
        except Exception as e:
            flash("Unable to send OTP email. Please check your email settings.", "danger")
            print("EMAIL ERROR:", e)
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


# ---------------------------------------------------------
# FORGOT PASSWORD - STEP 2: Verify OTP
# ---------------------------------------------------------
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "reset_user_id" not in session or "reset_otp" not in session:
        flash("Please start the password reset process again.", "warning")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()

        if datetime.utcnow().timestamp() > session.get("reset_otp_expiry", 0):
            flash("OTP has expired. Please request a new OTP.", "danger")
            session.pop("reset_otp", None)
            session.pop("reset_otp_expiry", None)
            return redirect(url_for("forgot_password"))

        if entered_otp == session.get("reset_otp"):
            session["otp_verified"] = True
            flash("OTP verified successfully.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Incorrect OTP. Please try again.", "danger")

    return render_template(
        "verify_otp.html",
        email=session.get("reset_email", "")
    )


# ---------------------------------------------------------
# FORGOT PASSWORD - STEP 3: Reset Password
# ---------------------------------------------------------
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_user_id" not in session or not session.get("otp_verified"):
        flash("Please verify your OTP first.", "warning")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))

        hashed_pw = generate_password_hash(new_password)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for("reset_password"))

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hashed_pw, session["reset_user_id"])
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Clear reset session data
        session.pop("reset_user_id", None)
        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        session.pop("reset_otp_expiry", None)
        session.pop("otp_verified", None)

        flash("Password reset successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD / VIEW ALL NOTES
# ---------------------------------------------------------
@app.route("/dashboard")
@app.route("/viewall")
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    )
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", notes=notes, username=session.get("username"))


# ---------------------------------------------------------
# ADD NOTE
# ---------------------------------------------------------
@app.route("/addnote", methods=["GET", "POST"])
@login_required
def add_note():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("add_note"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, user_id) VALUES (?, ?, ?)",
            (title, content, session["user_id"])
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Note added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_note.html")


# ---------------------------------------------------------
# VIEW SINGLE NOTE
# ---------------------------------------------------------
@app.route("/viewnotes/<int:note_id>")
@login_required
def view_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    note = cursor.fetchone()
    cursor.close()
    conn.close()

    if not note:
        flash("Note not found or access denied.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("view_note.html", note=note)


# ---------------------------------------------------------
# UPDATE NOTE
# ---------------------------------------------------------
@app.route("/updatenote/<int:note_id>", methods=["GET", "POST"])
@login_required
def update_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    note = cursor.fetchone()

    if not note:
        cursor.close()
        conn.close()
        flash("Note not found or access denied.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        update_cursor = conn.cursor()
        update_cursor.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ? AND user_id = ?",
            (title, content, note_id, session["user_id"])
        )
        conn.commit()
        update_cursor.close()
        cursor.close()
        conn.close()

        flash("Note updated successfully!", "success")
        return redirect(url_for("dashboard"))

    cursor.close()
    conn.close()
    return render_template("update_note.html", note=note)


# ---------------------------------------------------------
# DELETE NOTE
# ---------------------------------------------------------
@app.route("/deletenote/<int:note_id>")
@login_required
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Note deleted successfully!", "info")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------
# ABOUT / ADMIN INFO PAGE
# ---------------------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
