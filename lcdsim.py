from charmap import charmap

class LCD:
	"""Hitachi HD44780 LCD simulation"""
	
	ddram = bytearray([20] * 104)
	cgram = bytearray(64)
	
	rl = 1  # shift left/right
	sc = 0  # 0 = move cursor; 1 = shift display
	
	dl = 1  # 0 = 4-bit interface; 1 = 8-bit interface
	n = 0   # 0 = 1 line; 1 = 2 lines
	f = 0   # 0 = 5x8 dots; 1 = 5x10 dots
	
	d = 0   # display on/off
	c = 0   # cursor on/off
	b = 0   # cursor blink on/off
	
	id = 1  # decrement/increment cursor position
	s = 0   # display shift on/off
	
	latch = False # If 4-bit mode, are we awaiting a second set of 4 bits?
	fourBitBuf = 0
	
	ram_type = 0 # 0 = CGRAM, 1 = DDRAM
	ddram_addr = 0
	cgram_addr = 0
	
	def __init__(self):
		# Generate cgram from character map
		cgram = bytearray()
		for char in charmap:
			cgram += bytearray(char)
		self.cgram = cgram
	
	def data(self, rs, rw, enable, data):
		if not self.dl:
			# 4-bit mode - data is in D7..D4
			self.latch = not self.latch
			if self.latch:
				# This is the first half of data
				self.fourBitBuf = data >> 4 # Latch as D3..D0
				#print("L1", format(self.fourBitBuf, "08b"))
				return
			if not self.latch:
				# This is the second half of data
				#print("L2", format(data, "08b"))
				data &= 0xf0 # ignore D3..D0 on second half
				data |= self.fourBitBuf # merge first and second halves together
		#print(format(data, "08b"))
		if rs and rw:
			# read data
			print("(Reading data is not supported)")
			pass
		elif rs:
			# write data to CGRAM/DDRAM
			if self.ram_type:
				self.ddram[self.ddram_addr] = data
				self.ddram_addr = (self.ddram_addr + 1) % len(self.ddram) # increment addr and loop over
				if self.s:
					# shift the entire DDRAM based on I/D
					self.ddram = self.ddram[self.id:] + self.ddram[:self.id]
			else:
				self.cgram[self.cgram_addr] = data
				self.cgram_addr = (self.cgram_addr) % len(self.cgram)
		elif rw:
			# read busy flag + address
			print("(Reading is not supported)")
			pass
		elif data >> 7 == 1:
			# DDRAM address set
			self.ddram_addr = data & 0x7f
			self.ram_type = 1
		elif data >> 6 == 1:
			# CGRAM address set
			self.cgram_addr = data & 0x3f
			self.ram_type = 0
		elif data >> 5 == 1:
			# function set (interface, display line, font)
			self.dl = (data >> 4) & 1
			self.n = (data >> 3) & 1
			self.f = (data >> 2) & 1
		elif data >> 4 == 1:
			# cursor-move/display-shift, shift direction
			self.sc = (data >> 3) & 1
			self.rl = (data >> 2) & 1
		elif data >> 3 == 1:
			# display/cursor/blink toggle
			self.d = (data >> 2) & 1
			self.c = (data >> 1) & 1
			self.b = data & 1
		elif data >> 2 == 1:
			# cursor move/display shift
			self.id = (data >> 1) & 1
			if not self.id: self.id = -1
			self.s = data & 1
		elif data >> 1 == 1:
			# return cursor to home
			self.home()
		elif data == 1:
			# clear display
			self.clear()
	
	def clear(self):
		"""Refill DDRAM to its pristine state"""
		self.ddram = bytearray([20] * 104)
		self.id = 1
		self.ddram_addr = 0
		self.ram_type = 1
	
	def home(self):
		"""Bring the cursor back home"""
		# self.sc = 0 xxx: not the right thing
		self.ddram_addr = 0
		self.ram_type = 1
	
	def blink(self):
		"""Blink cursor"""
		pass
	