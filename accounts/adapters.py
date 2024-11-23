from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Link Google account automatically if the user is authenticated
        if request.user.is_authenticated:
            logger.debug("User is authenticated; linking Google account.")
            sociallogin.connect(request, request.user)
        else:
            email = user_email(sociallogin.user)
            existing_user = self.get_user_by_email(email)
            if existing_user:
                # Link Google account to the existing user
                sociallogin.connect(request, existing_user)
                logger.debug(f"Linked Google account to existing user: {existing_user.email}")

    def get_user_by_email(self, email):
        # Utility function to find an existing user by email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_login_redirect_url(self, request):
        # Redirect admin users to the admin panel, others to default URL
        if request.user.is_authenticated and request.user.is_superuser:
            logger.debug("Redirecting superuser to admin panel.")
            return reverse("admin:index")
        logger.debug("Redirecting non-superuser to default login URL.")
        return super().get_login_redirect_url(request)
