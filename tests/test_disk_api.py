from __future__ import annotations

import time

import pytest

from api.client import YandexDiskClient


@pytest.mark.smoke
def test_get_existing_folder_metadata(yandex_client: YandexDiskClient, test_data):
    response = yandex_client.get_resource(test_data["root"])
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "dir"
    assert body["name"] == test_data["root"].rsplit("/", 1)[-1]
    assert body["path"].endswith(test_data["root"])


@pytest.mark.smoke
def test_put_create_folder(yandex_client: YandexDiskClient, test_data):
    new_folder = f'{test_data["root"]}/created_by_put'
    response = yandex_client.create_folder(new_folder)
    assert response.status_code == 201

    check = yandex_client.get_resource(new_folder)
    assert check.status_code == 200
    assert check.json()["type"] == "dir"
    assert check.json()["name"] == "created_by_put"


@pytest.mark.negative
def test_put_existing_folder_returns_conflict(yandex_client: YandexDiskClient, test_data):
    folder = f'{test_data["root"]}/existing'
    assert yandex_client.create_folder(folder).status_code == 201
    response = yandex_client.create_folder(folder)
    assert response.status_code == 409


@pytest.mark.smoke
def test_post_copy_file(yandex_client: YandexDiskClient, test_data):
    destination = f'{test_data["root"]}/copied.txt'
    response = yandex_client.copy_resource(test_data["source_file"], destination)
    assert response.status_code in {201, 202}

    if response.status_code == 202:
        href = yandex_client.operation_href(response)
        assert href is not None
        yandex_client.wait_for_operation(href)

    check = yandex_client.get_resource(destination)
    assert check.status_code == 200
    assert check.json()["type"] == "file"
    assert check.json()["name"] == "copied.txt"


@pytest.mark.smoke
def test_delete_file(yandex_client: YandexDiskClient, test_data):
    resource = f'{test_data["root"]}/to_delete.txt'

    upload_link = yandex_client.get_upload_link(resource)
    assert upload_link.status_code == 200

    upload = yandex_client.upload_bytes(
        upload_link.json()["href"],
        b"delete me",
    )
    assert upload.status_code in {201, 202}

    if upload.status_code == 202:
        href = yandex_client.operation_href(upload)
        assert href is not None
        yandex_client.wait_for_operation(href)

    delete = yandex_client.delete_resource(resource)
    assert delete.status_code in {202, 204}

    if delete.status_code == 202:
        href = yandex_client.operation_href(delete)
        assert href is not None
        yandex_client.wait_for_operation(href)

    deadline = 30
    for _ in range(deadline):
        check = yandex_client.get_resource(resource)

        if check.status_code == 404:
            break

        time.sleep(1)
    else:
        pytest.fail(
            f"Ресурс не был удалён за {deadline} секунд. "
            f"Последний статус: {check.status_code}"
        )

@pytest.mark.negative
def test_get_nonexistent_resource_returns_404(yandex_client: YandexDiskClient, test_data):
    response = yandex_client.get_resource(
        f'{test_data["root"]}/resource_that_does_not_exist.txt'
    )
    assert response.status_code == 404


@pytest.mark.negative
def test_get_empty_path_returns_client_error(yandex_client: YandexDiskClient):
    response = yandex_client.get_resource("")
    assert response.status_code in {400, 404}
