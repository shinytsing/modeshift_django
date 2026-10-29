from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("users", "0014_alter_userrole_table")]
    operations = [
        migrations.CreateModel(
            name="WeChatMiniProgramIdentity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("appid", models.CharField(max_length=64)),
                ("openid", models.CharField(max_length=128)),
                ("unionid", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="wechat_mini_identity", to="auth.user"
                    ),
                ),
            ],
            options={
                "constraints": [models.UniqueConstraint(fields=("appid", "openid"), name="users_wechat_appid_openid_unique")]
            },
        ),
    ]
