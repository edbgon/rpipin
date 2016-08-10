#!/usr/bin/python3
#################################################################################
#
# Copyright (c) 2016 Eric Samuelson
# RpiPin by Eric Samuelson
# Currently in extreme beta/experimentation stages
# I wouldn't expect this to be used by anyone, but if so, please let me know 
# on github! 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#################################################################################

import math
import os

#################################################################################
# Sound library that will only load sounds once and keep in memory
#################################################################################
_sound_library = {}
def play_sound(pygame, wpath):
  global _sound_library
  wpath = 'audio/sounds/' + wpath + '.wav'
  if(os.path.isfile(wpath) != True): return
  sound = _sound_library.get(wpath)
  if sound == None:
    try:
       sound = pygame.mixer.Sound(wpath)
       _sound_library[wpath] = sound
    except:
      return
  sound.play()

#################################################################################
# Timed Event Class
#################################################################################
class tEvent:
  def __init__(self):
    self.initTick = 0
    self.started = "0"
    self.step = 0
    self.ledCol = [255, 0, 0]
    self.ledA = 255
    self.ledBackup = []

  def elapsedTime(self, nowTick):
    "Returns elapsed time since the event was started"
    if(self.started != "0"):
      return nowTick - self.initTick
    else:
      return 0

  def start(self, initTick, tag="1"):
    "Starts an event. Use an optional tag to set a unique ID per event"
    if(self.started == "0"):
      self.initTick = initTick
      self.started = tag

  def stop(self):
    "Stops an event"
    if(self.started != "0"):
      self.started = "0"

  def reset(self, initTick):
    "Starts the event as if it was newly triggered"
    self.initTick = initTick

  def ledHeartbeat(self, time, led):
    "Simple led heartbeat animation that cycles through colors"
    self.start(time)
    etime = self.elapsedTime(time)
    if self.step == 0:
      self.ledCol[0] = 255
      self.ledCol[1] = 0
      self.ledCol[2] = 0
      self.ledA = 255
      self.step += 1
    if self.step == 1:
      self.ledCol[0] = 255 - int(etime / 10)
      self.ledCol[1] = int(etime / 10)
    if self.step == 2:
      self.ledCol[1] = 255 - int(etime / 10)
      self.ledCol[2] = int(etime / 10)
    if self.step == 3:
      self.ledCol[2] = 255 - int(etime / 10)
      self.ledCol[0] = int(etime / 10)
    if self.step == 4:
      self.step = 0
    if etime >= 2550:
      self.step += 1
      self.reset(time)
    self.ledA = math.sin(time / 1000 % 360) + 1
    for x in range(0, led.count):
      led.ledcolor(x, int(self.ledA * self.ledCol[0]), int(self.ledA * self.ledCol[1]), int(self.ledA * self.ledCol[2]))

  def ledChase(self, time, led):
    "Marquee style led chase, only shows red, green, and blue colors"
    self.start(time)
    etime = self.elapsedTime(time)
    if etime > 50:
      last = self.step - 1
      if last < 0: last = led.count
      led.ledcolor(self.step, *self.ledCol)
      led.ledcolor(last, 0, 0, 0)
      self.step += 1
      if self.step > led.count:
        self.step = 0
        self.ledCol = self.ledCol[1:] + self.ledCol[:1]
      self.reset(time)

  def ledFlash(self, time, led, duration, repetition, r, g, b, tag="1"):
    "Flashes all LEDs to given color for 'duration' ms long and for 'repetition' times" 
    if(self.started == "0"):
        self.ledBackup = led.getleds()
    self.start(time, tag=tag)
    etime = self.elapsedTime(time)
    if math.floor(etime / duration) % 2 == 0:
      for x in range(0, led.count):
        led.ledcolor(x, r, g, b)
        self.step = 0
    else:
      if self.step == 0:
        for x in range(0, led.count):
          led.ledcolor(x, 0, 0, 0)
        self.step = 1
    if etime > (duration * repetition * 2) + duration:
      led.setstrip(self.ledBackup)
      self.stop()


  def binCount(self, time, led):
    "Binary counter LED animation. Counts up to whatever binary number your maximum amount of LEDs is."
    self.start(time)
    etime = self.elapsedTime(time)
    if etime > 200:
      ledList = list(bin(self.step)[2:].zfill(led.count))
      for x in range(len(ledList)):
        if ledList[x] == '1':
          led.ledcolor(x, *self.ledCol)
        else:
          led.ledcolor(x, 0, 0, 0)
      self.step += 1
      if self.step > (2 ** led.count):
        self.step = 0
        for x in range(0, led.count): led.ledcolor(x, 0, 0, 0)
        self.ledCol = self.ledCol[1:] + self.ledCol[:1]
      self.reset(time)

  def triggerSolenoid(self, time, io, pin, duration=100, tag="1"):
    "Triggers a solenoid for 'duration' milliseconds"
    self.start(time, tag)
    etime = self.elapsedTime(time)
    if etime < duration:
      io.pinout(pin, True)
    elif etime < (duration + io.debounce_time):
      io.pinout(pin, False)
    else:
      self.stop()

  def loadBall(self, time, pygame, score):
    "Testing the timed event system. Will be used to load a ball in the future."
    self.start(time)
    self.elapsedTime(time)
    if self.elapsedTime(time) > 1000 and self.step == 0:
      play_sound(pygame, "arugh")
      self.step += 1
      self.reset(time)
    if self.elapsedTime(time) > 2000 and self.step == 1:
      play_sound(pygame, "arugh")
      self.step += 1
      self.reset(time)
    if self.elapsedTime(time) > 2000 and self.step == 2:
      play_sound(pygame, "loser")
      score.modscore(100)
      self.step = 0
      self.stop()