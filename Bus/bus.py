from machine import Pin, I2C
from utime import sleep_ms

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_ADDR = 0x27

class LCD:
    def __init__(self, addr):
        self.addr = addr
        self.backlight = 0x08
        sleep_ms(100)
        self._init_display()
    
    def _write_nibble(self, nibble):
        """Write a 4-bit nibble to LCD"""
        val = (nibble & 0xF0) | self.backlight
        i2c.writeto(self.addr, bytes([val | 0x04]))  # EN high
        sleep_ms(1)
        i2c.writeto(self.addr, bytes([val & ~0x04]))  # EN low
        sleep_ms(1)
    
    def _write_byte(self, byte, mode=0):
        """Write 8-bit data (mode=0 for command, mode=1 for data)"""
        if mode:
            byte |= 0x01  # RS=1 for data
        else:
            byte &= ~0x01  # RS=0 for command
        
        self._write_nibble(byte & 0xF0)      # High nibble
        self._write_nibble((byte << 4) & 0xF0)  # Low nibble
    
    def _init_display(self):
        """Initialize LCD in 4-bit mode"""
        self._write_byte(0x33)  # Function set
        sleep_ms(5)
        self._write_byte(0x32)  # 4-bit mode
        sleep_ms(5)
        self._write_byte(0x28)  # 2 lines, 5x8 dots
        sleep_ms(5)
        self._write_byte(0x0C)  # Display on, cursor off
        sleep_ms(5)
        self._write_byte(0x01)  # Clear display
        sleep_ms(5)
        print("LCD initialized!")
    
    def clear(self):
        self._write_byte(0x01)
        sleep_ms(2)
    
    def write(self, text, line=0):
        """Write text to LCD. line: 0 or 1"""
        if line == 0:
            self._write_byte(0x80)  # Line 1
        else:
            self._write_byte(0xC0)  # Line 2
        sleep_ms(2)
        
        for char in text[:16]:
            self._write_byte(ord(char), mode=1)
            sleep_ms(1)

# Initialize LCD
lcd = LCD(LCD_ADDR)

# Test
counter = 0
while True:
    lcd.clear()
    lcd.write("Hello World", 0)
    lcd.write(f"Count: {counter}", 1)
    print(f"Line 1: Hello World | Line 2: Count: {counter}")
    
    counter += 1
    sleep_ms(1000)
