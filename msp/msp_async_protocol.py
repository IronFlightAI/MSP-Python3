from serial.threaded import Packetizer, Protocol

PAYLOAD_START_INDEX = 5

CODE_INDEX = 4

SIZE_INDEX = 3

CHECKSUM_LEN = 1

CODE_LEN = 1
HEADER_LEN = 4


class MspPacket:

    def __init__(self, code: int, data: bytes, checksum: int):
        self.code = code
        self.data = data
        self.checksum = checksum

    def __str__(self):
        return f"code: {self.code}, data: {self.data}, checksum: {self.checksum}"

    def __eq__(self, other):
        if not isinstance(other, MspPacket):
            return False
        return (self.code == other.code and
                self.data == other.data and
                self.checksum == other.checksum)


class MspAsyncProtocol(Protocol):
    def __init__(self):
        self.buffer = bytearray()
        self.transport = None

    def connection_made(self, transport):
        """Store transport"""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget transport"""
        self.transport = None
        super(Packetizer, self).connection_lost(exc)

    def data_received(self, data):
        print(data)
        """Buffer received data, find TERMINATOR, call handle_packet"""
        self.buffer.extend(data)
        while True:
            if len(self.buffer) > HEADER_LEN:
                payload_size = self.buffer[SIZE_INDEX]
                packet_len = HEADER_LEN + CODE_LEN + payload_size + CHECKSUM_LEN
                if len(self.buffer) >= packet_len:
                    payload = self.buffer[PAYLOAD_START_INDEX:PAYLOAD_START_INDEX + payload_size]
                    code = self.buffer[CODE_INDEX]
                    checksum = self.buffer[packet_len - 1]
                    packet = MspPacket(code, payload, checksum)
                    self.buffer = self.buffer[packet_len:]
                    self.handle_packet(packet)
                else:
                    break
            else:
                break

    def handle_packet(self, packet: MspPacket):
        print(packet)
        print()

    def send(self, data):
        self.transport.write(data)
