from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ObjectDoesNotExist

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider):
        try:
            app = SocialApp.objects.get(provider=provider)
            return app
        except ObjectDoesNotExist:
            if provider == 'google':
                app = SocialApp.objects.create(
                    provider='google',
                    name='Google',
                    client_id='264574147455-fe39bnpbocvkdiaiasks8ptdkr1lbruq.apps.googleusercontent.com',
                    secret='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',
                )
                return app
            raise
