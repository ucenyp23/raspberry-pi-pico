import network
import socket
from machine import Pin
from utime import sleep_ms

SSID = "access_point"
PASSWORD = "12345678"
RECEIVER_IP = "192.168.4.1"
RECEIVER_PORT = 5000

button = Pin(0, Pin.IN, Pin.PULL_UP)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

timeout = 100
while not wlan.isconnected() and timeout > 0:
    sleep_ms(100)
    timeout -= 1

if not wlan.isconnected():
    print("Wi-Fi connection failed")
    print("Status:", wlan.status())
    raise RuntimeError("Could not connect to access point")

print("Sender IP:", wlan.ifconfig())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

previous_state = None

while True:
    current_state = button.value()

    if current_state != previous_state:
        message = str(current_state).encode()
        sock.sendto(message, (RECEIVER_IP, RECEIVER_PORT))
        print("Sent:", message)
        previous_state = current_state

    sleep_ms(50)