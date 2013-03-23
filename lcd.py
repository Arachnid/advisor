import mcp23008
import time

class LCD(object):
  PIN_BACKLIGHT = 0x80
  PIN_ENABLE    = 0x40
  PIN_OTHER     = 0x20
  PIN_REGSEL    = 0x10
  
  # Commands
  LCD_CLEARDISPLAY = 0x01
  LCD_RETURNHOME = 0x02
  LCD_ENTRYMODESET = 0x04
  LCD_DISPLAYCONTROL = 0x08
  LCD_CURSORSHIFT = 0x10
  LCD_FUNCTIONSET = 0x20
  LCD_SETCGRAMADDR = 0x40
  LCD_SETDDRAMADDR = 0x80
  
  # Flags for display entry mode
  LCD_ENTRYRIGHT = 0x00
  LCD_ENTRYLEFT = 0x02
  LCD_ENTRYSHIFTINCREMENT = 0x01
  LCD_ENTRYSHIFTDECREMENT = 0x00
  
  # Flags for display on/off control
  LCD_DISPLAYON = 0x04
  LCD_DISPLAYOFF = 0x00
  LCD_CURSORON = 0x02
  LCD_CURSOROFF = 0x00
  LCD_BLINKON = 0x01
  LCD_BLINKOFF = 0x00
  
  # Flags for display/cursor shift
  LCD_DISPLAYMOVE = 0x08
  LCD_CURSORMOVE = 0x00
  LCD_MOVERIGHT = 0x04
  LCD_MOVELEFT = 0x00
  
  # Flags for function set
  LCD_8BITMODE = 0x10
  LCD_4BITMODE = 0x00
  LCD_2LINE = 0x08
  LCD_1LINE = 0x00
  LCD_5x10DOTS = 0x04
  LCD_5x8DOTS = 0x00
  
  def __init__(self, i2c, address):
    self.expander = mcp23008.Expander(i2c, address)
    self._displayfunction = LCD.LCD_4BITMODE | LCD.LCD_2LINE | LCD.LCD_5x8DOTS
    self._lines = 2
    self._currline = 0
    self._cols = 16
    self.config()
    
    # Set 4 bit mode
    for i in range(3):
      self.write4bits(0x03)
      time.sleep(0.0045)
    self.write4bits(0x02)
    
    self.command(LCD.LCD_FUNCTIONSET | self._displayfunction)
    
    self._displaycontrol = LCD.LCD_DISPLAYON | LCD.LCD_CURSOROFF | LCD.LCD_BLINKOFF
    self.display()
    
    self.clear()
    
    self._displaymode = LCD.LCD_ENTRYLEFT | LCD.LCD_ENTRYSHIFTDECREMENT
    self.command(LCD.LCD_ENTRYMODESET | self._displaymode)

  def clear(self):
    self.command(LCD.LCD_CLEARDISPLAY)
    time.sleep(0.002)
  
  def home(self):
    self.command(LCD.LCD_RETURNHOME)
    time.sleep(0.002)
  
  def set_cursor(self, col, row):
    if row > 1:
      row = 1
    self.command(LCD.LCD_SETDDRAMADDR | (col + 0x40 * row))
  
  def no_display(self):
    self._displaycontrol &= ~LCD.LCD_DISPLAYON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)
  
  def display(self):
    self._displaycontrol |= LCD.LCD_DISPLAYON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)
  
  def no_cursor(self):
    self._displaycontrol &= ~LCD.LCD_CURSORON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)
  
  def cursor(self):
    self._displaycontrol |= LCD.LCD_CURSORON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)

  def no_blink(self):
    self._displaycontrol &= ~LCD.LCD_BLINKON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)
  
  def blink(self):
    self._displaycontrol |= LCD.LCD_BLINKON
    self.command(LCD.LCD_DISPLAYCONTROL | self._displaycontrol)
  
  def scroll_display_left(self):
    self.command(LCD.LCD_CURSORSHIFT | LCD.LCD_DISPLAYMOVE | LCD.LCD_MOVELEFT)
  
  def scroll_display_right(self):
    self.command(LCD.LCD_CURSORSHIFT | LCD.LCD_DISPLAYMOVE | LCD.LCD_MOVERIGHT)
  
  def left_to_right(self):
    self._displaymode |= LCD_ENTRYLEFT
    self.command(LCD.LCD_ENTRYMODESET | self._displaymode)
  
  def right_to_left(self):
    self._displaymode &= ~LCD.LCD_ENTRYLEFT
    self.command(LCD.LCD_ENTRYMODESET | self._displaymode)

  def autoscroll(self):
    self._displaymode |= LCD.LCD_ENTRYSHIFTINCREMENT
    self.command(LCD.LCDENTRYMODESET | self._displaymode)
  
  def autoscroll(self):
    self._displaymode &= ~LCD.LCD_ENTRYSHIFTINCREMENT
    self.command(LCD.LCDENTRYMODESET | self._displaymode)

  def command(self, value):
    self.send(value, 0)
  
  def write(self, value):
    self.send(value, 1)
    
  def write4bits(self, value):
    value |= LCD.PIN_BACKLIGHT | LCD.PIN_ENABLE
    self.expander.gpio = [value, value ^ LCD.PIN_ENABLE, value]
  
  def send(self, value, mode):
    if mode != 0:
      mode = LCD.PIN_REGSEL
    self.write4bits((value >> 4) | mode)
    self.write4bits((value & 0x0F) | mode)
  
  def config(self):
    self.expander.iocon = 0x24 # SEQOP = 1, ODR = 1
    self.backlight()
  
  def backlight(self):
    self.expander.iodir = 0
  
  def no_backlight(self):
    self.expander.iodir = LCD.PIN_BACKLIGHT
    