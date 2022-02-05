import json
from typing import Any, Dict, List
from typing_extensions import Literal

from django.conf import settings
import requests

from .types.taskd import Certificate


HttpMethod = Literal["get", "post", "delete", "put", "patch"]


class TaskdAccountManagementError(Exception):
    pass


class TaskdAccountManager:
    def __init__(self, org_name: str, user_name: str):
        self._org_name = org_name
        self._user_name = user_name

        super().__init__()

    @classmethod
    def _make_request(
        cls,
        method: HttpMethod,
        path: str = "",
        raise_for_error=True,
        data: str = "",
        **request_kwargs: Any,
    ) -> requests.models.Response:
        response = requests.request(
            method, f"http://{settings.TASKD_HTTP}/{path}", data=data, **request_kwargs
        )
        if raise_for_error and not response.ok:
            raise TaskdAccountManagementError(response)
        return response

    @classmethod
    def get_ca_cert(cls, **request_kwargs: Any) -> str:
        return cls._make_request("get", **request_kwargs).json()["ca_cert"]

    @classmethod
    def get_signing_template(cls, **request_kwargs: Any) -> str:
        return cls._make_request("get", **request_kwargs).json()["signing_template"]

    def get_credentials(self, **request_kwargs: Any) -> str:
        return self.make_user_request("get", **request_kwargs).json()["credentials"]

    def make_user_request(
        self,
        method: HttpMethod,
        path: str = "",
        raise_for_error: bool = True,
        data: str = "",
        **request_kwargs: Any,
    ) -> requests.models.Response:
        final_path = f"{self._org_name}/{self._user_name}/"
        if path:
            final_path = final_path + path + "/"

        return self._make_request(
            method,
            final_path,
            raise_for_error=raise_for_error,
            data=data,
            **request_kwargs,
        )

    def get_certificates(self, **request_kwargs: Any) -> List[Certificate]:
        return self.make_user_request("get", "certificates", **request_kwargs).json()

    def get_new_certificate(
        self, csr: str, label: str = "", **request_kwargs: Any
    ) -> str:
        return self.make_user_request(
            "post",
            "certificates",
            data=json.dumps({"csr": csr, "label": label}, **request_kwargs),
        ).json()["certificate"]

    def revoke_certificate(self, fingerprint: str, **request_kwargs: Any) -> bool:
        return self.make_user_request(
            "delete",
            f"certificates/{fingerprint}",
            **request_kwargs,
        ).ok

    def register_certificate(
        self, fingerprint: str, label: str = "", **request_kwargs: Any
    ) -> bool:
        return self.make_user_request(
            "put",
            f"certificates/{fingerprint}",
            data=json.dumps(
                {
                    "label": label,
                }
            ),
            **request_kwargs,
        ).ok

    def create(self, **request_kwargs: Any) -> bool:
        return self.make_user_request("put", data=json.dumps({}), **request_kwargs).ok

    def get(self, **request_kwargs) -> Dict[str, Any]:
        result = self.make_user_request("get", **request_kwargs)
        result.raise_for_status()

        return result.json()

    def is_suspended(self, **request_kwargs: Any) -> bool:
        return self.get(**request_kwargs).get("is_suspended") or False

    def suspend(self, **request_kwargs: Any) -> bool:
        return self.make_user_request(
            "put", data=json.dumps({"is_suspended": True}), **request_kwargs
        ).ok

    def resume(self, **request_kwargs: Any) -> bool:
        return self.make_user_request(
            "put", data=json.dumps({"is_suspended": False}), **request_kwargs
        ).ok

    def delete(self, **request_kwargs: Any) -> bool:
        return self.make_user_request("delete", **request_kwargs).ok

    def exists(self, **request_kwargs: Any) -> bool:
        return (
            self.make_user_request(
                "get", raise_for_error=False, **request_kwargs
            ).status_code
            == 200
        )

    def get_data(self, **request_kwargs: Any) -> bytes:
        response = self.make_user_request("get", "data", **request_kwargs)
        return response.content

    def delete_data(self, **request_kwargs: Any) -> bool:
        try:
            return self.make_user_request("delete", "data", **request_kwargs).ok
        except TaskdAccountManagementError:
            return False
