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

class ImageCapture:
	def initialize(self, camera, callback):
		self.running = False
		self.camera = camera
		self.camera.resolution = (160, 120)
		self.callback = callback
	def run(self):
		if not self.running:
			self.running = True
			self.thread = threading.Thread(target=self.thread_method, args=())
			self.thread.start()
	def stop(self):
		if self.running:
			self.running = False
	def terminate(self):
		self.running = False
		self.camera.close()
	def thread_method(self):
		output = io.BytesIO()
		for i in self.camera.capture_continuous(output, "jpeg", use_video_port=True):
			if not self.running:
				break
			image = str(base64.b64encode(output.getvalue()))
			output.seek(0)
			output.truncate()
			self.callback(image)
			time.sleep(0.1)
		output.close()

class ClientManager:
	def __init__(self, image_capture):
		self.connections = []
		self.panic = False
		self.image_capture = image_capture
	def register_client(self, connections):
		self.connections.append(connections)
		self.send_message("COMMAND_USERS", len(self.connections))
	def deregister_client(self, connection):
		for i, c in enumerate(self.connections):
			if c.id == connection.id:
				self.connections[i].close()
				del self.connections[i]
		self.send_message("COMMAND_USERS", len(self.connections))
	def send_message(self, command, data = None):
		for c in self.connections:
			c.send_message(command, data)
	def takeover(self, connection, is_admin):
		any_has_control = False
		for c in self.connections:
			if c.has_control and c.id != connection.id:
				any_has_control = True
		if is_admin or not any_has_control:
			for c in self.connections:
				if c.id == connection.id:
					c.has_control = True
					c.send_message("COMMAND_TAKENOVER")
				else:
					c.has_control = False
					c.send_message("COMMAND_YIELDED")
	def update_camera(self):
		has_cameras = False
		for c in self.connections:
			if c.camera_enabled:
				has_cameras = True
		if has_cameras:
			self.image_capture.run()
		else:
			self.image_capture.stop()
	def distribute_image(self, image):
		for c in self.connections:
			if c.camera_enabled:
				c.send_message("CAMERA_IMAGE", { "image": image })

m = amoebatwo.AmoebaTwo()
capture = ImageCapture()
manager = ClientManager(capture)
camera = picamera.PiCamera()
capture.initialize(camera, manager.distribute_image)

class SocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		global m
		global manager
		self.m = m
		self.manager = manager
		self.id = random.randint(1, 999999999999)
		self.camera_enabled = False
		self.has_control = False
		self.manager.register_client(self)
		self.admin_keyword = "cja"
	def on_close(self):
		self.manager.deregister_client(self)
	def on_message(self, message):
		data = json.loads(message)
		if "command" not in data:
			return
		cmd = data["command"]
		is_admin = "data" in data and "admin" in data["data"] and data["data"]["admin"] == self.admin_keyword
		if self.has_control and not self.manager.panic:
			if cmd == "DRIVE_FORWARD":
				self.m.move.forwards()
				self.manager.send_message(cmd)
			elif cmd == "DRIVE_RIGHT":
				self.m.move.right()
				self.anager.send_message(cmd)
			elif cmd == "DRIVE_LEFT":
				self.m.move.left()
				self.manager.send_message(cmd)
			elif cmd == "DRIVE_STOP":
				self.m.move.stop()
				self.manager.send_message(cmd)
			elif cmd == "COMMAND_YIELD":
				self.m.move.stop()
				self.has_control = False
				self.manager.send_message("COMMAND_YIELDED")
		if cmd == "COMMAND_TAKEOVER":
			self.manager.takeover(self, is_admin)
		if cmd == "LIGHT_FRONT_ON":
			self.m.lights.front.on()
			self.manager.send_message(cmd)
		elif cmd == "LIGHT_FRONT_OFF":
			self.m.lights.front.off()
			self.manager.send_message(cmd)
		elif cmd == "LIGHT_TOP_ON":
			self.m.lights.top.on()
			self.manager.send_message(cmd)
		elif cmd == "LIGHT_TOP_OFF":
			self.m.lights.top.off()
			self.manager.send_message(cmd)
		elif cmd == "PANIC":
			self.m.move.stop()
			self.manager.panic = True
			self.manager.send_message(cmd)
		elif cmd == "UNPANIC" and is_admin:
			self.m.move.stop()
			self.manager.panic = False
			self.manager.send_message(cmd)
		elif cmd == "CAMERA_ON":
			self.camera_enabled = True
			self.manager.update_camera()
			self.send_message(cmd)
		elif cmd == "CAMERA_OFF":
			self.camera_enabled = False
			self.manager.update_camera()
			self.send_message(cmd)
	def send_message(self, command, data = None):
		self.write_message(json.dumps({ "command": command, "data": data }))

application = tornado.web.Application([
	(r"/socket", SocketHandler),
	(r"/(.*)", tornado.web.StaticFileHandler, { "path": "./static", "default_filename": "index.html" })
], debug=True)

if __name__ == "__main__":
	application.listen(8888, "0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()
	capture.terminate()
