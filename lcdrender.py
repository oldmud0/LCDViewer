import tkinter, time

class LCDCanvas:
	"""Tkinter renderer for the LCD"""
	
	bg = "#87AD34"
	fg_hard = "#050505"
	fg_soft = "#7C9F31"
	
	cursor_drawn = False
	
	# This size mapping dictionary defines where each row begins in DDRAM based on the LCD size.
	size_mappings = {
		(40, 2): [0x0, 0x40],
		(20, 4): [0x0, 0x40, 0x14, 0x54],
		(20, 2): [0x0, 0x40],
		(16, 2): [0x0, 0x40],
		(16, 1): [0x0], # Type 2 LCD; Type 1 not supported
		(16, 4): [0x0, 0x40, 0x10, 0x50]
	}
	
	def __init__(self, master, size, scale, lcd):
		#self.lcd = [[0 for c in range(width)] for r in range(height)]
		if not (size in self.size_mappings):
			raise NotImplementedError("Size " + size + " not implemented")
		
		self.w, self.h = size
		self.scale = scale
		self.lcd = lcd
		
		self.canvas = tkinter.Canvas(master, width=(6 * self.w + 1) * scale, height=(9 * self.h + 1)* scale, bg=self.bg, highlightthickness=0)
		self.canvas.pack()
		
	def render(self):
		self.canvas.delete("pixel")
		self.clear_cursor()
		
		s = self.scale
		if self.lcd.d: # if display is on
			for r in range(self.h):
				for c in range(self.w):
					char_addr = self.lcd.ddram[self.size_mappings[(self.w, self.h)][r] + c]
					#print(char_addr)
					for p_x in range(5):
						for p_y in range(8):
							if (self.lcd.cgram[char_addr * 8 + p_y] << p_x) & 0b10000 == 0b10000:
								#self.canvas.create_rectangle((c * p_x + 1) * s, (r * p_y + 1) * s, ((c+1) * p_x) * s, ((r+1) * p_y) * s, fill=self.fg_hard, width=0)
								self.canvas.create_rectangle((c * 6 + p_x + 1) * s, (r * 9 + p_y + 1) * s, (c * 6 + p_x + 2) * s, (r * 9 + p_y + 2) * s, fill=self.fg_hard, width=0, tags="pixel")
		else:
			for r in range(self.h):
				for c in range(self.w):
					self.canvas.create_rectangle((c * 6 + 1) * s, (r * 9 + 1) * s, ((c+1) * 6) * s, ((r+1) * 9) * s, fill=self.fg_soft, width=0)
		self.canvas.update_idletasks()
	
	def render_cursor(self):
		t = time.clock() % 1
		if (self.lcd.c or True) and (0 <= t <= .25 or .5 <= t <= .75): # draw cursor
			if not self.cursor_drawn:
				s = self.scale
				r = 0
				for addr in self.size_mappings[(self.w, self.h)]:
					if r == self.h - 1: break # Invisible cursor should not be drawn!
					if addr <= self.lcd.ddram_addr < addr + self.w:
						break
					r += 1
				if r > self.h - 1:
					return
				c = self.lcd.ddram_addr - self.size_mappings[(self.w, self.h)][r]
				self.canvas.create_rectangle((c * 6 + 1) * s, (r * 9 + 8) * s, (c * 6 + 6) * s, (r * 9 + 9) * s, fill=self.fg_hard, width=0, tags="cursor")
				self.cursor_drawn = True
		else:
			self.clear_cursor()
	
	def clear_cursor(self):
		if self.cursor_drawn:
			self.canvas.delete("cursor")
			self.cursor_drawn = False