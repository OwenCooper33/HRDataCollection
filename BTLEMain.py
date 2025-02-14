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

