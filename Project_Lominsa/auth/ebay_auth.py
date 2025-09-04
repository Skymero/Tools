"""Ebay OAuth2 authentication helper.

This module provides the `EbayAuth` class which can be imported
anywhere in the project to get a valid bearer token when calling
`get_token()`.  Credentials are read from environment variables that
should be placed in a local `.env` file in the project root:

    EBAY_APP_ID=<your app id>
    EBAY_CERT_ID=<your cert id>
    EBAY_REFRESH_TOKEN=<your long refresh token>

The `.env` file **must** be kept out of version control; the project
root `.gitignore` has been updated accordingly.
"""
from __future__ import annotations

import base64
import datetime as dt
import os
from typing import Final, Optional

import requests
from dotenv import load_dotenv

# Load variables from .env (if present) once on import
load_dotenv()

__all__ = [
    "AuthError",
    "EbayAuth",
]


class AuthError(RuntimeError):
    """Raised when authentication with eBay fails."""


class EbayAuth:
    """Handle OAuth2 token refresh for eBay APIs.

    Example
    -------
    >>> from auth.ebay_auth import EbayAuth
    >>> token = EbayAuth().get_token()
    """

    TOKEN_URL: Final[str] = "https://api.ebay.com/identity/v1/oauth2/token"
    SCOPE: Final[str] = "https://api.ebay.com/oauth/api_scope"

    def __init__(self) -> None:
        self.app_id: Optional[str] = os.getenv("EBAY_APP_ID")
        self.cert_id: Optional[str] = os.getenv("EBAY_CERT_ID")
        self.refresh_tok: Optional[str] = os.getenv("EBAY_REFRESH_TOKEN")

        if not all((self.app_id, self.cert_id, self.refresh_tok)):
            missing = [
                name
                for name, value in (
                    ("EBAY_APP_ID", self.app_id),
                    ("EBAY_CERT_ID", self.cert_id),
                    ("EBAY_REFRESH_TOKEN", self.refresh_tok),
                )
                if not value
            ]
            raise AuthError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        self._token: Optional[str] = None
        # Set expiry to epoch start so first call always triggers refresh
        self._token_expiry: dt.datetime = dt.datetime.utcfromtimestamp(0)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _build_auth_header(self) -> dict[str, str]:
        """Return HTTP header for Basic authentication using client credentials.

        eBay requires that the *client credentials* (the App ID and Cert ID)
        are sent in the `Authorization` header using the *HTTP Basic* scheme
        defined in RFC-7617. This means we must:

        1. Concatenate the App ID and Cert ID with a colon separator
           (i.e. ``<app_id>:<cert_id>``).
        2. Base-64 encode the resulting byte sequence so it is ASCII-safe.
        3. Prefix the encoded string with the literal text ``"Basic "``.

        The resulting header value looks like::

            Authorization: Basic QVBQX0lEPTpDRVJUX0lE

        Returns
        -------
        dict[str, str]
            Mapping that can be merged into other request headers.
        """
        # Step-1: combine credentials and encode to *bytes* so b64 works
        creds = f"{self.app_id}:{self.cert_id}".encode()

        # Step-2: Base64 encode and convert back to *str* for the header value
        encoded = base64.b64encode(creds).decode()

        # Step-3: Build and return the header dictionary.
        return {"Authorization": f"Basic {encoded}"}

    def _refresh_access_token(self) -> str:
        """Return a *fresh* OAuth2 access token, hitting the network only when
        the cached token is missing or expired.
        """
        # Current UTC time is used for all expiry comparisons to avoid timezone
        # issues. We *never* compare against ``datetime.now()`` (local time).
        now = dt.datetime.utcnow()

        # ------------------------------------------------------------------
        # Fast-path: token already cached *and* not expired → reuse it.
        # ------------------------------------------------------------------
        if self._token is not None and now < self._token_expiry:
            return self._token  # ♻️  Still valid, no HTTP request needed.

        # ------------------------------------------------------------------
        # Slow-path: we need to request a new token using the *refresh token*.
        # ------------------------------------------------------------------
        # HTTP body parameters ("application/x-www-form-urlencoded") as per
        # https://developer.ebay.com/api-docs/static/oauth-refresh-token.html
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_tok,
            "scope": self.SCOPE,
        }

        # Build headers: Basic auth + content type
        headers = self._build_auth_header()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        # Send POST request to the eBay identity service
        try:
            response = requests.post(
                self.TOKEN_URL,
                headers=headers,
                data=data,
                timeout=15,  # keep the UI snappy even if eBay is slow
            )
        except requests.RequestException as exc:
            # Network/connection error → wrap & raise as AuthError
            raise AuthError(f"Request to eBay token endpoint failed: {exc}") from exc

        # Any non-200 response is considered a failure for our purposes.
        if response.status_code != 200:
            raise AuthError(
                f"eBay token endpoint returned {response.status_code}: {response.text}"
            )

        # Parse the JSON response from eBay.
        # This should contain 'access_token' (the actual bearer token)
        # and 'expires_in' (the token's lifetime in seconds).
        try:
            payload = response.json()  # Convert HTTP response to Python dict
            self._token = payload["access_token"]  # Save the new access token

            # eBay returns the number of seconds the token is valid for,
            # starting from *now*. We subtract 60 seconds as a buffer to
            # avoid using a token that's just about to expire during a request.
            # This helps avoid subtle race conditions and HTTP 401 errors.
            ttl_seconds = payload["expires_in"]  # e.g., 7200 for 2 hours
            self._token_expiry = now + dt.timedelta(seconds=ttl_seconds - 60)
        except (KeyError, ValueError) as exc:
            # If the response doesn't have the expected fields (e.g.,
            # if eBay changes their API or returns an error payload),
            # raise a custom AuthError so the caller can handle it gracefully.
            raise AuthError(
                "Invalid response structure from eBay token endpoint. "
                "Expected keys: 'access_token', 'expires_in'. "
                f"Actual response: {getattr(response, 'text', repr(response))}"
            ) from exc

        # Return the valid access token (either new or cached)
        return self._token

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_token(self) -> str:
        """Return a valid bearer token, refreshing if necessary."""
        return self._refresh_access_token()
