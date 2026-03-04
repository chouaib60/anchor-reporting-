import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storage import (
    init_buckets,
    upload_template,
    download_template,
    upload_output,
    download_output,
    get_output_url,
)


def log(level, message):
    print(f"[{level}] {message}")


def test_init_buckets() -> bool:
    log("INFO", "=== TEST 1 : Initialisation des buckets ===")
    try:
        init_buckets()
        log("INFO", "TEST 1 PASSED - buckets templates et outputs prets")
        return True
    except Exception as e:
        log("ERROR", f"TEST 1 FAILED : {e}")
        return False


def test_upload_template() -> bool:
    log("INFO", "=== TEST 2 : Upload template DOCX ===")
    try:
        fake_docx = b"PK fake docx content for testing"
        key = upload_template(template_id="template-001", version=1, data=fake_docx)
        assert key == "template-001/v1.docx", f"Cle inattendue : {key}"
        log("INFO", f"TEST 2 PASSED - cle : {key}")
        return True
    except Exception as e:
        log("ERROR", f"TEST 2 FAILED : {e}")
        return False


def test_download_template() -> bool:
    log("INFO", "=== TEST 3 : Download template DOCX ===")
    try:
        fake_docx = b"PK fake docx content for testing"
        upload_template(template_id="template-001", version=1, data=fake_docx)
        downloaded = download_template("template-001/v1.docx")
        assert downloaded == fake_docx, "Contenu different de l'original"
        log("INFO", f"TEST 3 PASSED - {len(downloaded)} bytes recuperes")
        return True
    except Exception as e:
        log("ERROR", f"TEST 3 FAILED : {e}")
        return False


def test_upload_output() -> bool:
    log("INFO", "=== TEST 4 : Upload PDF output ===")
    try:
        fake_pdf = b"%PDF-1.4 fake pdf content"
        key = upload_output(job_id="job-001", data=fake_pdf)
        assert key == "job-001/output.pdf", f"Cle inattendue : {key}"
        log("INFO", f"TEST 4 PASSED - cle : {key}")
        return True
    except Exception as e:
        log("ERROR", f"TEST 4 FAILED : {e}")
        return False


def test_download_output() -> bool:
    log("INFO", "=== TEST 5 : Download PDF output ===")
    try:
        fake_pdf = b"%PDF-1.4 fake pdf content"
        upload_output(job_id="job-001", data=fake_pdf)
        downloaded = download_output("job-001/output.pdf")
        assert downloaded == fake_pdf, "Contenu different de l'original"
        log("INFO", f"TEST 5 PASSED - {len(downloaded)} bytes recuperes")
        return True
    except Exception as e:
        log("ERROR", f"TEST 5 FAILED : {e}")
        return False


def test_output_url() -> bool:
    log("INFO", "=== TEST 6 : Lien de telechargement temporaire ===")
    try:
        fake_pdf = b"%PDF-1.4 fake pdf content"
        upload_output(job_id="job-001", data=fake_pdf)
        url = get_output_url("job-001/output.pdf", expires_hours=1)
        assert url.startswith("http"), f"URL invalide : {url}"
        log("INFO", "TEST 6 PASSED - URL generee")
        return True
    except Exception as e:
        log("ERROR", f"TEST 6 FAILED : {e}")
        return False


if __name__ == "__main__":
    results = {
        "init_buckets":      test_init_buckets(),
        "upload_template":   test_upload_template(),
        "download_template": test_download_template(),
        "upload_output":     test_upload_output(),
        "download_output":   test_download_output(),
        "output_url":        test_output_url(),
    }

    passed = sum(v for v in results.values())
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Resultat : {passed}/{total} tests passes")

    for name, ok in results.items():
        print(f"  {'PASSED' if ok else 'FAILED'}  {name}")

    print(f"{'='*40}")
    print("GO - Storage operationnel" if passed == total else "NO-GO - Verifier les erreurs")
    exit(0 if passed == total else 1)