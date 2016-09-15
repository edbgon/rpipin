# Constants

I2C_ADDRESS           = 0x10

SET_SINGLE_COLOR      = 0x15
COLOR_WIPE            = 0x20
RAINBOW               = 0x50
RAINBOW_CYCLE         = 0x51
THEATER_CHASE         = 0x52
THEATER_CHASE_RAINBOW = 0x53

FLASHER               = 0x60

FLASHINF              = 0x71
FLASHALT              = 0x72
SPARKLE               = 0x73
SPARKLE_FADE          = 0x74
FLAME                 = 0x75
GLOW                  = 0x76

RESTORE_STATE         = 0xFD
SET_ALL               = 0xFE
CLEAR_ALL             = 0xFF

EMPTY_BYTES = [0, 0, 0, 0, 0, 0]

NUM_LEDS = 5

class ledStrip():
  """Arduino slave WS2812 interaction"""

  def __init__(self, i2c, address=I2C_ADDRESS):
      """Initialize"""
      self.i2c = i2c
      self.address = address
      self.ledState = [0] * 3 * NUM_LEDS 

  def setLed(self, led, r, g, b, wait, blink):
    self.i2c.write_i2c_block_data(self.address, SET_SINGLE_COLOR, [led, r, g, b, wait, blink])
    self.ledState[led * 3] = r
    self.ledState[led * 3 + 1] = g
    self.ledState[led * 3 + 2] = b

  def restoreState(self):
    self.i2c.write_i2c_block_data(self.address, RESTORE_STATE, EMPTY_BYTES)

  def colorWipe(self, wait, r, g, b):
    self.i2c.write_i2c_block_data(self.address, COLOR_WIPE, [0, r, g, b, wait, 0])

  def rainbow(self, wait):
    self.i2c.write_i2c_block_data(self.address, RAINBOW, [0, 0, 0, 0, wait, 0])

  def rainbowCycle(self, wait):
    self.i2c.write_i2c_block_data(self.address, RAINBOW_CYCLE, [0, 0, 0, 0, wait, 0])

  def theaterChase(self, wait, r, g, b):
    self.i2c.write_i2c_block_data(self.address, THEATER_CHASE, [0, r, g, b, wait, 0])

  def theaterChaseRainbow(self, wait):
    self.i2c.write_i2c_block_data(self.address, THEATER_CHASE_RAINBOW, [0, 0, 0, 0, wait, 0])

  def flash(self, wait, repetitions, r, g, b):
    self.i2c.write_i2c_block_data(self.address, FLASHER, [0, r, g, b, wait, repetitions])

  def flashInf(self, wait, r, g, b):
    self.i2c.write_i2c_block_data(self.address, FLASHINF, [0, r, g, b, wait, 0])

  def flashAlt(self, wait, r, g, b):
    self.i2c.write_i2c_block_data(self.address, FLASHALT, [0, r, g, b, wait, 0])

  def sparkle(self, wait, r, g, b):
    self.i2c.write_i2c_block_data(self.address, SPARKLE, [0, r, g, b, wait, 0])

  def sparkleFade(self, wait, chance, r, g, b):
    self.i2c.write_i2c_block_data(self.address, SPARKLE_FADE, [0, r, g, b, wait, chance])

  def flame(self, wait):
    self.i2c.write_i2c_block_data(self.address, FLAME, [0, 0, 0, 0, wait, 0])

  def glow(self, wait):
    self.i2c.write_i2c_block_data(self.address, GLOW, [0, 0, 0, 0, wait, 0])

  def setAll(self, r, g, b):
    self.i2c.write_i2c_block_data(self.address, SET_ALL, [0, r, g, b, 0, 0])

  def clear(self):
    self.i2c.write_i2c_block_data(self.address, CLEAR_ALL, EMPTY_BYTES)
    for x in range(0, len(self.ledState)):
      self.ledState[x] = 0