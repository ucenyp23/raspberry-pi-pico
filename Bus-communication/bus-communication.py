from machine import Pin, UART
from utime import sleep_ms

uart = UART(1, baudrate=9600, tx=Pin(6), rx=Pin(7))
button = Pin(0, Pin.IN, Pin.PULL_UP)

def main():
    previous_state = None
    
    while True:
        current_state = button.value()
        
        if current_state != previous_state:
            uart.write(str(current_state))
            previous_state = current_state
        
        sleep_ms(50)

if __name__ == "__main__":
    main()