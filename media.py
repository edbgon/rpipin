#!/usr/bin/python3

import math
import os

# Sound library that will only load sounds once and keep in memory
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

# Timed Event Class
class tEvent:
  def __init__(self):
    self.initTick = 0
    self.started = False
    self.step = 0
    self.ledCol = [255, 0, 0]
    self.ledA = 255

  def elapsedTime(self, nowTick):
    if(self.started == True):
      return nowTick - self.initTick
    else:
      return 0

  def start(self, initTick):
    if(self.started == False):
      self.initTick = initTick
      self.started = True

  def stop(self):
    if(self.started == True):
      self.started = False

  def reset(self, initTick):
    self.initTick = initTick

  def ledHeartbeat(self, time, led):
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

  def binCount(self, time, led):
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

  def loadBall(self, time, pygame, score):
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
      score.modscore(1000000)
      self.step = 0
      self.stop()