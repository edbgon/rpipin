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

# Imports
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import smbus
import pygame
import curses
import signal
import sys
import time

#################################################################################
# Definitions and Classes
#################################################################################

# Custom definitions and classes


#################################################################################
# Score class
#################################################################################
class Score:
  def __init__(self, init_score, init_mul, init_paddles):
    self.val = init_score
    self.mul = init_mul
    self.pad = init_paddles

  def modscore(self, amount):
    "Modifies score with respect to the current multiplier"
    self.val += (amount * self.mul)
    if self.val > 99999999: self.val = 99999999

  def setmul(self, mul):
    "Sets the multiplier"
    self.mul = mul

  def highscore(self):
    "Sets a new high score if applicable"
    pass

  def get_highscore(self):
    "Returns a list of the high scores"
    pass

#################################################################################
# Drop Target class
# Custom amount of drop targets and reset time
#################################################################################

class dropTarget:
  def __init__(self, minPin, maxPin, resetPin, restTime=1000, targetWorth=500, resetBonus=2000):
    self.minPin = minPin
    self.maxPin = maxPin
    self.resetPin = resetPin
    self.needReset = False
    self.rTime = 0
    self.ioRange = (maxPin - minPin) + 1
    self.targetTable = [False]*(self.maxPin + 1)
    self.restTime = restTime
    self.targetWorth = targetWorth
    self.resetBonus = resetBonus

  def reset(self, time):
    global io
    if solenoid.started != "2":
      solenoid.triggerSolenoid(time, io, self.resetPin, duration=80, tag="2")

  def check(self, time):
    global score
    global io
    global solenoid
    global flash
    totalCheck = 0
    if self.needReset is False:
      for x in range(self.minPin, self.maxPin + 1):
        if self.needReset is True: continue
        if io.getpin(x, reqDebounce=False):
          totalCheck += 1
          if self.targetTable[x] is False:
            score.modscore(self.targetWorth)
            play_sound(pygame, "Jump_03")
            leds.flash(25, 5, 255, 0, 0)
            self.targetTable[x] = True
    
    if totalCheck >= self.ioRange:
      if self.needReset is False:
        self.rTime = time
      self.needReset = True 

    if self.needReset and (time - self.rTime >= self.restTime):
      self.reset(time)

    if self.needReset and (time - self.rTime >= self.restTime + 100):
      self.needReset = False
      self.targetTable = [False]*(self.maxPin + 1)
      score.modscore(self.resetBonus)
      leds.flash(25, 10, 255, 255, 255)
      play_sound(pygame, "Jump_03")


#################################################################################
# Clean exit sigint handler
#################################################################################
def signal_handler(signal, frame):
  "Signal handler for Ctrl-C and related things"
  clean_exit("SIGINT detected. Closing program.")

def catch_uncaught(type, value, traceback):
  clean_exit(str(type) + " " + str(value) + " " + str(traceback))

#################################################################################
# Cleans up pin outputs and curses junk
#################################################################################
def clean_exit(message=""):
  "Tries to make for a clean exit since curses doesn't make for a nice one by default"
  try:
    sevSegL.clear()
    sevSegL.write_display()
    sevSegR.clear()
    sevSegR.write_display()
    io.cleanup()
  except:
    pass

  # Clean up screen
  leds.clear()
  curses.nocbreak()
  screen.keypad(False)
  curses.echo()
  curses.endwin()
  if(message): print(message)

  # Bye :)
  sys.exit(0)

#################################################################################
# Stops all animations
#################################################################################
def stopAnimations(dontStop=""):
  "Stops all animations excluding the one in dontStop"
  for obj in animList:
    if obj == dontStop: continue
    exec(obj + ".stop()")

#################################################################################
# Initialization
#################################################################################

# Custom Imports
from HT16K33 import *
from led import *
#from hmc5883l import *
from mcp23017 import *
from media import *
#from servo import *

