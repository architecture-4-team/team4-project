from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed

from project.model.user import User

ADMIN_EMAIL = "f4_admin@lge.com"


def check_auth(meta):
    if not meta.get("HTTP_AUTHORIZATION"):
        raise AuthenticationFailed("Authorization failed")
    uuid = meta["HTTP_AUTHORIZATION"]
    try:
        User.objects.get(uuid=uuid)
        return uuid
    except ObjectDoesNotExist:
        raise AuthenticationFailed("Authorization failed")
