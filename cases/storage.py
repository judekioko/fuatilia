"""Evidence files are encrypted at rest (Fernet: AES-128-CBC + HMAC-SHA256) before they reach the disk.
A stolen disk or backup is unreadable without FILE_ENCRYPTION_KEY, which lives only in the environment."""

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property


def _fernet() -> Fernet:
    key = os.environ.get("FILE_ENCRYPTION_KEY", "").strip()
    if not key:
        if not settings.DEBUG:
            raise ImproperlyConfigured("FILE_ENCRYPTION_KEY must be set in production")
        # Development only: derive a stable key so local files stay readable between restarts.
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest()).decode()
    return Fernet(key.encode())


class EncryptedFileSystemStorage(FileSystemStorage):
    @cached_property
    def fernet(self) -> Fernet:
        return _fernet()

    def _save(self, name, content):
        content.seek(0)
        encrypted = self.fernet.encrypt(content.read())
        return super()._save(name, ContentFile(encrypted))

    def _open(self, name, mode="rb"):
        with super()._open(name, "rb") as handle:
            data = handle.read()
        try:
            plain = self.fernet.decrypt(data)
        except InvalidToken as error:
            raise OSError(f"Could not decrypt {name}: wrong FILE_ENCRYPTION_KEY or corrupted file") from error
        return ContentFile(plain, name=name)


def evidence_storage():
    return EncryptedFileSystemStorage(location=settings.MEDIA_ROOT, base_url=None)
