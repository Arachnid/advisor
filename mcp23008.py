import i2ctools

class Expander(object):
  MCP_IODIR     = 0x00
  MCP_IPOL      = 0x01
  MCP_GPINTEN   = 0x02
  MCP_DEFVAL    = 0x03
  MCP_INTCON    = 0x04
  MCP_IOCON     = 0x05
  MCP_GPPU      = 0x06
  MCP_INTF      = 0x07
  MCP_INTCAP    = 0x08
  MCP_GPIO      = 0x09
  MCP_OLAT      = 0x0A

  def __init__(self, i2c, address):
    self.i2c = i2c
    self.address = address
    self.iodir = i2ctools.register_property(i2c, address, Expander.MCP_IODIR)
    self.iocon = i2ctools.register_property(i2c, address, Expander.MCP_IOCON)
    self.gpio = i2ctools.register_property(i2c, address, Expander.MCP_GPIO)
