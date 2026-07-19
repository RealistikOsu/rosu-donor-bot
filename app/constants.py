from __future__ import annotations

from enum import IntFlag


class Privileges(IntFlag):
    """Privileges v2 (see docs/reference/privileges.md)."""

    ACTIVATED = 1
    USER_DONOR = 2  # kept name (used by the donor-role sync); value is v2 DONOR
    MOD_MANAGE_USERS = 4
    MOD_VIEW_RAP_LOGS = 8
    MOD_MANAGE_REPORTS = 16
    MOD_MANAGE_CLANS = 32
    ADMIN_SEND_ALERTS = 64
    ADMIN_MANAGE_SETTINGS = 128
    ADMIN_MANAGE_BADGES = 256
    ADMIN_MANAGE_PRIVILEGES = 512
    DEV_VIEW_ERROR_LOGS = 1024
    TOURNAMENT_STAFF = 2048
    BOT = 4096
    BN_STD = 8192
    BN_TAIKO = 16384
    BN_CTB = 32768
    BN_MANIA = 65536
