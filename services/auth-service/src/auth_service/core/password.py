"""
Password hashing using Argon2id.

Argon2id is the recommended algorithm for password hashing
as of OWASP and NIST guidelines.
"""

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from auth_service.config import get_settings


def get_password_hasher() -> PasswordHasher:
    """
    Get configured Argon2 password hasher.
    
    Settings follow OWASP recommendations:
    - Memory: 64 MB
    - Iterations: 3
    - Parallelism: 4
    """
    settings = get_settings()
    return PasswordHasher(
        time_cost=settings.argon2_time_cost,
        memory_cost=settings.argon2_memory_cost,
        parallelism=settings.argon2_parallelism,
        hash_len=32,
        salt_len=16,
        type=Type.ID,  # Argon2id - hybrid of Argon2i and Argon2d
    )


_hasher = None


def _get_hasher() -> PasswordHasher:
    """Get or create singleton hasher instance."""
    global _hasher
    if _hasher is None:
        _hasher = get_password_hasher()
    return _hasher


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.
    
    Args:
        password: Plain text password.
        
    Returns:
        Argon2id hash string.
        
    Example:
        >>> hash_password("secure_password")
        '$argon2id$v=19$m=65536,t=3,p=4$...'
    """
    return _get_hasher().hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify.
        password_hash: Stored Argon2id hash.
        
    Returns:
        True if password matches, False otherwise.
        
    Note:
        This function is timing-safe to prevent timing attacks.
    """
    try:
        _get_hasher().verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except InvalidHashError:
        # Log this - indicates data corruption or tampering
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Check if a password hash needs to be rehashed.
    
    This is useful when upgrading hash parameters.
    After verifying a password, check if it needs rehashing
    with updated parameters.
    
    Args:
        password_hash: Existing password hash.
        
    Returns:
        True if the hash should be updated.
    """
    return _get_hasher().check_needs_rehash(password_hash)
