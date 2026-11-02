import machine
import network
import socket
import time

from machine import mem32

wlan = network.WLAN(network.STA_IF)

ssid = "Redmi"
cred = "redmitether"

# net init

# Micropython AP mode just no work
#wlan.config(ssid=ssid, key=cred)
#wlan.active(True)

#while wlan.active() == False:
#    pass

#print(f"AP initialized, ifconfig: {wlan.ifconfig()}")

wlan.active(True)
wlan.connect(ssid, cred)

print("connecting to AP", end="")
for i in range(5):
    print('.', end='')

    if wlan.status() < 0 or wlan.status() >= 3:
        break

    time.sleep(1)

print()

if wlan.status() != network.STAT_GOT_IP:
    raise RuntimeError(f"failed to connect to AP, wlan status: {wlan.status()}")

print(f"connection successful (ip: {wlan.ifconfig()[0]} RSSI: {wlan.status('rssi')})")

# output

led = machine.Pin(1, machine.Pin.OUT)
mem32[0x4001c00c] = mem32[0x4001c00c] & (~0b0110000) # selects the 2mA option with translates into an internal 100ohm resistor

# UDP socket comms

addr = ('0.0.0.0', 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(addr)

while True:
    buf, addr = sock.recvfrom(256)

    if buf == b'To who It may consern, please set your Light Emitting Diode to the on state.':
        led.value(1)
    elif buf == b'To who It may consern, please when most convinient turn your Light Emitting Diode to the off state.':
        led.value(0)
    else:
        print("In all respect, I must ignore the request as I regretfully cannot parse it. Please, when most convinient, try again.")
        sock.sendto(b'In all respect, I must ignore the request as I regretfully cannot parse it. Please, when most convinient, try again.', addr)

    time.sleep(5)