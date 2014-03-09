#/usr/bin/env python3

import io
import threading
import random
import base64
import json
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
import picamera
import amoebatwo

class RobotState:
	def __init__(self):
		self.panic = False
		self.control_available = True
		self.drive = "STOP"
		self.top_light = False
		self.front_light = False
		self.user_count = 0
		self.users = []
		
class ClientState:
	def __init__(self):
		self.id = random.randint(1, 999999999999)
		self.is_admin = False
		self.name = "Unnamed Being"
		self.has_control = False
		self.camera_on = False

class ImageCapture:
	def initialize(self, camera, callback):
		self.stop = threading.Event()
		self.stop.set()
		self.camera = camera
		self.camera.resolution = (160, 120)
		self.callback = callback
	def run(self):
		if self.stop.isSet():
			self.stop = threading.Event()
			self.thread = threading.Thread(target=self.thread_method, args=())
			self.thread.start()
	def stop(self):
		if not self.stop.isSet():
			self.stop.set()
	def terminate(self):
		self.stop.set()
		self.camera.close()
	def thread_method(self):
		output = io.BytesIO()
		for i in self.camera.capture_continuous(output, "jpeg", use_video_port=True):
			if self.stop.isSet():
				break
			image = base64.b64encode(output.getvalue()).decode("utf-8")
			output.seek(0)
			output.truncate()
			self.callback(image)
			time.sleep(0.05)
		output.close()

class ClientManager:
	def __init__(self, m, image_capture, password):
		self.connections = []
		self.m = m
		self.image_capture = image_capture
		self.password = password
		self.state = RobotState()
	def send_message(self, command, data = {}):
		for c in self.connections:
			c.send_message(command, data)
	def update_state(self):
		any_camera_on = True
		self.state.user_count = len(self.connections)
		for c in self.connections:
			if c.state.has_control:
				self.state.control_available = False
			if c.state.camera_on:
				any_camera_on = True
		if any_camera_on:
			self.image_capture.run()
		else:
			self.image_capture.stop()
	def get_users(self):
		users = []
		for c in self.connections:
			users.append(c.state.__dict__)
		return users
	def notify_state(self):
		self.update_state()
		for c in self.connections:
			if c.state.is_admin:
				self.state.users = self.get_users()
			else:
				self.state.users = []
			msg = json.dumps({ "command": "STATE", "data": { "robot": self.state.__dict__, "client": c.state.__dict__ } })
			c.send_message_string(msg)
	def register_client(self, connection):
		self.connections.append(connection)
		self.notify_state()
	def deregister_client(self, connection):
		for i, c in enumerate(self.connections):
			if c.state.id == connection.state.id:
				del self.connections[i]
		if connection.state.has_control:
			self.state.control_available = True
		self.notify_state()
	def take_control(self, connection):
		if connection.state.is_admin:
			self.remove_control()
		elif not self.state.control_available or connection.state.has_control:
			return
		self.state.control_available = False
		connection.state.has_control = True
	def yield_control(self, connection):
		if not connection.state.has_control or self.state.control_available:
			return
		connection.has_control = False
		self.state.control_available = True
	def distribute_image(self, image):
		for c in self.connections:
			if c.state.camera_on:
				c.send_message("CAMERA_IMAGE", { "image": image })
	def forward(self):
		self.m.move.forwards()
		self.state.drive = "FORWARD"
	def right(self): 
		self.m.move.right()
		self.state.drive = "RIGHT"
	def left(self):
		self.m.move.left()
		self.state.drive = "LEFT"
	def stop(self):
		self.m.move.stop()
		self.state.drive = "STOP"
	def remove_control(self):
		for c in self.connections:
			c.state.has_control = False
		self.state.control_available = True
	def panic(self):
		self.stop()
		self.remove_control()
		self.state.panic = True
	def unpanic(self):
		self.stop()
		self.remove_control()
		self.state.panic = False
	def handle_message(self, connection, command, data):
		self.update_state()
		if connection.state.has_control and not self.state.control_available and not self.state.panic:
			if command == "DRIVE_FORWARD":
				self.forward()
			elif command == "DRIVE_RIGHT":
				self.right()
			elif command == "DRIVE_LEFT":
				self.left()
			elif command == "DRIVE_STOP":
				self.stop()
			elif command == "COMMAND_YIELD":
				self.yield_control(connection)
				self.remove_control()
		if command == "COMMAND_TAKEOVER":
			self.take_control(connection)
		if command == "LIGHT_FRONT_ON":
			self.m.lights.front.on()
			self.state.front_light = True
		elif command == "LIGHT_FRONT_OFF":
			self.m.lights.front.off()
			self.state.front_light = False
		elif command == "LIGHT_TOP_ON":
			self.m.lights.top.on()
			self.state.top_light = True
		elif command == "LIGHT_TOP_OFF":
			self.m.lights.top.off()
			self.state.top_light = False
		elif command == "PANIC":
			self.panic()
		elif command == "UNPANIC" and connection.state.is_admin:
			self.unpanic()
		elif command == "ELEVATE" and not connection.state.is_admin:
			if "password" in data and data["password"] == self.password:
				connection.state.is_admin = True
		elif command == "CAMERA_ON":
			connection.state.camera_on = True
		elif command == "CAMERA_OFF":
			connection.state.camera_on = False
		self.notify_state()

with open("admin_password", "r") as f:
	admin_password = f.read().strip()
		
m = amoebatwo.AmoebaTwo()
capture = ImageCapture()
manager = ClientManager(m, capture, admin_password)
camera = picamera.PiCamera()
capture.initialize(camera, manager.distribute_image)

class Client(tornado.websocket.WebSocketHandler):
	def open(self, name):
		global manager
		self.manager = manager
		self.state = ClientState()
		if name:
			self.state.name = name.decode("utf-8")
		self.manager.register_client(self)
	def on_close(self):
		self.manager.deregister_client(self)
	def on_message(self, message):
		message_data = json.loads(message)
		if "command" not in message_data:
			return
		cmd = message_data["command"]
		data = message_data["data"] if "data" in message_data else {}
		self.manager.handle_message(self, cmd, data)
	def send_message(self, command, data = None):
		self.send_message_string(json.dumps({ "command": command, "data": data }))
	def send_message_string(self, message):
		self.write_message(message)

application = tornado.web.Application([
	(r"/socket/(.+)", Client),
	(r"/(.*)", tornado.web.StaticFileHandler, { "path": "./static", "default_filename": "index.html" })
], debug=True)

if __name__ == "__main__":
	application.listen(8888, "0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()
	capture.terminate()