# In the beginning...
time = 0
lastScore = -12345
playlistPos = 0
playlistPath = "audio/music/"

# Currently using pygame for sound and music and frame-rate control
pygame.init()
pygame.display.set_mode((1,1))
clock = pygame.time.Clock()
pygame.mixer.init(44100, -16,2,2048)

# Curses Initialization for game status (curses import)
screen = curses.initscr()
curses.noecho()
curses.curs_set(0)
screen.keypad(1)
screen.nodelay(1)

# Clean up nicely when sigint
signal.signal(signal.SIGINT, signal_handler)
#sys.excepthook = catch_uncaught

#################################################################################
# Init Music
# TODO: Playlist
#################################################################################
try:
  playlist = ['focus.mp3', 'forged.mp3', 'multiball-loop.ogg', 'song.mp3', 'spectra.mp3']
  pygame.mixer.music.set_volume(0.4)
  pygame.mixer.music.load(playlistPath + playlist[playlistPos])
  pygame.mixer.music.play(-1)
except:
  clean_exit(message="Error initializing audio!\n")

#################################################################################
# Init score: start score, multiplier, paddlings
#################################################################################
score = Score(0, 1, 0)

#################################################################################
# Init i2c bus (smbus)
# Use i2cdetect -y 1 to see what devices are on the bus
#################################################################################
smbus = smbus.SMBus(1)

#################################################################################
# Initialize i2c I/O Driver
# Init bus: smbus, start_addr, count, out_dir_reg, 
# in_dir_reg, out_reg, in_reg, pup_reg, pol_reg, debounce_time
#################################################################################
try:
  io = mcp23017(smbus, 0x20, 2, 0x00, 0x01, 0x14, 0x13, 0x0D, 0x03, 400)
except:
  clean_exit(message="Failed loading I2C IO!\n")

#################################################################################
# I2C Arduino WS2812 LED Controller
#################################################################################
leds = ledStrip(smbus, address=0x10)

#################################################################################
# 7Seg Display Initialization
# Uses left and right for a total of 8 digits
#################################################################################

try:
  sevSegL = SevenSegment(address=0x70, busnum=1, i2c=smbus)
  sevSegR = SevenSegment(address=0x71, busnum=1, i2c=smbus)
  sevSegL.begin()
  sevSegR.begin()
  sevSegL.set_brightness(15)
  sevSegR.set_brightness(15)
  sevSegL.clear()
  sevSegR.clear()
  sevSegL.write_display()
  sevSegR.write_display()
except:
  clean_exit(message="Failed initializing i2c 7-Segment display\n")


#################################################################################
# Init hmc5883l
# Magnetic tilt sensor, not to be used in proximity of solenoids.....
# Look for accelerometer instead?
#################################################################################
#axis = hmc5883l(smbus, 0x1E, 300)
x = y = z = 0

#################################################################################
# Init Servo Library
#################################################################################
#servo1 = servo(smbus, address=0x40)
#servoMin = 150  # Min pulse length out of 4096
#servoMax = 600  # Max pulse length out of 4096
#servo1.setPWMFreq(60)
#servo1.setPWM(0, 0, servoMin)


#################################################################################
# Animations and Scripts
#################################################################################
animList = ['loadBall', 'solenoid']
for obj in animList:
  exec(obj + "= tEvent()")

# Set up drop target with 5 targets from pin 9 to pin 13. Reset pin is 2.
dt1 = dropTarget(9, 13, 2)

