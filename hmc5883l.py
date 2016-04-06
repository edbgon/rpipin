#!/usr/bin/python3

class hmc5883l:
  def __init__(self, i2cbus, addr, tilt_magnitude):
    self.addr = addr
    self.i2cbus = i2cbus
    self.i2cbus.write_byte_data(addr, 0x00, 0xF8)  # CRA 75Hz.
    self.i2cbus.write_byte_data(addr, 0x02, 0x00)  # Mode continuous reads.

    self.valX = 0
    self.valY = 0
    self.valZ = 0

    self.iX = 0
    self.iY = 0
    self.iZ = 0

    self.tilt_magnitude = tilt_magnitude
    self.tilt_delta = 0
    self.tilted = False
     
  def update(self):
    X = (self.i2cbus.read_byte_data(self.addr, 0x03) << 8) | self.i2cbus.read_byte_data(self.addr, 0x04)
    Y = (self.i2cbus.read_byte_data(self.addr, 0x05) << 8) | self.i2cbus.read_byte_data(self.addr, 0x06)
    Z = (self.i2cbus.read_byte_data(self.addr, 0x07) << 8) | self.i2cbus.read_byte_data(self.addr, 0x08)

    # Update the values to be of two compliment
    self.valX = self.twos_to_int(X, 16);
    self.valY = self.twos_to_int(Y, 16);
    self.valZ = self.twos_to_int(Z, 16);

    if(self.iX == 0): self.iX = self.valX
    if(self.iY == 0): self.iY = self.valY
    if(self.iZ == 0): self.iZ = self.valZ

    self.tilt_delta = abs(self.valX - self.iX) + abs(self.valY - self.iY) + abs(self.valZ - self.iZ)
    if(self.tilt_delta > self.tilt_magnitude): self.tilted = True

    return

  def twos_to_int(self, val, len):
    # Convert twos compliment to integer
    if(val & (1 << len - 1)):
        val = val - (1<<len)
    return val