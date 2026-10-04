"""Brute-force protection for sign-in: a few failures per email or IP lock it out for a while."""

import hashlib

from django.conf import settings
from django.core.cache import cache


def _key(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.strip().lower().encode()).hexdigest()[:32]
    return f"login-fail:{kind}:{digest}"


def client_ip(request) -> str:
    # Behind a proxy the first X-Forwarded-For entry is the client.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


def is_locked(email: str, ip: str) -> bool:
    limit = settings.LOGIN_MAX_ATTEMPTS
    return (cache.get(_key("email", email), 0) >= limit) or (cache.get(_key("ip", ip), 0) >= limit * 4)


def record_failure(email: str, ip: str) -> None:
    for kind, value in (("email", email), ("ip", ip)):
        key = _key(kind, value)
        cache.add(key, 0, settings.LOGIN_LOCKOUT_SECONDS)
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, settings.LOGIN_LOCKOUT_SECONDS)


def clear(email: str) -> None:
    cache.delete(_key("email", email))
