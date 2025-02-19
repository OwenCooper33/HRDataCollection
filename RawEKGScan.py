import asyncio
from bleak import BleakClient

async def scan_services(device_address):

    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print("Failed to connect")
            return

        print("Connected! Scanning for services and characteristics...\n")

        for service in client.services:
            print(f"Service: {service.uuid} | {service.description}")
            for char in service.characteristics:
                print(f"  └─ Characteristic: {char.uuid} | {char.description} | Properties: {char.properties}")

async def main():
    device_address = input("Enter your Wahoo TICKR Bluetooth address: ")
    await scan_services(device_address)

if __name__ == "__main__":
    asyncio.run(main())
