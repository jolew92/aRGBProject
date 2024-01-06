from machine import ADC, Pin
import time
from neopixel import Neopixel

# Ustawienia pinu, do którego jest podłączony mikrofon (analogowy)
mic_pin = 26  # Zmień na właściwy numer pinu

mic = ADC(Pin(mic_pin))

sample_window = 50  # 50 ms sample window width (20 Hz)

def measure_amplitude():
    start_millis = time.ticks_ms()
    signal_max = 0
    signal_min = 65535  # Początkowa wartość sygnału min

    while time.ticks_diff(time.ticks_ms(), start_millis) < sample_window:
        sample = mic.read_u16()
        
        if sample < 65535:
            if sample > signal_max:
                signal_max = sample
            elif sample < signal_min:
                signal_min = sample

    peak_to_peak = signal_max - signal_min
    volts = (peak_to_peak * 3.3) / 65536  # Konwersja na wolt

    return volts

onoff = True

numpix = 60
strip = Neopixel(numpix, 0, 28, "RGB")

red = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

# same colors as normal RGB, just 0 added at the end
colors_rgbw = [color + tuple([0]) for color in colors_rgb]
colors_rgbw.append((0, 0, 0, 255))

# uncomment colors_rgbw if you have RGBW strip
colors = colors_rgb
# colors = colors_rgbw

step = round(numpix / len(colors))
current_pixel = 0
strip.brightness(50)

def initialize_led_strip():
    global current_pixel
    current_pixel = 0  # Reset current_pixel to 0
    for color1, color2 in zip(colors, colors[1:]):
        strip.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
        current_pixel += step
    strip.set_pixel_line_gradient(current_pixel, numpix - 1, violet, red)

# Initialize LED strip initially
initialize_led_strip()

# Function to check clapping
def check_clap():
    threshold = 0.8  # Próg detekcji klaśnięcia w woltach
    clap_detected = False
    mic_voltage = measure_amplitude()

    if mic_voltage > threshold:
        print("Clap detected - Turning on")
        clap_detected = True
    else:
        print("No clap detected")

    return clap_detected

try:
    while True:
        if check_clap():
            time.sleep(0.3)
            if onoff == False: #if it was previously off then initilize again
                initialize_led_strip()
            else:
                strip.fill((0, 0, 0))
                strip.show()
                #print("reset")
                
            onoff = not onoff # change the statuss
        else:
            if onoff:
                #print("LED")
                strip.rotate_right(1)
                time.sleep(0.042)
                strip.show()

except KeyboardInterrupt:
    # Clean up resources if the user interrupts the program (Ctrl+C)
    strip.fill((0, 0, 0))
    strip.show()
    print("\nProgram terminated.")