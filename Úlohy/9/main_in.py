from machine import Pin, UART
from utime import sleep_ms

# UART1: TX=Pin4, RX=Pin5
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
led = Pin(0, Pin.OUT)
led.off()

def main():
    print("IN: LED control started, waiting for commands...")
    buffer = ""
    
    while True:
        if uart.any():
            # Read available data
            data = uart.read()
            if data:
                buffer += data.decode('utf-8', errors='ignore')
                
                # Process complete messages (ending with newline)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    message = message.strip()
                    
                    if message == '0':
                        led.on()
                        print("IN: LED ON")
                    elif message == '1':
                        led.off()
                        print("IN: LED OFF")
                    else:
                        print(f"IN: Unknown command: {message}")
        
        sleep_ms(50)

if __name__ == "__main__":
    main()