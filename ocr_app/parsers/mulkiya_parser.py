import re
from datetime import datetime


def normalize_date(date_value):
    if not date_value:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_value

def get_value_before_label(lines, label):
    for i, line in enumerate(lines):
        if label.lower() in line.lower():
            if i > 0:
                return lines[i - 1].strip()
    return None


def get_value_after_label(lines, label):
    for i, line in enumerate(lines):
        if label.lower() in line.lower() and i + 1 < len(lines):
            return lines[i + 1].strip()
    return None

def parse_mulkiya(text):

    data = {"document_type":"mulkiya"}

    cleaned = re.sub(r"[ \t]+", " ", text)
    cleaned = re.sub(r"\n+", "\n", cleaned).strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_text = "\n".join(lines)
    compact_text = " ".join(lines)

    # ---------------- FRONT SIDE ----------------

    # Registration / plate number: U / 19033
    plate_match = re.search(r"\b([A-Z])\s*/\s*(\d{3,6})\b", cleaned)
    if plate_match:
        data["plate_code"] = plate_match.group(1)
        data["plate_number"] = plate_match.group(2)
        data["registration_no"] = f"{plate_match.group(1)}/{plate_match.group(2)}"

    # Traffic code / TCF No
    tc_match = re.search(r"(?:T\.?\s*C\.?\s*No\.?|TC\s*No\.?)\s*(\d{6,10})", cleaned, re.IGNORECASE)
    if not tc_match:
        tc_match = re.search(r"\b(1\d{7})\b", cleaned)
    if tc_match:
        data["tcf_no"] = tc_match.group(1)

    # Place of issue / plate source
    if re.search(r"\bDubai\b", cleaned, re.IGNORECASE):
        data["plate_source"] = "Dubai"

    #owner
    owner = get_value_before_label(lines, "Owner")
    if not owner:
        owner = get_value_after_label(lines, "Owner")

    if owner and re.search(r"[A-Za-z]", owner):
        data["owner"] = owner.title()

    #nationality 
    nationality = get_value_before_label(lines, "Nationality")
    if not nationality:
        nationality = get_value_after_label(lines, "Nationality")

    if nationality and re.match(r"^[A-Za-z]+$", nationality):
        data["nationality"] = nationality.title()

    if "Dubai" in compact_text or "دبي" in compact_text:
        data["plate_source"] = "Dubai"

    # Dates
    exp_match = re.search(r"Exp\.?\s*Date\s*(\d{2}[/-]\d{2}[/-]\d{4})", cleaned, re.IGNORECASE)
    if exp_match:
        data["registration_expiry_date"] = normalize_date(exp_match.group(1))

    reg_match = re.search(r"Reg\.?\s*Date\s*(\d{2}[/-]\d{2}[/-]\d{4})", cleaned, re.IGNORECASE)
    if reg_match:
        data["registration_date"] = normalize_date(reg_match.group(1))

    ins_match = re.search(r"Ins\.?\s*Exp\.?\s*(\d{2}[/-]\d{2}[/-]\d{4})", cleaned, re.IGNORECASE)
    if ins_match:
        data["insurance_expiry_date"] = normalize_date(ins_match.group(1))

    # Fallback dates in visible order: Exp Date, Reg Date, Ins Exp
    dates = re.findall(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", cleaned)
    if "registration_expiry_date" not in data and len(dates) >= 1:
        data["registration_expiry_date"] = normalize_date(dates[0])
    if "registration_date" not in data and len(dates) >= 2:
        data["registration_date"] = normalize_date(dates[1])
    if "insurance_expiry_date" not in data and len(dates) >= 3:
        data["insurance_expiry_date"] = normalize_date(dates[2])

    # Policy No
    policy_match = re.search(r"Policy\s*No\.?\s*([A-Z0-9]+)", cleaned, re.IGNORECASE)
    if not policy_match:
        policy_match = re.search(r"\b\d{3,}[A-Z]{1,5}\d{3,}\b", cleaned)
    if policy_match:
        data["policy_no"] = policy_match.group(1) if policy_match.lastindex else policy_match.group(0)
    

# =========================
# MULKIYA BACK FIELDS
# =========================

    # Model year
    for i, line in enumerate(lines):
        if "model" in line.lower():
            nearby = lines[max(0, i - 3): min(len(lines), i + 4)]
            for candidate in nearby:
                year_match = re.search(r"\b(19|20)\d{2}\b", candidate)
                if year_match:
                    data["model_year"] = year_match.group(0)
                    break
            break

    # Origin
    for i, line in enumerate(lines):
        if "origin" in line.lower():
            nearby = lines[max(0, i - 4): min(len(lines), i + 5)]

            for candidate in nearby:
                candidate = candidate.strip()

                if (
                    re.match(r"^[A-Za-z]+$", candidate)
                    and candidate.lower() not in [
                        "origin", "model", "vehicle", "information",
                        "rta", "uae", "licensing", "authority"]):
                    data["origin"] = candidate.title()
                    break
            break

     # Number of passengers
    for i, line in enumerate(lines):
        if "pass" in line.lower():
            nearby = lines[max(0, i - 3): min(len(lines), i + 4)]
            for candidate in nearby:
                m = re.search(r"\b\d{1,2}\b", candidate)
                if m:
                    data["number_of_passengers"] = m.group(0)
                    break
            break

    # Vehicle type / make / model
    for i, line in enumerate(lines):
        if "veh" in line.lower() and "type" in line.lower():
            nearby = lines[max(0, i - 2): min(len(lines), i + 5)]

            for candidate in nearby:
                candidate = candidate.strip()

                if any(x in candidate.lower() for x in ["veh", "type", "model", "origin", "g.v.w", "empty"]):
                    continue

                if re.search(r"[A-Za-z]{3,}", candidate):
                    vehicle_type = re.sub(r"\s+", " ", candidate).strip()
                    vehicle_type = re.split(
                        r"\bG\.?\s*V\.?\s*W\b|\bEmpty\b|\bEng\b|\bChassis\b",
                        vehicle_type,
                        flags=re.IGNORECASE
                    )[0].strip()

                    if vehicle_type:
                        data["vehicle_type"] = vehicle_type.title()
                        parts = vehicle_type.split()
                        if parts:
                            data["make"] = parts[0].title()
                        if len(parts) > 1:
                            data["model"] = " ".join(parts[1:]).title()

                    break
            break
    # Engine No
    engine_match = re.search(r"\bPR[A-Z0-9\s]{8,20}\b", compact_text, re.IGNORECASE)
    if engine_match:
        data["engine_no"] = re.sub(r"\s+", "", engine_match.group(0)).upper()

    # Chassis No
    chassis_match = re.search(r"\bJE[A-Z0-9]{10,20}\b", compact_text, re.IGNORECASE)
    if chassis_match:
        data["chassis_no"] = chassis_match.group(0).upper()

    front_keys = [
        "registration_no",
        "tcf_no",
        "owner",
        "nationality",
        "plate_source",
        "registration_date",
        "registration_expiry_date",
        "insurance_expiry_date",
        "policy_no",
        ]

    back_keys = [
        "model_year",
        "origin",
        "number_of_passengers",
        "vehicle_type",
        "make",
        "model",
        "engine_no",
        "chassis_no",
        ]

    front_data = {key: data[key] for key in front_keys if key in data}
    back_data = {key: data[key] for key in back_keys if key in data}

    final_data = {
        "document_type": "mulkiya"
        }

    if front_data:
        final_data["mulkiya_front"] = front_data

    if back_data:
        final_data["mulkiya_back"] = back_data
    return final_data


