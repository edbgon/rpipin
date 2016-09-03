# Constants

I2C_ADDRESS = 0x10
SET_SINGLE_COLOR = 0x15
COLOR_WIPE = 0x20
RAINBOW = 0x30
RAINBOW_CYCLE = 0x40
THEATER_CHASE = 0x50
THEATER_CHASE_RAINBOW = 0x60
FLASHER = 0x70

RESTORE_STATE = 0xFD
SET_ALL = 0xFE
CLEAR_ALL = 0xFF

EMPTY_BYTES = [0, 0, 0, 0, 0, 0]

NUM_LEDS = 5

class ledStrip():
  """Arduino slave WS2812 interaction"""

  def __init__(self, i2c, address=I2C_ADDRESS):
      """Initialize"""
      self.i2c = i2c
      self.address = address
      self.ledState = [0] * 3 * NUM_LEDS 

  def setLed(self, led, r, g, b):
    self.i2c.write_i2c_block_data(self.address, SET_SINGLE_COLOR, [led, r, g, b, 0, 0])
    self.ledState[led * 3] = r
    self.ledState[led * 3 + 1] = g
    self.ledState[led * 3 + 2] = b

  def restoreState(self):
    self.i2c.write_i2c_block_data(self.address, RESTORE_STATE, EMPTY_BYTES)

  def colorWipe(self, r, g, b):
    self.i2c.write_i2c_block_data(self.address, COLOR_WIPE, [0, r, g, b, 0, 0])

  def rainbow(self):
    self.i2c.write_i2c_block_data(self.address, RAINBOW, EMPTY_BYTES)

  def rainbowCycle(self):
    self.i2c.write_i2c_block_data(self.address, RAINBOW_CYCLE, EMPTY_BYTES)

  def theaterChase(self, r, g, b):
    self.i2c.write_i2c_block_data(self.address, THEATER_CHASE, [0, r, g, b, 0, 0])

  def theaterChaseRainbow(self):
    self.i2c.write_i2c_block_data(self.address, THEATER_CHASE_RAINBOW, EMPTY_BYTES)

  def flash(self, wait, repetitions, r, g, b):
    self.i2c.write_i2c_block_data(self.address, FLASHER, [0, r, g, b, wait, repetitions])

  def setAll(self, r, g, b):
    self.i2c.write_i2c_block_data(self.address, SET_ALL, [0, r, g, b, 0, 0])

  def clear(self):
    self.i2c.write_i2c_block_data(self.address, CLEAR_ALL, EMPTY_BYTES)
    for x in range(0, len(self.ledState)):
      self.ledState[x] = 0