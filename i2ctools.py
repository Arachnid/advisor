def register_property(i2c, address, reg):
  def _getter():
    return i2c.read_byte_data(address, reg)
  def _setter(values):
    if isinstance(values, (int, long)):
      values = (values,)
    i2c.write_block_data(address, reg, values)
  return property(_getter, _setter)
