import os

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ObjectDoesNotExist


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider):
        try:
            app = SocialApp.objects.get(provider=provider)
            return app
        except ObjectDoesNotExist:
            if provider == "google":
                client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
                secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
                app = SocialApp.objects.create(
                    provider="google",
                    name="Google",
                    client_id=client_id,
                    secret=secret,
                )
                return app
            raise
