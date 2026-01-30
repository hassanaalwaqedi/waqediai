"""
Google OAuth Token Verification (Enterprise Grade)

Validates Google ID tokens using Google's public keys.
Does NOT use client secret for verification.
Does NOT store any OAuth tokens.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

# Google OAuth endpoints
GOOGLE_ISSUER = "https://accounts.google.com"
GOOGLE_ISSUERS = ["accounts.google.com", "https://accounts.google.com"]


@dataclass
class GoogleUserInfo:
    """Verified Google user information."""
    provider_user_id: str  # sub claim
    email: str
    email_verified: bool
    name: Optional[str]
    picture: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    locale: Optional[str]


class GoogleTokenVerifier:
    """
    Verifies Google ID tokens securely.
    
    Features:
    - Validates signature using Google's public keys
    - Verifies issuer (accounts.google.com)
    - Verifies audience matches client ID
    - Checks token expiration
    - Does NOT use client secret
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self._request = google_requests.Request()

    async def verify_id_token(self, token: str) -> Optional[GoogleUserInfo]:
        """
        Verify Google ID token and extract user info.
        
        Uses google-auth library for secure verification.
        Returns None if verification fails.
        """
        try:
            # Verify token using Google's public keys
            idinfo = id_token.verify_oauth2_token(
                token,
                self._request,
                self.client_id,
            )

            # Verify issuer
            if idinfo.get("iss") not in GOOGLE_ISSUERS:
                logger.warning(f"Invalid issuer: {idinfo.get('iss')}")
                return None

            # Verify audience
            if idinfo.get("aud") != self.client_id:
                logger.warning("Token audience mismatch")
                return None

            return GoogleUserInfo(
                provider_user_id=idinfo.get("sub"),
                email=idinfo.get("email"),
                email_verified=idinfo.get("email_verified", False),
                name=idinfo.get("name"),
                picture=idinfo.get("picture"),
                given_name=idinfo.get("given_name"),
                family_name=idinfo.get("family_name"),
                locale=idinfo.get("locale"),
            )

        except ValueError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error verifying token: {e}")
            return None

    async def verify_id_token_fallback(self, token: str) -> Optional[GoogleUserInfo]:
        """
        Fallback verification using Google's tokeninfo endpoint.
        
        Use this if google-auth library is not available.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": token},
                )

                if response.status_code != 200:
                    logger.warning(f"Token verification failed: {response.text}")
                    return None

                data = response.json()

                # Verify audience
                if data.get("aud") != self.client_id:
                    logger.warning("Token audience mismatch")
                    return None

                # Verify issuer
                if data.get("iss") not in GOOGLE_ISSUERS:
                    logger.warning(f"Invalid issuer: {data.get('iss')}")
                    return None

                return GoogleUserInfo(
                    provider_user_id=data.get("sub"),
                    email=data.get("email"),
                    email_verified=data.get("email_verified", "false") == "true",
                    name=data.get("name"),
                    picture=data.get("picture"),
                    given_name=data.get("given_name"),
                    family_name=data.get("family_name"),
                    locale=data.get("locale"),
                )

        except Exception as e:
            logger.exception(f"Fallback verification failed: {e}")
            return None


def get_google_verifier(client_id: str) -> GoogleTokenVerifier:
    """Get Google token verifier instance."""
    return GoogleTokenVerifier(client_id)
