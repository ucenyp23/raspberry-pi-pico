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
        """Send byte to I2C"""
        i2c.writeto(self.addr, bytes([data]))
    
    def _pulse_enable(self, data):
        """Pulse enable pin"""
        self._write_i2c(data | 0x04)   # EN high (bit 2)
        sleep_ms(1)
        self._write_i2c(data & ~0x04)  # EN low
        sleep_ms(1)
    
    def _write_nibble(self, nibble, rs=0):
        """Write 4-bit nibble
        Bit mapping: [DB7 DB6 DB5 DB4 BL RW E RS]
                      7   6   5   4   3  1 2 0
        """
        backlight = 0x08  # Bit 3
        rw = 0x00         # Bit 1 = 0 for write (explicit)
        data = (nibble & 0xF0) | backlight | rw | (rs & 0x01)
        self._pulse_enable(data)
    
    def _write_byte(self, byte, rs=0):
        """Write 8-bit byte in 4-bit mode"""
        self._write_nibble(byte & 0xF0, rs)        # High nibble
        self._write_nibble((byte << 4) & 0xF0, rs) # Low nibble
        sleep_ms(1)
    
    def _init_display(self):
        """Initialize LCD in 4-bit mode"""
        sleep_ms(50)
        
        # Step 1-3: Set to 8-bit mode (3 times for safety)
        self._write_nibble(0x30)
        sleep_ms(10)
        self._write_nibble(0x30)
        sleep_ms(10)
        self._write_nibble(0x30)
        sleep_ms(10)
        
        # Step 4: Switch to 4-bit mode
        self._write_nibble(0x20)
        sleep_ms(10)
        
        # Step 5+: Full 4-bit commands
        self._write_byte(0x28)  # 4-bit, 2 lines, 5x8 font
        sleep_ms(5)
        self._write_byte(0x0C)  # Display ON, cursor OFF, blink OFF
        sleep_ms(5)
        self._write_byte(0x01)  # Clear display
        sleep_ms(10)
        self._write_byte(0x06)  # Entry mode: increment, no shift
        sleep_ms(5)
    
    def clear(self):
        self._write_byte(0x01)
        sleep_ms(2)
    
    def write(self, text, line=0):
        """Write text to LCD"""
        if line == 0:
            self._write_byte(0x80)  # Line 1 (address 0x00)
        else:
            self._write_byte(0xC0)  # Line 2 (address 0x40)
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
        print(f"Display: Hello World | Count: {counter}")
        
        counter += 1
        sleep_ms(1000)


if __name__ == "__main__":
    main()