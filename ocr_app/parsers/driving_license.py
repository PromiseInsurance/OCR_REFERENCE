import re
from datetime import datetime


def normalize_date(date_value):
    """Normalize various date formats to YYYY-MM-DD."""
    if not date_value:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d %m %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_value


def parse_driving_license_front(text):
    """Parse the front side of a driving license."""
    data = {"document_type": "driving_license"}
    
    cleaned = text.upper()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    # License Number
    lic_match = re.search(r'LICENSE(?:\s*NO\.?|:\s*)([A-Z0-9\-]{6,15})', cleaned)
    if lic_match:
        data["License_Number"] = lic_match.group(1).strip()
    
    # Name
    name_match = re.search(
        r'NAME[:\s]*([A-Z\s]+?)(?=\s(?:LICENSE|D\.?O\.?B|DATE|ISSUED|EXPIRY|CATEGORY|$))',
        cleaned
    )
    if name_match:
        data["Name"] = re.sub(r'\s+', ' ', name_match.group(1)).title()
    
    # Date of Birth
    dob_match = re.search(r'(?:D\.?O\.?B|DATE\s*OF\s*BIRTH)[:\s]*(\d{2}[/\-]\d{2}[/\-]\d{4})', cleaned)
    if dob_match:
        data["Date_of_Birth"] = normalize_date(dob_match.group(1))
    
    # Nationality
    nat_match = re.search(r'NATIONALITY[:\s]*([A-Z\s]+?)(?=\s(?:LICENSE|D\.?O\.?B|ISSUED|EXPIRY|$))', cleaned)
    if nat_match:
        nationality = nat_match.group(1).strip()
        data["Nationality"] = nationality.title()
    
    # License Category/Class
    cat_match = re.search(r'(?:CATEGORY|CLASS)[:\s]*([A-Z0-9\s]+?)(?=\s(?:ISSUED|EXPIRY|$))', cleaned)
    if cat_match:
        data["Category"] = cat_match.group(1).strip()
    
    # Issue Date
    issue_match = re.search(r'ISSUED[:\s]*(\d{2}[/\-]\d{2}[/\-]\d{4})', cleaned)
    if issue_match:
        data["Issued_Date"] = normalize_date(issue_match.group(1))
    
    # Expiry Date
    expiry_match = re.search(r'EXPIRY[:\s]*(\d{2}[/\-]\d{2}[/\-]\d{4})', cleaned)
    if expiry_match:
        data["Expiry_Date"] = normalize_date(expiry_match.group(1))
    
    # Fallback: Try to find dates in order
    dates = re.findall(r'\d{2}[/\-]\d{2}[/\-]\d{4}', cleaned)
    if not data.get("Date_of_Birth") and len(dates) >= 1:
        data["Date_of_Birth"] = normalize_date(dates[0])
    if not data.get("Issued_Date") and len(dates) >= 2:
        data["Issued_Date"] = normalize_date(dates[1])
    if not data.get("Expiry_Date") and len(dates) >= 3:
        data["Expiry_Date"] = normalize_date(dates[2])
    
    return {
        "document_type": "driving_license",
        "driving_license_front": {k: v for k, v in data.items() if k != "document_type" and v}
    }


def parse_driving_license_back(text):
    """Parse the back side of a driving license."""
    data = {"document_type": "driving_license"}
    
    cleaned = text.upper()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    # License conditions/restrictions
    conditions_match = re.search(r'CONDITIONS?[:\s]*([A-Z0-9\s\-,]+?)(?=\s(?:REMARKS|NOTE|$))', cleaned)
    if conditions_match:
        conditions = conditions_match.group(1).strip()
        data["Conditions"] = conditions
    
    # Remarks or special notes
    remarks_match = re.search(r'(?:REMARKS?|NOTES?)[:\s]*([A-Z0-9\s\-,\.]+?)$', cleaned)
    if remarks_match:
        data["Remarks"] = remarks_match.group(1).strip()
    
    # Points/Violations
    points_match = re.search(r'POINTS?[:\s]*(\d+)', cleaned)
    if points_match:
        data["Points"] = int(points_match.group(1))
    
    # Issuing Authority
    authority_match = re.search(r'(?:ISSUED\s*BY|AUTHORITY)[:\s]*([A-Z\s]+?)(?=\s(?:POINTS|REMARKS|$))', cleaned)
    if authority_match:
        data["Issuing_Authority"] = authority_match.group(1).strip().title()
    
    return {
        "document_type": "driving_license",
        "driving_license_back": {k: v for k, v in data.items() if k != "document_type" and v}
    }


def parse_driving_license(text):
    """Main entry point for parsing driving license (front or back or combined)."""
    data = {"document_type": "driving_license"}
    
    # Determine if it's front or back based on content
    is_front = bool(re.search(r'(LICENSE|D\.?O\.?B|DATE\s*OF\s*BIRTH|CATEGORY)', text.upper()))
    is_back = bool(re.search(r'(CONDITIONS?|REMARKS?|POINTS?|AUTHORITY)', text.upper()))
    
    if is_front:
        front_data = parse_driving_license_front(text)
        data.update(front_data)
    
    if is_back:
        back_data = parse_driving_license_back(text)
        data.update(back_data)
    
    # If no specific data was found, include the raw text
    if not data.get("driving_license_front") and not data.get("driving_license_back"):
        data["raw_text"] = text[:500]
    
    return data
