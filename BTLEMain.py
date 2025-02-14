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
heart_rate_data = []
rr_intervals = []
async def hr_data_handler(sender, data):
# gets the hr from the hr sensro incoming data
# checks the "flag" byte to see if the hr is stored in one or two
# bytes and reads in the appropriate byte
    flag = data[0]
    index = 1
    if flag & 0x01:
        hr_value = int.from_bytes(data[index:index+2], byteorder='little')
        index += 2
    else:
        hr_value = data[index]
        index += 1
    heart_rate_data.append(hr_value)
    time_stamps.append(time.time())

    if flag & 0x10:  # RR-Interval present
        while index < len(data):
            rr = int.from_bytes(data[index:index+2], byteorder='little') / 1024.0  # Convert to seconds
            rr_intervals.append(rr)
            index += 2