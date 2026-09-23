from machine import Pin, I2C
from utime import sleep_ms

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_ADDR = 0x27

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


def main():
    lcd = LCD(LCD_ADDR)
    counter = 0
    
    while True:
        lcd.clear()
        lcd.write("Hello World", 0)
        lcd.write(f"Count: {counter}", 1)
        
        counter += 1
        sleep_ms(1000)


if __name__ == "__main__":
    main()