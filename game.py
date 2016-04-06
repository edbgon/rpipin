#!/usr/bin/python3

# Imports
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import smbus
import pygame
import curses
import signal
import sys

# Custom Imports
from ws2812 import *
#from hmc5883l import *
from mcp23017 import *
from media import *

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
    self.val += (amount * self.mul)

  def setmul(self, mul):
    self.mul = mul

  def highscore(self):
    pass

  def get_highscore(self):
    pass


# Clean exit sigint handler
def signal_handler(signal, frame):
  clean_exit()


# Cleans up pin outputs and curses junk
def clean_exit(message=""):
  try:
    io.cleanup()
    led.cleanup()
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

#################################################################################
# Initialization
#################################################################################

# In the beginning...
time = 0

# Currently using pygame for sound and music and frame-rate control
pygame.init()
pygame.display.set_mode((1,1))
clock = pygame.time.Clock()

# Curses Initialization for game status (curses import)
screen = curses.initscr()
curses.noecho()
curses.curs_set(0)
screen.keypad(1)
screen.nodelay(True)

# Clean up nicely when sigint
signal.signal(signal.SIGINT, signal_handler)

# Init Music
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.load('audio/music/forged.mp3')
pygame.mixer.music.play(1)
pygame.mixer.music.queue('audio/music/focus.mp3')
pygame.mixer.music.play(1)
pygame.mixer.music.queue('audio/music/spectra.mp3')
pygame.mixer.music.play(-1)

# Init score: start score, multiplier, paddlings
score = Score(0, 1, 0)

# Init i2c bus
smbus = smbus.SMBus(1)

# Init bus: smbus, start_addr, count, out_dir_reg, 
# in_dir_reg, out_reg, in_reg, pup_reg, pol_reg, debounce_time
io = mcp23017(smbus, 0x20, 1, 0x00, 0x01, 0x14, 0x13, 0x0D, 0x03, 400)

# Initialize LED string
# led_count, led_brightness, led_pin, led_frequency, led_dma, led_invert
led = ws2812(5, 50, 18, 800000, 5, False)

# Init hmc5883l
#axis = hmc5883l(smbus, 0x1E, 300)
x = y = z = 0

# Animations and Scripts
idleAnimation = tEvent()
loadBall = tEvent()
lampTest = tEvent()
countAnim = tEvent()

#################################################################################
# Main Game Loop
#################################################################################
errors = 0
while 1:
  try:
    io.time = time = pygame.time.get_ticks()
    event = screen.getch()

    if event == ord("q"): break

    if event == ord("1") or io.getpin(1, False):
      io.pinout(8, True)
      score.pad += 1
    else:
      io.pinout(8, False)

    if event == ord("2") or io.getpin(2, False):
      io.pinout(2, True)
      score.pad += 1
    else:
      io.pinout(2, False)

    if event == ord("3") or io.getpin(3, True):
      play_sound(pygame, "Jump_03")
      led.ledcolor(0, 0, 0, 127)
      led.ledcolor(1, 0, 66, 66)
      score.modscore(500)

    if event == ord("4") or io.getpin(4, True):
      play_sound(pygame, "Jingle_Lose_00")
      led.ledcolor(0, 127, 0, 0)
      led.ledcolor(1, 66, 0, 0)
      score.modscore(250)

    if event == ord("5") or io.getpin(5, True):
      play_sound(pygame, "arugh")
      led.ledcolor(0, 127, 0, 0)
      led.ledcolor(1, 66, 0, 66)
      score.modscore(250)

    if event == ord("6") or io.getpin(6, True):
      pygame.mixer.music.load('audio/music/spectra.mp3')
      pygame.mixer.music.play(-1)

    if event == ord("7") or io.getpin(7, True):
      pygame.mixer.music.load('audio/music/forged.mp3')
      pygame.mixer.music.play(-1)

    if event == ord("8") or io.getpin(8, True):
      pygame.mixer.music.load('audio/music/focus.mp3')
      pygame.mixer.music.play(-1)

    # TESTING DELAYED ACTION
    if event == ord("9") or loadBall.started == True:
      loadBall.loadBall(time, pygame, score)

    # TESTING LIGHT ANIMATION
    if event == ord("0") or idleAnimation.started == True:
      lampTest.stop()
      countAnim.stop()
      idleAnimation.ledHeartbeat(time, led)

    if event == ord("-"):
      idleAnimation.stop()
      lampTest.stop()
      countAnim.stop()
      for x in range(0, led.count):
        led.ledcolor(x, 0, 0, 0)

    if event == ord("=") or lampTest.started == True:
      idleAnimation.stop()
      countAnim.stop()
      lampTest.ledChase(time, led)

    if event == ord("`") or countAnim.started == True:
      idleAnimation.stop()
      lampTest.stop()
      countAnim.binCount(time, led)    

  except OSError:
    errors += 1
    pass

  screen.addstr(12, 12, "Shitball 3000! Ticks thus far: " + str(time).ljust(20," "))
  screen.addstr(14, 12, "SCORE:       " + str(score.val).ljust(20," "))
  screen.addstr(15, 12, "Paddle Time: " + str(score.pad).ljust(20," "))
  screen.addstr(16, 12, "OSErrors:    "  + str(errors).ljust(20," "))
  screen.addstr(17, 12, "Step:        "  + str(countAnim.step).ljust(20," "))
  
  #if(time % 2 == 0): axis.update()
  
  #screen.addstr(17, 12, "XYZ T:     " + str(axis.valX).ljust(6," ") + " " + \
  #                                    str(axis.valY).ljust(6," ") + " " + \
  #                                    str(axis.valZ).ljust(6," ") + " " + \
  #                                    str(axis.tilt_delta).ljust(20," "))
  #screen.addstr(18, 12, "Tilted:    "  + str(axis.tilted).ljust(20," "))
  
  clock.tick(120)

clean_exit()
