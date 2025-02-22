'''scans for heart strap signals'''
import asyncio
from bleak import BleakClient

async def raw_data_handler(sender, data):
    print(f"Raw Data from {sender}: {data}")

async def run_client(device_address):
    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print("Failed to connect")
            return

        print("Connected! Scanning for services and characteristics...")

        UUID = " a026e004-0a7d-4ab3-97fa-f1500f9feb8b"
        await client.start_notify(UUID, raw_data_handler)

        print("Collecting data, press Ctrl+C to stop...")

        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await client.stop_notify(UUID)

async def main():

    device_address = input("Enter your Wahoo TICKR Bluetooth address: ")
    await run_client(device_address)
#40ED4EEF-107E-2438-6DC1-8C57CCE2563A
if __name__ == "__main__":
    asyncio.run(main())
