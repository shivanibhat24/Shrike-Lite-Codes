from machine import Pin, PWM
import utime

# -------- CONFIG --------
IR_PIN = 27
BUZZER_PIN = 18

ir = Pin(IR_PIN, Pin.IN)
buzzer = PWM(Pin(BUZZER_PIN))

# Notes (Hz)
notes = {
    "C": 262,
    "D": 294,
    "E": 330,
    "G": 392,
    "A": 440
}

# -------- PLAY NOTE --------
def play(freq, duration=200):
    buzzer.freq(freq)
    buzzer.duty_u16(30000)
    utime.sleep_ms(duration)
    buzzer.duty_u16(0)

# -------- GESTURE DETECTION --------
last_trigger = 0
tap_count = 0
start_time = 0
holding = False

print("🎹 Air Piano Ready!")

while True:
    state = ir.value()

    # -------- HAND DETECTED --------
    if state == 0:
        if not holding:
            holding = True
            start_time = utime.ticks_ms()

    # -------- HAND REMOVED --------
    if state == 1 and holding:
        duration = utime.ticks_diff(utime.ticks_ms(), start_time)
        holding = False

        now = utime.ticks_ms()

        # Check for double tap
        if utime.ticks_diff(now, last_trigger) < 400:
            tap_count += 1
        else:
            tap_count = 1

        last_trigger = now

        # -------- CLASSIFY GESTURE --------
        if tap_count == 2:
            print("Double Tap → G")
            play(notes["G"])
            tap_count = 0

        elif duration < 200:
            print("Quick Tap → C")
            play(notes["C"])

        elif duration < 600:
            print("Medium Hold → D")
            play(notes["D"])

        elif duration < 1200:
            print("Long Hold → E")
            play(notes["E"])

        else:
            print("Very Long → A")
            play(notes["A"])

    utime.sleep_ms(10)

