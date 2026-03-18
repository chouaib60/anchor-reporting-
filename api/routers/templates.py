from fastapi import APIRouter, UploadFile, File, Header
from fastapi.responses import Response
import asyncpg
from core.config import get_settings
from core.rbac import check_permission
from services import template_service
from services.preview_service import generate_preview
from schemas.template import TemplateCreate, TemplateUpdate

router = APIRouter()
settings = get_settings()


async def get_conn():
    return await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))


@router.get("/")
async def list_templates(x_role: str = Header(...)):
    check_permission(x_role, "template:read")
    conn = await get_conn()
    templates = await template_service.list_templates(conn)
    await conn.close()
    return templates


@router.post("/")
async def create_template(body: TemplateCreate, x_role: str = Header(...), x_user_id: str = Header(...)):
    check_permission(x_role, "template:create")
    conn = await get_conn()
    template = await template_service.create_template(conn, body.name, body.description, x_user_id)
    await conn.close()
    return template


@router.get("/{template_id}")
async def get_template(template_id: str, x_role: str = Header(...)):
    check_permission(x_role, "template:read")
    conn = await get_conn()
    template = await template_service.get_template(conn, template_id)
    await conn.close()
    return template


@router.patch("/{template_id}")
async def update_template(template_id: str, body: TemplateUpdate, x_role: str = Header(...)):
    check_permission(x_role, "template:update")
    conn = await get_conn()
    template = await template_service.update_template(conn, template_id, body.name, body.description)
    await conn.close()
    return template


@router.delete("/{template_id}")
async def delete_template(template_id: str, x_role: str = Header(...)):
    check_permission(x_role, "template:delete")
    conn = await get_conn()
    await template_service.delete_template(conn, template_id)
    await conn.close()
    return {"message": "Template supprime"}



@router.get("/{template_id}/versions")
async def list_versions(template_id: str, x_role: str = Header(...)):
    check_permission(x_role, "template:read")
    conn = await get_conn()
    versions = await template_service.list_versions(conn, template_id)
    await conn.close()
    return versions


@router.post("/{template_id}/versions")
async def upload_version(template_id: str, file: UploadFile = File(...), x_role: str = Header(...)):
    check_permission(x_role, "version:upload")
    data = await file.read()
    conn = await get_conn()
    version = await template_service.upload_template_version(conn, template_id, data)
    await conn.close()
    return version


@router.put("/{template_id}/versions/{version}/activate")
async def activate_version(template_id: str, version: int, x_role: str = Header(...)):
    check_permission(x_role, "version:activate")
    conn = await get_conn()
    result = await template_service.activate_version(conn, template_id, version)
    await conn.close()
    return result


@router.put("/{template_id}/versions/{version}/deactivate")
async def deactivate_version(template_id: str, version: int, x_role: str = Header(...)):
    check_permission(x_role, "version:deactivate")
    conn = await get_conn()
    result = await template_service.deactivate_version(conn, template_id, version)
    await conn.close()
    return result



@router.post("/{template_id}/versions/{version}/preview")
async def preview(template_id: str, version: int, mock_data: dict, x_role: str = Header(...)):
    check_permission(x_role, "preview:generate")
    conn = await get_conn()
    versions = await template_service.list_versions(conn, template_id)
    await conn.close()

    version_row = next((v for v in versions if v["version"] == version), None)
    if not version_row:
        from core.errors import TemplateNotFoundError
        raise TemplateNotFoundError(f"Version {version} introuvable")

    pdf_bytes = await generate_preview(version_row["object_key"], mock_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=preview_v{version}.pdf"}
    )