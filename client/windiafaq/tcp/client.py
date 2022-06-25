import asyncio

from async_timeout import timeout
import zmq
import zmq.asyncio

from windiafaq.tcp.response import Response


class TCPClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

        self.context = zmq.asyncio.Context()
        self.sock: zmq.asyncio.Socket = self.context.socket(zmq.REQ)

    async def send_command(self, command: str, *args: list[int | str | bool]) -> None:
        print("sending")
        return await self.sock.send_json({"command": command, "args": args})

    async def wait_response(self) -> Response:
        print("receiving")
        try:
            async with timeout(5.0):
                return Response(**await self.sock.recv_json(0))
        except asyncio.TimeoutError:
            return Response(error="no response from the server/timeout")

    def connect(self) -> None:
        self.sock.bind(self.endpoint)

    def disconnect(self) -> None:
        self.sock.close(5)
        self.context.term()
