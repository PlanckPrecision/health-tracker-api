from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
from datetime import datetime
from app import db
from app.models import Entry, Goal
from app.validate import check_weight, get_dashboard_stats

entries_bp = Blueprint("entries", __name__)


@entries_bp.route("/")
def index():
    today = datetime.now().strftime("%d.%m.%Y")
    user_id = current_user.id if current_user.is_authenticated else None
    stats = get_dashboard_stats(user_id)
    return render_template(
        "index.html",
        today=today,
        user=current_user.username if current_user.is_authenticated else None,
        stats=stats,
    )


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
            user_id = current_user.id if current_user.is_authenticated else None
            return render_template(
                "index.html",
                message=f"Invalid date format: '{date_raw}'. Use DD.MM.YYYY",
                today=today,
                user=current_user.username if current_user.is_authenticated else None,
                stats=get_dashboard_stats(user_id),
            )

    # Convert to real date object (IMPORTANT!)
    parsed_date = datetime.strptime(date_raw, "%d.%m.%Y").date()

    # 2. Validate weight
    is_valid, result = check_weight(weight_raw)
    if not is_valid:
        today = datetime.now().strftime("%d.%m.%Y")
        user_id = current_user.id if current_user.is_authenticated else None
        return render_template(
            "index.html",
            message=result,
            today=today,
            user=current_user.username if current_user.is_authenticated else None,
            stats=get_dashboard_stats(user_id),
        )

    user_id = current_user.id if current_user.is_authenticated else None

    # 3. Check for existing entry for this user on this date
    existing_entry = Entry.query.filter_by(date=parsed_date, user_id=user_id).first()

    if existing_entry:
        existing_entry.weight = result
        message = f"Updated weight for {date_raw} to {result} kg."
    else:
        new_entry = Entry(weight=result, date=parsed_date, user_id=user_id)
        db.session.add(new_entry)
        message = f"Registered {result} kg for {date_raw}."

    # 4. Commit changes
    db.session.commit()

    stats = get_dashboard_stats(user_id)
    if stats["seven_day_avg"] is not None:
        message += f" 7-day average: {stats['seven_day_avg']:.2f} kg."

    today = datetime.now().strftime("%d.%m.%Y")
    return render_template(
        "index.html",
        today=today,
        user=current_user.username if current_user.is_authenticated else None,
        weight=result,
        date=date_raw,
        message=message,
        stats=stats,
    )

@entries_bp.route("/history")
def history():
    if current_user.is_authenticated:
        raw = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).all()
    else:
        raw = Entry.query.filter_by(user_id=None).order_by(Entry.date.desc()).all()

    # Pre-compute delta vs the chronologically previous entry (next item in DESC list)
    entries = []
    for i, entry in enumerate(raw):
        if i < len(raw) - 1:
            delta = round(entry.weight - raw[i + 1].weight, 2)
        else:
            delta = None
        entries.append({"entry": entry, "delta": delta})

    return render_template("history.html", entries=entries, total=len(raw))


@entries_bp.route("/api/entries")
def get_entries_json():
    if current_user.is_authenticated:
        entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date).all()
    else:
        entries = Entry.query.filter_by(user_id=None).order_by(Entry.date).all()

    data = [
        {
            "date": entry.date.strftime("%d.%m.%Y"),  # Convert date object to string
            "weight": entry.weight
        }
        for entry in entries
    ]

    return jsonify(data)

@entries_bp.route("/goals", methods=["GET", "POST"])
def goals():
    existing_goal = None
    if current_user.is_authenticated:
        existing_goal = Goal.query.filter_by(user_id=current_user.id).first()

    if request.method == "GET":
        return render_template("goals.html", goal=existing_goal)

    start_weight_raw = request.form.get("start_weight", "").strip()
    goal_weight_raw = request.form.get("goal_weight", "").strip()

    is_valid_start, start_result = check_weight(start_weight_raw)
    if not is_valid_start:
        return render_template(
            "goals.html",
            message=f"Starting weight: {start_result}",
            goal=existing_goal,
        )

    is_valid_goal, goal_result = check_weight(goal_weight_raw)
    if not is_valid_goal:
        return render_template(
            "goals.html",
            message=f"Goal weight: {goal_result}",
            goal=existing_goal,
        )

    if current_user.is_authenticated:
        if existing_goal:
            existing_goal.goal_weight = goal_result
            existing_goal.start_weight = start_result
        else:
            db.session.add(Goal(
                user_id=current_user.id,
                goal_weight=goal_result,
                start_weight=start_result,
            ))
        db.session.commit()
        message = f"Goal saved! Targeting {goal_result} kg from {start_result} kg."
    else:
        session["goal_weight"] = goal_result
        session["start_weight"] = start_result
        message = (
            f"Goal set to {goal_result} kg from {start_result} kg. "
            "Log in to save it permanently."
        )

    return render_template(
        "goals.html",
        message=message,
        goal_weight=goal_result,
        start_weight=start_result,
    )
