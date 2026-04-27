import re
from datetime import datetime, timedelta


def validate_registration_number(reg_number):
    """
    Validate registration/plate number format.
    Format: Letter/Digits (e.g., U/19033)
    """
    if not reg_number:
        return False, "Registration number is required"
    
    reg_number = str(reg_number).strip()
    
    # Check format: Letter/Digits
    if not re.match(r"^[A-Z]{1}/\d{1,6}$", reg_number):
        return False, "Invalid format. Expected: Letter/Digits (e.g., U/19033)"
    
    return True, "Valid"


def validate_tcf_number(tcf_number):
    """Validate Traffic Code (TCF) number."""
    if not tcf_number:
        return False, "TCF number is required"
    
    tcf_number = str(tcf_number).strip()
    
    if not tcf_number.isdigit():
        return False, "TCF number must contain only digits"
    
    if len(tcf_number) < 6 or len(tcf_number) > 10:
        return False, "TCF number must be 6-10 digits"
    
    return True, "Valid"


def validate_name(name):
    """Validate owner name (minimum 2 words)."""
    if not name:
        return False, "Owner name is required"
    
    name = str(name).strip()
    
    # Check for minimum 2 words
    words = name.split()
    if len(words) < 2:
        return False, "Name must contain at least first and last name"
    
    # Check length
    if len(name) < 3 or len(name) > 100:
        return False, "Name must be between 3 and 100 characters"
    
    # Check for valid characters
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, "Name contains invalid characters"
    
    # Check if all uppercase (likely OCR error)
    if name.isupper() and len(name) > 5:
        return False, "Name appears to be improperly formatted"
    
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


def validate_emirate(emirate):
    """Validate emirate name."""
    if not emirate:
        return False, "Emirate is required"
    
    valid_emirates = [
        "Abu Dhabi", "Dubai", "Sharjah", "Ajman",
        "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"
    ]
    
    emirate = str(emirate).strip()
    
    if not any(e.lower() == emirate.lower() for e in valid_emirates):
        return False, f"Invalid emirate. Must be one of: {', '.join(valid_emirates)}"
    
    return True, "Valid"


def validate_date_format(date_str):
    """Validate date format."""
    if not date_str:
        return False, None, "Date is required"
    
    date_str = str(date_str).strip()
    
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return True, datetime.strptime(date_str, fmt), "Valid"
        except ValueError:
            continue
    
    return False, None, "Invalid date format. Expected DD/MM/YYYY"


