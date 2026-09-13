from django.db import migrations, models


def keep_latest_session_per_user_platform(apps, schema_editor):
    CookieSession = apps.get_model("tools", "CookieSession")
    seen = set()
    for session in CookieSession.objects.order_by("user_id", "platform", "-last_used", "-id"):
        key = (session.user_id, session.platform)
        if key in seen:
            session.delete()
        else:
            seen.add(key)


class Migration(migrations.Migration):
    dependencies = [
        ("tools", "0087_repair_cookie_session_tables"),
    ]

    operations = [
        migrations.RunPython(keep_latest_session_per_user_platform, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="cookiesession",
            constraint=models.UniqueConstraint(
                fields=("user", "platform"),
                name="unique_cookie_session_user_platform",
            ),
        ),
    ]
