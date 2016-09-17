import tkinter, time
from threading import Thread
from serial import Serial

from lcdsim import LCD
from lcdrender import LCDCanvas

scale = 4
lcd_dimensions = (20, 4)
serialport = "COM3"

master = tkinter.Tk()
master.title("Serial LCD Monitor")
master.call("wm", "resizable", ".", 0, 0)

lcd = LCD()
lcd_renderer = LCDCanvas(master, lcd_dimensions, scale, lcd)
lcd_renderer.render()

class LCDBlinker(Thread):
	"""Yes, this is an actual thing now."""
	def __init__(self, lcd_renderer):
		super().__init__()
		self.lcd_renderer = lcd_renderer
		
	def run(self):
		while True:
			self.lcd_renderer.render_cursor()
			time.sleep(.1)

class LCDListener(Thread):
	def __init__(self, lcd, lcd_renderer):
		super().__init__()
		self.serial = Serial(serialport, timeout=0)
		self.lcd = lcd
		self.lcd_renderer = lcd_renderer
		
		self.blinker = LCDBlinker(lcd_renderer)
		self.blinker.daemon = True
		self.blinker.start()
		
	def run(self):
		old_fragment = bytes()
		while True:
			render = False
			data = self.serial.read(1024);
			if len(old_fragment) > 0:
				data = old_fragment + data
				old_fragment = bytes()
			if len(data) > 0:
				# where could LCD packets be?
				candidates = []
				i = 0
				for x in data:
					# if candidates are too close to end of stream or 
					# upper half of next byte is not 0xF, then ignore
					if x == 0xfe and len(data) - i < 4:
						# Found truncated data, see if we can cram it back in on the next batch.
						old_fragment = data[i:]
					if x == 0xfe and len(data) - i >= 4 and data[i + 1] == 0xbf and data[i + 2] & 0xf0 == 0xf0:
						candidates.append(i)
					i += 1
				
				for addr in candidates:
					#print("{:08b}, {:08b}, {:08b}, {:08b}".format(data[addr], data[addr+1], data[addr+2], data[addr+3]))
					rs = (data[addr + 2] >> 2) & 1
					rw = (data[addr + 2] >> 1) & 1
					enable = data[addr + 2] & 1
					self.lcd.data(rs, rw, enable, data[addr + 3])
					render = True
			if render:
				self.lcd_renderer.render()

listener = LCDListener(lcd, lcd_renderer)
listener.daemon = True
listener.start()

tkinter.mainloop()