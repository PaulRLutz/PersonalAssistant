"""
  First POST:
    initial_input (str)
  Following POSTS:
    interaction_id (str)
    input (str)
  Response:
    interaction_id (str)
    output (str)
    prompt (str)
    finished (bool)

  Test CURL:
  curl -X POST --data "user_input=hello" localhost:6666
"""

import http.server
import urllib
from threading import Thread
from base_classes.Input import Input
import time
import readline
import os
import json
import uuid

class HttpInput(Input):
  def __init__(self, log, assistant):
    self.log = log
    self.assistant = assistant
    
    self.interaction_output_queue = {}
    self.interaction_output_queue_status = {}
    self.interaction_output_queue_finished_status = {}

    self.LOG_FOLDER = self.assistant.LOG_FOLDER + os.sep + "http_input_user_logs"
    if not os.path.exists(self.LOG_FOLDER):
      os.makedirs(self.LOG_FOLDER)

  def start(self):
    port=6666 # TODO port number in config
    self.log.debug("Starting HTTP Server on port: {}".format(str(port)))

    self.http_server = http.server.HTTPServer(("", port), MyHttpHandler)

    self.http_server.assistant_input = self
    self.http_server.assistant = self.assistant
    self.http_server.log = self.log
    
    self.thread = Thread(target = self.http_server.serve_forever)
    self.thread.start()

  def stop(self):
    self.log.debug("Stopping http input")
    if self.http_server is not None:
      self.http_server.shutdown()
      self.http_server.server_close()
      self.thread.join()
    else:
      self.log.warn("Http server didn't exist")

  def send_output(self, output_text, interaction_id):
    if interaction_id not in self.interaction_output_queue:
      self.interaction_output_queue[interaction_id] = []
    self.interaction_output_queue[interaction_id].append(output_text)
    self.interaction_output_queue_status[interaction_id] = True

  def get_input(self, prompt_text, interaction_id):
    self.interaction_output_queue[interaction_id] = [prompt_text]

  def finished(self, output_text, interaction_id):
    self.interaction_output_queue_finished_status[interaction_id] = True
    self.send_output(output_text, interaction_id)

  def get_interaction_output(self, interaction_id):
    if interaction_id in self.interaction_output_queue_status and self.interaction_output_queue_status[interaction_id]:
      self.interaction_output_queue_status[interaction_id] = False
      output = self.interaction_output_queue[interaction_id]
    else:
      output = None

    if interaction_id in self.interaction_output_queue_finished_status:
      finished = self.interaction_output_queue_finished_status[interaction_id]
    else:
      finished = False
    
    return output, finished

class MyHttpHandler(http.server.BaseHTTPRequestHandler):
  def _set_headers(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

  def do_HEAD(self):
    self._set_headers()

  def do_POST(self):
    self.log_http_request()
    length = int(self.headers.get('content-length', 0))
    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    post_data = self.rfile.read(content_length) # <--- Gets the data itself
    print("POST DATA")
    print(str(post_data))
    print(str(type(post_data)))

    #post_data = self.rfile.read(length).decode('utf-8')
    #post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

    self.server.log.debug("New post:")
    self.server.log.debug(str(type(post_data)))
    self.server.log.debug(str(post_data))
    
    self._set_headers()
    post_data = post_data.decode("utf-8")

    self.server.log.debug("New post utf-8:")
    self.server.log.debug(str(type(post_data)))
    self.server.log.debug(str(post_data))

    post_data = json.loads(post_data)
    assistant_data = json.dumps(self.handle_post(post_data))

    self.wfile.write(str.encode(assistant_data))

    
  def handle_post(self, post_data):
    if "user_input" not in post_data:
      self.server.log.warn(f"Got http post without user input: '{post_data}'")
      return "Please include user input"
    if "interaction_id" in post_data:
      self.server.log.debug("interaction_id found, continuing interaction")
      interaction_id = post_data["interaction_id"]
    else:
      self.server.log.debug("no interaction_id, starting a new interaction")
      interaction_id = self.server.assistant.new_user_input(post_data["user_input"], input_object=self.server.assistant_input)
      interaction_id = str(interaction_id)

    response_dict = {"interaction_id" : interaction_id}
    interaction_id_uuid = uuid.UUID(interaction_id)
    wait_time = 0.5 # TODO put in config
    timeout = 5
    duration = 0

    while duration < timeout:
      interaction_output, finished = self.server.assistant_input.get_interaction_output(interaction_id_uuid)
      response_dict["finished"] = finished
      if interaction_output is not None:
        response_dict["output"] = "\n".join(interaction_output)
        break
      time.sleep(wait_time)
      duration += wait_time
    else:
      response_dict["output"] = "Timeout processing request"

    return response_dict

  def log_message(self, format, *args):
    return

  def log_http_request(self):
    timestamp = time.time()
    
    logDict = {}
    logDict["timestamp"] = timestamp
    logDict["command"] = self.command
    logDict["path"] = self.path
    logDict["client_address"] = self.client_address

    self.server.log.debug("New http request")
    self.server.log.debug(str(logDict))
