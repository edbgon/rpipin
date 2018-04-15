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
# Drop Target class
# Custom amount of drop targets and reset time
#################################################################################

class dropTarget:
  def __init__(self, minPin, maxPin, resetPin, pygame, solenoid, score, io, leds, restTime=2000, targetWorth=500, resetBonus=2000, ledTable=[0,1,2,3,4]):
    self.score = score
    self.io = io
    self.leds = leds
    self.pygame = pygame
    self.solenoid = solenoid

    self.minPin = minPin
    self.maxPin = maxPin
    self.resetPin = resetPin
    self.needReset = False
    self.rTime = 0
    self.ioRange = (maxPin - minPin) + 1
    self.targetTable = [False]*(self.maxPin + 1)
    self.ledTable = ledTable
    self.restTime = restTime
    self.targetWorth = targetWorth
    self.resetBonus = resetBonus

  def reset(self, time):
    if self.solenoid.started != "1":
      self.solenoid.triggerSolenoid(time, self.io, self.resetPin, duration=100, tag="1")

  def check(self, time):
    totalCheck = 0
    count = 0

    for x in range(self.minPin, self.maxPin + 1):
      if self.io.getpin(x, time=time, reqDebounce=True):
        if self.targetTable[x] is False:
          self.score.modscore(self.targetWorth)
          play_sound(self.pygame, "Pickup_00")
          self.leds.setLed(self.ledTable[count], 255, 0, 0, 0, 0)
          self.leds.flash(25, 5, 255, 0, 0) # Need to make flash consider changes in LED state during flash.
          self.targetTable[x] = True
      count += 1
    
    if self.targetTable.count(True) is self.ioRange:
      if self.needReset is False:
        self.rTime = time
      self.needReset = True 

    if self.needReset and (time - self.rTime >= self.restTime):
      self.reset(time)

    if self.needReset and (time - self.rTime >= self.restTime + 100):
      self.needReset = False
      self.targetTable = [False]*(self.maxPin + 1)
      self.score.modscore(self.resetBonus)
      play_sound(self.pygame, "Pickup_02")
      for x in range(len(self.ledTable)):
        self.leds.setLed(self.ledTable[x], 0, 0, 0, 0, 0)
      self.leds.flash(25, 10, 255, 255, 255)

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


  def triggerSolenoid(self, time, io, pin, duration=100, tag="1"):
    "Triggers a solenoid for 'duration' milliseconds"
    self.start(time, tag)
    etime = self.elapsedTime(time)
    if etime < duration:
      io.pinout(pin, True)
    elif etime < (duration + io.debounce_time):
      io.pinout(pin, False)
    else:
      io.pinout(pin, False)
      self.stop()

  def triggerPWM(self, time, io, pin, duration=100, dutyCycle=100, dutyLength=10, tag="1"):
    "Triggers an output for 'duration' milliseconds with a duty cycle of 'dutyCycle' percent. Frequency can be set up to 2 millisecond resolution, dutyLength is total length of PWM cycle."
    self.start(time, tag)
    etime = self.elapsedTime(time)
    if etime < duration:
      if((etime % dutyLength) < dutyLength*(dutyCycle / 100)):
        io.pinout(pin, True)
      else:
        io.pinout(pin, False)
    else:
      io.pinout(pin, False)
      self.stop()

  def loadBall(self, time, pygame, score, tag="1"):
    "Testing the timed event system. Will be used to load a ball in the future."
    self.start(time, tag)
    #self.elapsedTime(time)
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

  def ufoFly(self, time, twoAxis, duration=5000, tag="1"):
    "Makes the UFO servo fly around in a little pattern."
    self.start(time, tag)
    etime = self.elapsedTime(time) / 400
    twoAxis.setX(math.fabs(100*math.sin(etime)))
    twoAxis.setY(math.fabs(25*math.cos(etime*0.5)))
    if self.elapsedTime(time) > duration:
      twoAxis.setX(50)
      twoAxis.setY(0)
      self.stop()
