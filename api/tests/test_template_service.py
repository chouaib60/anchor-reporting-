import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from core.config import get_settings
from models.user import CREATE_USERS_TABLE
from models.template import CREATE_TEMPLATES_TABLE, CREATE_TEMPLATE_VERSIONS_TABLE
from services.template_service import (
    create_template,
    get_template,
    list_templates,
    update_template,
    delete_template,
    upload_template_version,
    list_versions,
    activate_version,
    deactivate_version,
)
from core.errors import TemplateNotFoundError

settings = get_settings()


def log(level, message):
    print(f"[{level}] {message}")


async def get_conn():
    return await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))


async def setup(conn):
    await conn.execute(CREATE_USERS_TABLE)
    await conn.execute(CREATE_TEMPLATES_TABLE)
    await conn.execute(CREATE_TEMPLATE_VERSIONS_TABLE)

    user_id = await conn.fetchval("""
        INSERT INTO users (email, hashed_password, role)
        VALUES ('admin@raas.com', 'hashedpwd', 'ADMIN')
        ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
        RETURNING id
    """)
    return str(user_id)


async def cleanup(conn, template_id: str = None):
    if template_id:
        await conn.execute("DELETE FROM template_versions WHERE template_id = $1", template_id)
        await conn.execute("DELETE FROM templates WHERE id = $1", template_id)


# -- Test 1 : Créer un template --

