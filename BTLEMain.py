import asyncio
import time
import numpy as np
import matplotlib.pyplot as plt
from bleak import BleakClient
from scipy import stats, signal

# Wahoo TICKR btle and  UUID
HRM_SERVICE_UUID = '0000180d-0000-1000-8000-00805f9b34fb'
HRM_CHAR_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

time_stamps = []
rr_intervals = []
async def hr_data_handler(sender, data):
# gets the hr from the hr sensro incoming data
# checks the "flag" byte to see if the hr is stored in one or two
# bytes and reads in the appropriate byte
    flag = data[0]
    if flag & 0x10:
        rr_bytes = data[2:]
        for i in range(0, len(rr_bytes), 2):
            rr_interval = int.from_bytes(rr_bytes[i:i+2], byteorder='little') / 1000.0
            rr_intervals.append(rr_interval)
            time_stamps.append(time.time())
