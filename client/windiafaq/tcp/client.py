import asyncio

from loguru import logger
import zmq
import zmq.asyncio

from windiafaq.tcp.response import Response


class TCPClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

        self.context = zmq.asyncio.Context()
        self.sock: zmq.asyncio.Socket = self.context.socket(zmq.REQ)

    async def send_command(self, command: str, *args: list[int | str | bool]) -> None:
        while self.sock._state == zmq.POLLIN:
            await asyncio.sleep(1)

        return await self.sock.send_json({"command": command, "args": args})

    async def wait_response(self) -> Response:
        return Response(**await self.sock.recv_json(0))

    def reconnect(self) -> None:
        self.sock.close()
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.endpoint)

    def connect(self) -> None:
        self.sock.connect(self.endpoint)
        logger.info("bound to {}", self.endpoint)

    def disconnect(self) -> None:
        self.sock.close(5)
        self.context.term()
