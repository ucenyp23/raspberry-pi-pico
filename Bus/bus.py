from machine import Pin, I2C, SPI
from utime import sleep_ms

i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400000
)
LCD_ADDR = 0x27
spi = SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(2),
    mosi=Pin(3)
)
max_cs = Pin(5, Pin.OUT, value=1)

class LCD:
    def __init__(self, addr):
        self.addr = addr
        sleep_ms(500)
        self._init_display()

    def _write_i2c(self, data):
        i2c.writeto(self.addr, bytes([data]))

    def _pulse_enable(self, data):
        self._write_i2c(data | 0x04)
        sleep_ms(1)
        self._write_i2c(data & ~0x04)
        sleep_ms(1)

    def _write_nibble(self, nibble, rs=0):
        backlight = 0x08
        rw = 0x00
        data = (nibble & 0xF0) | backlight | rw | (rs & 0x01)
        self._pulse_enable(data)

    def _write_byte(self, byte, rs=0):
        self._write_nibble(byte & 0xF0, rs)
        self._write_nibble((byte << 4) & 0xF0, rs)
        sleep_ms(1)

    def _init_display(self):
        sleep_ms(50)
        self._write_nibble(0x30)
        sleep_ms(10)
        self._write_nibble(0x30)
        sleep_ms(10)
        self._write_nibble(0x30)
        sleep_ms(10)
        self._write_nibble(0x20)
        sleep_ms(10)
        self._write_byte(0x28)
        sleep_ms(5)
        self._write_byte(0x0C)
        sleep_ms(5)
        self._write_byte(0x01)
        sleep_ms(10)
        self._write_byte(0x06)
        sleep_ms(5)

    def clear(self):
        self._write_byte(0x01)
        sleep_ms(2)

    def write(self, text, line=0):
        if line == 0:
            self._write_byte(0x80)
        else:
            self._write_byte(0xC0)
        sleep_ms(2)
        for char in text[:16]:
            self._write_byte(ord(char), rs=1)
            sleep_ms(1)

class MAX7219:
    def __init__(self, spi, cs, intensity=3):
        self.spi = spi
        self.cs = cs
        self._write_register(0x09, 0x00)
        self._write_register(0x0A, intensity)
        self._write_register(0x0B, 0x07)
        self._write_register(0x0C, 0x01)
        self._write_register(0x0F, 0x00)
        self.clear()

    def _write_register(self, register, value):
        self.cs.value(0)
        self.spi.write(bytes([register, value]))
        self.cs.value(1)

    def clear(self):
        for row in range(1, 9):
            self._write_register(row, 0x00)

    def show_digit(self, digit):
        digits = {
            0: (
                0b00111100,
                0b01100110,
                0b01101110,
                0b01110110,
                0b01100110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
            1: (
                0b00011000,
                0b00111000,
                0b00011000,
                0b00011000,
                0b00011000,
                0b00011000,
                0b01111110,
                0b00000000,
            ),
            2: (
                0b00111100,
                0b01100110,
                0b00000110,
                0b00001100,
                0b00110000,
                0b01100000,
                0b01111110,
                0b00000000,
            ),
            3: (
                0b00111100,
                0b01100110,
                0b00000110,
                0b00011100,
                0b00000110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
            4: (
                0b00001100,
                0b00011100,
                0b00101100,
                0b01001100,
                0b01111110,
                0b00001100,
                0b00001100,
                0b00000000,
            ),
            5: (
                0b01111110,
                0b01100000,
                0b01100000,
                0b00111100,
                0b00000110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
            6: (
                0b00111100,
                0b01100110,
                0b01100000,
                0b01111100,
                0b01100110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
            7: (
                0b01111110,
                0b00000110,
                0b00001100,
                0b00011000,
                0b00110000,
                0b00110000,
                0b00110000,
                0b00000000,
            ),
            8: (
                0b00111100,
                0b01100110,
                0b01100110,
                0b00111100,
                0b01100110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
            9: (
                0b00111100,
                0b01100110,
                0b01100110,
                0b00111110,
                0b00000110,
                0b01100110,
                0b00111100,
                0b00000000,
            ),
        }
        pattern = digits.get(digit, digits[0])
        for row, data in enumerate(pattern, start=1):
            self._write_register(row, data)

def main():
    lcd = LCD(LCD_ADDR)
    matrix = MAX7219(spi, max_cs, intensity=3)
    counter = 0
    while True:
        lcd.clear()
        lcd.write("Hello World", 0)
        lcd.write("Count: {}".format(counter), 1)
        matrix.show_digit(counter % 10)
        counter += 1
        sleep_ms(1000)

if __name__ == "__main__":
    main()