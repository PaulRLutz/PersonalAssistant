from base_classes.Plugin import Plugin
import time
import serial
import serial.tools.list_ports
import traceback
import termios

FAN_NUM = 1
STARS_NUM = 2
ORB_NUM = 3
CHAIR_LIGHT_NUM = 5
class ArduinoPlugin(Plugin):


  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.serial_connection = None

    self.tv_audio_commands = ['RCA_PWR', 'RCA_VOL_UP', 'RCA_VOL_DN', 'RCA_MUTE']

    self.sony_tv_commands = {'VOL_DN': '0xc90', 'NINE': '0x110', 'RGB_IN_2': '0x230', 'SIX': '0xa10', 'TWO': '0x810', 'DOWN': '0xaf0', 'PWR_ON': '0x750', 'DISPLAY': '0x5d0', 'VID_5': '0x130', 'VID_4': '0xe30', 'VID_6': '0x930', 'VID_1': '0x30', 'VID_3': '0x430', 'VID_2': '0x830', 'ONE': '0x10', 'VIDEO': '0xa50', 'EIGHT': '0xe10', 'CH_DN': '0x890', 'PWR_OFF': '0xf50', 'LEFT': '0x2d0', 'MENU_ENTER': '0xa70', 'MUTE': '0x290', 'THREE': '0x410', 'ZERO': '0x910', 'FIVE': '0x210', 'RGB_IN_1': '0xc30', 'CH_UP': '0x90', 'FOUR': '0xc10', 'SEVEN': '0x610', 'RIGHT': '0xcd0', 'PWR': '0xa90', 'MENU': '0x70', 'UP': '0x2f0', 'EXIT': '0xc70', 'VOL_UP': '0x490'}


  def cmd_peace_out(self):
    """Turns off shit
    Returns:
      bool: True if successful, False otherwise.
      str: Notifies user of command.
    """
    self.cmd_chair_light("off")
    time.sleep(.1)
    self.cmd_orb("off")
    time.sleep(.1)
    self.cmd_fan("off")
    time.sleep(.1)
    self.cmd_tv_off()
    time.sleep(.1)
    self.cmd_stars("off")
    time.sleep(.1)
    return True, "peace out, dog"

  def cmd_wake_up(self):
    """Turns on shit
    Returns:
      bool: True if successful, False otherwise.
      str: Notifies user of command.
    """
    self.cmd_stars("on")
    time.sleep(.1)
    self.cmd_tv_on()
    time.sleep(.1)
    self.cmd_orb("on")
    time.sleep(.1)
    self.cmd_fan("on")
    time.sleep(.1)
    self.cmd_chair_light("on")
    time.sleep(.1)
    return True, "welcome home"




  def cmd_tv_on(self):
    """Turn off the tv.
    Returns:
      bool: True if successful, False otherwise.
      str: Notifies user of command.
    """
    success = self.send_serial(f"TVCMD {self.sony_tv_commands['PWR_ON']}")
    return success, "tv on"

  def cmd_tv_off(self):
    """Turn on the tv.
    Returns:
      bool: True if successful, False otherwise.
      str: Notifies user of command.
    """
    success = self.send_serial(f"TVCMD {self.sony_tv_commands['PWR_OFF']}")
    return success, "tv off"

  def cmd_tv_audio(self, command=None): #TODO finish docstring
    """Controls the tv audio.
    Returns:
      bool: True if successful, False otherwise.
      str: Notifies user of command.
    """
    if command == "power":
      success = self.send_serial("AUDIOCMD RCA_PWR")
    elif command == "up":
      success = self.send_serial("AUDIOCMD RCA_VOL_UP")
    elif command == "down":
      success = self.send_serial("AUDIOCMD RCA_VOL_DN")
    elif command == "mute" or command == "unmute":
      success = self.send_serial("AUDIOCMD RCA_VOL_MUTE")
    else:
      return False, f"don't recognize tv audio command {command}"

    return True, f"tv audio {command}"

  def cmd_all_lights(self, command):
    """Control all of the room lights.""" # TODO docstring
    if command in ["on", "off"]:
      success_a = self.send_serial(f"LIGHT {command.upper()}")
      success_b = self.cmd_chair_light(f"{command.lower()}")
    else:
      return False, f"don't recognize lights command command"
    return True, f"lights {command}"

  def cmd_room_lights(self, command):
    """Control the room lights.""" # TODO docstring
    if command in ["on", "off", "up", "down"]:
      success = self.send_serial(f"LIGHT {command.upper()}")
    else:
      return False, f"don't recognize lights command command"
    return True, f"lights {command}"

  def cmd_chair_light(self, command): # TODO docstring
    if command == "on":
      success = self.send_serial(f"RF {CHAIR_LIGHT_NUM}1")
    elif command == "off":
      success = self.send_serial(f"RF {CHAIR_LIGHT_NUM}0")
    return True, f"chair light {command}"

  def cmd_fan(self, command): # TODO docstring
    if command == "on":
      success = self.send_serial(f"RF {FAN_NUM}1")
    elif command == "off":
      success = self.send_serial(f"RF {FAN_NUM}0")
    return True, f"fan {command}"

  def cmd_stars(self, command): # TODO docstring
    if command == "on":
      success = self.send_serial(f"RF {STARS_NUM}1")
    elif command == "off":
      success = self.send_serial(f"RF {STARS_NUM}0")
    return True, f"stars {command}"

  def cmd_orb(self, command): # TODO docstring
    if command == "on":
      success = self.send_serial(f"RF {ORB_NUM}1")
    elif command == "off":
      success = self.send_serial(f"RF {ORB_NUM}0")
    return True, f"orb {command}"


  """
  def cmd_wireless(self, command): # TODO docstring
    if command == "on":
      success = self.send_serial(f"RF {WIRELESS_NUM}1")
    elif command == "off":
      success = self.send_serial(f"RF {WIRELESS_NUM}0")
    elif command == "restart":
      success_a = self.send_serial(f"RF {WIRELESS_NUM}0")
      time.sleep(2)
      success_b = self.send_serial(f"RF {WIRELESS_NUM}1")
    return True, f"wireless {command}"
  """

  def cmd_computer_lights(self, color="default"):
    color_dict = {
        "default" : "0xEE55EE",
        "red" : "0xFF0000",
        "green" : "0x0000FF",
        "blue" : "0x00FF00",
        "off" : "0x000000",
        }
    if color not in color_dict.keys():
      return False, f"couldn't find color {color}"
    else:
      success = self.send_serial(f"COLOR {color_dict[color]}")
      return success, f"computer lights {color}"

  def start(self):
    if self.serial_connection is None:
      self.serial_connection = self.get_serial_connection()
      if self.serial_connection is not None:
        self.log.debug("serial connection made")
      else:
        self.log.warn("serial connection failed")
    else:
      self.log.warn("serial is already connected, try 'reconnect'")
  
  def stop(self):
    if self.serial_connection is None:
      self.log.warn("no serial connection exists")
    else:
      self.close_serial_connection()
 
  def get_serial_connection(self, timeout=1):
  
    available_ports = list(serial.tools.list_ports.comports())
    self.log.debug(f"found '{len(available_ports)}' serial ports.")

    for p in available_ports:
      self.log.debug("found port with info:")
      for p_item in p:
        self.log.debug(p_item)
      if "VID:PID=2341:0001" in p[2]:
        self.log.warn(f"Found Arduino at port: {str(p[0])}")
        try:
          temp_serial_connection = serial.Serial(p[0], 9600, timeout=timeout)
          time.sleep(.1)
          temp_serial_connection.flushInput()
          time.sleep(.1)
          temp_serial_connection.write(b"STATUS")
          time.sleep(.1)
          response = temp_serial_connection.readline().strip()
          if response == b"ready":
            self.log.debug(f"arduino connection successful (response: '{response}')")
          else:
            self.log.debug(f"arduino connection unsuccessful (response: '{response}')")
          return temp_serial_connection
        except:
          self.log.warn("problem connecting with arduino")
          self.log.warn(traceback.format_exc())
          
    return None
    
  def close_serial_connection(self):
    self.serial_connection.close()
    self.serial_connection = None
    
    
  def send_serial(self, send_string, attempt=1):
    self.log.warn(f"Sending serial: {send_string}")
    try:
      self.serial_connection.flushInput()
      time.sleep(.1)
      self.serial_connection.write(str.encode(send_string))
      time.sleep(.1)
      response = self.serial_connection.readline().strip()
      self.log.debug(f"Arduino response: '{response}'")
      success_string = str.encode(f"done '{send_string}'")
      if response == success_string:
        return True
      elif response == "":
        self.log.warn("Error getting Arduino response.")
        return False
      else:
        self.log.warn("Unkown Arduino error")
        return False
      return True
    except (termios.error, serial.SerialException) as e:
      self.log.warn(f"sending serial failed (attempt #: {attempt})")
      self.log.warn(e)
      if attempt > 3: # TODO Put max attempts into config file
        return False
      else:
        self.stop()
        time.sleep(1)
        self.start()
        attempt+=1
        return self.send_serial(send_string, attempt=attempt)


