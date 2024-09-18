#!/usr/bin/env python

"""test-altitude.py: Test script to send RC commands to a MultiWii Board."""

import sys
import time
from email._header_value_parser import MessageID

from msp.message_ids import MessageIDs
from msp.multiwii import MultiWii

if __name__ == "__main__":
    # print_debug = sys.argv[1].lower() == 'true'
    fc = MultiWii("/dev/tty.usbmodem0x80000001", False)
    try:
        while True:
            print(fc.get_altitude())
            
    except Exception as err:
        print("Error on Main: " + str(err))
