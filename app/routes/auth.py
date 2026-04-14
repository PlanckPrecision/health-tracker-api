from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, Entry, Goal, Measurement
from app.validate import is_valid_password

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
    return redirect(url_for("entries.index"))


@auth_bp.route("/settings", methods=["GET"])
@login_required
def settings():
    return render_template("settings.html")


@auth_bp.route("/settings/change-username", methods=["POST"])
@login_required
def change_username():
    current_password = request.form.get("current_password", "").strip()
    new_username = request.form.get("new_username", "").strip()

    if not current_password or not new_username:
        flash("All fields are required.", "error")
        return redirect(url_for("auth.settings"))

    if not current_user.check_password(current_password):
        flash("Incorrect password.", "error")
        return redirect(url_for("auth.settings"))

    if len(new_username) < 3 or len(new_username) > 80:
        flash("Username must be between 3 and 80 characters.", "error")
        return redirect(url_for("auth.settings"))

    if new_username == current_user.username:
        flash("That's already your username.", "error")
        return redirect(url_for("auth.settings"))

    if User.query.filter_by(username=new_username).first():
        flash("Username already taken.", "error")
        return redirect(url_for("auth.settings"))

    current_user.username = new_username
    db.session.commit()
    flash("Username updated successfully.", "success")
    return redirect(url_for("auth.settings"))


@auth_bp.route("/settings/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password or not confirm_password:
        flash("All fields are required.", "error")
        return redirect(url_for("auth.settings"))

    if not current_user.check_password(current_password):
        flash("Incorrect current password.", "error")
        return redirect(url_for("auth.settings"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("auth.settings"))

    if not is_valid_password(new_password):
        flash("Password must be at least 6 characters, include a letter and a special character.", "error")
        return redirect(url_for("auth.settings"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("auth.settings"))


@auth_bp.route("/settings/reset-journey", methods=["POST"])
@login_required
def reset_journey():
    current_password = request.form.get("current_password", "").strip()
    confirmation = request.form.get("confirmation", "").strip()

    if not current_user.check_password(current_password):
        flash("Incorrect password. Reset cancelled.", "error")
        return redirect(url_for("auth.settings"))

    if confirmation != "RESET":
        flash("Please type RESET exactly to confirm.", "error")
        return redirect(url_for("auth.settings"))

    Entry.query.filter_by(user_id=current_user.id).delete()
    Measurement.query.filter_by(user_id=current_user.id).delete()
    if current_user.goal:
        db.session.delete(current_user.goal)
    db.session.commit()

    flash("Your journey has been reset. All entries, measurements, and your goal have been deleted.", "success")
    return redirect(url_for("entries.index"))


@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password():
    return render_template("forgot_password.html")
