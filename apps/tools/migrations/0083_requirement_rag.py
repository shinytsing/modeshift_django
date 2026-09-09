from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("tools", "0082_verificationcode_and_more")]

    operations = [
        migrations.CreateModel(
            name="RequirementDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("source_file", models.FileField(upload_to="rag_requirements/%Y/%m/%d/")),
                ("source_type", models.CharField(max_length=10)),
                ("extracted_text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="requirement_documents", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RequirementChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequence", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("vector", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="tools.requirementdocument")),
            ],
            options={"ordering": ["document_id", "sequence"]},
        ),
        migrations.AddIndex(model_name="requirementdocument", index=models.Index(fields=["owner", "created_at"], name="tools_requi_owner_i_0bfbdc_idx")),
        migrations.AddConstraint(model_name="requirementchunk", constraint=models.UniqueConstraint(fields=("document", "sequence"), name="unique_requirement_chunk")),
        migrations.AddIndex(model_name="requirementchunk", index=models.Index(fields=["document", "sequence"], name="tools_requi_documen_4d601a_idx")),
    ]
