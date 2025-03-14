#!/usr/bin/env python

"""test-altitude.py: Test script to send RC commands to a MultiWii Board."""

import time

from msp.message_ids import MessageIDs
from msp.multiwii import MultiWii

if __name__ == "__main__":
    fc = MultiWii("COM3")
    try:
        while True:
            print(fc.get_attribute(MessageIDs.ALTITUDE))
            time.sleep(0.5)
    except Exception as error:
        import traceback

        print("Error on Main: " + str(error))
        traceback.print_exc()
