from machine import Pin
from utime import sleep_ms

button = Pin(1, Pin.IN, Pin.PULL_UP)
led = Pin(0, Pin.OUT)

def main():
    State = False
    
    while True:
        if button.value() == False:
            sleep_ms(100)
            
            if State == False:
                led.value(True)
                State = True
            else:
                led.value(False)
                State = False
            
            while button.value() == False:
                sleep_ms(20)

if __name__ == '__main__':
    main()
