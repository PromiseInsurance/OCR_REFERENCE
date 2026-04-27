from django.db import models

class OCRDocument(models.Model):
    STATUS_CHOICES=[
        ('processed','Processed'),
        ('needs_review','Needs Review'),
        ('failed','Failed'),
        ('LOW_CONFIDENCE', 'Low Confidence'),
        ('PENDING', 'Pending'),
    ]

    # Legacy field for backward compatibility
    image=models.ImageField(upload_to='documents/', blank=True, null=True)
    
    # Emirates ID
    emirates_id_front = models.ImageField(upload_to='documents/emirates_id/', blank=True, null=True)
    emirates_id_back = models.ImageField(upload_to='documents/emirates_id/', blank=True, null=True)
    
    # Mulkiya
    mulkiya_front = models.ImageField(upload_to='documents/mulkiya/', blank=True, null=True)
    mulkiya_back = models.ImageField(upload_to='documents/mulkiya/', blank=True, null=True)
    
    # Driving License
    driving_license_front = models.ImageField(upload_to='documents/driving_license/', blank=True, null=True)
    driving_license_back = models.ImageField(upload_to='documents/driving_license/', blank=True, null=True)
    
    # Extracted data
    extracted_text=models.TextField(blank=True, null=True)
    customer_name=models.CharField(max_length=255,blank=True,null=True)
    date_of_birth=models.CharField(max_length=50,blank=True,null=True)
    kyc_id=models.CharField(max_length=100,blank=True,null=True)
    
    # Processing metadata
    confidence_score = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Raw OCR and parsed data - now stores data for all document types
    ocr_raw_json = models.JSONField(blank=True, null=True)  # {emirates_id: {...}, mulkiya: {...}, driving_license: {...}}
    parsed_data = models.JSONField(blank=True, null=True)   # {emirates_id: {...}, mulkiya: {...}, driving_license: {...}}
    validation_errors = models.JSONField(blank=True, null=True)  # {emirates_id: {...}, mulkiya: {...}, driving_license: {...}}
    document_type = models.CharField(max_length=50, null=True, blank=True)  # Legacy field
    
    # Track which documents were uploaded
    submitted_documents = models.JSONField(default=list, blank=True)  # ["emirates_id", "mulkiya", "driving_license"]

    def __str__(self):
        return f"Document {self.id} - {self.status}"