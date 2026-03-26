#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example. 
# https://github.com/rpi-ws281x/rpi-ws281x-python/tree/master
# Showcases various animations on a strip of NeoPixels.

#wiring diagram https://tutorials-raspberrypi.de/wp-content/uploads/Raspberry-Pi-WS2812-Steckplatine-600x361.png

import time
from datetime import date
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 600     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 30     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


def C(r, g, b):
    """Convenience helper for creating Color values."""
    return Color(int(r), int(g), int(b))

# Commonly used colors (kept near the top for easy tweaks).
RED = C(255, 0, 0)
DEEP_RED = C(127, 0, 0)
GREEN = C(0, 255, 0)
BLUE = C(0, 0, 255)
DEEP_BLUE = C(0, 0, 127)
AQUA = C(0, 255, 255)
GOLD = C(255, 215, 0)
PURPLE = C(128, 0, 128)
WHITE = C(127, 127, 127)
ORANGE = C(255, 165, 0)


def apply_palette(overrides):
    """Update global color constants from an overrides dict of name -> (r, g, b)."""
    if not overrides:
        return
    for name, rgb in overrides.items():
        if name in globals():
            globals()[name] = C(*rgb)

def _fourth_thursday(year, month):
    """Return the day number of the fourth Thursday for the given month/year."""
    first = date(year, month, 1)
    offset = (3 - first.weekday() + 7) % 7  # Thursday is 3 when Monday is 0
    return 1 + offset + 21  # fourth Thursday

def detect_holiday_palette(today=None):
    """Return (holiday_name, palette_overrides) for major US holidays if matched."""
    today = today or date.today()
    y, m, d = today.year, today.month, today.day

    thanksgiving_day = _fourth_thursday(y, 11)
    memorial_last_monday = max(day for day in range(25, 32) if date(y, 5, day).weekday() == 0)
    labor_first_monday = next(day for day in range(1, 8) if date(y, 9, day).weekday() == 0)

    holidays = [
        ("New Year's Day", lambda mm, dd: mm == 1 and dd == 1, {
            'RED': (255, 80, 80),
            'GREEN': (240, 240, 240),
            'BLUE': (80, 80, 255),
            'GOLD': (255, 215, 120),
        }),
        ("New Year's Eve", lambda mm, dd: mm == 12 and dd == 31, {
            'RED': (200, 60, 60),
            'GOLD': (255, 230, 140),
            'WHITE': (245, 245, 245),
            'BLUE': (70, 90, 160),
        }),
        ("Valentine's Day", lambda mm, dd: mm == 2 and dd == 14, {
            'RED': (255, 60, 120),
            'WHITE': (255, 230, 240),
            'PURPLE': (200, 80, 200),
        }),
        ("Cinco de Mayo", lambda mm, dd: mm == 5 and dd == 5, {
            'RED': (210, 30, 30),
            'WHITE': (245, 245, 245),
            'GREEN': (0, 180, 60),
            'GOLD': (255, 200, 80),
        }),
        ("Memorial Day", lambda mm, dd: mm == 5 and dd == memorial_last_monday, {
            'RED': (180, 30, 30),
            'WHITE': (235, 235, 235),
            'BLUE': (40, 70, 140),
        }),
        ("St. Patrick's Day", lambda mm, dd: mm == 3 and dd == 17, {
            'GREEN': (0, 255, 80),
            'GOLD': (255, 200, 40),
            'WHITE': (80, 160, 80),
        }),
        ("Independence Day", lambda mm, dd: mm == 7 and dd == 4, {
            'RED': (255, 0, 40),
            'WHITE': (255, 255, 255),
            'BLUE': (0, 60, 200),
        }),
        ("Labor Day", lambda mm, dd: mm == 9 and dd == labor_first_monday, {
            'ORANGE': (230, 140, 40),
            'AQUA': (0, 180, 180),
            'GOLD': (255, 200, 120),
            'WHITE': (230, 230, 230),
        }),
        ("Veteran's Day", lambda mm, dd: mm == 11 and dd == 11, {
            'RED': (170, 20, 40),
            'WHITE': (240, 240, 240),
            'BLUE': (20, 50, 110),
            'GOLD': (200, 170, 80),
        }),
        ("Halloween", lambda mm, dd: mm == 10 and dd == 31, {
            'ORANGE': (255, 120, 0),
            'PURPLE': (160, 0, 200),
            'GREEN': (0, 160, 0),
        }),
        ("Birthday", lambda mm, dd: (mm, dd) in {(1, 8), (10, 29)}, {
            'RED': (255, 105, 180),
            'BLUE': (80, 180, 255),
            'GOLD': (255, 220, 120),
            'WHITE': (245, 245, 245),
        }),
        ("Thanksgiving", lambda mm, dd: mm == 11 and thanksgiving_day - 1 <= dd <= thanksgiving_day + 1, {
            'ORANGE': (220, 120, 40),
            'GOLD': (255, 200, 90),
            'RED': (160, 60, 20),
            'GREEN': (80, 120, 40),
        }),
        ("Christmas", lambda mm, dd: mm == 12 and 18 <= dd <= 25, {
            'RED': (220, 30, 30),
            'GREEN': (0, 150, 60),
            'GOLD': (255, 215, 120),
            'WHITE': (230, 230, 230),
        }),
    ]

    for name, matcher, overrides in holidays:
        if matcher(m, d):
            return name, overrides
    return None, {}


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=10):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorWipeReverse(strip, color, wait_ms=5):
    """Wipe color across display a pixel at a time."""
    for i in reversed(range(strip.numPixels())):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseReverse(strip, color, wait_ms=25, iterations=50):
    """Movie theater light style chaser animation."""
    for j in reversed(range(iterations)):
        for q in reversed(range(3)):
            for i in reversed(range(0, strip.numPixels(), 3)):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in reversed(range(0, strip.numPixels(), 3)):
                strip.setPixelColor(i+q, 0)

