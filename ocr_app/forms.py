from django import forms
from .models import OCRDocument

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading multiple document types (Emirates ID, Mulkiya, Driving License)
    with front and back images for each type."""
    
    emirates_id_front = forms.ImageField(required=False, label="Emirates ID - Front")
    emirates_id_back = forms.ImageField(required=False, label="Emirates ID - Back")
    
    mulkiya_front = forms.ImageField(required=False, label="Mulkiya - Front")
    mulkiya_back = forms.ImageField(required=False, label="Mulkiya - Back")
    
    driving_license_front = forms.ImageField(required=False, label="Driving License - Front")
    driving_license_back = forms.ImageField(required=False, label="Driving License - Back")
    
    class Meta:
        model = OCRDocument
        fields = []  # We handle files manually
    
    def clean(self):
        cleaned_data = super().clean()
        # At least one document type with at least one image must be uploaded
        has_emirates = cleaned_data.get('emirates_id_front') or cleaned_data.get('emirates_id_back')
        has_mulkiya = cleaned_data.get('mulkiya_front') or cleaned_data.get('mulkiya_back')
        has_driving = cleaned_data.get('driving_license_front') or cleaned_data.get('driving_license_back')
        
        if not (has_emirates or has_mulkiya or has_driving):
            raise forms.ValidationError("Please upload at least one document image.")
        
        return cleaned_data
