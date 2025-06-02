from struct import unpack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs


class Analog(DataStructure):
    def __init__(self):
        super().__init__(MessageIDs.ANALOG)
        self.vbat = 0  # U8 (Battery voltage in tenths of a volt)
        self.intPowerMeterSum = 0  # U16 (mAh drawn)
        self.rssi = 0  # U16 (RSSI)
        self.amperage = 0  # S16 (Amperage in 0.01A steps)

    @staticmethod
    def parse(data: bytes) -> Analog:
        if len(data) < 7:
            raise ValueError("Invalid data length for MSP_ANALOG packet, expected 7 bytes")
        analog = Analog()
        analog.vbat, analog.intPowerMeterSum, analog.rssi, analog.amperage = unpack('<BHHh', data[:7])
        return analog
