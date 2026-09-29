from __future__ import annotations

import time
from typing import Any

import requests


class YandexDiskClient:
    BASE_URL = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: str, timeout: int = 20):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"OAuth {token}",
            "Accept": "application/json",
        })
        self.timeout = timeout

    def get_resource(self, path: str) -> requests.Response:
        return self.session.get(
            f"{self.BASE_URL}/resources",
            params={"path": path},
            timeout=self.timeout,
        )

    def create_folder(self, path: str, *, overwrite: bool = False) -> requests.Response:
        return self.session.put(
            f"{self.BASE_URL}/resources",
            params={"path": path, "overwrite": str(overwrite).lower()},
            timeout=self.timeout,
        )

    def get_upload_link(self, path: str) -> requests.Response:
        return self.session.get(
            f"{self.BASE_URL}/resources/upload",
            params={"path": path, "overwrite": "false"},
            timeout=self.timeout,
        )

    def upload_bytes(self, href: str, content: bytes) -> requests.Response:
        return self.session.put(
            href,
            data=content,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.timeout,
        )

    def copy_resource(self, source_path: str, destination_path: str,
                      *, overwrite: bool = False) -> requests.Response:
        return self.session.post(
            f"{self.BASE_URL}/resources/copy",
            params={
                "from": source_path,
                "path": destination_path,
                "overwrite": str(overwrite).lower(),
                "force_async": "false",
            },
            timeout=self.timeout,
        )

    def delete_resource(self, path: str) -> requests.Response:
        return self.session.delete(
            f"{self.BASE_URL}/resources",
            params={
                "path": path,
                "permanently": "true",
                "force_async": "false",
            },
            timeout=self.timeout,
        )

    def wait_for_operation(self, href: str, *, timeout_seconds: int = 30,
                           poll_interval: float = 0.5) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self.session.get(href, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            status = payload.get("status")
            if status == "success":
                return payload
            if status == "failed":
                raise AssertionError(f"Yandex Disk operation failed: {payload}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Operation did not finish within {timeout_seconds} seconds")

    @staticmethod
    def operation_href(response: requests.Response) -> str | None:
        try:
            return response.json().get("href")
        except ValueError:
            return None
