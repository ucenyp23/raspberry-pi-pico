from machine import Pin, UART
from utime import sleep_ms

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
led = Pin(4, Pin.OUT)
led.off()

def main():
    print("IN: Waiting for LED commands...")
    while True:
        if uart.any():
            data = uart.read()
            if data:
                message = data.decode().strip()
                if message == '0':
                    led.on()
                    print("IN: LED ON")
                elif message == '1':
                    led.off()
                    print("IN: LED OFF")
        sleep_ms(50)

if __name__ == "__main__":
    main()