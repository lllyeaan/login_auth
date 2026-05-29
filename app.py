from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import re


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "secret-key-login-auth"
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = ""
    app.config["MYSQL_DATABASE"] = "login_auth_db"

    if test_config:
        app.config.update(test_config)

    init_db(app)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            valid, message = validate_register_input(username, password, confirm_password)
            if not valid:
                flash(message, "danger")
                return render_template("register.html")

            db = get_db(app)
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                db.close()
                flash("Username sudah digunakan.", "danger")
                return render_template("register.html")

            password_hash = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, "user")
            )

            db.commit()
            cursor.close()
            db.close()

            flash("Registrasi berhasil. Silakan login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username or not password:
                flash("Username dan password wajib diisi.", "danger")
                return render_template("login.html")

            db = get_db(app)
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

            cursor.close()
            db.close()

            if user is None:
                flash("Username tidak ditemukan.", "danger")
                return render_template("login.html")
            
            if not check_password_hash(user["password_hash"], password):
                flash("Password salah.", "danger")
                return render_template("login.html")
            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login berhasil.", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "danger")
            return redirect(url_for("login"))

        return render_template("dashboard.html", username=session.get("username"))
    
    @app.route("/admin/dashboard")
    def admin_dashboard():
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "danger")
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            flash("Anda tidak memiliki akses ke halaman admin.", "danger")
            return redirect(url_for("dashboard"))

        return render_template("admin_dashboard.html", username=session.get("username"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Anda berhasil logout.", "success")
        return redirect(url_for("login"))

    return app


def get_db(app):
    conn = mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DATABASE"]
    )
    return conn


def init_db(app):
    db = get_db(app)
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)

    db.commit()
    cursor.close()
    db.close()


def validate_register_input(username, password, confirm_password):
    if not username:
        return False, "Username wajib diisi."

    if len(username) < 4:
        return False, "Username minimal 4 karakter."

    if not password:
        return False, "Password wajib diisi."

    if len(password) < 8:
        return False, "Password minimal 8 karakter."

    if not re.search(r"[A-Z]", password):
        return False, "Password harus memiliki minimal 1 huruf besar."

    if not re.search(r"[a-z]", password):
        return False, "Password harus memiliki minimal 1 huruf kecil."

    if not re.search(r"[0-9]", password):
        return False, "Password harus memiliki minimal 1 angka."

    if password != confirm_password:
        return False, "Konfirmasi password tidak sama."

    return True, "Valid"


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)