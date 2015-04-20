
"""
show   - show all devices
"""

from openaps.devices.device import Device
from openaps import vendors

def configure_app (app, parser):
  parser.set_defaults(name='*')
  parser._actions[-1].nargs = '?'
def main (args, app):
  print args
  for device in Device.FromConfig(vendors, app.config):
    print device.format_url( )

