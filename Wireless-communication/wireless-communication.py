import network
import socket
from machine import Pin
from utime import sleep_ms

SSID = "your_wifi_name"
PASSWORD = "your_wifi_password"
RECEIVER_IP = "192.168.1.100"
RECEIVER_PORT = 5000

button = Pin(0, Pin.IN, Pin.PULL_UP)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    sleep_ms(100)
print(f"IP: {wlan.ifconfig()[0]}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def main():
    previous_state = None
    
    while True:
        current_state = button.value()
        
        if current_state != previous_state:
            message = str(current_state)
            sock.sendto(message.encode(), (RECEIVER_IP, RECEIVER_PORT))
            previous_state = current_state
        
        sleep_ms(50)

if __name__ == "__main__":
    main()