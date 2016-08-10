#!/usr/bin/python3

import neopixel

class ws2812:
  def __init__(self, led_count, led_brightness, led_pin, led_frequency, led_dma, led_invert):
    self.strip = neopixel.Adafruit_NeoPixel(led_count, led_pin, led_frequency, led_dma, led_invert, led_brightness)
    self.count = led_count
    self.strip.begin()

  def ledcolor(self, i, r, g, b):
    if r > 255: r = 255
    if g > 255: g = 255
    if b > 255: b = 255
    if r < 0: r = 0
    if g < 0: g = 0
    if b < 0: b = 0
    color = neopixel.Color(r, g, b)
    self.strip.setPixelColor(i, color)
    self.strip.show()

  def setstrip(self, data):
    for i in range(0, self.count):
      self.strip.setPixelColor(i, data[i])
    self.strip.show()

  def getleds(self):
    ledList = []
    for i in range(0, self.count):
      ledList.append(self.strip.getPixelColor(i))
    return ledList

  def cleanup(self):
    for i in range(0, self.count):
      self.ledcolor(i, 0, 0, 0)