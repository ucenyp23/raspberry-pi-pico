from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

def main():
    while True:
        try:
            pin.toggle()
            sleep(1) # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()

if __name__ == '__main__':
    main()