import base64
import time
from typing import Any, Dict

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec as cryptography_ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicNumbers
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

# Constants
JWKS_TTL = 300  # JWKS cache time-to-live in seconds
JWT_DECODE_OPTIONS = {"verify_aud": False}
HS256_ALGORITHMS = ["HS256"]
JWKS_ALGORITHMS = ["RS256", "ES256"]
# Allow small clock skew when verifying `exp`
LEEWAY = 10  # seconds

# Security schemes
bearer_scheme = HTTPBearer()

# JWKS cache
JWKS_CACHE: Dict[str, Any] = {"keys": None, "fetched_at": 0}


def _fetch_jwks() -> Dict[str, Any]:
    """Fetch JWKS from Supabase with caching."""
    now = time.time()

    # Return cached JWKS if still valid
    if JWKS_CACHE["keys"] and (now - JWKS_CACHE["fetched_at"]) < JWKS_TTL:
        return JWKS_CACHE["keys"]

    # Fetch fresh JWKS
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    response = requests.get(jwks_url, timeout=5)
    response.raise_for_status()

    jwks = response.json()
    JWKS_CACHE["keys"] = jwks
    JWKS_CACHE["fetched_at"] = now

    # print(f"Fetched JWKS from: {jwks_url}")
    return jwks


def _base64url_to_int(val: str) -> int:
    """Decode base64url string to integer."""
    val_padded = val + "=" * (-len(val) % 4)
    data = base64.urlsafe_b64decode(val_padded)
    return int.from_bytes(data, "big")


def _check_expiration(payload: Dict[str, Any]) -> None:
    """Check `exp` claim manually applying `LEEWAY` seconds.

    Raises HTTPException with 401 when token is expired.
    """
    exp = payload.get("exp")
    if exp is None:
        return

    now = int(time.time())
    if now > int(exp) + LEEWAY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )


def _jwk_to_pem(jwk: Dict[str, Any]) -> bytes:
    """Convert a JWK to PEM format for RSA or EC keys."""
    kty = jwk.get("kty")

    if kty == "RSA":
        n = _base64url_to_int(jwk["n"])
        e = _base64url_to_int(jwk["e"])
        pub_key = RSAPublicNumbers(e, n).public_key(default_backend())
    elif kty == "EC":
        x = _base64url_to_int(jwk["x"])
        y = _base64url_to_int(jwk["y"])
        curve_name = jwk.get("crv", "")

        if curve_name != "P-256":
            raise ValueError(f"Unsupported EC curve: {curve_name}")

        curve = cryptography_ec.SECP256R1()
        pub_key = EllipticCurvePublicNumbers(x, y, curve).public_key(default_backend())
    else:
        raise ValueError(f"Unsupported JWK key type: {kty}")

    return pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _verify_token_hs256(token: str) -> Dict[str, Any]:
    """Attempt HS256 verification with Supabase secret."""
    try:
        # Disable automatic exp verification so we can apply a leeway check manually
        opts = dict(JWT_DECODE_OPTIONS)
        opts_with_no_exp = {**opts, "verify_exp": False}
        payload = jwt.decode(
            token=token,
            key=settings.supabase_secret_key,
            algorithms=HS256_ALGORITHMS,
            options=opts_with_no_exp,
        )
        print("JWT Payload (verified HS256):", payload)
        _check_expiration(payload)
        return payload
    except JWTError as e:
        print(f"HS256 verification failed: {e}")
        raise


def _verify_token_jwks(token: str) -> Dict[str, Any]:
    """Attempt JWKS-based verification with public keys."""
    try:
        jwks = _fetch_jwks()
    except Exception as e:
        print(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to fetch JWKS for token verification",
        )

    last_exc = None
    opts = dict(JWT_DECODE_OPTIONS)
    opts_with_no_exp = {**opts, "verify_exp": False}
    for jwk in jwks.get("keys", []):
        try:
            pem = _jwk_to_pem(jwk)
            payload = jwt.decode(
                token=token,
                key=pem,
                algorithms=JWKS_ALGORITHMS,
                options=opts_with_no_exp,
            )
            print("JWT Payload (verified via JWKS):", payload)
            _check_expiration(payload)
            return payload
        except (JWTError, ValueError) as e:
            last_exc = e
            continue

    print(f"JWT verification via JWKS failed: {last_exc}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token signature",
    )


def _extract_user_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user information from JWT payload."""
    user_metadata = payload.get("user_metadata", {})

    # Try to get role from different possible locations
    role = (
        user_metadata.get("role")
        or payload.get("app_metadata", {}).get("role")
        or payload.get("role")
        or "patient"
    )

    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": role,
        "user_metadata": user_metadata,
    }


def get_current_user(token: str = Depends(bearer_scheme)) -> Dict[str, Any]:
    """Verify JWT token and extract user information."""
    # Try HS256 verification first, then fall back to JWKS
    try:
        payload = _verify_token_hs256(token.credentials)
    except JWTError:
        payload = _verify_token_jwks(token.credentials)

    return _extract_user_data(payload)


def require_role(*allowed_roles: str):
    """
    Dependency for requiring specific user roles.

    Args:
        *allowed_roles: Variable number of role names that are allowed access

    Returns:
        Dependency function that validates user role

    Raises:
        HTTPException: If user doesn't have required role
    """

    def role_checker(
        user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation",
            )
        return user

    return role_checker


require_admin = require_role("admin")
