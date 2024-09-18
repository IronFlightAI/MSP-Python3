#!/usr/bin/env python

"""test-altitude.py: Test script to send RC commands to a MultiWii Board."""

from serial.threaded import Packetizer, ReaderThread

from msp.message_ids import MessageIDs
from msp.msp_async_protocol import MspAsyncProtocol
from msp.multiwii import MultiWii

if __name__ == "__main__":
    class MspPacket:

        def __init__(self, code: int, data: bytes, checksum: int):
            self.code = code
            self.data = data
            self.checksum = checksum

        def __str__(self):
            return f"code: {self.code}, data: {self.data}, checksum: {self.checksum}"


    class MspPacketReader2(Packetizer):

        def __init__(self):
            self.TERMINATOR = b'$'
            super().__init__()

        def data_received(self, data):
            print(data)
            """Buffer received data, find TERMINATOR, call handle_packet"""
            self.buffer.extend(data)
            while True:
                if len(self.buffer) > 4:
                    payload_len = self.buffer[3]
                    if len(self.buffer) >= 4 + 1 + payload_len + 1:
                        packet = MspPacket(self.buffer[4], self.buffer[5:-1], self.buffer[-1])
                        self.buffer = self.buffer[4 + 1 + payload_len + 1:]
                        self.handle_packet(packet)
                    else:
                        break
                else:
                    break
            # while self.TERMINATOR in self.buffer:
            #     packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            #     self.handle_packet(packet)

        def handle_packet(self, packet):
            print(packet)
            print()

        def send(self, data):
            self.transport.write(data)


    class MspPacketReader(Packetizer):
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
            split = self.buffer.split(b'$', 1)
            print("Split", split)
            return
            # Get message header information
            header = data[:3].decode("utf-8")

            # Determine if an error was thrown
            is_error = '!' in header

            # Get message length
            length = data[3]
            # Get message code
            code = data[4]

            # Get message data
            message_data = data[5:length + 1]
            # # Get message checksum
            check_sum = data[length + 1]
            packet = MspPacket(code=code, data=message_data, checksum=check_sum)
            # if expected_chksusm != actual_chksum:
            #     raise DataStructure.ChecksumMismatch(code, expected_chksum, actual_chksum)

            if is_error:
                self.handle_error(packet)
            else:
                self.handle_packet(packet)

        def handle_packet(self, packet):
            print(packet)

        def handle_error(self, packet):
            raise Exception(f"FC Responded with an error Code: {packet.message_id},, Data: {packet.data}")

        def send(self, data):
            self.transport.write(data)


    # # class PrintLines(LineReader):
    # #     def connection_made(self, transport):
    # #         super(PrintLines, self).connection_made(transport)
    # #         sys.stdout.write('port opened\n')
    # #         self.write_line('hello world')
    # #
    # #     def handle_line(self, data):
    # #         sys.stdout.write('line received: {}\n'.format(repr(data)))
    # #
    # #     def connection_lost(self, exc):
    # #         if exc:
    # #             traceback.print_exc(exc)
    # #         sys.stdout.write('port closed\n')
    #
    #
    # ser = serial.serial_for_url('loop://', baudrate=115200, timeout=1)
    # with PacketReader(ser, PrintLines) as protocol:
    #     protocol.write_line('hello')
    #     time.sleep(2)
    #
    # print_debug = sys.argv[1].lower() == 'true'
    fc = MultiWii("/dev/tty.usbmodem0x80000001", False)
    msg_id = MessageIDs.ALTITUDE
    msg: bytes = fc.get_tx_action(msg_id)([])
    if not fc.ser.is_open:
        raise Exception("Serial Port not open yet")
    def handle_packet(packet):
        print(fc.get_rx_action(packet.message_id)(packet.data))

    t = ReaderThread(fc.ser, MspAsyncProtocol)
    t.start()
    transport, protocol = t.connect()
    protocol.default_packet_handler = handle_packet
    rate = 1400
    protocol.send(fc.get_tx_action(MessageIDs.SET_RAW_RC)([rate, rate, rate, rate, rate, rate, rate, rate, ]))
    protocol.send(fc.get_tx_action(MessageIDs.ALTITUDE)([]))
    protocol.send(fc.get_tx_action(MessageIDs.RC)([]))
    protocol.send(fc.get_tx_action(MessageIDs.ALTITUDE)([]))
    protocol.send(fc.get_tx_action(MessageIDs.RAW_GPS)([]))
    protocol.send(fc.get_tx_action(MessageIDs.ALTITUDE)([]))
    protocol.send(fc.get_tx_action(MessageIDs.ATTITUDE)([]))

    # time.sleep(2)
    t.join()
    t.close()

    #
    #
    # value = fc.command(msg, with_response=False)
    # value = fc.command(msg, with_response=False)
    # # fc.ser.flushInput()
    # # while fc.ser.is_open:
    # waiting = fc.ser.in_waiting
    # buff = fc.ser.read(waiting)
    # print(buff)
    # # try:
    # #     altitude = None
    # #     start = time.time()
    # #     times = 1000
    # #     for i in range(times):
    # #         altitude = fc.get_attribute(MessageIDs.ALTITUDE)
    # #     print(round((time.time() - start) / times, 8),"s", altitude)
    # #
    # # except Exception as err:
    # #     print("Error on Main: " + str(err))
