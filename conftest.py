from __future__ import annotations

import os
from uuid import uuid4

import pytest

from api.client import YandexDiskClient


@pytest.fixture(scope="session")
def yandex_client() -> YandexDiskClient:
    token = os.getenv("YANDEX_OAUTH_TOKEN")
    if not token:
        pytest.fail("Не задан YANDEX_OAUTH_TOKEN.")
    return YandexDiskClient(token)


@pytest.fixture()
def test_data(yandex_client: YandexDiskClient):
    root = f"/qa_autotests_{uuid4().hex[:10]}"
    source_file = f"{root}/source.txt"

    response = yandex_client.create_folder(root)
    assert response.status_code == 201, response.text

    upload_link = yandex_client.get_upload_link(source_file)
    assert upload_link.status_code == 200, upload_link.text

    upload = yandex_client.upload_bytes(
        upload_link.json()["href"],
        b"QA test file for Yandex Disk API",
    )
    assert upload.status_code in {201, 202}, upload.text

    if upload.status_code == 202:
        href = yandex_client.operation_href(upload)
        assert href is not None
        yandex_client.wait_for_operation(href)

    yield {"root": root, "source_file": source_file}

    cleanup = yandex_client.delete_resource(root)
    if cleanup.status_code == 202:
        href = yandex_client.operation_href(cleanup)
        if href:
            yandex_client.wait_for_operation(href)
    assert cleanup.status_code in {202, 204}, cleanup.text
