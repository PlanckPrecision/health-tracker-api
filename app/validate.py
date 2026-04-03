from flask import Flask
from datetime import datetime

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
        # This triggers if there are letters, emojis, or multiple separators
        return False, "Invalid format. Only numbers and ',' are allowed"

    return True, val

def check_date(date_raw):
    date_raw = (date_raw or "").strip()

    if not date_raw:
        return True, datetime.today().date()

    try:
        date_obj = datetime.strptime(date_raw, "%d.%m.%Y").date()
        return True, date_obj
    except ValueError:
        return False, "Invalid date format. Use DD.MM.YYYY"