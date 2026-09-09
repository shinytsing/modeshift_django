from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("tools", "0084_align_requirement_rag_indexes")]

    operations = [
        migrations.AlterField(
            model_name="requirementdocument",
            name="owner",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="requirement_documents", to="auth.user"),
        )
    ]
