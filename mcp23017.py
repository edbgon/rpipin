#!/usr/bin/python3

# i2c Class for communication with mcp23017.
# Using A side for outputs and B side for inputs
# Set inputs to have built-in pullup resistors and activate on connection to GND

class mcp23017:
  def __init__(self, i2cbus, start_addr, count, out_dir_reg, in_dir_reg, out_reg, in_reg, pup_reg, pol_reg, debounce_time):
    self.i2cbus  = i2cbus
    self.outreg  = out_reg
    self.inreg   = in_reg
    self.outputs = [0b00000000] * count
    self.debtime = [0] * 8 * count
    self.bouncereg = [0] * 8 * count
    self.start_addr = start_addr
    self.count = count
    self.debounce_time = debounce_time
    self.time = 0
    try:
      for i in range(start_addr, start_addr + count):
        self.i2cbus.write_byte_data(i, out_dir_reg, 0x00) 
        self.i2cbus.write_byte_data(i, in_dir_reg, 0xFF)
        self.i2cbus.write_byte_data(i, out_reg, 0x00)
        self.i2cbus.write_byte_data(i, pol_reg, 0xFF)
        self.i2cbus.write_byte_data(i, pup_reg, 0xFF)
    except OSError:
      raise Exception("Cannot initialize i2c I/O at address " + str(i))

  def get_dpin(self, pin):
    pin -= 1
    return(pin // 8, pin % 8)

  def pinout(self, cpin, action):
    (device, pin) = self.get_dpin(cpin)
    old = self.outputs[device]
    if(action):
      self.outputs[device] = self.setBit(self.outputs[device], pin)
    else:
      self.outputs[device] = self.clearBit(self.outputs[device], pin)
    if(old == self.outputs[device]): return False
    try:
      self.i2cbus.write_byte_data(self.start_addr + device, self.outreg, self.outputs[device])
    except OSError:
      # Intermittent I2C errors shouldn't stop the entire program. 
      pass
    return True
  
  def getpin(self, pin, time, reqDebounce=True):
    if(pin > self.count * 8 or pin < 1): return
    (device, dpin) = self.get_dpin(pin)
    mask = 1 << dpin
    result = 0
    try:
      result = self.i2cbus.read_byte_data(self.start_addr + device, self.inreg) & mask
    except OSError:
      # Intermittent I2C errors shouldn't stop the entire program.
      pass
    debounce = False

    if(result > 0):
      if reqDebounce:
        if(self.bouncereg[pin - 1] == 0):
          self.debtime[pin - 1] = time
          self.bouncereg[pin - 1] = 1

        if(time - self.debtime[pin - 1] >= self.debounce_time):
          return True
        else:
          return False
      else:
        return True
    else:
      if(self.bouncereg[pin - 1] == 1):
        self.bouncereg[pin - 1] = 0
      return False

  def cleanup(self):
    for i in range(self.start_addr, self.start_addr + self.count):
      try:
        self.i2cbus.write_byte_data(i, self.outreg, 0b00000000)
      except OSError:
        pass
    return True

  # Binary math
  def setBit(self, int_type, offset):
    mask = 1 << offset
    return(int_type | mask)
  def clearBit(self, int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)
