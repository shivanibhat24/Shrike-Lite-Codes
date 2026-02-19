from machine import Pin
import utime

ir = Pin(27, Pin.IN)

start = 0
last_state = 1

while True:
    state = ir.value()

    if state == 0 and last_state == 1:
        start = utime.ticks_ms()

    if state == 1 and last_state == 0:
        duration = utime.ticks_diff(utime.ticks_ms(), start)

        speed = 1000 / (duration + 1)  # arbitrary scale
        print("Speed:", speed)

    last_state = state
    utime.sleep_ms(10)

