from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db, login_manager
from app.models import User
from app.validate import check_weight, is_valid_password

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app.validate import is_valid_password  # your password checker

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Check if fields are empty
        if not username or not password:
            flash("Username and password required", "error")
            return redirect(url_for("auth.signup"))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("auth.signup"))

        # Password validation
        if not is_valid_password(password):
            flash("Password must be at least 6 characters, include a letter and a special character.", "error")
            return redirect(url_for("auth.signup"))

        # Create user and hash password
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"Welcome, {username}!", "success")
        return redirect(url_for("entries.index"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("auth.login"))