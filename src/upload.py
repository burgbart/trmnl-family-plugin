"""Cloudflare R2 upload helpers.

R2 is S3-compatible, so we use boto3 with a custom endpoint.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from src.config import DASHBOARD_JSON_FILENAME

load_dotenv()


def get_r2_client() -> boto3.client:
    """Return a boto3 S3 client configured for Cloudflare R2."""
    endpoint = os.getenv("CLOUDFLARE_R2_ENDPOINT")
    access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
    secret_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")

    if not endpoint or not access_key or not secret_key:
        raise RuntimeError(
            "Missing Cloudflare R2 credentials. Set CLOUDFLARE_R2_ENDPOINT, "
            "CLOUDFLARE_R2_ACCESS_KEY_ID, and CLOUDFLARE_R2_SECRET_ACCESS_KEY."
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(
            # R2 does not support regions in the same way AWS S3 does.
            signature_version="s3v4",
        ),
    )


def upload_to_r2(
    file_path: str | Path,
    key: str,
    bucket: str | None = None,
    content_type: str = "application/json",
) -> str:
    """Upload a file to Cloudflare R2 and return the public URL if available.

    Args:
        file_path: Local path to the file to upload.
        key: Object key in the R2 bucket (e.g. "dashboard-v2.json").
        bucket: R2 bucket name. Defaults to CLOUDFLARE_R2_BUCKET_NAME env var.
        content_type: MIME type for the uploaded object.

    Returns:
        The public URL of the uploaded object, or the R2 URI if no public URL
        base is configured.
    """
    client = get_r2_client()

    file_path = Path(file_path)
    bucket = bucket or os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    if not bucket:
        raise RuntimeError(
            "Missing R2 bucket name. Set CLOUDFLARE_R2_BUCKET_NAME."
        )
    extra_args = {
        "ContentType": content_type,
        "CacheControl": "max-age=0, must-revalidate",
    }

    try:
        client.upload_file(
            str(file_path),
            bucket,
            key,
            ExtraArgs=extra_args,
        )
    except ClientError as exc:
        raise RuntimeError(f"Failed to upload {key} to R2: {exc}") from exc

    public_url_base = os.getenv("CLOUDFLARE_R2_PUBLIC_URL", "").rstrip("/")
    if public_url_base:
        return urljoin(public_url_base + "/", key)
    return f"r2://{bucket}/{key}"


def upload_json(
    file_path: str | Path,
    key: str = DASHBOARD_JSON_FILENAME,
    bucket: str | None = None,
) -> str:
    """Upload a JSON file to Cloudflare R2 and return the public URL.

    Args:
        file_path: Local path to the JSON file.
        key: Object key in the R2 bucket.
        bucket: R2 bucket name. Defaults to CLOUDFLARE_R2_BUCKET_NAME env var.

    Returns:
        The public URL of the uploaded object, or the R2 URI if no public URL
        base is configured.
    """
    return upload_to_r2(file_path, key, bucket=bucket, content_type="application/json")


if __name__ == "__main__":
    import sys

    json_path = sys.argv[1] if len(sys.argv) > 1 else f"output/{DASHBOARD_JSON_FILENAME}"
    url = upload_json(json_path)
    print(url)