def theaterChase(strip, color, wait_ms=25, iterations=50):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=150):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def _run_steps(strip, steps):
    """Execute a list of (callable, args, kwargs) animation steps."""
    for fn, args, kwargs in steps:
        fn(strip, *args, **kwargs)

def _color_from_tuple(rgb):
    """Clamp an (r, g, b) tuple to the valid range and return a Color."""
    r, g, b = rgb
    return Color(max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))

def spinningReels(strip, reel_pixels=None, lit_span=12, laps=2, wait_ms=8, reverse=False, accent=(255, 180, 60), frame_color=(5, 5, 5)):
    """Spin a warm block around the reel segment while keeping the cabinet softly lit."""
    total = strip.numPixels()
    reel_pixels = reel_pixels or total // 2
    reel_pixels = max(1, min(reel_pixels, total))
    frame_start = reel_pixels
    lit_span = max(1, min(lit_span, reel_pixels))

    frame_fill = _color_from_tuple(frame_color)
    for i in range(frame_start, total):
        strip.setPixelColor(i, frame_fill)

    previous = []
    for step in range(reel_pixels * laps):
        head = step % reel_pixels
        if reverse:
            head = reel_pixels - 1 - head

        for idx in previous:
            strip.setPixelColor(idx, 0)

        block = [(head + offset) % reel_pixels for offset in range(lit_span)]
        accent_color = _color_from_tuple(accent)
        for idx in block:
            strip.setPixelColor(idx, accent_color)

        previous = block
        strip.show()
        time.sleep(wait_ms / 1000.0)

    for idx in previous:
        strip.setPixelColor(idx, 0)
    strip.show()

def cabinetPulse(strip, reel_pixels=None, frame_color=(0, 120, 255), cycles=3, step_ms=15, floor_color=(0, 0, 15)):
    """Breathe the cabinet outline while leaving the reel dimly visible."""
    total = strip.numPixels()
    reel_pixels = reel_pixels or total // 2
    reel_pixels = max(1, min(reel_pixels, total))
    frame_start = reel_pixels
    steps = list(range(0, 256, 6)) + list(range(255, -1, -6))

    floor = _color_from_tuple(floor_color)
    for i in range(0, reel_pixels):
        strip.setPixelColor(i, floor)

    for _ in range(cycles):
        for level in steps:
            scaled = (
                frame_color[0] * level / 255.0,
                frame_color[1] * level / 255.0,
                frame_color[2] * level / 255.0,
            )
            scaled_color = _color_from_tuple(scaled)
            for i in range(frame_start, total):
                strip.setPixelColor(i, scaled_color)
            strip.show()
            time.sleep(step_ms / 1000.0)

    for i in range(frame_start, total):
        strip.setPixelColor(i, floor)
    strip.show()

