import re
from datetime import datetime, timedelta


def validate_license_number(license_number):
    """
    Validate UAE driving license number format.
    Format: 8-12 digits (emirate code + sequence)
    """
    if not license_number:
        return False, "License number is required"
    
    license_number = str(license_number).strip()
    
    if not license_number.isdigit():
        return False, "License number must contain only digits"
    
    if len(license_number) < 8 or len(license_number) > 12:
        return False, "License number must be 8-12 digits"
    
    # Check if starts with valid emirate code (01-07)
    emirate_code = license_number[:2]
    if emirate_code not in ["01", "02", "03", "04", "05", "06", "07"]:
        return False, "Invalid emirate code in license number"
    
    return True, "Valid"


def validate_name(name):
    """Validate driver name (minimum 2 words)."""
    if not name:
        return False, "Name is required"
    
    name = str(name).strip()
    
    # Check for minimum 2 words
    words = name.split()
    if len(words) < 2:
        return False, "Name must contain at least 2 words"
    
    # Check length
    if len(name) < 3 or len(name) > 100:
        return False, "Name must be between 3 and 100 characters"
    
    # Check for valid characters
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, "Name contains invalid characters"
    
    return True, "Valid"


def validate_date_format(date_str):
    """Validate and parse date in various formats."""
    if not date_str:
        return False, None, "Date is required"
    
    date_str = str(date_str).strip()
    
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return True, datetime.strptime(date_str, fmt), "Valid"
        except ValueError:
            continue
    
    return False, None, "Invalid date format. Expected DD/MM/YYYY"


