# Write your code here :-)
import time
import usb_hid
import board
import touchio
import neopixel
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer


#print(ConsumerControlCode.PLAY_PAUSE)

MODE_LAUNCH = 1
COLOR_LAUNCH = (0,255,255)
MODE_CLICK  = 2
COLOR_CLICK = (255,0,0)
MODE_THREE = 3
COLOR_THREE = (0,0,255)

WHITE = (255,255,255)
BLACK = (0,0,0)

CLICK_TIME = 1

# avoid race condition
time.sleep(1)

# look for touch
# touch selects mode
# mode determines which subroutine is run

# setup touch sensor
touch = touchio.TouchIn(board.TOUCH)

# setup RGB pixel
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

# setup mechanical key button
button = DigitalInOut(board.SWITCH)
button.switch_to_input(pull=Pull.DOWN)
bs = False
db = Debouncer(button)

# setup USB keyboard output
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
key_output = "Hello World!\n"

# setup USB mouse output
mouse = Mouse(usb_hid.devices)


latch = False
button_state = False
clicker_running = False
hold_running = False
prev_time = time.monotonic()
mode = MODE_CLICK
pixels.fill(COLOR_CLICK)

def next_mode():
    global mode
    if mode == MODE_LAUNCH:
        mode = MODE_CLICK
        pixels.fill(COLOR_CLICK)
    elif mode == MODE_CLICK:
        mode = MODE_THREE
        pixels.fill(COLOR_THREE)
    else:
        mode = MODE_LAUNCH
        pixels.fill(COLOR_LAUNCH)
    print("next mode", mode)

def process_launch():
    global db    
    # on press
    if db.rose:
        pixels.fill(WHITE)
    if db.fell:
        pixels.fill(COLOR_LAUNCH)
        keyboard.send(Keycode.COMMAND, Keycode.SHIFT, Keycode.OPTION, Keycode.R)

    
def process_clicker():
    global clicker_running
    global prev_time
    global db
    if db.rose:
        pixels.fill(WHITE)
    if db.fell:
        clicker_running = not clicker_running
        pixels.fill(COLOR_CLICK)
    if clicker_running:
        if time.monotonic() - prev_time > CLICK_TIME:            
            pixels.fill(BLACK)
            time.sleep(0.1)
            pixels.fill(COLOR_CLICK)
            prev_time = time.monotonic()
            mouse.click(Mouse.LEFT_BUTTON)

def process_hold():
    global hold_running
    global prev_time
    global db
    if db.rose:
        pixels.fill(WHITE)
    if db.fell:
        hold_running = not hold_running
        pixels.fill(COLOR_THREE)
        if hold_running:
            mouse.press(Mouse.LEFT_BUTTON)
        else:
            mouse.release(Mouse.LEFT_BUTTON)

    if hold_running:
        if time.monotonic() - prev_time > 0.5:
            pixels.fill(BLACK)
            time.sleep(0.1)
            pixels.fill(COLOR_THREE)
            prev_time = time.monotonic()
        


while True:
    # cycle mode on touch
    if not touch.value:
        latch = False
    if touch.value and not latch:
        latch = True
        next_mode()
    db.update()
    # print("mode = ", mode)
    time.sleep(0.01)
    # run current mode
    if mode == MODE_CLICK:
        process_clicker()
    if mode == MODE_LAUNCH:
        process_launch()
    if mode == MODE_THREE:
        process_hold()
    