def spliceRunner(strip, reel_pixels=None, block_size=10, wait_ms=10, cycles=2, head_color=(255, 60, 0), frame_color=(0, 150, 255)):
    """Send a bright block from reel to cabinet, fading as it travels the full length."""
    total = strip.numPixels()
    reel_pixels = reel_pixels or total // 2
    reel_pixels = max(1, min(reel_pixels, total))
    block_size = max(1, block_size)
    previous = []

    for step in range(total * cycles):
        head = step % total
        for idx in previous:
            strip.setPixelColor(idx, 0)

        block = [((head - offset) + total) % total for offset in range(block_size)]
        for offset, idx in enumerate(block):
            fade = 1.0 - (offset / block_size)
            target = head_color if idx < reel_pixels else frame_color
            scaled = (
                target[0] * fade,
                target[1] * fade,
                target[2] * fade,
            )
            strip.setPixelColor(idx, _color_from_tuple(scaled))

        previous = block
        strip.show()
        time.sleep(wait_ms / 1000.0)

    for idx in previous:
        strip.setPixelColor(idx, 0)
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        holiday_name, palette = detect_holiday_palette()
        if holiday_name:
            apply_palette(palette)
            print(f"Holiday palette active: {holiday_name}")
        else:
            print('Using default palette.')

        color_and_chase = [
            (colorWipe, (RED,), {'wait_ms': 10}),
            (theaterChase, (DEEP_RED,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChaseReverse, (DEEP_RED,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipeReverse, (BLUE,), {'wait_ms': 5}),
            (colorWipe, (GOLD,), {'wait_ms': 10}),
            (theaterChaseReverse, (GOLD,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (GOLD,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipeReverse, (PURPLE,), {'wait_ms': 5}),
            (colorWipe, (WHITE,), {'wait_ms': 10}),
            (theaterChaseReverse, (WHITE,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipe, (BLUE,), {'wait_ms': 10}),
            (theaterChaseReverse, (BLUE,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (BLUE,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipe, (AQUA,), {'wait_ms': 10}),
            (theaterChase, (AQUA,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChaseReverse, (AQUA,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipe, (GREEN,), {'wait_ms': 10}),
            (theaterChase, (DEEP_BLUE,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChaseReverse, (DEEP_RED,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipe, (PURPLE,), {'wait_ms': 10}),
            (theaterChaseReverse, (PURPLE,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (PURPLE,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipe, (ORANGE,), {'wait_ms': 10}),
            (theaterChase, (ORANGE,), {'wait_ms': 25, 'iterations': 50}),
            (colorWipeReverse, (ORANGE,), {'wait_ms': 5}),
        ]

        theater_focus = [
            (theaterChase, (WHITE,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (ORANGE,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (DEEP_RED,), {'wait_ms': 25, 'iterations': 50}),
            (theaterChase, (DEEP_BLUE,), {'wait_ms': 25, 'iterations': 50}),
        ]

        rainbow_block = [
            (rainbow, tuple(), {'wait_ms': 20, 'iterations': 1}),
            (rainbowCycle, tuple(), {'wait_ms': 20, 'iterations': 5}),
            (theaterChaseRainbow, tuple(), {'wait_ms': 150}),
        ]

        reel_cabinet_block = [
            (spinningReels, tuple(), {'lit_span': 14, 'laps': 2, 'wait_ms': 6, 'accent': (255, 200, 90), 'frame_color': (10, 10, 10)}),
            (spliceRunner, tuple(), {'block_size': 12, 'wait_ms': 8, 'cycles': 2, 'head_color': (255, 80, 20), 'frame_color': (0, 160, 255)}),
            (cabinetPulse, tuple(), {'cycles': 2, 'step_ms': 12, 'frame_color': (0, 130, 255), 'floor_color': (0, 0, 12)}),
        ]

        while True:
            print('Color wipe and theater chase animations.')
            _run_steps(strip, color_and_chase)

            print('Theater chase animations.')
            _run_steps(strip, theater_focus)

            print('Rainbow animations.')
            _run_steps(strip, rainbow_block)

            print('Reel + cabinet animations.')
            _run_steps(strip, reel_cabinet_block)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)



