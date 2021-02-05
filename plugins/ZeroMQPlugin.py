from base_classes.Plugin import Plugin
from threading import Thread
import zmq
import json


class ZeroMQPlugin(Plugin):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


  def start(self):
    self.zmq_running = True

    self.zmq_status_server_thread = Thread(target=self.zmq_status_server)
    self.zmq_status_server_thread.start()

  def stop(self):
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    socket.send(b"quit")

  def zmq_status_server(self):
    context = zmq.Context()
    self.zmq_socket = context.socket(zmq.REP)
    self.zmq_socket.bind("tcp://*:5555")   

    while self.zmq_running:
      message = self.zmq_socket.recv()
      #self.log.debug(f"received zmq request: {message}")
      
      if message == b"status":
        data_to_send = self.assistant.status_dict
      elif message == b"widget_templates":
        data_to_send = self.assistant.status_templates_config_dict
      elif message == b"quit":
        self.zmq_running = False
        continue
      else:
        data_to_send = {}
      
      self.zmq_socket.send(str.encode(json.dumps(data_to_send)))




