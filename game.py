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

# Score class
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

# Clean exit sigint handler
def signal_handler(signal, frame):
  "Signal handler for Ctrl-C and related things"
  clean_exit()


# Cleans up pin outputs and curses junk
def clean_exit(message=""):
  "Tries to make for a clean exit since curses doesn't make for a nice one by default"
  try:
    io.cleanup()
    led.cleanup()
    sevSegL.clear()
    sevSegL.write_display()
    sevSegR.clear()
    sevSegR.write_display()
  except:
    pass

  # Clean up screen
  curses.nocbreak()
  screen.keypad(False)
  curses.echo()
  curses.endwin()
  if(message): print(message)

  # Bye :)
  sys.exit(0)

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
from ws2812 import *
#from hmc5883l import *
from mcp23017 import *
from media import *
from servo import *

# In the beginning...
time = 0
lastScore = -12345

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

#################################################################################
# Init Music
# TODO: Playlist
#################################################################################
try:
  pygame.mixer.music.set_volume(0.3)
  pygame.mixer.music.load('audio/music/forged.mp3')
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
  io = mcp23017(smbus, 0x20, 1, 0x00, 0x01, 0x14, 0x13, 0x0D, 0x03, 400)
except:
  clean_exit(message="Failed loading I2C IO!\n")

#################################################################################
# Initialize LED string
# Uses PWM output #18
# led_count, led_brightness, led_pin, led_frequency, led_dma, led_invert
#################################################################################
try:
  led = ws2812(5, 50, 18, 800000, 5, False)
except:
  clean_exit(message="Failed initializing i2c library!\n")

#################################################################################
# 7Seg Display Initialization
# Uses left and right for a total of 8 digits
#################################################################################
try:
  sevSegL = SevenSegment(address=0x70, busnum=1, i2c=smbus)
  sevSegR = SevenSegment(address=0x71, busnum=1, i2c=smbus)
  sevSegL.begin()
  sevSegR.begin()
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
servo1 = servo(smbus, address=0x40)
servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096
servo1.setPWMFreq(60)
servo1.setPWM(0, 0, servoMin)


#################################################################################
# Animations and Scripts
#################################################################################
animList = ['idleAnimation', 'loadBall', 'lampTest', 'countAnim', 'flash', 'solenoid']
for obj in animList:
  exec(obj + "= tEvent()")

#################################################################################
# Main Game Loop
#################################################################################
errors = 0
while 1:
  try:
    io.time = time = pygame.time.get_ticks()
    event = screen.getch()

    if event == ord("q"): break

    if event == ord("1") or io.getpin(1) or solenoid.started == "1":
      solenoid.triggerSolenoid(time, io, 1, duration=100, tag="1")

    if event == ord("2") or io.getpin(2) or solenoid.started == "2":
      solenoid.triggerSolenoid(time, io, 2, duration=80, tag="2")

    if event == ord("3") or io.getpin(3):
      play_sound(pygame, "Jump_03")
      led.ledcolor(0, 0, 0, 127)
      led.ledcolor(1, 0, 66, 66)
      score.modscore(1)

    if event == ord("4") or io.getpin(4):
      play_sound(pygame, "Jingle_Lose_00")
      led.ledcolor(0, 127, 0, 0)
      led.ledcolor(1, 66, 0, 0)
      score.modscore(10)

    if event == ord("5") or io.getpin(5):
      play_sound(pygame, "arugh")
      led.ledcolor(0, 127, 0, 0)
      led.ledcolor(1, 66, 0, 66)
      score.modscore(100)

    if event == ord("6") or io.getpin(6):
      pygame.mixer.music.load('audio/music/spectra.mp3')
      pygame.mixer.music.play(-1)
      score.modscore(1000)

    if event == ord("7") or io.getpin(7):
      pygame.mixer.music.load('audio/music/forged.mp3')
      pygame.mixer.music.play(-1)
      score.modscore(10000)

    if event == ord("8") or io.getpin(8):
      pygame.mixer.music.load('audio/music/focus.mp3')
      pygame.mixer.music.play(-1)
      score.modscore(100000)

    if event == ord("9"):
      score.modscore(1000000)

    # TESTING LIGHT ANIMATION
    if event == ord("0") or idleAnimation.started == "1":
      if idleAnimation.started == "0": stopAnimations("idleAnimation")
      idleAnimation.ledHeartbeat(time, led)

    # TESTING DELAYED ACTION
    if event == ord("r") or loadBall.started == "1":
      if loadBall.started == "0": stopAnimations("loadBall")
      loadBall.loadBall(time, pygame, score)

    # Testing flash animation
    if event == ord("f") or flash.started == "f1":
      flash.ledFlash(time, led, 40, 5, 255, 255, 255, "f1")

    if event == ord("-"):
      score.val = 0
      stopAnimations()
      for x in range(0, led.count):
        led.ledcolor(x, 0, 0, 0)

    if event == ord("=") or lampTest.started == "1":
      if lampTest.started == "0": stopAnimations("lampTest")
      lampTest.ledChase(time, led)

    if event == ord("`") or countAnim.started == "1":
      if countAnim.started == "0": stopAnimations("countAnim")
      countAnim.binCount(time, led)

    if event == curses.KEY_LEFT:
      servo1.setPWM(0, 0, servoMin)
      
    if event == curses.KEY_RIGHT:
      servo1.setPWM(0, 0, servoMax)
      
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
  #screen.addstr(18, 12, "Debug:       " + ' '.join(flash.ledBackup).ljust(20," "))
  
  #if(time % 2 == 0): axis.update()
  
  #screen.addstr(17, 12, "XYZ T:     " + str(axis.valX).ljust(6," ") + " " + \
  #                                    str(axis.valY).ljust(6," ") + " " + \
  #                                    str(axis.valZ).ljust(6," ") + " " + \
  #                                    str(axis.tilt_delta).ljust(20," "))
  #screen.addstr(18, 12, "Tilted:    "  + str(axis.tilted).ljust(20," "))
  
  clock.tick(120)
#################################################################################
# END Main Game Loop
#################################################################################

clean_exit(message="Exited normally")
