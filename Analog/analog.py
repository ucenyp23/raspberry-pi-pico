from machine import Pin, ADC, PWM
from utime import sleep_ms

adc = ADC(Pin(26))
led = PWM(Pin(0))
led.freq(1000)

def main():
    while True:
        adc_value = adc.read_u16()
        
        led.duty_u16(adc_value)
        
        sleep_ms(100)

if __name__ == '__main__':
    main()