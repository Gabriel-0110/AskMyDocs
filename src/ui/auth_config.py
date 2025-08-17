# src/utils/auth_config.py
import os

AUTH_MODE = os.getenv("AUTH_MODE", "auto")

def easy_auth_enabled() -> bool:
    if AUTH_MODE == "azure":
        return True
    if AUTH_MODE == "public":
        return False
    if AUTH_MODE == "custom":
        return False
    # auto-detect Azure App Service EasyAuth
    return bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("WEBSITE_AUTH_ENABLED"))

EASY_AUTH = easy_auth_enabled()
