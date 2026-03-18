from fastapi import Header, HTTPException
from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"


PERMISSIONS = {
    Role.ADMIN: [
        "template:create",
        "template:read",
        "template:update",
        "template:delete",
        "version:upload",
        "version:activate",
        "version:deactivate",
        "preview:generate",
        "job:submit",
        "job:read",
        "user:manage",
    ],
    Role.EDITOR: [
        "template:read",
        "version:upload",
        "version:activate",
        "version:deactivate",
        "preview:generate",
        "job:submit",
        "job:read",
    ],
}


def check_permission(role: str, permission: str) -> None:

    try:
        role_enum = Role(role)
    except ValueError:
        raise HTTPException(status_code=403, detail=f"Role inconnu : {role}")

    if permission not in PERMISSIONS.get(role_enum, []):
        raise HTTPException(
            status_code=403,
            detail=f"Role {role} non autorise pour {permission}"
        )