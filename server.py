#/usr/bin/env python3

import tornado.ioloop
import tornado.web
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

application = tornado.web.Application([
	(r"/drive/(.+)", DriveHandler, { "m": m }),
	(r"/light/(.+)/(.+)", LightHandler, { "m": m })
])

if __name__ == "__main__":
	application.listen(8888, "0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()