async def test_create_template(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 1 : Creer un template ===")
    try:
        t = await create_template(conn, "Facture client", "Template facture", user_id)
        assert t["name"] == "Facture client"
        assert t["description"] == "Template facture"
        log("INFO", f"TEST 1 PASSED - id : {t['id']}")
        await cleanup(conn, str(t["id"]))
        return True
    except Exception as e:
        log("ERROR", f"TEST 1 FAILED : {e}")
        return False


# -- Test 2 : Récupérer un template --

async def test_get_template(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 2 : Recuperer un template ===")
    try:
        t = await create_template(conn, "Contrat CDI", None, user_id)
        fetched = await get_template(conn, str(t["id"]))
        assert str(fetched["id"]) == str(t["id"])
        assert fetched["name"] == "Contrat CDI"
        log("INFO", "TEST 2 PASSED")
        await cleanup(conn, str(t["id"]))
        return True
    except Exception as e:
        log("ERROR", f"TEST 2 FAILED : {e}")
        return False


# -- Test 3 : Template introuvable --

async def test_template_not_found(conn) -> bool:
    log("INFO", "=== TEST 3 : Template introuvable ===")
    try:
        import uuid
        await get_template(conn, str(uuid.uuid4()))
        log("ERROR", "TEST 3 FAILED - aurait du lever une erreur")
        return False
    except TemplateNotFoundError:
        log("INFO", "TEST 3 PASSED - TemplateNotFoundError levee")
        return True
    except Exception as e:
        log("ERROR", f"TEST 3 FAILED : {e}")
        return False


# -- Test 4 : Lister les templates --

async def test_list_templates(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 4 : Lister les templates ===")
    try:
        t1 = await create_template(conn, "Template 1", None, user_id)
        t2 = await create_template(conn, "Template 2", None, user_id)
        templates = await list_templates(conn)
        assert len(templates) >= 2
        log("INFO", f"TEST 4 PASSED - {len(templates)} templates trouves")
        await cleanup(conn, str(t1["id"]))
        await cleanup(conn, str(t2["id"]))
        return True
    except Exception as e:
        log("ERROR", f"TEST 4 FAILED : {e}")
        return False


# -- Test 5 : Mettre à jour un template --

async def test_update_template(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 5 : Mettre a jour un template ===")
    try:
        t = await create_template(conn, "Ancien nom", None, user_id)
        updated = await update_template(conn, str(t["id"]), "Nouveau nom", None)
        assert updated["name"] == "Nouveau nom"
        log("INFO", "TEST 5 PASSED")
        await cleanup(conn, str(t["id"]))
        return True
    except Exception as e:
        log("ERROR", f"TEST 5 FAILED : {e}")
        return False


# -- Test 6 : Suppression douce --

async def test_delete_template(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 6 : Suppression douce ===")
    try:
        t = await create_template(conn, "A supprimer", None, user_id)
        await delete_template(conn, str(t["id"]))
        try:
            await get_template(conn, str(t["id"]))
            log("ERROR", "TEST 6 FAILED - template encore visible")
            return False
        except TemplateNotFoundError:
            log("INFO", "TEST 6 PASSED - template marque deleted, invisible")
            await conn.execute("DELETE FROM templates WHERE id = $1", t["id"])
            return True
    except Exception as e:
        log("ERROR", f"TEST 6 FAILED : {e}")
        return False


# -- Test 7 : Upload + versioning --

async def test_versioning(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 7 : Versioning ===")
    try:
        t = await create_template(conn, "Template versionne", None, user_id)
        template_id = str(t["id"])

        v1 = await upload_template_version(conn, template_id, b"PK docx content v1")
        assert v1["version"] == 1
        log("INFO", f"Version 1 creee : {v1['object_key']}")

        v2 = await upload_template_version(conn, template_id, b"PK docx content v2")
        assert v2["version"] == 2
        log("INFO", f"Version 2 creee : {v2['object_key']}")

        versions = await list_versions(conn, template_id)
        assert len(versions) == 2
        log("INFO", f"TEST 7 PASSED - {len(versions)} versions trouvees")

        await cleanup(conn, template_id)
        return True
    except Exception as e:
        log("ERROR", f"TEST 7 FAILED : {e}")
        return False


# -- Test 8 : Activation de version --

async def test_activate_version(conn, user_id: str) -> bool:
    log("INFO", "=== TEST 8 : Activation de version ===")
    try:
        t = await create_template(conn, "Template activation", None, user_id)
        template_id = str(t["id"])

        await upload_template_version(conn, template_id, b"PK docx v1")
        await upload_template_version(conn, template_id, b"PK docx v2")
        await upload_template_version(conn, template_id, b"PK docx v3")

        # Activer la version 2
        activated = await activate_version(conn, template_id, 2)
        assert activated["is_active"] is True
        assert activated["version"] == 2
        log("INFO", "TEST 8a PASSED - version 2 activee")

        # Activer la version 3 - version 2 doit être désactivée automatiquement
        activated = await activate_version(conn, template_id, 3)
        assert activated["version"] == 3
        assert activated["is_active"] is True
        log("INFO", "TEST 8b PASSED - version 3 activee")

        # Vérifier que version 2 est bien désactivée
        versions = await list_versions(conn, template_id)
        v2 = next(v for v in versions if v["version"] == 2)
        assert v2["is_active"] is False
        log("INFO", "TEST 8c PASSED - version 2 desactivee automatiquement")

        await cleanup(conn, template_id)
        return True
    except Exception as e:
        log("ERROR", f"TEST 8 FAILED : {e}")
        return False


# -- Main --

async def main():
    conn = await get_conn()
    user_id = await setup(conn)

    results = {
        "create_template":    await test_create_template(conn, user_id),
        "get_template":       await test_get_template(conn, user_id),
        "template_not_found": await test_template_not_found(conn),
        "list_templates":     await test_list_templates(conn, user_id),
        "update_template":    await test_update_template(conn, user_id),
        "delete_template":    await test_delete_template(conn, user_id),
        "versioning":         await test_versioning(conn, user_id),
        "activate_version":   await test_activate_version(conn, user_id),
    }

    await conn.close()

    passed = sum(v for v in results.values())
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Resultat : {passed}/{total} tests passes")
    for name, ok in results.items():
        print(f"  {'PASSED' if ok else 'FAILED'}  {name}")
    print(f"{'='*40}")
    exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())