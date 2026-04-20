#!/usr/bin/env python3
"""
Chained-strip test (single data line on GPIO18):
- First segment: all white
- Second segment: all green

Hardware: two BTF-LIGHTING WS2812B strips end-to-end (e.g., 300 + 300 pixels) on one data line.
"""
import time
from rpi_ws281x import Adafruit_NeoPixel, Color
import sys

SEGMENT1_COUNT = 600
SEGMENT2_COUNT =300
TOTAL_PIXELS = SEGMENT1_COUNT + SEGMENT2_COUNT

PIN = 18           # PWM0, physical pin 12
FREQ = 800000
DMA = 10
BRIGHTNESS = 96    # bump a bit for visibility
INVERT = False
CHANNEL = 0

def fill_strip(strip: Adafruit_NeoPixel, start: int, end: int, color: Color):
    for i in range(start, end):
        strip.setPixelColor(i, color)
    strip.show()

def main():
    strip = Adafruit_NeoPixel(
        TOTAL_PIXELS,
        PIN,
        FREQ,
        DMA,
        INVERT,
        BRIGHTNESS,
        CHANNEL,
    )

    try:
        strip.begin()
    except RuntimeError as exc:  # Likely permissions (/dev/mem) when not run as root
        sys.stderr.write("Error initializing strips: {}\n".format(exc))
        sys.stderr.write("Tip: run with sudo (access to /dev/mem) or rebuild rpi_ws281x with gpiomem support.\n")
        sys.exit(1)

    try:
        print("Light test: first {} pixels white, next {} pixels green on GPIO18.".format(SEGMENT1_COUNT, SEGMENT2_COUNT))
        fill_strip(strip, 0, SEGMENT1_COUNT, Color(255, 255, 255))
        fill_strip(strip, SEGMENT1_COUNT, SEGMENT1_COUNT + SEGMENT2_COUNT, Color(0, 255, 0))
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Clearing both strips...")
        fill_strip(strip, 0, strip.numPixels(), Color(0, 0, 0))

if __name__ == "__main__":
    main()
