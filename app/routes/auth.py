import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app import db, limiter, login_manager, mail
from app.models import Entry, User
from app.validate import is_valid_password

auth_bp = Blueprint("auth", __name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _generate_reset_token(user_id: int) -> str:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(user_id, salt="password-reset")


def _verify_reset_token(token: str, max_age: int = 1800):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token, salt="password-reset", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None
    return db.session.get(User, user_id)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.signup"))

        if not _EMAIL_RE.match(email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("auth.signup"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for("auth.signup"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.signup"))

        if not is_valid_password(password):
            flash("Password must be at least 6 characters, include a letter and a special character.", "error")
            return redirect(url_for("auth.signup"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid username/email or password.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"Welcome, {user.username}!", "success")
        next_page = request.args.get("next", "")
        # Guard against open-redirect
        if next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)
        return redirect(url_for("entries.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("entries.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show the same message to prevent email enumeration
        if user:
            token = _generate_reset_token(user.id)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            msg = Message(
                subject="Reset your password",
                recipients=[user.email],
                body=(
                    f"Hi {user.username},\n\n"
                    "Click the link below to reset your password. "
                    "This link expires in 30 minutes.\n\n"
                    f"{reset_url}\n\n"
                    "If you did not request this, ignore this email."
                ),
            )
            mail.send(msg)

        flash("If that email is registered, a reset link has been sent.", "success")
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = _verify_reset_token(token)
    if user is None:
        flash("That reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not password or not confirm:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        if not is_valid_password(password):
            flash("Password must be at least 6 characters, include a letter and a special character.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user.set_password(password)
        db.session.commit()
        flash("Password reset successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)


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
    if current_user.goal:
        db.session.delete(current_user.goal)
    db.session.commit()

    flash("Your journey has been reset. All entries and your goal have been deleted.", "success")
    return redirect(url_for("entries.index"))
