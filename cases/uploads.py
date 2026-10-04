"""Upload checks. The file type is decided from the file's own bytes, never from the browser's claim, and only
a short list of document and image types is accepted. Everything else is rejected."""

from django.conf import settings
from django.core.exceptions import ValidationError

# extension -> (content type, checker on the first bytes)
ALLOWED = {
    "pdf": ("application/pdf", lambda b: b.startswith(b"%PDF-")),
    "png": ("image/png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    "jpg": ("image/jpeg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "jpeg": ("image/jpeg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "webp": ("image/webp", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
    "heic": ("image/heic", lambda b: b[4:8] == b"ftyp"),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        lambda b: b.startswith(b"PK\x03\x04"),
    ),
    "txt": ("text/plain", lambda b: b"\x00" not in b),
    "eml": ("message/rfc822", lambda b: b"\x00" not in b),
}

ACCEPT_ATTR = ",".join(f".{ext}" for ext in ALLOWED)


def validate_upload(upload) -> tuple[str, str]:
    """Returns (extension, content type) or raises ValidationError."""
    if upload.size > settings.MAX_UPLOAD_BYTES:
        raise ValidationError(f"Files must be {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB or smaller.")
    name = upload.name or ""
    extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if extension not in ALLOWED:
        raise ValidationError("Upload a photo, screenshot, PDF, Word document, text or email file.")
    content_type, looks_right = ALLOWED[extension]
    head = upload.read(2048)
    upload.seek(0)
    if not looks_right(head):
        raise ValidationError("This file does not look like a real ." + extension + " file.")
    return extension, content_type


# Types safe to show in the browser; everything else is downloaded.
INLINE_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
