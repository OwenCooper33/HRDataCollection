import asyncio
import time
import matplotlib
matplotlib.use('TkAgg')  # Force TkAgg backend
from bleak import BleakClient
import signal
import csv

# Wahoo TICKR btle and  UUID
HRM_SERVICE_UUID = '0000180d-0000-1000-8000-00805f9b34fb'
HRM_CHAR_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

csv_file = "hrv_data.csv"
async def hr_data_handler(sender, data):
# gets the hr from the hr sensro incoming data
# checks the "flag" byte to see if the hr is stored in one or two
# bytes and reads in the appropriate byte
    flag = data[0]
    hr_value = data[1]  # Heart rate value seems to be the second byte

    print(f"Heart Rate: {hr_value} bpm")  # Print the HR value each time it's read
# gets the rr from the 2nd byte
    rr_intervals = []
    if flag & 0x10:
        rr_bytes = data[2:]
        for i in range(0, len(rr_bytes), 2):
            rr_interval = int.from_bytes(rr_bytes[i:i+2], byteorder='little') / 1000.0
            rr_intervals.append(rr_interval)

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        for rr in rr_intervals:
            writer.writerow([time.time(), hr_value, rr])

async def run_client(device_address):
    #connects to the hr sensor
    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print("Failed to connect")
            return
        await client.start_notify(HRM_CHAR_UUID, hr_data_handler)
        print("Collecting data, press Ctrl+C to stop...")

        # Signal handling for Windows
        def signal_handler(sig, frame):
            print("\nStopping data collection...")
            asyncio.create_task(stop_and_exit(client))
#need to fix the quit on cntrl c but it works without
        signal.signal(signal.SIGINT, signal_handler)

        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await client.stop_notify(HRM_CHAR_UUID)

#stop the connection and process the data
async def stop_and_exit(client):
    await client.stop_notify(HRM_CHAR_UUID)

#get the adress from the Scanner file
# my wahoo tickr is 40ED4EEF-107E-2438-6DC1-8C57CCE2563A
async def main():
    """Runs the Bluetooth client."""
    device_address = input("Enter HR address: ")
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Heart Rate", "RR Interval"])  # CSV Header
    await run_client(device_address)


if __name__ == "__main__":
    asyncio.run(main())