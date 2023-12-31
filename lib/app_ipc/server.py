import zmq
import json
from typing import Any
from threading import Event
from app_ipc.payloads import RepPayload, ReqPayload


class Server:
    def __init__(
        self,
        obj_instance: Any,
        host: str="127.0.0.1",
        port: str="5555",
    ) -> None:
        self.obj_instance = obj_instance
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://{host}:{port}")

        self.cancel_event = Event()

    def process_request(self, req_payload: ReqPayload) -> RepPayload:
        command = req_payload.get("command", "")
        args = req_payload.get("args", {})

        if command == "shutdown_server":
            self.shutdown_server()
            return RepPayload(status="ok", payload="Server shutting down")

        if hasattr(self.obj_instance, command):
            method = getattr(self.obj_instance, command)
            resp_payload: RepPayload = method(**args)
            return resp_payload
        else:
            return RepPayload(status="error", payload="Invalid command")

    def run(self) -> None:
        while not self.cancel_event.is_set():
            message = self.socket.recv_string()
            req_payload: ReqPayload = json.loads(message)
            rep_payload: RepPayload = self.process_request(req_payload)
            self.socket.send_string(json.dumps(rep_payload))

    def shutdown_server(self) -> None:
        self.cancel_event.set()

