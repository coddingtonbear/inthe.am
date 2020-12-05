from typing import Any, Dict
from typing_extensions import TypedDict, Literal


GitSHA = str
UUIDStr = str


class Announcement(TypedDict, total=False):
    title: str
    message: str


class PublicAnnouncement(Announcement):
    system: bool


class PrivateAnnouncement(Announcement):
    username: str


class LocalSync(TypedDict):
    username: str
    debounce_id: str
    start: GitSHA
    head: GitSHA


class ChangedTask(TypedDict):
    username: str
    start: GitSHA
    head: GitSHA
    task_id: UUIDStr
    task_data: Dict[str, Any]


class LogMessage(TypedDict):
    username: str
    md5hash: str  # Deduplication hash
    last_seen: str
    created: str
    error: bool
    silent: bool
    message: str
    count: int


class IncomingMail(TypedDict, total=False):
    username: str
    message_id: Any
    subject: str
    accepted: bool
    rejected_reason: Literal["passlist", "subject"]
    task_id: str


class Sync(TypedDict):
    action: Literal["sync"]
    username: str
    org: str
    client: str
    ip: str
    port: int
    client_key: str
    record_count: int
    branch_point: str
    branch_record_count: int
    delta_count: int
    stored_count: int
    merged_count: int
    service_duration: float


class CertificateUse(TypedDict):
    username: str
    org: str
    client: str
    ip: str
    port: int
    fingerprint: str
    certificate_recognized: bool
    certificate_accepted: bool
