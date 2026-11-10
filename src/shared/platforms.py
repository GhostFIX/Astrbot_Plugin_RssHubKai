"""Platform name helpers shared by commands, dispatcher and Web API."""

from __future__ import annotations

from collections.abc import Callable

PLATFORM_ALIASES: dict[str, str] = {
    "aiocqhttp": "aiocqhttp",
    "onebot": "aiocqhttp",
    "onebot11": "aiocqhttp",
    "onebotv11": "aiocqhttp",
    "telegram": "telegram",
    "tg": "telegram",
    "qq_official": "qq_official",
    "qqofficial": "qq_official",
    "weixin_oc": "weixin_oc",
    "weixin": "weixin_oc",
}


def normalize_platform_name(value: str | None) -> str:
    """Normalize a user-supplied platform type name.

    Args:
        value: Raw platform name, e.g. ``tg`` or ``OneBot11``.

    Returns:
        Canonical lower-case platform type, or an empty string.
    """
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""
    return PLATFORM_ALIASES.get(normalized, normalized)


def platform_name_from_session(session: str | None) -> str:
    """Infer the platform type from an AstrBot unified message origin.

    ``unified_msg_origin`` is ``<platform_id>:<message_type>:<session_id>``.
    The platform id usually equals the adapter type, so the first segment is a
    safe fallback when the user leaves the platform field empty.

    Args:
        session: Target session string.

    Returns:
        Canonical platform type, or an empty string when the session is empty.
    """
    prefix = str(session or "").split(":", 1)[0].strip()
    return normalize_platform_name(prefix)


def resolve_platform_name(
    target_session: str | None,
    platform_name: str | None = None,
    *,
    resolver: Callable[[str], str] | None = None,
) -> str:
    """Resolve the effective platform type for a subscription.

    Priority: explicit value, optional AstrBot instance resolver, then the
    session prefix.

    Args:
        target_session: Target session string.
        platform_name: Explicit platform value from the Web API or command.
        resolver: Optional callback that maps a platform instance id to its
            adapter type using AstrBot's platform manager.

    Returns:
        Canonical platform type, possibly empty.
    """
    explicit = normalize_platform_name(platform_name)
    if explicit:
        return explicit

    session = str(target_session or "").strip()
    if not session:
        return ""

    prefix = session.split(":", 1)[0].strip()
    if not prefix:
        return ""

    if resolver is not None:
        try:
            resolved = normalize_platform_name(resolver(prefix))
            if resolved:
                return resolved
        except Exception:
            pass
    return normalize_platform_name(prefix)