def validate_registration_date(reg_date_str):
    """Validate registration date."""
    valid, reg_date, msg = validate_date_format(reg_date_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    
    if reg_date > today:
        return False, "Registration date cannot be in the future"
    
    if reg_date.year < 2000:
        return False, "Registration date must be after 2000"
    
    return True, "Valid"


def validate_expiry_date(expiry_str):
    """Validate registration expiry date."""
    valid, expiry_date, msg = validate_date_format(expiry_str)
    if not valid:
        return False, msg
    
    today = datetime.now()
    grace_period = today - timedelta(days=30)
    
    if expiry_date < grace_period:
        return False, "Registration has expired (more than 30 days)"
    
    if expiry_date < today:
        days_expired = (today - expiry_date).days
        return False, f"Registration expired {days_expired} days ago"
    
    # Check if expiring soon
    days_to_expiry = (expiry_date - today).days
    if days_to_expiry < 30:
        return False, f"Registration expiring soon (in {days_to_expiry} days)"
    
    return True, "Valid"


def validate_dates_consistency(reg_date_obj, expiry_date_obj):
    """Validate that registration date is before expiry date."""
    if not (reg_date_obj and expiry_date_obj):
        return True, "Valid"
    
    if reg_date_obj >= expiry_date_obj:
        return False, "Registration date must be before expiry date"
    
    # Check reasonable validity period (typically 1 year)
    days_diff = (expiry_date_obj - reg_date_obj).days
    if days_diff < 30:
        return False, "Validity period too short (minimum 30 days)"
    
    if days_diff > 3650:  # 10 years
        return False, "Validity period too long (maximum 10 years)"
    
    return True, "Valid"


def validate_vehicle_type(vehicle_type):
    """Validate vehicle type."""
    if not vehicle_type:
        return False, "Vehicle type is required"
    
    valid_types = [
        "Car", "Truck", "Bus", "Motorcycle", "Taxi",
        "Minibus", "Trailer", "Heavy Vehicle", "Pickup",
        "Van", "Commercial", "Sedan", "SUV", "Coupe"
    ]
    
    vehicle_type = str(vehicle_type).strip()
    
    if not any(vt.lower() == vehicle_type.lower() for vt in valid_types):
        return False, f"Invalid vehicle type: {vehicle_type}"
    
    return True, "Valid"


def validate_model_year(year_str):
    """Validate vehicle model year."""
    if not year_str:
        return False, "Model year is required"
    
    year_str = str(year_str).strip()
    
    if not year_str.isdigit() or len(year_str) != 4:
        return False, "Model year must be 4 digits (e.g., 2015)"
    
    year = int(year_str)
    current_year = datetime.now().year
    
    if year < 1900:
        return False, "Model year cannot be before 1900"
    
    if year > current_year + 1:
        return False, "Model year cannot be in the future"
    
    return True, "Valid"


def validate_engine_number(engine_number):
    """Validate engine number format."""
    if not engine_number:
        return False, "Engine number is required"
    
    engine_number = str(engine_number).strip()
    
    if len(engine_number) < 6 or len(engine_number) > 20:
        return False, "Engine number must be 6-20 characters"
    
    if not re.match(r"^[A-Z0-9]+$", engine_number):
        return False, "Engine number must be alphanumeric"
    
    return True, "Valid"


def validate_chassis_number(chassis_number):
    """Validate chassis/VIN number format."""
    if not chassis_number:
        return False, "Chassis number is required"
    
    chassis_number = str(chassis_number).strip()
    
    if len(chassis_number) < 10 or len(chassis_number) > 30:
        return False, "Chassis number must be 10-30 characters"
    
    if not re.match(r"^[A-Z0-9]+$", chassis_number):
        return False, "Chassis number must be alphanumeric"
    
    return True, "Valid"


def validate_number_of_passengers(passengers_str):
    """Validate number of passengers."""
    if not passengers_str:
        return False, "Number of passengers is required"
    
    passengers_str = str(passengers_str).strip()
    
    if not passengers_str.isdigit():
        return False, "Number of passengers must be numeric"
    
    passengers = int(passengers_str)
    
    if passengers < 1 or passengers > 100:
        return False, "Number of passengers must be between 1 and 100"
    
    return True, "Valid"


def validate_origin(origin):
    """Validate vehicle origin/manufacturer country."""
    if not origin:
        return False, "Origin/manufacturer is required"
    
    origin = str(origin).strip()
    
    if len(origin) < 2 or len(origin) > 50:
        return False, "Invalid origin format"
    
    if any(char.isdigit() for char in origin):
        return False, "Origin cannot contain numbers"
    
    return True, "Valid"


def validate_mulkiya(data):
    """
    Comprehensive validation for Mulkiya (Vehicle Registration) data.
    Validates both front and back sides with all business rules.
    """
    errors = {}

    front_required = [
        "registration_no", "tcf_no", "owner", "nationality",
        "registration_date", "registration_expiry_date",
    ]

    back_required = [
        "model_year", "origin", "number_of_passengers",
        "vehicle_type", "engine_no", "chassis_no",
    ]

    front_data = data.get("mulkiya_front", {})
    back_data = data.get("mulkiya_back", {})

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
            "errors": {"document": "No Mulkiya data extracted"},
            "side": side
        }

    # FRONT SIDE VALIDATION
    if side in ["front", "combined"]:
        # Registration number
        reg_no = front_data.get("registration_no")
        if not reg_no:
            errors["mulkiya_front.registration_no"] = "Missing registration number"
        else:
            valid, msg = validate_registration_number(reg_no)
            if not valid:
                errors["mulkiya_front.registration_no"] = msg

        # TCF number
        tcf = front_data.get("tcf_no")
        if not tcf:
            errors["mulkiya_front.tcf_no"] = "Missing TCF number"
        else:
            valid, msg = validate_tcf_number(tcf)
            if not valid:
                errors["mulkiya_front.tcf_no"] = msg

        # Owner name
        owner = front_data.get("owner")
        if not owner:
            errors["mulkiya_front.owner"] = "Missing owner name"
        else:
            valid, msg = validate_name(owner)
            if not valid:
                errors["mulkiya_front.owner"] = msg

        # Nationality
        nationality = front_data.get("nationality")
        if not nationality:
            errors["mulkiya_front.nationality"] = "Missing nationality"
        else:
            valid, msg = validate_nationality(nationality)
            if not valid:
                errors["mulkiya_front.nationality"] = msg

        # Plate source (emirate)
        if front_data.get("plate_source"):
            valid, msg = validate_emirate(front_data["plate_source"])
            if not valid:
                errors["mulkiya_front.plate_source"] = msg

        # Registration date
        reg_date = front_data.get("registration_date")
        reg_date_obj = None
        if not reg_date:
            errors["mulkiya_front.registration_date"] = "Missing registration date"
        else:
            valid, msg = validate_registration_date(reg_date)
            if not valid:
                errors["mulkiya_front.registration_date"] = msg
            else:
                _, reg_date_obj, _ = validate_date_format(reg_date)

        # Expiry date
        expiry_date = front_data.get("registration_expiry_date")
        expiry_date_obj = None
        if not expiry_date:
            errors["mulkiya_front.registration_expiry_date"] = "Missing registration expiry date"
        else:
            valid, msg = validate_expiry_date(expiry_date)
            if not valid:
                errors["mulkiya_front.registration_expiry_date"] = msg
            else:
                _, expiry_date_obj, _ = validate_date_format(expiry_date)

        # Date consistency check
        if reg_date_obj and expiry_date_obj:
            valid, msg = validate_dates_consistency(reg_date_obj, expiry_date_obj)
            if not valid:
                errors["mulkiya_front.date_consistency"] = msg

        # Insurance expiry date check (if present)
        if front_data.get("insurance_expiry_date"):
            valid, msg = validate_expiry_date(front_data["insurance_expiry_date"])
            if not valid:
                errors["mulkiya_front.insurance_expiry_date"] = msg

    # BACK SIDE VALIDATION
    if side in ["back", "combined"]:
        # Model year
        model_year = back_data.get("model_year")
        if not model_year:
            errors["mulkiya_back.model_year"] = "Missing model year"
        else:
            valid, msg = validate_model_year(model_year)
            if not valid:
                errors["mulkiya_back.model_year"] = msg

        # Origin
        origin = back_data.get("origin")
        if not origin:
            errors["mulkiya_back.origin"] = "Missing origin"
        else:
            valid, msg = validate_origin(origin)
            if not valid:
                errors["mulkiya_back.origin"] = msg

        # Number of passengers
        passengers = back_data.get("number_of_passengers")
        if not passengers:
            errors["mulkiya_back.number_of_passengers"] = "Missing number of passengers"
        else:
            valid, msg = validate_number_of_passengers(passengers)
            if not valid:
                errors["mulkiya_back.number_of_passengers"] = msg

        # Vehicle type
        vehicle_type = back_data.get("vehicle_type")
        if not vehicle_type:
            errors["mulkiya_back.vehicle_type"] = "Missing vehicle type"
        else:
            valid, msg = validate_vehicle_type(vehicle_type)
            if not valid:
                errors["mulkiya_back.vehicle_type"] = msg

        # Engine number
        engine_no = back_data.get("engine_no")
        if not engine_no:
            errors["mulkiya_back.engine_no"] = "Missing engine number"
        else:
            valid, msg = validate_engine_number(engine_no)
            if not valid:
                errors["mulkiya_back.engine_no"] = msg

        # Chassis number
        chassis_no = back_data.get("chassis_no")
        if not chassis_no:
            errors["mulkiya_back.chassis_no"] = "Missing chassis number"
        else:
            valid, msg = validate_chassis_number(chassis_no)
            if not valid:
                errors["mulkiya_back.chassis_no"] = msg

        # Engine and Chassis number consistency
        if engine_no and chassis_no:
            if engine_no.upper() == chassis_no.upper():
                errors["mulkiya_back.engine_chassis"] = "Engine and chassis numbers must be different"

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