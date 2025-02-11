
import time
import serial
import matplotlib.pyplot as plt
from openant.easy.node import Node
from openant.easy.channel import Channel

USB_PORT = "" #when i get the ANT+ dongle it will go here

HRM_DEVICE_TYPE = 120  #120 is the hr sensor
HRM_CHANNEL_PERIOD = 8070  # standard ANT+ heart rate period
NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]  # public ANT+ network key

node = Node(serial_device=USB_PORT)
channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

channel.set_period(HRM_CHANNEL_PERIOD)
channel.set_search_timeout(255)
channel.set_rf_freq(57) #standard frequency
channel.set_network_key(0, NETWORK_KEY)
channel.set_id(0, HRM_DEVICE_TYPE, 0)

#array to store the hr data
heart_rate_data = []

#function to get the incoming data and store it
def store_data(data):
    hr_value = data[7]  # ANT+ HR data is in byte 7 of the incoming data
    heart_rate_data.append(hr_value)

channel.on_broadcast_data = store_data
channel.open()
node.start()
#continue the program until it is stoppped manually
while True:
    time.sleep(1)
#closes the connection
node.stop()