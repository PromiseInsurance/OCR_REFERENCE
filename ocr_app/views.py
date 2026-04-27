from django.shortcuts import render, redirect
from .forms import DocumentUploadForm
from .models import OCRDocument
from .parsers.parser import parse_document
from .services.azure_ocr_service import extract_text_with_azure
from .services.document_detector import detect_document_type
from .validators.mulkiya_validator import validate_mulkiya
from .validators.emirate_validator import validate_emirates_id
from .validators.driving_license_validator import validate_driving_license
import os

def process_document_pair(front_image_path, back_image_path, doc_type):
    """Process front and back images of a document together."""
    results = {
        "document_type": doc_type,
        "front": {},
        "back": {},
        "combined": {}
    }
    
    try:
        # Process front image
        if front_image_path and os.path.exists(front_image_path):
            front_result = extract_text_with_azure(front_image_path)
            results["front"]["text"] = front_result["text"]
            results["front"]["raw"] = front_result["raw"]
            results["front"]["confidence"] = front_result["confidence_score"]
            results["front"]["parsed"] = parse_document(front_result["text"], f"{doc_type}_front")
    except Exception as e:
        results["front"]["error"] = str(e)
    
    try:
        # Process back image
        if back_image_path and os.path.exists(back_image_path):
            back_result = extract_text_with_azure(back_image_path)
            results["back"]["text"] = back_result["text"]
            results["back"]["raw"] = back_result["raw"]
            results["back"]["confidence"] = back_result["confidence_score"]
            results["back"]["parsed"] = parse_document(back_result["text"], f"{doc_type}_back")
    except Exception as e:
        results["back"]["error"] = str(e)
    
    # Combine results
    combined_text = ""
    if results["front"].get("text"):
        combined_text += results["front"]["text"] + "\n"
    if results["back"].get("text"):
        combined_text += results["back"]["text"]
    
    if combined_text:
        try:
            combined_parsed = parse_document(combined_text, doc_type)
            results["combined"] = combined_parsed
        except Exception as e:
            results["combined"]["error"] = str(e)
    
    return results


def validate_document_data(parsed_data, doc_type):
    """Validate parsed document data based on document type."""
    if doc_type == "mulkiya":
        return validate_mulkiya(parsed_data)
    elif doc_type == "emirates_id":
        return validate_emirates_id(parsed_data)
    elif doc_type == "driving_license":
        return validate_driving_license(parsed_data)
    else:
        return {
            "status": "PENDING",
            "errors": {},
            "side": None
        }


def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create new document record
            document = OCRDocument()
            
            # Store uploaded files
            submitted_docs = []
            all_ocr_results = {}
            all_parsed_data = {}
            all_validation_errors = {}
            overall_status = "processed"
            
            # Process Emirates ID
            if form.cleaned_data.get('emirates_id_front') or form.cleaned_data.get('emirates_id_back'):
                submitted_docs.append("emirates_id")
                document.emirates_id_front = form.cleaned_data.get('emirates_id_front')
                document.emirates_id_back = form.cleaned_data.get('emirates_id_back')
                
                try:
                    front_path = document.emirates_id_front.path if document.emirates_id_front else None
                    back_path = document.emirates_id_back.path if document.emirates_id_back else None
                    
                    result = process_document_pair(front_path, back_path, "emirates_id")
                    all_ocr_results["emirates_id"] = result
                    
                    # Parse and validate
                    if result["combined"].get("emirates_id_front"):
                        parsed = result["combined"]
                        validation = validate_document_data(parsed, "emirates_id")
                        all_parsed_data["emirates_id"] = parsed
                        all_validation_errors["emirates_id"] = validation.get("errors", {})
                        
                        # Update status if validation failed
                        if validation["status"] != "processed":
                            overall_status = validation["status"]
                    
                except Exception as e:
                    all_validation_errors["emirates_id"] = {"error": str(e)}
                    overall_status = "failed"
            
            # Process Mulkiya
            if form.cleaned_data.get('mulkiya_front') or form.cleaned_data.get('mulkiya_back'):
                submitted_docs.append("mulkiya")
                document.mulkiya_front = form.cleaned_data.get('mulkiya_front')
                document.mulkiya_back = form.cleaned_data.get('mulkiya_back')
                
                try:
                    front_path = document.mulkiya_front.path if document.mulkiya_front else None
                    back_path = document.mulkiya_back.path if document.mulkiya_back else None
                    
                    result = process_document_pair(front_path, back_path, "mulkiya")
                    all_ocr_results["mulkiya"] = result
                    
                    # Parse and validate
                    if result["combined"]:
                        parsed = result["combined"]
                        validation = validate_document_data(parsed, "mulkiya")
                        all_parsed_data["mulkiya"] = parsed
                        all_validation_errors["mulkiya"] = validation.get("errors", {})
                        
                        if validation["status"] != "processed":
                            overall_status = validation["status"]
                    
                except Exception as e:
                    all_validation_errors["mulkiya"] = {"error": str(e)}
                    overall_status = "failed"
            
            # Process Driving License
            if form.cleaned_data.get('driving_license_front') or form.cleaned_data.get('driving_license_back'):
                submitted_docs.append("driving_license")
                document.driving_license_front = form.cleaned_data.get('driving_license_front')
                document.driving_license_back = form.cleaned_data.get('driving_license_back')
                
                try:
                    front_path = document.driving_license_front.path if document.driving_license_front else None
                    back_path = document.driving_license_back.path if document.driving_license_back else None
                    
                    result = process_document_pair(front_path, back_path, "driving_license")
                    all_ocr_results["driving_license"] = result
                    
                    # Parse and validate
                    if result["combined"]:
                        parsed = result["combined"]
                        validation = validate_document_data(parsed, "driving_license")
                        all_parsed_data["driving_license"] = parsed
                        all_validation_errors["driving_license"] = validation.get("errors", {})
                        
                        if validation["status"] != "processed":
                            overall_status = validation["status"]
                    
                except Exception as e:
                    all_validation_errors["driving_license"] = {"error": str(e)}
                    overall_status = "failed"
            
            # Save document with all results
            document.submitted_documents = submitted_docs
            document.ocr_raw_json = all_ocr_results
            document.parsed_data = all_parsed_data
            document.validation_errors = all_validation_errors
            document.status = overall_status
            document.save()
            
            return redirect('detail', pk=document.pk)
    else:
        form = DocumentUploadForm()

    return render(request, 'upload.html', {'form': form})


def detail(request, pk):
    document = OCRDocument.objects.get(pk=pk)
    return render(request, 'detail.html', {'document': document})

