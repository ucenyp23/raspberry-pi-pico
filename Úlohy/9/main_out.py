from machine import Pin, UART
from utime import sleep_ms

# UART1: TX=Pin4, RX=Pin5
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
button = Pin(0, Pin.IN, Pin.PULL_UP)

def main():
    print("OUT: Button monitoring started...")
    previous_state = None
    
    while True:
        current_state = button.value()
        
        # Send only when state changes
        if current_state != previous_state:
            message = f"{current_state}\n"
            uart.write(message.encode())
            print(f"OUT: Sent {current_state}")
            previous_state = current_state
        
        sleep_ms(50)

if __name__ == "__main__":
    main()