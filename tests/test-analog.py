#!/usr/bin/env python

"""test-attitude.py: Test script to send RC commands to a MultiWii Board."""
import time
import sys

from msp.message_ids import MessageIDs
from msp.multiwii import MultiWii

if __name__ == "__main__":
    try:
        fc = MultiWii("/dev/tty.usbmodem0x80000001")
        while True:
            print(fc.get_attribute(MessageIDs.ANALOG))
            time.sleep(.5)


    except Exception as error:
        import traceback

        print("Error on Main: " + str(error))
        traceback.print_exc()
