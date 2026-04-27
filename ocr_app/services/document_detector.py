def detect_document_type(text: str) -> str:
    text_lower = text.lower()

    if "driving license" in text_lower and "license no" in text_lower:
        return "driving_license_front"

    if "traffic code no" in text_lower and "permitted vehicles" in text_lower:
        return "driving_license_back"

    #Must have << AND numeric MRZ pattern
    if "<<" in text and any(char.isdigit() for char in text):
        return "emirates_id_back"


    #EMIRATES ID FRONT (STRICT CHECK)

    if (
        "id number" in text_lower
        or "date of birth" in text_lower
        or "nationality" in text_lower
        or "issuing date" in text_lower
        or "expiry date" in text_lower
    ):
        return "emirates_id_front"
    

    if ("vehicle license" in text_lower 
        or "vehicle information" in text_lower
        or "traffic plate no" in text_lower 
        or "policy no" in text_lower  
        or "chassis no" in text_lower
        or "eng. no" in text_lower
        or "registration date" in text_lower
    ):
        return "mulkiya"

    return "unknown"