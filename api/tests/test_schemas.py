import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime, timezone
from schema.user import UserOut
from schema.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateVersionOut,
    TemplateOut,
)


def log(level, message):
    print(f"[{level}] {message}")


def test_template_create():
    log("INFO", "=== TEST 1 : TemplateCreate ===")

    t = TemplateCreate(name="Facture client", description="Template facture")
    assert t.name == "Facture client"
    assert t.description == "Template facture"
    log("INFO", "TEST 1a PASSED - avec description")

    t2 = TemplateCreate(name="Contrat CDI")
    assert t2.description is None
    log("INFO", "TEST 1b PASSED - sans description")

    try:
        t3 = TemplateCreate(description="sans nom")
        log("ERROR", "TEST 1c FAILED - aurait du lever une erreur")
        return False
    except Exception:
        log("INFO", "TEST 1c PASSED - erreur levee car name manquant")

    return True


def test_template_update():
    log("INFO", "=== TEST 2 : TemplateUpdate ===")

    u = TemplateUpdate(name="Nouveau nom")
    assert u.name == "Nouveau nom"
    assert u.description is None
    log("INFO", "TEST 2a PASSED - mise a jour partielle nom")

    u2 = TemplateUpdate(description="Nouvelle description")
    assert u2.name is None
    assert u2.description == "Nouvelle description"
    log("INFO", "TEST 2b PASSED - mise a jour partielle description")

    u3 = TemplateUpdate()
    assert u3.name is None
    assert u3.description is None
    log("INFO", "TEST 2c PASSED - mise a jour vide")

    return True


def test_template_version_out():
    log("INFO", "=== TEST 3 : TemplateVersionOut ===")

    v = TemplateVersionOut(
        id=uuid.uuid4(),
        version=1,
        object_key="uuid-001/v1.docx",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    assert v.version == 1
    assert v.is_active is True
    assert v.object_key == "uuid-001/v1.docx"
    log("INFO", "TEST 3 PASSED")
    return True


def test_template_out():
    log("INFO", "=== TEST 4 : TemplateOut ===")

    user = UserOut(
        id=uuid.uuid4(),
        email="admin@raas.com",
        role="ADMIN",
    )

    version = TemplateVersionOut(
        id=uuid.uuid4(),
        version=1,
        object_key="uuid-001/v1.docx",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    t = TemplateOut(
        id=uuid.uuid4(),
        name="Facture client",
        description="Template facture",
        created_by=user,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        versions=[version],
    )

    assert t.name == "Facture client"
    assert t.created_by.role == "ADMIN"
    assert len(t.versions) == 1
    assert t.versions[0].version == 1
    log("INFO", "TEST 4 PASSED")
    return True


def test_user_out():
    log("INFO", "=== TEST 5 : UserOut ===")

    u = UserOut(
        id=uuid.uuid4(),
        email="editor@raas.com",
        role="EDITOR",
    )
    assert u.email == "editor@raas.com"
    assert u.role == "EDITOR"
    log("INFO", "TEST 5 PASSED")
    return True


if __name__ == "__main__":
    results = {
        "template_create":      test_template_create(),
        "template_update":      test_template_update(),
        "template_version_out": test_template_version_out(),
        "template_out":         test_template_out(),
        "user_out":             test_user_out(),
    }

    passed = sum(v for v in results.values())
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Resultat : {passed}/{total} tests passes")
    for name, ok in results.items():
        print(f"  {'PASSED' if ok else 'FAILED'}  {name}")
    print(f"{'='*40}")
    exit(0 if passed == total else 1)