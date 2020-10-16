import json
from typing_extensions import Literal

import requests

from django.conf import settings


HttpMethod = Literal["get", "post", "delete", "put", "patch"]


class TaskdAccountManagementError(Exception):
    pass


class TaskdAccountManager:
    def __init__(self, org_name: str, user_name: str):
        self._org_name = org_name
        self._user_name = user_name

        super().__init__()

    def _make_request(
        self, method: HttpMethod, path: str = "", raise_for_error=True, data: str = ""
    ) -> requests.models.Response:
        response = requests.request(
            method, f"http://{settings.TASKD_HTTP}/{path}", data=data,
        )
        if raise_for_error and not response.ok:
            raise TaskdAccountManagementError(response)
        return response

    def get_ca_cert(self) -> str:
        return self._make_request("get").json()["ca_cert"]

    def get_signing_template(self) -> str:
        return self._make_request("get").json()["signing_template"]

    def get_credentials(self) -> str:
        return self.make_user_request("get").json()["credentials"]

    def make_user_request(
        self,
        method: HttpMethod,
        path: str = "",
        raise_for_error: bool = True,
        data: str = "",
    ) -> requests.models.Response:
        final_path = f"{self._org_name}/{self._user_name}/"
        if path:
            final_path = final_path + path + "/"

        return self._make_request(
            method, final_path, raise_for_error=raise_for_error, data=data,
        )

    def get_new_certificate(self, csr: str, label: str = "") -> str:
        return self.make_user_request(
            "post", "certificates", data=json.dumps({"csr": csr, "label": label,})
        ).json()["certificate"]

    def create(self) -> None:
        self.make_user_request("put", data=json.dumps({}))

    def suspend(self) -> None:
        self.make_user_request("put", data=json.dumps({"is_suspended": True}))

    def resume(self) -> None:
        self.make_user_request("put", data=json.dumps({"is_suspended": False}))

    def delete(self) -> None:
        self.make_user_request("delete")

    def exists(self) -> bool:
        return self.make_user_request("get", raise_for_error=False).status_code == 200

    def get_data(self) -> bytes:
        response = self.make_user_request("get", "data")
        return response.content

    def delete_data(self) -> None:
        try:
            self.make_user_request("delete", "data")
        except TaskdAccountManagementError:
            pass
