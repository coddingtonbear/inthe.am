from typing import Optional
from typing_extensions import TypedDict


class Certificate(TypedDict):
    fingerprint: str
    label: str
    created: str  # ISO
    revoked: Optional[str]  # ISO
