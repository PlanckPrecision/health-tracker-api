from datetime import datetime, timedelta
import re
from app.models import Entry, Goal

def check_weight(weight_str):
    """
    Validates the weight based on specific rules:
    - Must be a number (allowing ',' as a separator)
    - No text or emojis
    - Maximum of two decimal places
    - Must be within the allowed weights list (0-500)
    """
    if not weight_str:
        return False, "Weight is required"

    # Replace comma with dot for standard float processing
    processed_weight = weight_str.replace(',', '.')

    try:
        # Check if it's a valid float
        val = float(processed_weight)

        # Check for maximum two decimals
        if '.' in processed_weight:
            decimals = processed_weight.split('.')[1]
            if len(decimals) > 2:
                return False, "Maximum two decimal places allowed"

        # Check if the weight is in the range 0 to 500
        if val < 0 or val > 500:
            return False, "Weight must be between 0 and 500"

    except ValueError:
        return False, "Invalid format. Only numbers with maximum of 2 decimal places allowed"

    return True, val

def check_date(date_raw):
    date_raw = (date_raw or "").strip()

    if not date_raw:
        return True, datetime.today().date()

    try:
        date_obj = datetime.strptime(date_raw, "%Y-%m-%d").date()
        return True, date_obj
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def is_valid_password(password):
    """
    Returns True if the password:
    - Is at least 6 characters long
    - Contains at least one letter
    - Contains at least one special character (non-alphanumeric)
    """
    if len(password) < 6:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True

def get_seven_day_average(user_id, end_date):
    """
    Calculates the 7-day average weight for a specific user ending on end_date_str.
    Returns the average as a float, or None if no entries exist.
    """
    start_date = end_date - timedelta(days=6)

    entries = Entry.query.filter(
        Entry.user_id == user_id,
        Entry.date >= start_date,
        Entry.date <= end_date
    ).all()

    if not entries:
        return None

    average = sum(entry.weight for entry in entries) / len(entries)
    rounded_average = round(average, 2)
    return rounded_average


def get_dashboard_stats(user_id):
    from datetime import date as date_type

    today = date_type.today()

    # Anchor all date-window calculations to the most recent entry's actual date,
    # so backdated entries recalculate correctly on every page load.
    latest_entry = (
        Entry.query.filter_by(user_id=user_id).order_by(Entry.date.desc()).first()
        if user_id is not None else None
    )
    reference_date = latest_entry.date if latest_entry else today

    # 7-day moving average relative to the reference date
    seven_day_avg = get_seven_day_average(user_id, reference_date)
    if seven_day_avg is None and latest_entry:
        seven_day_avg = round(latest_entry.weight, 2)

    # Starting weight: Goal.start_weight → first entry → 0
    starting_weight = 0.0
    if user_id is not None:
        goal = Goal.query.filter_by(user_id=user_id).first()
        if goal and goal.start_weight:
            starting_weight = goal.start_weight
        else:
            first_entry = Entry.query.filter_by(user_id=user_id).order_by(Entry.date.asc()).first()
            if first_entry:
                starting_weight = first_entry.weight

    # Rolling 7-day velocity anchored to most_recent.date, not today.
    # This means backdated entries recalculate correctly on every page load.
    weekly_pace = None
    weekly_pace_label = "Need more data"
    weekly_trend = "neutral"

    if latest_entry:
        most_recent = latest_entry
        anchor_upper = most_recent.date - timedelta(days=6)
        anchor_lower = most_recent.date - timedelta(days=10)

        anchor = (
            Entry.query
            .filter(
                Entry.user_id == user_id,
                Entry.date >= anchor_lower,
                Entry.date < anchor_upper,
            )
            .order_by(Entry.date.desc())
            .first()
        )

        if anchor:
            elapsed_days = (most_recent.date - anchor.date).days
            weeks = elapsed_days / 7
            weekly_pace = round((most_recent.weight - anchor.weight) / weeks, 2)
            if weekly_pace < 0:
                weekly_trend = "down"
            elif weekly_pace > 0:
                weekly_trend = "up"
            else:
                weekly_trend = "neutral"
            weekly_pace_label = f"{weekly_pace:+.2f} kg / week"

    # Change from starting weight: latest entry vs starting weight (goal or first entry)
    weight_change_from_start = None
    if latest_entry and starting_weight:
        weight_change_from_start = round(latest_entry.weight - starting_weight, 2)

    return {
        "seven_day_avg": seven_day_avg,
        "starting_weight": starting_weight,
        "weekly_pace": weekly_pace,
        "weekly_pace_label": weekly_pace_label,
        "weekly_trend": weekly_trend,
        "weight_change_from_start": weight_change_from_start,
    }
