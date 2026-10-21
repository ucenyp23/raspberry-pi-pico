from gpiozero import LED, Button
 
button = Button(27)
led = LED(17)
 
button.when_pressed = led.on
button.when_released = led.off
 
pause()