#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

#wiring diagram https://tutorials-raspberrypi.de/wp-content/uploads/Raspberry-Pi-WS2812-Steckplatine-600x361.png

import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 300     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 80     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



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

        while True:
            print ('Color wipe and theater chase animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChaseReverse(strip, Color(127,   0,   0))  # Red reverse theater chase
            colorWipeReverse(strip, Color(0, 0, 255))  # blue reverse wipe
            colorWipe(strip, Color(255,215,0))  # Gold wipe
            theaterChaseReverse(strip, Color(255,215,0))  # Gold reverse theater chase
            theaterChase(strip, Color(255,215,0))  # Gold theater chase
            colorWipeReverse(strip, Color(128,0,128))  # Purple reverse wipe
            colorWipe(strip, Color(127, 127, 127))  # white wipe
            theaterChaseReverse(strip, Color(127, 127, 127))  # White theater chase
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            theaterChaseReverse(strip, Color(0, 0, 255))  # Green theater chase
            theaterChase(strip, Color(0, 0, 255))  # Green theater chase
            colorWipe(strip, Color(0,255,255))  # Aqua wipe
            theaterChase(strip, Color(0, 255, 255))  # Aqua theater chase
            theaterChaseReverse(strip, Color(0, 255, 255))  # Aqua theater chase
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            theaterChaseReverse(strip, Color(127,   0,   0))  # Red reverse theater chase
            colorWipe(strip, Color(128,0,128))  # Purple wipe
            theaterChaseReverse(strip, Color( 128,0,128))  # Purple theater chase
            theaterChase(strip, Color( 128,0,128))  # Purple theater chase
            colorWipe(strip, Color(255,165,0))  # Orange wipe
            theaterChase(strip, Color(255,165,0))  # Orange theater chase
            colorWipeReverse(strip, Color(255,165,0))  # Orange wipe
            print ('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            theaterChase(strip, Color(255,165,0))  # Orange theater chase
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
