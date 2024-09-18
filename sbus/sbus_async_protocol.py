import traceback

from serial.threaded import Protocol


class Sbus:
    START_BYTE = 0x0F
    END_BYTE = 0x00
    SBUS_FRAME_LEN = 25

    BYTE_MASK = 0xFF
    CH_MASK = 0x7FF
    CH17_MASK = 0x01
    CH18_MASK = 0x02
    LOST_FRAME_MASK = 0x04
    FAILSAFE_MASK = 0x08

    OUT_OF_SYNC_THD = 10
    SBUS_NUM_CHANNELS = 18
    SBUS_SIGNAL_OK = 0
    SBUS_SIGNAL_LOST = 1
    SBUS_SIGNAL_FAILSAFE = 2
    SBUS_CHANNEL_MIN_VALUE = 192
    SBUS_CHANNEL_MAX_VALUE = 1792


class SbusFrame:

    def __init__(self, sbus_channels, fail_safe):
        self.sbus_channels = sbus_channels
        self.fail_safe = fail_safe

    @staticmethod
    def parse(frame: bytearray):
        sbus_channels = [0] * Sbus.SBUS_NUM_CHANNELS

        channel_sum = int.from_bytes(frame[1:23], byteorder="little")

        for ch in range(0, 16):
            sbus_channels[ch] = channel_sum & 0x7ff
            channel_sum = channel_sum >> 11

        # to be tested, No 17 & 18 channel on taranis X8R
        if (frame[23]) & 0x0001:
            sbus_channels[16] = 2047
        else:
            sbus_channels[16] = 0
        # to be tested, No 17 & 18 channel on taranis X8R
        if ((frame[23]) >> 1) & 0x0001:
            sbus_channels[17] = 2047
        else:
            sbus_channels[17] = 0

        # Failsafe
        fail_safe_status = Sbus.SBUS_SIGNAL_OK
        if (frame[Sbus.SBUS_FRAME_LEN - 2]) & (1 << 2):
            fail_safe_status = Sbus.SBUS_SIGNAL_LOST
        if (frame[Sbus.SBUS_FRAME_LEN - 2]) & (1 << 3):
            fail_safe_status = Sbus.SBUS_SIGNAL_FAILSAFE
        return SbusFrame(sbus_channels, fail_safe_status)

    def serialize(self):
        channels = [0] * Sbus.SBUS_NUM_CHANNELS
        for i in range(Sbus.SBUS_NUM_CHANNELS):
            channels[i] = max(0, min(self.sbus_channels[i], Sbus.CH_MASK))

        buff = bytearray()
        buff.append(Sbus.START_BYTE)
        buff.append(channels[0] & 0xFF)
        buff.append(((channels[0] & 0x07FF) >> 8 | (channels[1] & 0x07FF) << 3) & 0xFF)
        buff.append(((channels[1] & 0x07FF) >> 5 | (channels[2] & 0x07FF) << 6) & 0xFF)
        buff.append(((channels[2] & 0x07FF) >> 2) & 0xFF)
        buff.append(((channels[2] & 0x07FF) >> 10 | (channels[3] & 0x07FF) << 1) & 0xFF)
        buff.append(((channels[3] & 0x07FF) >> 7 | (channels[4] & 0x07FF) << 4) & 0xFF)
        buff.append(((channels[4] & 0x07FF) >> 4 | (channels[5] & 0x07FF) << 7) & 0xFF)
        buff.append(((channels[5] & 0x07FF) >> 1) & 0xFF)
        buff.append(((channels[5] & 0x07FF) >> 9 | (channels[6] & 0x07FF) << 2) & 0xFF)
        buff.append(((channels[6] & 0x07FF) >> 6 | (channels[7] & 0x07FF) << 5) & 0xFF)
        buff.append((channels[7] & 0x07FF) >> 3)
        buff.append(channels[8] & 0xFF)
        buff.append(((channels[8] & 0x07FF) >> 8 | (channels[9] & 0x07FF) << 3) & 0xFF)
        buff.append(((channels[9] & 0x07FF) >> 5 | (channels[10] & 0x07FF) << 6) & 0xFF)
        buff.append(((channels[10] & 0x07FF) >> 2) & 0xFF)
        buff.append(((channels[10] & 0x07FF) >> 10 | (channels[11] & 0x07FF) << 1) & 0xFF)
        buff.append(((channels[11] & 0x07FF) >> 7 | (channels[12] & 0x07FF) << 4) & 0xFF)
        buff.append(((channels[12] & 0x07FF) >> 4 | (channels[13] & 0x07FF) << 7) & 0xFF)
        buff.append(((channels[13] & 0x07FF) >> 1) & 0xFF)
        buff.append(((channels[13] & 0x07FF) >> 9 | (channels[14] & 0x07FF) << 2) & 0xFF)
        buff.append(((channels[14] & 0x07FF) >> 6 | (channels[15] & 0x07FF) << 5) & 0xFF)
        buff.append((channels[15] & 0x07FF) >> 3)
        buff.append(0x00 | (channels[16] * Sbus.CH17_MASK) | (channels[17] * Sbus.CH18_MASK) |
                    (self.fail_safe * Sbus.FAILSAFE_MASK) | (self.fail_safe * Sbus.LOST_FRAME_MASK))
        buff.append(Sbus.END_BYTE)
        return buff

    def get_rx_channels(self):
        """
        Used to retrieve the last SBUS channels values reading
        :return:  an array of 18 unsigned short elements containing 16 standard channel values + 2 digitals (ch 17 and 18)
        """

        return self.sbus_channels

    def get_rx_channel(self, num_ch):
        """
        Used to retrieve the last SBUS channel value reading for a specific channel
        :param: num_ch: the channel which to retrieve the value for
        :return:  a short value containing
        """

        return self.sbus_channels[num_ch]

    def get_failsafe_status(self):
        """
        Used to retrieve the last FAILSAFE status
        :return:  a short value containing
        """

        return self.fail_safe

    def __str__(self):
        result = {}

        # Iterate over the array and construct the dictionary
        for i, value in enumerate(self.sbus_channels, start=1):
            key = f'C{i:02d}'
            result[key] = value
        result["FL"] = self.fail_safe & Sbus.SBUS_SIGNAL_LOST > 0
        result["FS"] = self.fail_safe & Sbus.SBUS_SIGNAL_LOST > 0
        return result.__str__()
        # return ",".join(str(ch) for i, ch in enumerate(self.sbus_channels))


class SbusAsyncProtocol(Protocol):

    def __init__(self, frame_handler=lambda frame: print(frame)):
        self.transport = None
        self.frame_handler = frame_handler
        self._buffer = bytearray()
        self._in_frame = False

    def connection_made(self, transport):
        """Store transport"""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget transport"""
        self.transport = None
        super(self).connection_lost(exc)

    def data_received(self, data):
        for b in data:
            if self._in_frame:
                self._buffer.append(b)
                if len(self._buffer) == Sbus.SBUS_FRAME_LEN:
                    decoded_frame = SbusFrame.parse(self._buffer)
                    try:
                        self.frame_handler(decoded_frame)
                    except:
                        # Print the stack trace
                        traceback.print_exc()
                    self._in_frame = False
            elif b == Sbus.START_BYTE:
                self._in_frame = True
                self._buffer.clear()
                self._buffer.append(b)


if __name__ == '__main__':
    b = bytearray(b'\x0f\x0f\xdb\x03\x9f+\xc8\xf7\x8b_\xfc\xa2|\xbf(_\xf9\xca\x07\x00\x00\x00\x00\x00\x00')
    print("ex", b)
    frame = SbusFrame.parse(b)
    processed = frame.serialize()
    print("ac", processed)
    print(frame)
