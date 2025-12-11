"""Authentication package initialization"""

from backend.auth.auth_handler import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
)
from backend.auth.dependencies import (
    get_current_user,
    get_current_active_admin,
    get_optional_current_user,
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "get_current_user",
    "get_current_active_admin",
    "get_optional_current_user",
]
