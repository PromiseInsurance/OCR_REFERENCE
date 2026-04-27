# Generated migration for multi-document upload feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ocr_app", "0004_ocrdocument_document_type"),
    ]

    operations = [
        # Make image field optional for backward compatibility
        migrations.AlterField(
            model_name="ocrdocument",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="documents/"),
        ),
        
        # Add Emirates ID fields
        migrations.AddField(
            model_name="ocrdocument",
            name="emirates_id_front",
            field=models.ImageField(blank=True, null=True, upload_to="documents/emirates_id/"),
        ),
        migrations.AddField(
            model_name="ocrdocument",
            name="emirates_id_back",
            field=models.ImageField(blank=True, null=True, upload_to="documents/emirates_id/"),
        ),
        
        # Add Mulkiya fields
        migrations.AddField(
            model_name="ocrdocument",
            name="mulkiya_front",
            field=models.ImageField(blank=True, null=True, upload_to="documents/mulkiya/"),
        ),
        migrations.AddField(
            model_name="ocrdocument",
            name="mulkiya_back",
            field=models.ImageField(blank=True, null=True, upload_to="documents/mulkiya/"),
        ),
        
        # Add Driving License fields
        migrations.AddField(
            model_name="ocrdocument",
            name="driving_license_front",
            field=models.ImageField(blank=True, null=True, upload_to="documents/driving_license/"),
        ),
        migrations.AddField(
            model_name="ocrdocument",
            name="driving_license_back",
            field=models.ImageField(blank=True, null=True, upload_to="documents/driving_license/"),
        ),
        
        # Add submitted_documents field to track which documents were uploaded
        migrations.AddField(
            model_name="ocrdocument",
            name="submitted_documents",
            field=models.JSONField(blank=True, default=list),
        ),
        
        # Add LOW_CONFIDENCE and PENDING status choices
        migrations.AlterField(
            model_name="ocrdocument",
            name="status",
            field=models.CharField(
                choices=[
                    ("processed", "Processed"),
                    ("needs_review", "Needs Review"),
                    ("failed", "Failed"),
                    ("LOW_CONFIDENCE", "Low Confidence"),
                    ("PENDING", "Pending"),
                ],
                default="processed",
                max_length=20,
            ),
        ),
    ]
