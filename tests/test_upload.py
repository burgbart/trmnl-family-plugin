"""Tests for Cloudflare R2 upload helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.upload import upload_json, upload_to_r2


@patch("src.upload.boto3.client")
def test_upload_to_r2_returns_public_url(mock_boto_client, tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_R2_ENDPOINT", "https://fake.r2.cloudflarestorage.com")
    monkeypatch.setenv("CLOUDFLARE_R2_ACCESS_KEY_ID", "fake-key")
    monkeypatch.setenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.setenv("CLOUDFLARE_R2_BUCKET_NAME", "fake-bucket")
    monkeypatch.setenv("CLOUDFLARE_R2_PUBLIC_URL", "https://dash.example.com")

    file_path = tmp_path / "dashboard.json"
    file_path.write_bytes(b"{}")

    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    url = upload_to_r2(file_path, "dashboard.json")

    mock_boto_client.assert_called_once()
    mock_s3.upload_file.assert_called_once_with(
        str(file_path),
        "fake-bucket",
        "dashboard.json",
        ExtraArgs={
            "ContentType": "application/json",
            "CacheControl": "max-age=0, must-revalidate",
        },
    )
    assert url == "https://dash.example.com/dashboard.json"


@patch("src.upload.boto3.client")
def test_upload_to_r2_without_public_url(mock_boto_client, tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_R2_ENDPOINT", "https://fake.r2.cloudflarestorage.com")
    monkeypatch.setenv("CLOUDFLARE_R2_ACCESS_KEY_ID", "fake-key")
    monkeypatch.setenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.setenv("CLOUDFLARE_R2_BUCKET_NAME", "fake-bucket")
    monkeypatch.delenv("CLOUDFLARE_R2_PUBLIC_URL", raising=False)

    file_path = tmp_path / "dashboard.json"
    file_path.write_bytes(b"{}")

    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    url = upload_to_r2(file_path, "dashboard.json")

    assert url == "r2://fake-bucket/dashboard.json"


def test_upload_to_r2_missing_credentials(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_R2_ENDPOINT", raising=False)
    monkeypatch.delenv("CLOUDFLARE_R2_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", raising=False)

    with pytest.raises(RuntimeError, match="Missing Cloudflare R2 credentials"):
        upload_to_r2("output/dashboard.json", "dashboard.json")


def test_upload_to_r2_missing_bucket(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_R2_ENDPOINT", "https://fake.r2.cloudflarestorage.com")
    monkeypatch.setenv("CLOUDFLARE_R2_ACCESS_KEY_ID", "fake-key")
    monkeypatch.setenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.delenv("CLOUDFLARE_R2_BUCKET_NAME", raising=False)

    with pytest.raises(RuntimeError, match="Missing R2 bucket name"):
        upload_to_r2("output/dashboard.json", "dashboard.json")


@patch("src.upload.upload_to_r2")
def test_upload_json(mock_upload, tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_R2_BUCKET_NAME", "fake-bucket")
    mock_upload.return_value = "https://dash.example.com/dashboard.json"

    file_path = tmp_path / "dashboard.json"
    file_path.write_bytes(b"{}")

    url = upload_json(file_path)

    mock_upload.assert_called_once_with(
        file_path, "dashboard.json", bucket=None, content_type="application/json"
    )
    assert url == "https://dash.example.com/dashboard.json"
