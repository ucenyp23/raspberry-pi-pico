from gpiozero import PWMLED
from time import sleep
 
led = PWMLED(18)
 
for i in range(0, 101):
    led.value = i / 100
    sleep(0.01)
led.pulse(fade_in_time=1, fade_out_time=1)
