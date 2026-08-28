"""Read-only mode guard for tools that act on the device or make it place
calls / send messages / launch apps.

Defaults to enabled (fail-closed): set PHONE_READONLY=false to allow calls,
SMS sending, contact creation, app launch/termination, alarm creation, and
screen input (tap/swipe/key/text).
"""

import os


def is_read_only() -> bool:
    return os.environ.get("PHONE_READONLY", "true") not in ("0", "false", "False", "")


#: Message returned by a guarded tool when blocked; ``None`` means "proceed".
#: Tools in this codebase return plain result/error strings rather than
#: raising, so the guard follows the same convention:
#:
#:     if (blocked := require_writable()) is not None:
#:         return blocked
_BLOCKED_MESSAGE = (
    "This server is running in read-only mode (PHONE_READONLY=true). "
    "Set PHONE_READONLY=false to enable calls, SMS, contact creation, "
    "app launch/termination, alarms, and screen input."
)


def require_writable() -> str | None:
    return _BLOCKED_MESSAGE if is_read_only() else None
