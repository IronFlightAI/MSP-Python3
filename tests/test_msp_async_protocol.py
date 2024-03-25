from unittest import TestCase
from unittest.mock import patch

from msp.msp_async_protocol import MspAsyncProtocol, MspPacket


class TestMspProtocol(TestCase):
    def test_data_received__happy_path(self):
        data_chunks = [
            b'$',
            b'M>\x06m\xaf\xfd\xff\xff\x00\x009',
            b'$',
            b'M>$i\xdc\x05\xdc\x05\xdc\x05u\x03\x8b\x06\xdc\x05',
            b'\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05',
            b'\xdc\x05\xdc\x05\xb6$M>\x06m\x9e\xfd\xff\xff\x00\x00\x08',
            b'$',
            b'M>\x12j\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x$M>\x06m\xb7\xfd\xff\xff\x00\x00!',
            b'$',
            b'M>\x06l\xe3\xffM\x00>\x00\x05',
        ]
        with patch('msp.msp_async_protocol.MspAsyncProtocol.handle_packet') as handle_packet_method:
            sut = MspAsyncProtocol()
            for chunk in data_chunks:
                sut.data_received(chunk)

            # Assert that my_method was called three times
            self.assertEqual(handle_packet_method.call_count, 6)

            # Assert that my_method was called with specific parameters each time
            handle_packet_method.assert_any_call(MspPacket(109, bytearray(b'\xaf\xfd\xff\xff\x00\x00'), 57))
            handle_packet_method.assert_any_call(MspPacket(105, bytearray(b'\xdc\x05\xdc\x05\xdc\x05u\x03\x8b\x06\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05\xdc\x05'), 182))
            handle_packet_method.assert_any_call(MspPacket(109, bytearray(b'\x9e\xfd\xff\xff\x00\x00'), 8))
            handle_packet_method.assert_any_call(MspPacket(106, bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), 120))
            handle_packet_method.assert_any_call(MspPacket(109, bytearray(b'\xb7\xfd\xff\xff\x00\x00'), 33))
            handle_packet_method.assert_any_call(MspPacket(108, bytearray(b'\xe3\xffM\x00>\x00'), 5))
