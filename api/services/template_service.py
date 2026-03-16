import uuid
import asyncpg
from core.errors import TemplateNotFoundError
from services.storage import upload_template


async def create_template(conn: asyncpg.Connection, name: str, description: str | None, created_by: str) -> dict:
    row = await conn.fetchrow("""
        INSERT INTO templates (name, description, created_by)
        VALUES ($1, $2, $3)
        RETURNING id, name, description, created_by, created_at, updated_at
    """, name, description, uuid.UUID(created_by))
    return dict(row)


async def get_template(conn: asyncpg.Connection, template_id: str) -> dict:
    row = await conn.fetchrow("""
        SELECT t.id, t.name, t.description, t.created_at, t.updated_at,
               u.id as user_id, u.email, u.role
        FROM templates t
        JOIN users u ON u.id = t.created_by
        WHERE t.id = $1 AND t.deleted = FALSE
    """, uuid.UUID(template_id))
    if not row:
        raise TemplateNotFoundError(f"Template {template_id} introuvable")
    return dict(row)


async def list_templates(conn: asyncpg.Connection) -> list[dict]:
    rows = await conn.fetch("""
        SELECT t.id, t.name, t.description, t.created_at, t.updated_at,
               u.id as user_id, u.email, u.role
        FROM templates t
        JOIN users u ON u.id = t.created_by
        WHERE t.deleted = FALSE
        ORDER BY t.created_at DESC
    """)
    return [dict(r) for r in rows]


async def update_template(conn: asyncpg.Connection, template_id: str, name: str | None, description: str | None) -> dict:
    await get_template(conn, template_id)
    row = await conn.fetchrow("""
        UPDATE templates
        SET name        = COALESCE($2, name),
            description = COALESCE($3, description),
            updated_at  = NOW()
        WHERE id = $1
        RETURNING id, name, description, created_at, updated_at
    """, uuid.UUID(template_id), name, description)
    return dict(row)


async def delete_template(conn: asyncpg.Connection, template_id: str) -> None:
    await get_template(conn, template_id)
    await conn.execute("""
        UPDATE templates
        SET deleted = TRUE, updated_at = NOW()
        WHERE id = $1
    """, uuid.UUID(template_id))


async def upload_template_version(conn: asyncpg.Connection, template_id: str, data: bytes) -> dict:
    await get_template(conn, template_id)

    last_version = await conn.fetchval("""
        SELECT COALESCE(MAX(version), 0)
        FROM template_versions
        WHERE template_id = $1
    """, uuid.UUID(template_id))
    next_version = last_version + 1

    object_key = upload_template(
        template_id=template_id,
        version=next_version,
        data=data,
    )

    row = await conn.fetchrow("""
        INSERT INTO template_versions (template_id, version, object_key)
        VALUES ($1, $2, $3)
        RETURNING id, version, object_key, is_active, created_at
    """, uuid.UUID(template_id), next_version, object_key)

    return dict(row)


async def list_versions(conn: asyncpg.Connection, template_id: str) -> list[dict]:
    await get_template(conn, template_id)
    rows = await conn.fetch("""
        SELECT id, version, object_key, is_active, created_at
        FROM template_versions
        WHERE template_id = $1
        ORDER BY version DESC
    """, uuid.UUID(template_id))
    return [dict(r) for r in rows]


async def activate_version(conn: asyncpg.Connection, template_id: str, version: int) -> dict:
    await get_template(conn, template_id)

    await conn.execute("""
        UPDATE template_versions
        SET is_active = FALSE
        WHERE template_id = $1
    """, uuid.UUID(template_id))

    row = await conn.fetchrow("""
        UPDATE template_versions
        SET is_active = TRUE
        WHERE template_id = $1 AND version = $2
        RETURNING id, version, object_key, is_active, created_at
    """, uuid.UUID(template_id), version)

    if not row:
        raise TemplateNotFoundError(f"Version {version} introuvable")
    return dict(row)


async def deactivate_version(conn: asyncpg.Connection, template_id: str, version: int) -> dict:
    await get_template(conn, template_id)
    row = await conn.fetchrow("""
        UPDATE template_versions
        SET is_active = FALSE
        WHERE template_id = $1 AND version = $2
        RETURNING id, version, object_key, is_active, created_at
    """, uuid.UUID(template_id), version)
    if not row:
        raise TemplateNotFoundError(f"Version {version} introuvable")
    return dict(row)