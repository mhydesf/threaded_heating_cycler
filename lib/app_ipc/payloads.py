from typing import TypedDict, Any


class ReqPayload(TypedDict):
    command: str
    args: Any

class RepPayload(TypedDict):
    status: str
    payload: Any

