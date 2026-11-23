"""Cryptographically secure opaque session-token provider."""

import secrets


class SecureTokenProvider:
    def generate_token(self) -> str:
        # token_urlsafe(32) is generated from 32 random bytes (256 bits).
        return secrets.token_urlsafe(32)
