"""Thin Google Drive API primitives; orchestration policy belongs elsewhere."""
from __future__ import annotations

import hashlib
import io
import time
from pathlib import Path

from google_drive_auth import AuthAttentionError, get_credentials

FIELDS = "id,name,mimeType,modifiedTime,md5Checksum,size,parents"
GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_FOLDER = "application/vnd.google-apps.folder"


class RetryableDriveError(RuntimeError): pass


def classify_error(exc):
    status = getattr(getattr(exc, "resp", None), "status", None)
    if status in (401, 403): return AuthAttentionError
    if status == 429 or (status and status >= 500): return RetryableDriveError
    return RuntimeError


class DriveClient:
    def __init__(self, service=None):
        if service is None:
            try:
                from googleapiclient.discovery import build
            except ImportError as exc: raise RuntimeError("install requirements-drive.txt") from exc
            service = build("drive", "v3", credentials=get_credentials(), cache_discovery=False)
        self.service = service

    def list_children(self, parent_id):
        result, token = [], None
        while True:
            response = self.service.files().list(q=f"'{parent_id}' in parents and trashed=false", fields=f"nextPageToken,files({FIELDS})", pageToken=token).execute()
            result.extend(response.get("files", [])); token = response.get("nextPageToken")
            if not token: return result

    def metadata(self, file_id):
        return self.service.files().get(fileId=file_id, fields=FIELDS).execute()

    def download(self, file_id, destination, *, google_doc=False):
        try:
            from googleapiclient.http import MediaIoBaseDownload
        except ImportError as exc: raise RuntimeError("install requirements-drive.txt") from exc
        request = (self.service.files().export_media(fileId=file_id, mimeType="text/plain") if google_doc
                   else self.service.files().get_media(fileId=file_id))
        target = Path(destination); target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as stream:
            downloader = MediaIoBaseDownload(stream, request)
            done = False
            while not done: _, done = downloader.next_chunk()
        return target

    def generate_id(self):
        return self.service.files().generateIds(count=1, space="drive").execute()["ids"][0]

    def upload(self, path, *, file_id, name, parent_id, mime_type="video/mp4", attempts=3):
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc: raise RuntimeError("install requirements-drive.txt") from exc
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)
        body = {"id": file_id, "name": name, "parents": [parent_id]}
        for attempt in range(attempts):
            try:
                try:
                    existing = self.metadata(file_id)
                except Exception as lookup_error:
                    status = getattr(getattr(lookup_error, "resp", None), "status", None)
                    if status not in (None, 404): raise
                    existing = None
                if existing:
                    return self.service.files().update(fileId=file_id, body={"name": name}, media_body=media, fields=FIELDS).execute()
                return self.service.files().create(body=body, media_body=media, fields=FIELDS).execute()
            except Exception as exc:
                error = classify_error(exc)
                if error is not RetryableDriveError or attempt + 1 == attempts: raise error(str(exc)) from exc
                time.sleep(min(2 ** attempt, 8))

    def confirm_upload(self, file_id, *, parent_id, name, local_path):
        value = self.metadata(file_id); path = Path(local_path)
        if value.get("name") != name or parent_id not in value.get("parents", []):
            raise RuntimeError("uploaded file name or parent does not match")
        if value.get("size") and int(value["size"]) != path.stat().st_size:
            raise RuntimeError("uploaded file size does not match")
        return value


def normalize_google_doc(text):
    import re
    return "\n\n".join(part.strip() for part in re.split(r"\n\s*\n+", text.replace("\r\n", "\n").strip()) if part.strip()) + "\n"