#################################################################################
# Main Game Loop
#################################################################################
errors = 0
while 1:
  try:
    #io.time = 
    time = pygame.time.get_ticks()
    event = screen.getch()

    if event == ord("q"): break

    if event == ord("1") or io.getpin(1) or solenoid.started == "1":
      solenoid.triggerSolenoid(time, io, 1, duration=100, tag="1")

    if event == ord("2") or io.getpin(2) or solenoid.started == "2":
      solenoid.triggerSolenoid(time, io, 2, duration=80, tag="2")

    if event == ord("3"):
      score.modscore(1)

    if event == ord("4"):
      score.modscore(10)

    if event == ord("5"):
      score.modscore(100)

    if event == ord("6"):
      score.modscore(1000)

    if event == ord("7"):
      score.modscore(10000)

    if event == ord("8"):
      score.modscore(100000)

    if event == ord("9"):
      score.modscore(1000000)

    # TESTING DELAYED ACTION
    #if event == ord("r") or loadBall.started == "1":
      #if loadBall.started == "0": stopAnimations("loadBall")
      #loadBall.loadBall(time, pygame, score)

    # Change music around
    if event == ord("m"):
      playlistPos += 1
      if playlistPos >= len(playlist):
        playlistPos = 0
      pygame.mixer.music.load(playlistPath + playlist[playlistPos])
      pygame.mixer.music.play(-1)

    if event == ord("s"):
      play_sound(pygame, "arugh")

    #  Testing Animations with LEDs
    if event == ord("-"):
      score.val = 0
      stopAnimations()

    #if event == curses.KEY_LEFT:
      #servo1.setPWM(0, 0, servoMin)
      
    #if event == curses.KEY_RIGHT:
      #servo1.setPWM(0, 0, servoMax)

    if event == ord("j") or solenoid.started == "Motor":
      solenoid.triggerPWM(time, io, 9, duration=1000, tag="Motor", dutyCycle=12, dutyLength=4)

    if event == ord("z"):
      leds.colorWipe(255, 0, 0)

    if event == ord("x"):
      leds.colorWipe(0, 255, 0)

    if event == ord("c"):
      leds.colorWipe(0, 0, 255)

    if event == ord("v"):
      leds.rainbow()

    if event == ord("b"):
      leds.theaterChase(255, 255, 255)

    if event == ord("n"):
      leds.setLed(2, 127, 0, 127)

    if event == ord("m"):
      leds.restoreState()

    if event == ord(","):
      leds.clear()

    if event == ord("f"):
      leds.flash(50, 5, 255, 255, 255)

    dt1.check(time)
      
  except OSError:
    errors += 1
    pass

  #################################################################################
  # Seven Segment Score Display
  #################################################################################
  if lastScore != score.val:
    sevSegL.clear()
    sevSegR.clear()
    strString = str(score.val)
    lStrString = strString[:-4]
    rStrString = strString[-4:]
    if rStrString is '': rStrString = '0'
    sevSegL.print_number_str(lStrString)
    if score.val > 9999: rStrString = rStrString.zfill(4)
    sevSegR.print_number_str(rStrString)
    sevSegL.write_display()
    sevSegR.write_display()
    lastScore = score.val

  # Debug Information
  screen.addstr(12, 12, "Super Pinball 3000! Ticks thus far: " + str(time).ljust(20," "))
  screen.addstr(14, 12, "SCORE:       " + str(score.val).ljust(20," "))
  screen.addstr(15, 12, "Paddle Time: " + str(score.pad).ljust(20," "))
  #screen.addstr(16, 12, "OSErrors:    " + str(errors).ljust(20," "))
  #screen.addstr(17, 12, "Step:        " + str(countAnim.step).ljust(20," "))
  #screen.addstr(18, 12, "Debug:       " + str(totdt).ljust(20," "))
  
  #if(time % 2 == 0): axis.update()
  
  #screen.addstr(17, 12, "XYZ T:     " + str(axis.valX).ljust(6," ") + " " + \
  #                                    str(axis.valY).ljust(6," ") + " " + \
  #                                    str(axis.valZ).ljust(6," ") + " " + \
  #                                    str(axis.tilt_delta).ljust(20," "))
  #screen.addstr(18, 12, "Tilted:    "  + str(axis.tilted).ljust(20," "))
  
  clock.tick(150)
#################################################################################
# END Main Game Loop
#################################################################################

clean_exit(message="Exited normally")
