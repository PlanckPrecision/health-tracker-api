import math
import re
from datetime import date as date_type
from datetime import datetime, timedelta

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


def get_streak(user_id):
    if user_id is None:
        return 0
    entries = Entry.query.filter_by(user_id=user_id).order_by(Entry.date.desc()).all()
    if not entries:
        return 0

    entry_dates = {e.date for e in entries}
    today = date_type.today()
    check = today if today in entry_dates else today - timedelta(days=1)

    streak = 0
    while check in entry_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


def get_dashboard_stats(user_id):
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
    # goal_weight: from Goal.goal_weight if set
    starting_weight = 0.0
    goal_weight = None
    goal = Goal.query.filter_by(user_id=user_id).first() if user_id is not None else None

    if goal:
        if goal.start_weight:
            starting_weight = goal.start_weight
        if goal.goal_weight:
            goal_weight = goal.goal_weight
    elif user_id is not None:
        first_entry = Entry.query.filter_by(user_id=user_id).order_by(Entry.date.asc()).first()
        if first_entry:
            starting_weight = first_entry.weight

    # Weekly pace: weight from 7 days ago minus the average weight of the past 7 days.
    # Positive = lost weight (current avg is lower than the anchor weight 7 days ago).
    weekly_pace = None
    weekly_pace_label = "Need more data"
    weekly_trend = "neutral"

    if latest_entry and seven_day_avg is not None:
        target_date = reference_date - timedelta(days=7)
        anchor_7 = (
            Entry.query
            .filter(Entry.user_id == user_id, Entry.date <= target_date)
            .order_by(Entry.date.desc())
            .first()
        )
        if anchor_7:
            weekly_pace = round(seven_day_avg - anchor_7.weight, 2)
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

    # Weight lost over the past 7 days (positive = lost weight)
    lost_7_days = None
    if user_id is not None and latest_entry:
        cutoff_7 = reference_date - timedelta(days=7)
        oldest_7 = (
            Entry.query
            .filter(Entry.user_id == user_id, Entry.date >= cutoff_7, Entry.date <= reference_date)
            .order_by(Entry.date.asc())
            .first()
        )
        if oldest_7 and oldest_7.date != latest_entry.date:
            lost_7_days = round(oldest_7.weight - latest_entry.weight, 2)

    # Weight lost over the past 30 days (positive = lost weight)
    lost_30_days = None
    if user_id is not None and latest_entry:
        cutoff_30 = reference_date - timedelta(days=30)
        oldest_30 = (
            Entry.query
            .filter(Entry.user_id == user_id, Entry.date >= cutoff_30, Entry.date <= reference_date)
            .order_by(Entry.date.asc())
            .first()
        )
        if oldest_30 and oldest_30.date != latest_entry.date:
            lost_30_days = round(oldest_30.weight - latest_entry.weight, 2)

    # All-time weight lost from starting weight (positive = lost weight)
    lost_all_time = None
    if latest_entry and starting_weight:
        lost_all_time = round(starting_weight - latest_entry.weight, 2)

    # Forecast: date user will hit goal_weight at current weekly_pace.
    # weekly_pace is negative when losing weight (seven_day_avg < weight_7_days_ago).
    forecast_date = None
    forecast_weeks = None
    goal_progress_pct = 0

    if (
        latest_entry is not None
        and goal_weight is not None
        and weekly_pace is not None
        and weekly_pace < 0
        and latest_entry.weight > goal_weight
    ):
        kg_per_week = abs(weekly_pace)
        kg_remaining = latest_entry.weight - goal_weight
        weeks_needed = kg_remaining / kg_per_week
        forecast_date = reference_date + timedelta(days=round(weeks_needed * 7))
        forecast_weeks = round(weeks_needed, 1)

    if starting_weight and goal_weight and latest_entry and starting_weight != goal_weight:
        total = starting_weight - goal_weight
        done = starting_weight - latest_entry.weight
        goal_progress_pct = max(0, min(100, round((done / total) * 100, 1)))

    # Committed-rate forecast: uses compound loss formula.
    # Each week the user loses `weekly_loss_pct`% of their current weight.
    # weeks = ln(goal_weight / current_weight) / ln(1 - rate)
    committed_forecast_date = None
    committed_forecast_weeks = None
    committed_kg_per_week = None

    if (
        latest_entry is not None
        and goal_weight is not None
        and goal is not None
        and goal.weekly_loss_pct is not None
        and latest_entry.weight > goal_weight
    ):
        rate = goal.weekly_loss_pct / 100.0
        committed_kg_per_week = round(latest_entry.weight * rate, 3)
        weeks_needed = math.log(goal_weight / latest_entry.weight) / math.log(1 - rate)
        committed_forecast_weeks = round(weeks_needed, 1)
        committed_forecast_date = reference_date + timedelta(days=round(weeks_needed * 7))

    return {
        "seven_day_avg": seven_day_avg,
        "starting_weight": starting_weight,
        "goal_weight": goal_weight,
        "weekly_loss_pct": goal.weekly_loss_pct if goal else None,
        "weekly_pace": weekly_pace,
        "weekly_pace_label": weekly_pace_label,
        "weekly_trend": weekly_trend,
        "weight_change_from_start": weight_change_from_start,
        "lost_7_days": lost_7_days,
        "lost_30_days": lost_30_days,
        "lost_all_time": lost_all_time,
        "forecast_date": forecast_date,
        "forecast_weeks": forecast_weeks,
        "committed_forecast_date": committed_forecast_date,
        "committed_forecast_weeks": committed_forecast_weeks,
        "committed_kg_per_week": committed_kg_per_week,
        "goal_progress_pct": goal_progress_pct,
        "streak": get_streak(user_id),
    }
