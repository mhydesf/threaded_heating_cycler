import zmq
import json
from typing import Dict, Any, Optional
from app_ipc.payloads import RepPayload, ReqPayload


class Client:
    def __init__(
        self,
        host: str="127.0.0.1",
        port: str="5555",
    ) -> None:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{port}")

    def send_request(
        self,
        command: str,
        args: Optional[Dict[str, Any]]=None,
    ) -> RepPayload:
        if args is None:
            args = {}
        req_payload: ReqPayload = {"command": command, "args": args}
        self.socket.send_string(json.dumps(req_payload))
        
        resp = self.socket.recv_string()
        rep_payload: RepPayload = json.loads(resp)
        return rep_payload

