"""
  TODO:
    false positive on networks with login portal
    timeout is definitely not working    
"""

import socket

def internet_check(url="www.google.com", port=80, timeout=2):
  try:
    socket.setdefaulttimeout(timeout)
    s = socket.create_connection((url, port), timeout=timeout)
    s.close()
    return True
  except OSError:
    pass
  return False

class NoInternetException(Exception):
  pass
