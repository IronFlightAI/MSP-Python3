from struct import unpack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs

class GPS(DataStructure):
    def __init__(self):
        super().__init__(MessageIDs.RAW_GPS)
        self.fix = False
        self.numSat = 0
        self.lat = 0
        self.lon = 0
        self.altitude = 0       # meter
        self.speed = 0          # cm/s
        self.ground_course = 0  # degree*10

    @staticmethod
    def parse(data) -> GPS:
        if len(data) != 18:
            raise ValueError(f"Invalid GPS data length: {len(data)} != 18")

        gps = GPS()
        gps.fix = data[0]
        gps.numSat = data[1]
        gps.lat = unpack('<i', data[2:6])[0] / 1e7
        gps.lon = unpack('<i', data[6:10])[0] / 1e7
        gps.altitude = unpack('<H', data[10:12])[0]
        gps.speed = unpack('<H', data[12:14])[0] / 100.0
        gps.heading = unpack('<H', data[14:16])[0] / 100.0
        return gps

    def serialize(self, data=None) -> bytes:
        # Check if Setting or Getting
        if not data:
            # If getting use super's serialize
            return super().serialize()

        # Serialize Data
        result = int(14).to_bytes(1, 'little')
        result += int(MessageIDs.SET_RAW_GPS).to_bytes(1, 'little')

        result += int(data[0]).to_bytes(1, 'little')
        result += int(data[1]).to_bytes(1, 'little')
        result += int(data[2]).to_bytes(4, 'little')
        result += int(data[3]).to_bytes(4, 'little')
        result += int(data[4]).to_bytes(2, 'little')
        result += int(data[5]).to_bytes(2, 'little')

        # Serialize Checksum
        result = DataStructure.get_header() + result + DataStructure.perform_checksum(result)

        # Return result
        return result
