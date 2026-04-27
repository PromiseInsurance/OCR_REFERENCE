import re
from datetime import datetime



#HELPERS

def normalize_date(date_value):
    if not date_value:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d %m %Y"):
        try:
            return datetime.strptime(date_value, fmt).strftime("%Y-%m-%d")
        except:
            continue

    return None


def format_mrz_date(date_str):
    try:
        year = int(date_str[:2])
        month = date_str[2:4]
        day = date_str[4:6]

        year += 2000 if year < 50 else 1900
        return f"{year}-{month}-{day}"
    except:
        return None


#FRONT PARSER

def parse_emirates_id_front(text):

    data = {"document_type": "emirates_id"}

    cleaned = text.upper()
    cleaned = re.sub(r'[\u0600-\u06FF]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # ID Number
    id_match = re.search(r'784[\s-]?\d{4}[\s-]?\d{7}[\s-]?\d', cleaned)
    if id_match:
        raw = re.sub(r'[\s-]', '', id_match.group(0))
        data["ID_Number"] = f"{raw[:3]}-{raw[3:7]}-{raw[7:14]}-{raw[14]}"

    # Name
    name_match = re.search(
        r'NAME[:\s]+([A-Z\s]+?)(?=\s(NATIONALITY|DATE|DOB|ID|EXPIRY|ISSUING|SEX|$))',
        cleaned
    )
    if name_match:
        data["Name"] = re.sub(r'\s+', ' ', name_match.group(1)).title()

    # Nationality
    nat_match = re.search(r'NATIONALITY[:\s]+([A-Z\s]+)', cleaned)
    if nat_match:
        data["Nationality"] = nat_match.group(1).strip().title()

    # Gender
    gender_match = re.search(r'(SEX|GENDER)[:\s]+([MF])', cleaned)
    if gender_match:
        data["Sex"] = gender_match.group(2)

    # Dates
    dob = re.search(r'(DOB|DATE OF BIRTH)[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})', cleaned)
    if dob:
        data["Date_of_Birth"] = normalize_date(dob.group(2))

    issue = re.search(r'ISSUING DATE[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})', cleaned)
    if issue:
        data["Issuing_Date"] = normalize_date(issue.group(1))

    expiry = re.search(r'EXPIRY DATE[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})', cleaned)
    if expiry:
        data["Expiry_Date"] = normalize_date(expiry.group(1))

    # fallback expiry (last date)
    if not data.get("Expiry_Date"):
        dates = re.findall(r'\d{2}/\d{2}/\d{4}', cleaned)
        if dates:
            data["Expiry_Date"] = normalize_date(dates[-1])

    final = {"document_type": "emirates_id"}

    fields = ["ID_Number","Name","Date_of_Birth","Nationality","Issuing_Date","Expiry_Date","Sex"]
    front = {k: data[k] for k in fields if k in data}

    if front:
        final["emirates_id_front"] = front

    return final



#BACK PARSER (FIXED)

def parse_emirates_id_back(text):

    data = {"document_type": "emirates_id"}

    cleaned = text.upper()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    lines = [l.strip() for l in text.split("\n") if l.strip()]


    #CARD NUMBER

    card_match = re.search(r'CARD NUMBER[:\s]*([0-9]{6,12})', cleaned)
    if card_match:
        data["Card_Number"] = card_match.group(1)
    else:
        # fallback (standalone number)
        fallback = re.search(r'\b\d{7,10}\b', cleaned)
        if fallback:
            data["Card_Number"] = fallback.group(0)


    #OCCUPATION

    occ_match = re.search(r'OCCUPATION[:\s]*([A-Z\s]+)', text.upper())

    if occ_match:
        occupation = occ_match.group(1).strip()

        # Remove OCR noise
        occupation = occupation.split("IF")[0].strip()

        data["Occupation"] = occupation.title()

    
    #EMPLOYER (NEW FIELD)
    emp_match = re.search(r'Employer[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
    if emp_match:
        employer = emp_match.group(1).strip()
        employer = re.split(r'If you find|ILARE|<', employer)[0].strip()
        data["Employer"] = employer.title()


    #ISSUING PLACE

    place_match = re.search(r'ISSUING PLACE[:\s]*([A-Z\s]+)', text.upper())
    if place_match:
        place = place_match.group(1).strip()
        stop_words = ["IF", "PLEASE", "RETURN", "POLICE", "STATION"]
        for word in stop_words:
            if word in place:
                place = place.split(word)[0].strip()
        place = " ".join(place.split()[:2])
        data["Issuing_Place"] = place.title()

    #MRZ EXTRACTION (FALLBACK)

    mrz_lines = [l for l in lines if "<" in l and len(l) > 20]

    if len(mrz_lines) >= 2:
        line2 = re.sub(r'[^A-Z0-9<]', '', mrz_lines[-2])
        line3 = re.sub(r'[^A-Z<]', '', mrz_lines[-1])

        # DOB + SEX + EXPIRY
        match = re.search(r'(\d{6})\d?([MF])(\d{6})', line2)
        if match:
            dob_raw = match.group(1)
            sex = match.group(2)
            exp_raw = match.group(3)

            data["Date_of_Birth"] = format_mrz_date(dob_raw)
            data["Sex"] = sex
            data["Expiry_Date"] = format_mrz_date(exp_raw)

        # NATIONALITY
        nat_match = re.search(r'([A-Z]{3})', line2)
        if nat_match:
            data["Nationality"] = nat_match.group(1)

        # NAME (CLEAN FIX)
        name_section = line3.replace("<", " ").strip()
        if name_section:
            data["Name"] = re.sub(r'\s+', ' ', name_section).title()


    # FINAL STRUCTURE

    final = {"document_type": "emirates_id"}

    fields = ["Card_Number", "Occupation", "Issuing_Place"]
    back = {k: data[k] for k in fields if k in data}

    if back:
        final["emirates_id_back"] = back

    return final

# MAIN ENTRY

def parse_emirates_id(text, document_type=None):

    if document_type == "emirates_id_back":
        return parse_emirates_id_back(text)

    return parse_emirates_id_front(text)