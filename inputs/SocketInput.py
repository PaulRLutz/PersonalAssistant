import socket
from threading import Thread

class SocketInput:
  def __init__(self, log, processing_queue):
    self.log = log
    self.processing_queue = processing_queue

    self.HOST = "192.168.1.28"
    self.PORT = 65432

    self.running = True
    self.thread = Thread(target=self.socket_server())

  def start(self):
    self.running = True

    self.thread.start()

  def stop(self):
    self.running = False
    self.thread.join()

  def socket_server(self):
    print("starting socket server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.bind((self.HOST, self.PORT))
      s.listen()
      self.conn, self.addr = s.accept()
      with self.conn:
        print('Connected by', self.addr)
        while self.running:
          data = self.conn.recv(4096)
          if not data:
            break
          print(data.decode().strip())
          print("Sending response...")
          self.conn.sendall(b"THIS IS A RECORDING")
          #self.send_output("HI", 666)

  def send_output(self, output_text, interaction_id):
    self.conn.sendall(b"THIS IS A RECORDING")

  def get_input(self, prompt_text, interaction_id):
    raise NotImplementedError

  def finished(self, output_text, interaction_id):
    raise NotImplementedError

