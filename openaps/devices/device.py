import json
class Device (object):
  name = None
  vendor = None
  required = ['name', 'vendor']
  optional = [ ]
  prefix = 'device'

  def __init__ (self, name, vendor):
    self.name = name
    self.vendor = vendor
    self.fields = dict(vendor=vendor.__name__)
  def section_name (self):
    return '%s "%s"' % (self.prefix, self.name)
  def add_option (self, k, v):
    # section = self.section_name( )
    # self._config.set(section, k, v)
    self.fields[k] = v
    if k not in self.required + self.optional:
      self.optional.append(k)
  def items (self):
    return self.fields.items( )

  def read (self, args=None, config=None):
    if args:
      self.vendor.set_config(args, self)
      self.name = args.name
    if config:
      # self.vendor.read_config(config)
      self.fields.update(dict(config.items(self.section_name( ))))

  def format_url (self):
    parts = ['{0:s}://{1:s}'.format(self.vendor.__name__.split('.').pop( ), self.name), ]
    parts.append(self.vendor.display_device(self))
    return ' '.join(parts)

  @classmethod
  def FromConfig (klass, vendors, config):
    devices = [ ]
    for candidate in config.sections( ):
      if candidate.startswith(klass.prefix):
        name = json.loads(candidate.split(' ').pop( ))
        vendor = vendors.lookup(config.get(candidate, 'vendor').split('.').pop( ))
        device = klass(name, vendor)
        device.read(config=config)
        devices.append(device)
    return devices

