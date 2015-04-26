
"""
Medtronic - openaps driver for Medtronic
"""
from openaps.uses.use import Use
from openaps.configurable import Configurable
import decocare
from decocare import stick, session, link, commands, history
from datetime import datetime
from dateutil import relativedelta
from dateutil.parser import parse

def configure_use_app (app, parser):
  pass
  # parser.add_argument('foobar', help="LOOK AT ME")

def configure_add_app (app, parser):
  parser.add_argument('serial')

def configure_app (app, parser):
  if app.parent.name == 'add':
    print "CONFIG INNER", app, app.parent.name, app.name
def configure_parser (parser):
  pass
def main (args, app):
  print "MEDTRONIC", args, app
  print "app commands", app.selected.name


__USES__ = { }
def use ( ):
  def decorator (cls):
    if cls.__name__ not in __USES__:
      __USES__[cls.__name__] = cls
    return cls
  return decorator

@use( )
class scan (Use):
  """ scan for usb stick """
  def configure_app (self, app, parser):
    pass
    # print "hahaha"
  def scanner (self):
    from decocare.scan import scan
    return scan( )
  def main (self, args, app):
    return self.scanner( )

class MedtronicTask (scan):
  requires_session = True
  save_session = True
  record_stats = True
  def before_main (self, args, app):
    self.setup_medtronic( )
    if self.requires_session:
      self.check_session(app)
  def after_main (self, args, app):
    if self.save_session:
      self.device.store(app.config)
      app.config.save( )
  def get_session_info (self):
    expires = self.device.fields.get('expires', None)
    now = datetime.now( )
    out = dict(device=self.device.name
      , vendor=__name__
      , used=now
      )
    if expires is None or parse(expires) < now:
      fields = self.create_session( )
      self.device.add_option('expires', fields['expires'].isoformat( ))
      self.device.add_option('model', fields['model'])
      out['expires'] = fields['expires']
      out['model'] = fields['model']
    else:
      out['expires'] = parse(expires)
      out['model'] = self.get_model( )
    return out
  def create_session (self):
    minutes = int(self.device.fields.get('minutes', 10))
    self.pump.power_control(minutes=minutes)
    model = self.get_model( )
    now = datetime.now( )
    offset = relativedelta.relativedelta(minutes=minutes)
    out = dict(device=self.device.name
      , model=model
      , vendor=__name__
      , created_at=now
      , started=now
      , expires=now + offset
      )
    return out
  def check_session (self, app):
    self.session = self.get_session_info( )
    self.device.add_option('model', self.device.fields.get('model', self.get_model( )))
  def get_model (self):
    model = self.pump.read_model( ).getData( )
    return model
  def setup_medtronic (self):
    self.uart = stick.Stick(link.Link(self.scanner( )))
    self.uart.open( )
    serial = self.device.fields['serial']
    self.pump = session.Pump(self.uart, serial)
    stats = self.uart.interface_stats( )
  def main (self, args, app):
    return self.scanner( )

class Session (MedtronicTask):
  """ session for pump
  """
  def configure_parser (self, parser):
    parser.add_argument('--minutes', type=int, default='10')
  def setup_application (self):
    print self.parser, self
  def main (self, args, app):
    self.pump.power_control(minutes=args.minutes)
    model = self.pump.read_model( ).getData( )
    offset = relativedelta.relativedelta(minutes=args.minutes)
    created_at = datetime.now( )
    out = dict(device=self.device.name
      , model=model
      , vendor=__name__
      , created_at=created_at
      , started=created_at
      , expires=created_at + offset
      )
    return out

@use( )
class model (MedtronicTask):
  """ Get model number
  """
  def configure_app (self, app, parser):
    pass
  def main (self, args, app):
    model = self.pump.read_model( ).getData( )
    return model

@use( )
class status (MedtronicTask):
  """ Get pump status
  """
  def main (self, args, app):
    return self.pump.model.read_status( )

@use( )
class reservoir (MedtronicTask):
  """ Get pump remaining insulin
  """
  def main (self, args, app):
    return self.pump.model.read_reservoir( )

@use( )
class settings (MedtronicTask):
  """ Get pump remaining insulin
  """
  def main (self, args, app):
    return self.pump.model.read_settings( )


@use( )
class read_temp_basal (MedtronicTask):
  """ Get pump remaining insulin
  """
  def main (self, args, app):
    return self.pump.model.read_temp_basal( )

@use( )
class Pump (Session):
  """ Query pump model
  """
  pass

@use( )
class CGM (Session):
  """ Query CGM model
  """
  pass

def set_config (args, device):
  device.add_option('serial', args.serial)

def display_device (device):
  return ''

known_uses = [
  Session,
  # Device, Pump, CGM
] + __USES__.values( )
def get_uses (device, config):
  return  known_uses[:]



