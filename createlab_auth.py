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
    if len(password or "") < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password must be no more than {PASSWORD_MAX_LENGTH} characters.")
    return normalized_email, name


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
    user = createlab_db.create_user(
        str(uuid4()), normalized_email, name, hash_password(password), path=path
    )
    return user


def authenticate(email, password, path=None):
    normalized_email = normalize_email(email)
    user = createlab_db.get_user_by_email(normalized_email, path=path)
    if not user or not verify_password(password or "", user["password_hash"]):
        return None
    return {key: user[key] for key in ("id", "email", "display_name", "created_at")}
