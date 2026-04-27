from .mulkiya_parser import parse_mulkiya
from .emirates_id import parse_emirates_id
from .driving_license import parse_driving_license


def parse_document(text, document_type=None):
    """
    Main document parser that routes to appropriate parser based on document type.
    
    Args:
        text: Extracted OCR text
        document_type: Type of document (mulkiya, emirates_id, emirates_id_front, 
                      emirates_id_back, driving_license, driving_license_front, 
                      driving_license_back)
    
    Returns:
        dict: Parsed document data
    """

    if document_type == "mulkiya":
        return parse_mulkiya(text)

    if document_type in ["emirates_id", "emirates_id_front", "emirates_id_back"]:
        return parse_emirates_id(text, document_type)
    
    if document_type in ["driving_license", "driving_license_front", "driving_license_back"]:
        return parse_driving_license(text)

    return {}