import re
from datetime import datetime, timedelta


def luhn_checksum(card_number):
    """Calculate Luhn checksum for ID number validation."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10


def validate_id_number(id_number):
    """
    Validate Emirates ID number format and check digit.
    Format: 784-XXXX-XXXXXXX-D
    """
    if not id_number:
        return False, "ID number is required"
    
    # Remove common formatting
    cleaned = id_number.replace("-", "").replace(" ", "").upper()
    
    # Check basic format
    if not re.match(r'^784\d{13}$', cleaned):
        return False, "Invalid ID number format. Expected: 784-XXXX-XXXXXXX-D"
    
    # Validate Luhn check digit
    check_digit = int(cleaned[-1])
    calculated = luhn_checksum(cleaned[:-1])
    
    if check_digit != calculated:
        return False, "Invalid ID number check digit"
    
    return True, "Valid"


def validate_name(name):
    """Validate name format (minimum 2 words)."""
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    
    # Check for minimum 2 words
    words = name.split()
    if len(words) < 2:
        return False, "Name must contain at least 2 words"
    
    # Check length
    if len(name) < 3 or len(name) > 100:
        return False, "Name must be between 3 and 100 characters"
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, "Name contains invalid characters"
    
    return True, "Valid"


def validate_date_format(date_str):
    """Validate and parse date in DD/MM/YYYY or DD-MM-YYYY format."""
    if not date_str:
        return False, None, "Date is required"
    
    # Try different formats
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return True, datetime.strptime(date_str, fmt), "Valid"
        except ValueError:
            continue
    
    return False, None, "Invalid date format. Expected DD/MM/YYYY"


def validate_date_of_birth(dob_str):
    """Validate date of birth (age 18+ and reasonable)."""
    valid, dob_date, msg = validate_date_format(dob_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    
    if age < 18:
        return False, "Age must be 18 or older"
    
    if age > 120:
        return False, "Age cannot exceed 120 years"
    
    if dob_date > today:
        return False, "Date of birth cannot be in the future"
    
    if dob_date.year < 1900:
        return False, "Date of birth must be after 1900"
    
    return True, "Valid"


def validate_expiry_date(expiry_str):
    """Validate expiry date (must be in future)."""
    valid, expiry_date, msg = validate_date_format(expiry_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    
    if expiry_date < today:
        return False, "Document has expired"
    
    # Check if expiring soon (within 30 days)
    days_to_expiry = (expiry_date - today).days
    if days_to_expiry < 30:
        return False, f"Document expiring soon (in {days_to_expiry} days)"
    
    return True, "Valid"


def validate_nationality(nationality):
    """Validate nationality is recognized."""
    if not nationality:
        return False, "Nationality is required"
    
    nationality = nationality.strip()
    
    if len(nationality) < 2 or len(nationality) > 50:
        return False, "Invalid nationality format"
    
    if any(char.isdigit() for char in nationality):
        return False, "Nationality cannot contain numbers"
    
    return True, "Valid"


def validate_gender(gender):
    """Validate gender format."""
    if not gender:
        return False, "Gender is required"
    
    gender = gender.strip().upper()
    
    if gender not in ['M', 'F']:
        return False, "Gender must be 'M' or 'F'"
    
    return True, "Valid"


def validate_card_number(card_number):
    """Validate card number (numeric, 7-10 digits)."""
    if not card_number:
        return False, "Card number is required"
    
    card_number = str(card_number).strip()
    
    if not card_number.isdigit():
        return False, "Card number must contain only digits"
    
    if len(card_number) < 7 or len(card_number) > 10:
        return False, "Card number must be 7-10 digits"
    
    return True, "Valid"


def validate_occupation(occupation):
    """Validate occupation format."""
    if not occupation:
        return False, "Occupation is required"
    
    occupation = occupation.strip()
    
    if len(occupation) < 2 or len(occupation) > 100:
        return False, "Occupation must be between 2 and 100 characters"
    
    if not re.match(r"^[a-zA-Z\s\-/]+$", occupation):
        return False, "Occupation contains invalid characters"
    
    return True, "Valid"


def validate_issuing_place(issuing_place):
    """Validate issuing place is valid UAE emirate."""
    if not issuing_place:
        return False, "Issuing place is required"
    
    valid_emirates = [
        "Abu Dhabi", "Dubai", "Sharjah", "Ajman",
        "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"
    ]
    
    issuing_place = issuing_place.strip()
    
    # Case-insensitive matching
    if not any(emirate.lower() == issuing_place.lower() for emirate in valid_emirates):
        return False, f"Invalid emirate. Must be one of: {', '.join(valid_emirates)}"
    
    return True, "Valid"


def validate_emirates_id(data):
    """
    Comprehensive validation for Emirates ID data.
    Validates both front and back sides with all business rules.
    """
    errors = {}
    front = data.get("emirates_id_front", {})
    back = data.get("emirates_id_back", {})

    # Determine which side(s) we have
    if front and back:
        side = "combined"
    elif front:
        side = "front"
    elif back:
        side = "back"
    else:
        return {
            "status": "FAILED",
            "errors": {"document": "No Emirates ID data found"},
            "side": "unknown"
        }

    # FRONT SIDE VALIDATION
    if side in ["front", "combined"]:
        # ID Number validation
        id_number = front.get("ID_Number")
        if not id_number:
            errors["emirates_id_front.ID_Number"] = "Missing ID number"
        else:
            valid, msg = validate_id_number(id_number)
            if not valid:
                errors["emirates_id_front.ID_Number"] = msg

        # Name validation
        name = front.get("Name")
        if not name:
            errors["emirates_id_front.Name"] = "Missing name"
        else:
            valid, msg = validate_name(name)
            if not valid:
                errors["emirates_id_front.Name"] = msg

        # Date of Birth validation
        dob = front.get("Date_of_Birth")
        if not dob:
            errors["emirates_id_front.Date_of_Birth"] = "Missing date of birth"
        else:
            valid, msg = validate_date_of_birth(dob)
            if not valid:
                errors["emirates_id_front.Date_of_Birth"] = msg

        # Nationality validation
        nationality = front.get("Nationality")
        if not nationality:
            errors["emirates_id_front.Nationality"] = "Missing nationality"
        else:
            valid, msg = validate_nationality(nationality)
            if not valid:
                errors["emirates_id_front.Nationality"] = msg

        # Sex/Gender validation (optional but if present, validate)
        sex = front.get("Sex")
        if sex:
            valid, msg = validate_gender(sex)
            if not valid:
                errors["emirates_id_front.Sex"] = msg

        # Issuing Date validation (if present)
        issuing_date = front.get("Issuing_Date")
        if issuing_date:
            valid, issue_date, msg = validate_date_format(issuing_date)
            if not valid:
                errors["emirates_id_front.Issuing_Date"] = msg
            elif issue_date and issue_date > datetime.now():
                errors["emirates_id_front.Issuing_Date"] = "Issuing date cannot be in the future"

        # Expiry Date validation
        expiry_date = front.get("Expiry_Date")
        if not expiry_date:
            errors["emirates_id_front.Expiry_Date"] = "Missing expiry date"
        else:
            valid, msg = validate_expiry_date(expiry_date)
            if not valid:
                errors["emirates_id_front.Expiry_Date"] = msg

    # BACK SIDE VALIDATION
    if side in ["back", "combined"]:
        # Card Number validation
        card_number = back.get("Card_Number")
        if not card_number:
            errors["emirates_id_back.Card_Number"] = "Missing card number"
        else:
            valid, msg = validate_card_number(card_number)
            if not valid:
                errors["emirates_id_back.Card_Number"] = msg

        # Occupation validation
        occupation = back.get("Occupation")
        if not occupation:
            errors["emirates_id_back.Occupation"] = "Missing occupation"
        else:
            valid, msg = validate_occupation(occupation)
            if not valid:
                errors["emirates_id_back.Occupation"] = msg

        # Issuing Place validation
        issuing_place = back.get("Issuing_Place")
        if not issuing_place:
            errors["emirates_id_back.Issuing_Place"] = "Missing issuing place"
        else:
            valid, msg = validate_issuing_place(issuing_place)
            if not valid:
                errors["emirates_id_back.Issuing_Place"] = msg

        # Employer validation (optional)
        employer = back.get("Employer")
        if employer and len(employer.strip()) < 2:
            errors["emirates_id_back.Employer"] = "Employer name too short"

    # Determine final status
    if errors:
        status = "FAILED" if len(errors) > 2 else "PENDING"
    else:
        status = "VERIFIED"

    return {
        "status": status,
        "errors": errors,
        "side": side
    }