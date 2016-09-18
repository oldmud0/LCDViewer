# LCD Monitor
This is a fully functional LCD monitor for Hitachi HD44780 controller, written in Python 3.

Every LCD packet sent via serial conforms to the following format:

Byte|Value                 |Description
----|----------------------|-----------
   0|`0xFE`                |Magic number
   1|`0xBF`                |Magic number
   2|`0b1111_0[RS, RW, E]` |RS/RW/E pins
   3|`0b[D7...D1]`         |Data pins

If you're interfacing with a plaintext serial monitor and you encounter a message starting with
`FE BF`, it's best to ignore the next two bytes that follow it.

## Requirements
 - Tkinter
 - pyserial
 
## Setup
 - Connect your Arduino.
 - Compile against the modified LiquidCrystal library instead of the vanilla one.
 - Edit `serialport` in `main.py` to the match the Arduino's serial port.
 - Invoke `python main.py`.
 - The Arduino will automatically restart, and the LCD output will appear.

## To do
 - Command-line arguments
 - Safer multithreading
 - Make it flicker less
 - Built-in general serial monitor
 - Change the magic numbers to standard ASCII control characters