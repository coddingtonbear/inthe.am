from typing import List, Optional

from dateutil.parser import parse
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import TaskStore
from ..decorators import requires_task_store
from ..serializers.certificate import CertificateSerializer


class CertificateViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def _get_certificates(self, store: TaskStore) -> List[dict]:
        certs: List[dict] = []
        for cert in store.taskd_account.get_certificates():
            revoked = cert["revoked"]
            certs.append(
                {
                    "fingerprint": cert["fingerprint"],
                    "label": cert["label"],
                    "created": cert["created"],
                    "revoked": parse(revoked) if revoked else None,
                }
            )

        return certs

    def _get_certificate_by_fingerprint(
        self, store: TaskStore, fingerprint: str
    ) -> Optional[dict]:
        try:
            return list(
                filter(
                    lambda x: x["fingerprint"] == fingerprint,
                    self._get_certificates(store),
                )
            )[0]
        except IndexError:
            return None

    @requires_task_store
    def list(self, request, *, store: TaskStore):
        serializer = CertificateSerializer(self._get_certificates(store), many=True)
        return Response(serializer.data)

    @requires_task_store
    def create(self, request, *, store: TaskStore):
        label = request.data.get("label", "")

        if not store.generate_new_certificate(label=label):
            return Response(status=500)

        return Response()

    @requires_task_store
    def retrieve(self, request, pk=None, *, store: TaskStore):
        cert = self._get_certificate_by_fingerprint(store, pk)

        if not cert:
            raise NotFound()

        serializer = CertificateSerializer(cert)
        return Response(serializer.data)

    @requires_task_store
    def destroy(self, request, pk=None, *, store: TaskStore):
        cert = self._get_certificate_by_fingerprint(store, pk)

        if not cert:
            raise NotFound()

        result = store.taskd_account.revoke_certificate(pk)

        if not result:
            return Response(status=500)

        return Response()
