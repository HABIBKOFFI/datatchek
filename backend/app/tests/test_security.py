import uuid

import pytest

from app.utils.security import (
    create_access_token,
    decode_access_token,
    decrypt_value,
    encrypt_value,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("CorrectPassword")
        assert not verify_password("WrongPassword", hashed)

    def test_different_hashes_for_same_password(self):
        password = "SamePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # bcrypt generates different salts each time
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWT:
    def test_create_and_decode_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        decoded_id = decode_access_token(token)

        assert decoded_id == user_id

    def test_invalid_token_returns_none(self):
        result = decode_access_token("invalid.token.here")
        assert result is None

    def test_empty_token_returns_none(self):
        result = decode_access_token("")
        assert result is None


class TestFernetEncryption:
    @pytest.fixture(autouse=True)
    def _setup_key(self, monkeypatch):
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()
        monkeypatch.setattr("app.utils.security.settings.ENCRYPTION_KEY", key)

    def test_encrypt_and_decrypt(self):
        original = "my_database_password"
        encrypted = encrypt_value(original)

        assert encrypted != original
        assert decrypt_value(encrypted) == original

    def test_different_ciphertexts_for_same_value(self):
        value = "same_password"
        enc1 = encrypt_value(value)
        enc2 = encrypt_value(value)

        # Fernet uses unique IV each time
        assert enc1 != enc2
        assert decrypt_value(enc1) == value
        assert decrypt_value(enc2) == value
