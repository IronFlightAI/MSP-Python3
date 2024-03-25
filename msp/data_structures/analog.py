from typing import List
from struct import unpack

from msp.data_structures.data_structure import DataStructure
from msp.message_ids import MessageIDs


class Analog(DataStructure):
    def __init__(self):
        super().__init__(MessageIDs.ANALOG)
        self.vbat = 0
        self.intPowerMeterSum = 0
        self.rssi = 0
        self.amperage = 0
        self.voltage = 0

    @staticmethod
    def parse(data: List[int]) -> DataStructure:
        analog = Analog()
        (analog.vbat,
         analog.intPowerMeterSum,
         analog.rssi,
         analog.amperage,
         analog.voltage) = unpack('<bhhhh', bytes(data[:9]))
        return analog
