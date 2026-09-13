from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tools", "0085_requirementdocument_system_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobsearchrequest",
            name="search_options",
            field=models.JSONField(blank=True, default=dict, verbose_name="搜索扩展配置"),
        ),
    ]
