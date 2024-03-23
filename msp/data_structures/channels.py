from struct import unpack, pack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs

MAX_VALUE = 2100
MIN_VALUE = 950
MID_VALUE = 1500
ARM_VALUE = 2050
OFF_VALUE = 850


class Channel(DataStructure):
    def __init__(self):
        super().__init__(MessageIDs.RC)
        self.roll = MID_VALUE
        self.pitch = MID_VALUE
        self.yaw = MID_VALUE
        self.throttle = MID_VALUE
        self.aux1 = MIN_VALUE
        self.aux2 = MIN_VALUE
        self.aux3 = MIN_VALUE
        self.aux4 = MIN_VALUE

    @staticmethod
    def parse(data):
        channel = Channel()
        if len(data) != 0:
            channel.roll = unpack('<H', bytes(data[:2]))[0]
            channel.pitch = unpack('<H', bytes(data[2:4]))[0]
            channel.yaw = unpack('<H', bytes(data[4:6]))[0]
            channel.throttle = unpack('<H', bytes(data[6:8]))[0]
            channel.aux1 = unpack('<H', bytes(data[8:10]))[0]
            channel.aux2 = unpack('<H', bytes(data[10:12]))[0]
            channel.aux3 = unpack('<H', bytes(data[12:14]))[0]
            channel.aux4 = unpack('<H', bytes(data[14:16]))[0]
            # Channel 9 not used

        return channel

    def serialize(self, data=None):
        # Check if Setting or Getting
        if not data:
            # If getting use super's serialize
            return super().serialize()

        # Serialize Data
        result = int(16).to_bytes(1, 'little')
        result += int(MessageIDs.SET_RAW_RC).to_bytes(1, 'little')
        for i in data:
            result += int(i).to_bytes(2, 'little')

        # Serialize Checksum
        result = DataStructure.get_header() + result + DataStructure.perform_checksum(result)

        # Return result
        return result
