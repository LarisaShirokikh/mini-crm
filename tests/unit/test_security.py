"""Tests for security module."""

import pytest
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    decode_token,
)
from app.core.exceptions import InvalidTokenException


class TestPasswordHashing:
    """Tests for password hashing."""

    def test_hash_password(self):
        """Password is hashed."""
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Correct password is verified."""
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password is rejected."""
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Same password produces different hashes (salt)."""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token handling."""

    def test_create_access_token(self):
        """Access token is created."""
        token = create_access_token(subject=1)
        
        assert token is not None
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Refresh token is created."""
        token = create_refresh_token(subject=1)
        
        assert token is not None
        assert len(token) > 0

    def test_verify_access_token(self):
        """Access token is verified correctly."""
        user_id = 123
        token = create_access_token(subject=user_id)
        
        payload = verify_access_token(token)
        
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_verify_refresh_token(self):
        """Refresh token is verified correctly."""
        user_id = 123
        token = create_refresh_token(subject=user_id)
        
        payload = verify_refresh_token(token)
        
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_access_token_with_extra_claims(self):
        """Access token can include extra claims."""
        token = create_access_token(
            subject=1,
            extra_claims={"role": "admin"},
        )
        
        payload = verify_access_token(token)
        
        assert payload["role"] == "admin"

    def test_verify_access_token_with_refresh_token_fails(self):
        """Refresh token cannot be used as access token."""
        token = create_refresh_token(subject=1)
        
        with pytest.raises(InvalidTokenException):
            verify_access_token(token)

    def test_verify_refresh_token_with_access_token_fails(self):
        """Access token cannot be used as refresh token."""
        token = create_access_token(subject=1)
        
        with pytest.raises(InvalidTokenException):
            verify_refresh_token(token)

    def test_invalid_token_raises_exception(self):
        """Invalid token raises exception."""
        with pytest.raises(InvalidTokenException):
            decode_token("invalid.token.here")

    def test_expired_token_raises_exception(self):
        """Expired token raises exception."""
        token = create_access_token(
            subject=1,
            expires_delta=timedelta(seconds=-1),
        )
        
        with pytest.raises(InvalidTokenException) as exc_info:
            verify_access_token(token)
        
        assert "expired" in str(exc_info.value.message).lower()