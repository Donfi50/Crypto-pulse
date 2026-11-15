import hashlib
import hmac
import re
import secrets
from uuid import uuid4

import createlab_db


PBKDF2_ITERATIONS = 310_000
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(email):
    return (email or "").strip().lower()


def validate_account(email, display_name, password):
    normalized_email = normalize_email(email)
    name = (display_name or "").strip()
    if len(normalized_email) > 254 or not _EMAIL_RE.fullmatch(normalized_email):
        raise ValueError("Enter a valid email address.")
    if not name or len(name) > 80:
        raise ValueError("Name must be between 1 and 80 characters.")
    validate_password(password)
    return normalized_email, name


def validate_password(password):
    if not isinstance(password, str) or len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password must be no more than {PASSWORD_MAX_LENGTH} characters.")


def hash_password(password, salt=None):
    salt_bytes = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_bytes.hex()}${digest.hex()}"


def verify_password(password, encoded_hash):
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds)
        if rounds < 100_000 or rounds > 2_000_000:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), rounds)
        return hmac.compare_digest(actual, expected)
    except (AttributeError, ValueError, TypeError):
        return False


def register(email, display_name, password, path=None):
    normalized_email, name = validate_account(email, display_name, password)
    return createlab_db.create_user(
        str(uuid4()), normalized_email, name, hash_password(password), path=path
    )


def authenticate(email, password, path=None):
    normalized_email = normalize_email(email)
    user = createlab_db.get_user_by_email(normalized_email, path=path)
    if not user or not verify_password(password or "", user["password_hash"]):
        return None
    return {key: user[key] for key in ("id", "email", "display_name", "created_at")}


def change_password(user_id, current_password, new_password, path=None):
    """Change an account password only after verifying the existing credential."""
    validate_password(new_password)
    user = createlab_db.get_user_by_id(user_id, path=path)
    stored = createlab_db.get_user_by_email(user["email"], path=path) if user else None
    if not stored or not verify_password(current_password or "", stored["password_hash"]):
        raise ValueError("Current password is incorrect.")
    if hmac.compare_digest(current_password, new_password):
        raise ValueError("Choose a new password different from your current password.")
    if not createlab_db.update_password_hash(user_id, hash_password(new_password), path=path):
        raise ValueError("Could not update the password. Please try again.")
