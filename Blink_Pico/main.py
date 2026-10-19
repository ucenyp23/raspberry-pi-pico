from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

def main():
    while True:
        pin.toggle()
        sleep(1)

if __name__ == '__main__':
    main()
