from struct import unpack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs


class Attitude(DataStructure):

    def __init__(self):
        super().__init__(MessageIDs.ATTITUDE)
        self.angx = 0  # Range [-1800, 1800] 1/10°
        self.angy = 0  # Range [-900, 900] 1/10°
        self.heading = 0  # Range [-180, 180]

    @staticmethod
    def parse(data: bytes) -> 'Attitude':
        if len(data) < 6:
            raise ValueError("Invalid data length for MSP_ATTITUDE packet, expected 6 bytes")
        attitude = Attitude()
        attitude.angx, attitude.angy, attitude.heading = unpack('<hhh', data[:6])
        return attitude
