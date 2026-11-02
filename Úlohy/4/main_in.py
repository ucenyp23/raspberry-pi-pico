import machine
from machine import mem32

# input

bus = machine.UART(1, 9600, tx=machine.Pin(4), rx=machine.Pin(5))
bus.init(9600, bits=8, parity=None, stop=1)

# output

led = machine.Pin(1, machine.Pin.OUT)
mem32[0x4001c00c] = mem32[0x4001c00c] & (~0b0110000) # selects the 2mA option with translates into an internal 100ohm resistor

while True:
    state = bus.read(1)
    if state is None:
        continue

    print(state)
    led.value(state == b'0')