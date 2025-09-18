from django.urls import path
from apps.tools.views.google_oauth_views import (
    GoogleOAuthStartView,
    GoogleOAuthCallbackView,
    GoogleOAuthTestView
)

urlpatterns = [
    path('auth/google/start/', GoogleOAuthStartView.as_view(), name='google_oauth_start'),
    path('auth/google/callback/', GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    path('auth/google/test/', GoogleOAuthTestView.as_view(), name='google_oauth_test'),
]