def validate_date_of_birth(dob_str):
    """Validate date of birth (18+ and reasonable age)."""
    valid, dob_date, msg = validate_date_format(dob_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    
    if age < 18:
        return False, "Driver must be 18 years or older"
    
    if age > 120:
        return False, "Age cannot exceed 120 years"
    
    if dob_date > today:
        return False, "Date of birth cannot be in the future"
    
    if dob_date.year < 1900:
        return False, "Date of birth must be after 1900"
    
    return True, "Valid"


def validate_nationality(nationality):
    """Validate nationality."""
    if not nationality:
        return False, "Nationality is required"
    
    nationality = str(nationality).strip()
    
    if len(nationality) < 2 or len(nationality) > 50:
        return False, "Invalid nationality format"
    
    if any(char.isdigit() for char in nationality):
        return False, "Nationality cannot contain numbers"
    
    return True, "Valid"


def validate_gender(gender):
    """Validate gender."""
    if not gender:
        return False, "Gender is required"
    
    gender = str(gender).strip().upper()
    
    if gender not in ['M', 'F']:
        return False, "Gender must be 'M' or 'F'"
    
    return True, "Valid"


def validate_license_category(category):
    """Validate driving license category/class."""
    if not category:
        return False, "License category is required"
    
    category = str(category).strip().upper()
    
    valid_categories = ['A', 'B', 'B+', 'C', 'C+', 'D', 'E', 'F', 'G']
    
    # Handle multiple categories (e.g., "A, B, C")
    categories = [cat.strip() for cat in category.split(",")]
    
    for cat in categories:
        if cat not in valid_categories:
            return False, f"Invalid category: {cat}. Valid categories: {', '.join(valid_categories)}"
    
    return True, "Valid"


def validate_issued_date(issued_date_str):
    """Validate license issued date."""
    valid, issued_date, msg = validate_date_format(issued_date_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    
    if issued_date > today:
        return False, "Issued date cannot be in the future"
    
    if issued_date.year < 2000:
        return False, "Issued date must be after 2000"
    
    return True, "Valid"


def validate_expiry_date(expiry_str):
    """Validate license expiry date."""
    valid, expiry_date, msg = validate_date_format(expiry_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    grace_period = today - timedelta(days=30)
    
    if expiry_date < grace_period:
        return False, "License has expired (more than 30 days)"
    
    if expiry_date < today:
        days_expired = (today - expiry_date).days
        return False, f"License expired {days_expired} days ago"
    
    # Check if expiring soon
    days_to_expiry = (expiry_date - today).days
    if days_to_expiry < 30:
        return False, f"License expiring soon (in {days_to_expiry} days)"
    
    return True, "Valid"


def validate_dates_consistency(issued_date_obj, expiry_date_obj):
    """Validate issued and expiry dates consistency."""
    if not (issued_date_obj and expiry_date_obj):
        return True, "Valid"
    
    if issued_date_obj >= expiry_date_obj:
        return False, "Issued date must be before expiry date"
    
    # Check validity period (typically 3, 5, or 10 years)
    days_diff = (expiry_date_obj - issued_date_obj).days
    years_diff = days_diff / 365.25
    
    # Valid periods: 3, 5, or 10 years (with some tolerance)
    valid_periods = [3, 5, 10]
    is_valid_period = any(abs(years_diff - period) < 0.5 for period in valid_periods)
    
    if not is_valid_period and (days_diff < 365 or days_diff > 3650):
        return False, "License validity period must be 1-10 years"
    
    return True, "Valid"


def validate_issuing_authority(authority):
    """Validate issuing authority."""
    if not authority:
        return False, "Issuing authority is required"
    
    authority = str(authority).strip()
    
    valid_authorities = [
        "RTA Dubai", "RTA Abu Dhabi", "Sharjah Police",
        "Ajman Police", "Umm Al Quwain Police",
        "Ras Al Khaimah Police", "Fujairah Police",
        "Dubai Police", "Abu Dhabi Police"
    ]
    
    # Case-insensitive matching
    if not any(auth.lower() == authority.lower() for auth in valid_authorities):
        return False, "Invalid issuing authority"
    
    return True, "Valid"


def validate_points(points_str):
    """Validate violation points."""
    if not points_str:
        return True, "Valid"  # Optional field
    
    points_str = str(points_str).strip()
    
    if not points_str.isdigit():
        return False, "Points must be numeric"
    
    points = int(points_str)
    
    if points < 0 or points > 1000:
        return False, "Points must be between 0 and 1000"
    
    return True, "Valid"


def validate_conditions(conditions):
    """Validate driving conditions/restrictions."""
    if not conditions:
        return True, "Valid"  # Optional field
    
    conditions = str(conditions).strip()
    
    valid_conditions = [
        "None", "Automatic", "Glasses Required", "Hearing Aid Required",
        "Daytime Only", "Speed Limited", "Manual", "Prosthetic Limb"
    ]
    
    # Case-insensitive matching
    if not any(cond.lower() == conditions.lower() for cond in valid_conditions):
        # Accept if it's a reasonable custom restriction
        if len(conditions) > 100:
            return False, "Conditions text too long"
    
    return True, "Valid"


def validate_remarks(remarks):
    """Validate remarks/notes field."""
    if not remarks:
        return True, "Valid"  # Optional field
    
    remarks = str(remarks).strip()
    
    if len(remarks) > 200:
        return False, "Remarks must be less than 200 characters"
    
    if not re.match(r"^[a-zA-Z0-9\s\-.,()]+$", remarks):
        return False, "Remarks contains invalid characters"
    
    return True, "Valid"


def validate_driving_license(data):
    """
    Comprehensive validation for Driving License data.
    Validates both front and back sides with all business rules.
    """
    errors = {}

    front_data = data.get("driving_license_front", {})
    back_data = data.get("driving_license_back", {})

    # Determine which side(s) we have
    if front_data and back_data:
        side = "combined"
    elif front_data and not back_data:
        side = "front"
    elif back_data and not front_data:
        side = "back"
    else:
        side = "unknown"
        return {
            "status": "FAILED",
            "errors": {"document": "No driving license data extracted"},
            "side": side
        }

    # FRONT SIDE VALIDATION
    if side in ["front", "combined"]:
        # License number
        license_number = front_data.get("License_Number")
        if not license_number:
            errors["driving_license_front.License_Number"] = "Missing license number"
        else:
            valid, msg = validate_license_number(license_number)
            if not valid:
                errors["driving_license_front.License_Number"] = msg

        # Name
        name = front_data.get("Name")
        if not name:
            errors["driving_license_front.Name"] = "Missing driver name"
        else:
            valid, msg = validate_name(name)
            if not valid:
                errors["driving_license_front.Name"] = msg

        # Date of Birth
        dob = front_data.get("Date_of_Birth")
        if not dob:
            errors["driving_license_front.Date_of_Birth"] = "Missing date of birth"
        else:
            valid, msg = validate_date_of_birth(dob)
            if not valid:
                errors["driving_license_front.Date_of_Birth"] = msg

        # Nationality
        nationality = front_data.get("Nationality")
        if not nationality:
            errors["driving_license_front.Nationality"] = "Missing nationality"
        else:
            valid, msg = validate_nationality(nationality)
            if not valid:
                errors["driving_license_front.Nationality"] = msg

        # Gender (optional)
        gender = front_data.get("Sex")
        if gender:
            valid, msg = validate_gender(gender)
            if not valid:
                errors["driving_license_front.Sex"] = msg

        # License Category
        category = front_data.get("Category")
        if not category:
            errors["driving_license_front.Category"] = "Missing license category"
        else:
            valid, msg = validate_license_category(category)
            if not valid:
                errors["driving_license_front.Category"] = msg

        # Issued Date
        issued_date = front_data.get("Issued_Date")
        issued_date_obj = None
        if not issued_date:
            errors["driving_license_front.Issued_Date"] = "Missing issued date"
        else:
            valid, msg = validate_issued_date(issued_date)
            if not valid:
                errors["driving_license_front.Issued_Date"] = msg
            else:
                _, issued_date_obj, _ = validate_date_format(issued_date)

        # Expiry Date
        expiry_date = front_data.get("Expiry_Date")
        expiry_date_obj = None
        if not expiry_date:
            errors["driving_license_front.Expiry_Date"] = "Missing expiry date"
        else:
            valid, msg = validate_expiry_date(expiry_date)
            if not valid:
                errors["driving_license_front.Expiry_Date"] = msg
            else:
                _, expiry_date_obj, _ = validate_date_format(expiry_date)

        # Date consistency
        if issued_date_obj and expiry_date_obj:
            valid, msg = validate_dates_consistency(issued_date_obj, expiry_date_obj)
            if not valid:
                errors["driving_license_front.date_consistency"] = msg

        # Issuing Authority
        authority = front_data.get("Issuing_Authority")
        if not authority:
            errors["driving_license_front.Issuing_Authority"] = "Missing issuing authority"
        else:
            valid, msg = validate_issuing_authority(authority)
            if not valid:
                errors["driving_license_front.Issuing_Authority"] = msg

    # BACK SIDE VALIDATION
    if side in ["back", "combined"]:
        # Conditions (optional)
        conditions = back_data.get("Conditions")
        if conditions:
            valid, msg = validate_conditions(conditions)
            if not valid:
                errors["driving_license_back.Conditions"] = msg

        # Points (optional)
        points = back_data.get("Points")
        if points:
            valid, msg = validate_points(points)
            if not valid:
                errors["driving_license_back.Points"] = msg

        # Remarks (optional)
        remarks = back_data.get("Remarks")
        if remarks:
            valid, msg = validate_remarks(remarks)
            if not valid:
                errors["driving_license_back.Remarks"] = msg

    # Determine final status
    if errors:
        # Check severity: critical errors (missing required front fields) = FAILED
        critical_fields = [
            "driving_license_front.License_Number",
            "driving_license_front.Name",
            "driving_license_front.Date_of_Birth",
            "driving_license_front.Category",
            "driving_license_front.Expiry_Date"
        ]
        
        has_critical_error = any(field in errors for field in critical_fields)
        status = "FAILED" if has_critical_error else "PENDING"
    else:
        status = "VERIFIED"

    return {
        "status": status,
        "errors": errors,
        "side": side
    }
