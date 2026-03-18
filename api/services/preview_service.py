import tempfile
import subprocess
import os
from pathlib import Path
from docxtpl import DocxTemplate
from core.config import get_settings
from core.errors import TemplateRenderError
from services.storage import download_template, upload_output

settings = get_settings()


def render_docx(docx_bytes: bytes, data: dict) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docx_path = tmp_path / "template.docx"
        docx_path.write_bytes(docx_bytes)

        try:
            doc = DocxTemplate(str(docx_path))
            doc.render(data)
            output_path = tmp_path / "rendered.docx"
            doc.save(str(output_path))
            return output_path.read_bytes()
        except Exception as e:
            raise TemplateRenderError(f"Erreur de rendu : {str(e)}")


def convert_to_pdf(docx_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docx_path = tmp_path / "rendered.docx"
        docx_path.write_bytes(docx_bytes)

        profile_dir = tmp_path / "lo_profile"
        profile_dir.mkdir()

        cmd = [
            settings.libreoffice_path,
            "--headless",
            "--norestore",
            "--nofirststartwizard",
            f"-env:UserInstallation=file:///{profile_dir.as_posix()}",
            "--convert-to", "pdf",
            "--outdir", str(tmp_path),
            str(docx_path),
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                timeout=settings.worker_job_timeout_seconds,
            )
            if proc.returncode != 0:
                raise TemplateRenderError(f"LibreOffice erreur : {proc.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise TemplateRenderError("Timeout LibreOffice depasse")

        pdf_path = tmp_path / "rendered.pdf"
        if not pdf_path.exists():
            raise TemplateRenderError("PDF non genere")

        return pdf_path.read_bytes()


async def generate_preview(object_key: str, mock_data: dict) -> bytes:

    docx_bytes = download_template(object_key)

    rendered_docx = render_docx(docx_bytes, mock_data)

    pdf_bytes = convert_to_pdf(rendered_docx)

    return pdf_bytes