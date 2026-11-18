"""Desktop OAuth setup and noninteractive Drive credential loading."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.readonly",
          "https://www.googleapis.com/auth/drive.file"]


class AuthAttentionError(RuntimeError):
    pass


def secret_dir():
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "TTS_gen" / "secrets"


def credential_paths():
    root = secret_dir()
    return (Path(os.environ.get("GOOGLE_OAUTH_CLIENT_FILE", root / "client_secret.json")),
            Path(os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", root / "token.json")))


def get_credentials(*, interactive=False):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise AuthAttentionError("install requirements-drive.txt") from exc
    client_file, token_file = credential_paths()
    credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES) if token_file.is_file() else None
    try:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        elif not credentials or not credentials.valid:
            if not interactive:
                raise AuthAttentionError("Drive authorization needs attention; run --setup-auth interactively")
            if not client_file.is_file():
                raise AuthAttentionError(f"OAuth client file not found: {client_file}")
            credentials = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES).run_local_server(port=0)
    except AuthAttentionError:
        raise
    except Exception as exc:
        raise AuthAttentionError(f"Drive authorization refresh failed: {exc}") from exc
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--setup-auth", action="store_true")
    args = parser.parse_args(argv)
    if not args.setup_auth:
        parser.error("--setup-auth is required for interactive setup")
    try:
        value = get_credentials(interactive=True)
    except Exception as exc:
        print(f"Error: {exc}"); return 1
    print(f"Authorization stored outside the repository; valid={value.valid}"); return 0


if __name__ == "__main__": raise SystemExit(main())

