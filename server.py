#/usr/bin/env python3

import io
import time
import threading
import tornado.ioloop
import tornado.web
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

class ImageHandler(tornado.web.RequestHandler):
	def initialize(self, capture):
		self.capture = capture
	def get(self):
		self.set_header("Content-Type", "image/jpeg")
		if self.capture.image is not None:
			self.write(self.capture.image)

class ImageCapture:
	def initialize(self, camera):
		self.running = False
		self.camera = camera
		self.camera.resolution = (1024, 768)
		self.image = None
	def run(self):
		self.running = True
		self.thread = threading.Thread(target=self.thread_method, args=())
		self.thread.start()
	def stop(self):
		self.running = False
	def thread_method(self):
		while self.running:
			print("Starting capture")
			output = io.BytesIO()
			self.camera.capture(output, "jpeg")
			self.image = output.getvalue()
			output.close()
			print("Finished capture")
			time.sleep(0.1)
		self.camera.close()

camera = picamera.PiCamera()

capture = ImageCapture()
capture.initialize(camera)
capture.run()

application = tornado.web.Application([
	(r"/drive/(.+)", DriveHandler, { "m": m }),
	(r"/light/(.+)/(.+)", LightHandler, { "m": m }),
	(r"/image", ImageHandler, { "capture": capture }),
	(r"/(.*)", tornado.web.StaticFileHandler, { "path": "./static", "default_filename": "index.html" })
], debug=True)

if __name__ == "__main__":
	application.listen(8888, "0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()
	capture.stop()
