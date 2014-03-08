#/usr/bin/env python3

import io
import threading
import random
import base64
import tornado.ioloop
import tornado.web
import tornado.websocket
import picamera
import amoebatwo

m = amoebatwo.AmoebaTwo()

class DriveHandler(tornado.web.RequestHandler):
	def initialize(self, m):
		self.m = m
	def get(self, direction):
		if direction == "forwards":
			self.m.move.forwards()
			self.write("Forwards")
		elif direction == "right":
			self.m.move.right()
			self.write("Right")
		elif direction == "left":
			self.m.move.left()
			self.write("Left")
		else:
			self.m.move.stop()
			self.write("Stop")

class LightHandler(tornado.web.RequestHandler):
	def initialize(self, m):
		self.m = m
	def get(self, light, state):
		if light == "top" and state == "on":
			self.m.lights.top.on()
			self.write("Top, On")
		elif light == "top" and state == "off":
			self.m.lights.top.off()
			self.write("Top, Off")
		elif light == "front" and state == "on":
			self.m.lights.front.on()
			self.write("Front, On")
		elif light == "front" and state == "off":
			self.m.lights.front.off()
			self.write("Front, Off")

class ImageCapture:
	def initialize(self, camera):
		self.running = False
		self.camera = camera
		self.camera.resolution = (160, 120)
		self.connections = []
	def run(self):
		if not self.running and len(self.connections) > 0:
			self.running = True
			self.thread = threading.Thread(target=self.thread_method, args=())
			self.thread.start()
	def stop(self):
		self.running = False
	def terminate(self):
		self.running = False
		self.camera.close()
	def thread_method(self):
		output = io.BytesIO()
		for i in self.camera.capture_continuous(output, "jpeg", use_video_port=True):
			if not self.running:
				break
			image = base64.b64encode(output.getvalue())
			output.seek(0)
			output.truncate()
			for o in self.connections:
				o.write_message(image)
		output.close()
	def register_connection(self, connection):
		self.connections.append(connection)
		self.run()
	def deregister_connection(self, connection):
		for i, o in enumerate(self.connections):
			if o.id == connection.id:
				del self.connections[i]
		if len(self.connections) < 1:
			self.stop()

camera = picamera.PiCamera()

capture = ImageCapture()
capture.initialize(camera)

class ImageConnectionHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		global capture
		self.capture = capture
		self.id = random.randint(1, 99999999999)
		self.capture.register_connection(self)
	def on_close(self):
		self.capture.deregister_connection(self)

application = tornado.web.Application([
	(r"/drive/(.+)", DriveHandler, { "m": m }),
	(r"/light/(.+)/(.+)", LightHandler, { "m": m }),
	(r"/image", ImageConnectionHandler),
	(r"/(.*)", tornado.web.StaticFileHandler, { "path": "./static", "default_filename": "index.html" })
], debug=True)

if __name__ == "__main__":
	application.listen(8888, "0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()
	capture.terminate()
