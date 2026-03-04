import io
from datetime import timedelta
from minio import Minio
from core.config import get_settings

settings = get_settings()


def get_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def init_buckets() -> None:
    client = get_client()
    for bucket in [settings.minio_bucket_templates, settings.minio_bucket_outputs]:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def upload_template(template_id: str, version: int, data: bytes) -> str:
    client = get_client()
    object_key = f"{template_id}/v{version}.docx"
    client.put_object(
        settings.minio_bucket_templates,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    return object_key


def download_template(object_key: str) -> bytes:
    client = get_client()
    response = client.get_object(settings.minio_bucket_templates, object_key)
    data = response.read()
    response.close()
    return data


def upload_output(job_id: str, data: bytes) -> str:
    client = get_client()
    object_key = f"{job_id}/output.pdf"
    client.put_object(
        settings.minio_bucket_outputs,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type="application/pdf",
    )
    return object_key


def download_output(object_key: str) -> bytes:
    client = get_client()
    response = client.get_object(settings.minio_bucket_outputs, object_key)
    data = response.read()
    response.close()
    return data


def get_output_url(object_key: str, expires_hours: int = 1) -> str:
    client = get_client()
    return client.presigned_get_object(
        settings.minio_bucket_outputs,
        object_key,
        expires=timedelta(hours=expires_hours),
    )