from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from datetime import datetime
from app import db
from app.models import Entry
from app.validate import check_weight

entries_bp = Blueprint("entries", __name__)

@entries_bp.route("/")
def index():
    today = datetime.now().strftime("%d.%m.%Y")
    return render_template("index.html", today=today)

@entries_bp.route("/register", methods=["POST"])
def register():
    weight_raw = request.form.get("weight", "").strip()
    date_raw = request.form.get("date", "").strip()

    # 1. Handle default date
    if not date_raw:
        date_raw = datetime.now().strftime("%d.%m.%Y")
    else:
        try:
            datetime.strptime(date_raw, "%d.%m.%Y")
        except ValueError:
            today = datetime.now().strftime("%d.%m.%Y")
            return render_template(
                "index.html",
                message=f"Invalid date format: '{date_raw}'. Use DD.MM.YYYY",
                today=today,
            )

    # 2. Validate weight
    is_valid, result = check_weight(weight_raw)
    if not is_valid:
        today = datetime.now().strftime("%d.%m.%Y")
        return render_template("index.html", message=result, today=today)

    user_id = current_user.id if current_user.is_authenticated else None

    # 3. Check for existing entry for this user on this date
    existing_entry = Entry.query.filter_by(date=date_raw, user_id=user_id).first()

    if existing_entry:
        # Update the existing record
        existing_entry.weight = result
        message = f"Updated weight for {date_raw} to {result} kg."
    else:
        # Create a new record
        new_entry = Entry(weight=result, date=date_raw, user_id=user_id)
        db.session.add(new_entry)
        message = f"Registered {result} kg for {date_raw}."

    # 4. Commit changes to the database
    db.session.commit()

    today = datetime.now().strftime("%d.%m.%Y")
    return render_template(
        "index.html",
        today=today,
        weight=result,
        date=date_raw,
        message=message # Added a message to show if it was updated or new
    )

@entries_bp.route("/history")
def history():
    if current_user.is_authenticated:
        # Show only logged-in user's entries
        entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.id).all()
    else:
        # Show anonymous entries (where user_id is None)
        entries = Entry.query.filter_by(user_id=None).order_by(Entry.id).all()
    return render_template("history.html", entries=entries)

@entries_bp.route("/api/entries")
def get_entries_json():
    if current_user.is_authenticated:
        entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date).all()
    else:
        entries = Entry.query.filter_by(user_id=None).order_by(Entry.date).all()
    
    data = [{"date": entry.date, "weight": entry.weight} for entry in entries]
    return jsonify(data)

@entries_bp.route("/goals")
def goals():
    goals_raw = request.form.get("goal_weight", "").strip()
    return render_template("goals.html", goal_weight=goals_raw)