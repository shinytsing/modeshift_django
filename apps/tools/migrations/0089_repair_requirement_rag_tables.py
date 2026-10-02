"""Repair RAG tables when an older deployment recorded 0083 as applied early."""

from django.db import migrations


def ensure_requirement_rag_tables(apps, schema_editor):
    existing = set(schema_editor.connection.introspection.table_names())
    for model_name in ("RequirementDocument", "RequirementChunk"):
        model = apps.get_model("tools", model_name)
        if model._meta.db_table not in existing:
            schema_editor.create_model(model)
            existing.add(model._meta.db_table)


class Migration(migrations.Migration):
    dependencies = [("tools", "0088_unique_cookie_session_user_platform")]

    operations = [migrations.RunPython(ensure_requirement_rag_tables, migrations.RunPython.noop)]
