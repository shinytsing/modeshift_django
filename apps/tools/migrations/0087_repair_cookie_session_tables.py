"""Repair tables from 0081 when that migration was previously faked.

Some deployed databases recorded 0081 as applied even though its two tables
were never created.  This migration is intentionally idempotent so it is safe
for both those databases and clean installs where 0081 already created them.
"""

from django.db import migrations


def ensure_cookie_tables(apps, schema_editor):
    existing = set(schema_editor.connection.introspection.table_names())
    for model_name in ("CookieSession", "UserCookie"):
        model = apps.get_model("tools", model_name)
        if model._meta.db_table not in existing:
            schema_editor.create_model(model)
            existing.add(model._meta.db_table)


class Migration(migrations.Migration):
    dependencies = [
        ("tools", "0086_jobsearchrequest_search_options"),
    ]

    operations = [
        migrations.RunPython(ensure_cookie_tables, migrations.RunPython.noop),
    ]
