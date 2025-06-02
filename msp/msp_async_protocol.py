import sys
from typing import Any

from serial.threaded import Packetizer, Protocol

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs

# Error codes
CHECKSUM_MISSMATCH = 0

SIZE_INDEX = 3
CODE_INDEX = 4
PAYLOAD_START_INDEX = 5

HEADER_LEN = 4
CHECKSUM_LEN = 1
CODE_LEN = 1


class MspPacket:

    def __init__(self, message_id: int, data: bytes, checksum: int):
        self.message_id = message_id
        self.data = data
        self.checksum = checksum

    def __str__(self):
        return f"code: {self.message_id}, data: {self.data}, checksum: {self.checksum}"

    def __eq__(self, other):
        if not isinstance(other, MspPacket):
            return False
        return (self.message_id == other.message_id and
                self.data == other.data and
                self.checksum == other.checksum)


class MspAsyncProtocol(Protocol):
    def __init__(self, default_packet_handler=None,
                 error_handler=lambda error_code, packet: print("ERROR:", error_code, packet)):
        self.transport = None
        self._buffer = bytearray()
        self.default_packet_handler = default_packet_handler
        self.error_handler = error_handler
        self._packet_handlers = dict()

    def connection_made(self, transport):
        """Store transport"""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget transport"""
        self.transport = None
        super().connection_lost(exc)

    def data_received(self, data):
        self._buffer.extend(data)
        while True:
            if len(self._buffer) > HEADER_LEN:
                payload_size = self._buffer[SIZE_INDEX]
                packet_len = HEADER_LEN + CODE_LEN + payload_size + CHECKSUM_LEN
                if len(self._buffer) >= packet_len:
                    actual_checksum = DataStructure.perform_checksum(
                        self._buffer[SIZE_INDEX:PAYLOAD_START_INDEX + payload_size])
                    payload = self._buffer[PAYLOAD_START_INDEX:PAYLOAD_START_INDEX + payload_size]
                    code = self._buffer[CODE_INDEX]
                    checksum = self._buffer[packet_len - 1:packet_len]
                    packet = MspPacket(code, payload, checksum[0])
                    self._buffer = self._buffer[packet_len:]
                    if checksum == actual_checksum:
                        self.handle_packet(packet)
                    else:
                        self._handle_error(CHECKSUM_MISSMATCH, packet)
                else:
                    break
            else:
                break

    def handle_packet(self, packet: MspPacket):
        handler = self._packet_handlers.get(packet.message_id, self.default_packet_handler)
        if handler:
            try:
                handler(packet)
            except Exception as e:
                print("Unexpected packet handler error:", str(e))

    def send(self, data):
        self.transport.write(data)

    def set_handler(self, message_id: int, handler):
        self._packet_handlers[message_id] = handler

    def remove_handler(self, message_id: int):
        del self._packet_handlers[message_id]

    def _handle_error(self, error_code, packet):
        if self.error_handler:
            try:
                self.error_handler(error_code, packet)
            except Exception as e:
                print("Unexpected error handler error:", str(e))
