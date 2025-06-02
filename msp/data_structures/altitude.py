from struct import unpack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs


class Altitude(DataStructure):
    def __init__(self):
        super().__init__(MessageIDs.ALTITUDE)
        self.estimated_altitude = 0  # cm
        self.vertical_velocity = 0  # cm/s
        self.baro_altitude = 0  # if barometer enabled

    @staticmethod
    def parse(data: bytes) -> 'Altitude':
        if len(data) < 10:
            raise ValueError("Invalid data length for MSP_ANALOG packet, expected 7 bytes")
        altitude = Altitude()
        altitude.estimated_altitude, altitude.vertical_velocity, altitude.baro_altitude = unpack('<ihi', data[:10])
        return altitude
