############################################################################################################
# OPTIONS
############################################################################################################

PRIVILEGES = "user" # "root" or "user"
USERNAME = "lucas"
SHORTCUT = [ "Win", "windows", "Key.cmd" ]
D_BUS_SESSION_ADDRESS = "unix:path=/run/user/1000/bus" # most likely this is right. Otherwise substitute it by the output of the command in terminal "echo $DBUS_SESSION_BUS_ADDRESS"
CMD_WRAPPER = "su - {username} -c 'env DBUS_SESSION_BUS_ADDRESS=" + D_BUS_SESSION_ADDRESS + " {cmd}'"
MODE = 'python/pynput' # or python/keyboard/bg or python/keyboard/fg or python/pynput or python/xlib (not implemented)
SLEEP_TIME = 10 # seconds!
BOOT_TIME = 5 # seconds!

CMD_SETUP = [
    "xfconf-query -n -c xfce4-panel -p /panels/panel-0/popdown-speed -t int -s 0", # Panel 0 - No hide animation
    "xfconf-query -n -c xfce4-panel -p /panels/panel-1/popdown-speed -t int -s 0", # Panel 1 - No hide animation
    #"", # Panel 0 - Hide speed 1 ms ? Now setup at ~/.config/gtk-3.0/gtk.css
    #"", # Panel 1 - Hide speed 1 ms ? Now setup at ~/.config/gtk-3.0/gtk.css
]

# List of commands to run when shortcut is pressed
CMD_SHOW = [
    "xfconf-query --channel 'xfce4-panel' --property '/panels/panel-1/position' --type string --set \"p=0;x={center_x};y={center_y}\"", # Panel 1 - Position in the middle of the screen
    "xfconf-query --channel 'xfce4-panel' --property '/panels/panel-1/autohide-behavior' --type int --set 0", # Panel 1 - Make visible (hide never)
    #"xfconf-query --channel 'xfce4-panel' --property '/panels/panel-0/autohide-behavior' --type int --set 0", # Panel 0 - Make visible (hide never)
]

# List of commands to run when shotcut is released
CMD_HIDE = [
    #"xfconf-query --channel 'xfce4-panel' --property '/panels/panel-0/autohide-behavior' --type int --set 1", # Panel 0 - Make hidden (hide inteligentlly)
    "xfconf-query --channel 'xfce4-panel' --property '/panels/panel-1/autohide-behavior' --type int --set 2", # Panel 1 - Make invisible (hide always)
    "xfconf-query --channel 'xfce4-panel' --property '/panels/panel-1/position' --type string --set \"p=0;x=0;y=0\"", # Panel 1 - Mode to 0, 0 (there are four little pixels left when hidden)
    #"xfconf-query --channel 'xfce4-panel' --property '/panels/panel-1/length' --type int --set 10"
]


############################################################################################################
# CODE BEGINNING
############################################################################################################

######################################
# LOAD PACKAGES
######################################

import os
import time
import threading
import subprocess
from Xlib import display

if MODE == "python/keyboard/bg" or MODE == "python/keyboard/fg":
    import keyboard
elif MODE == "python/pynput":
    import pynput
elif MODE == "python/xlib":
    import Xlib

######################################
# GLOBAL VARIABLES
######################################


######################################
# SCREEN FUNCTIONS
######################################

def get_mouse_position():
    d = display.Display()
    root = d.screen().root
    pointer = root.query_pointer()
    return pointer.root_x, pointer.root_y

def get_monitors():
    output = subprocess.check_output(['xrandr']).decode()
    monitors = []
    for line in output.splitlines():
        if ' connected' in line:
            parts = line.split()
            name = parts[0]
            for part in parts:
                if '+' in part and 'x' in part:
                    res_pos = part
                    break
            else:
                continue
            res, x, y = res_pos.split('+')
            width, height = map(int, res.split('x'))
            x = int(x)
            y = int(y)
            monitors.append({'name': name, 'x': x, 'y': y, 'width': width, 'height': height})
    return monitors

def get_current_screen_center():
    mouse_x, mouse_y = get_mouse_position()
    monitors = get_monitors()

    for mon in monitors:
        if (mon['x'] <= mouse_x < mon['x'] + mon['width'] and
            mon['y'] <= mouse_y < mon['y'] + mon['height']):
            center_x = mon['x'] + mon['width'] // 2
            center_y = mon['y'] + mon['height'] // 2
            return center_x, center_y

    return None, None  # Mouse not on any screen

######################################
# PYNPUT FUNCTIONS
######################################

def pynput_is_trigger(key):
    keycode = None
    try:
       keycode = str(key.char)
    except AttributeError:
       keycode = str(key)
    #print(keycode)
    if keycode in SHORTCUT:
        return True
    else:
        return False

def pynput_on_press(key):
    if pynput_is_trigger(key):
        show_panel()

def pynput_on_release(key):
    if pynput_is_trigger(key):
        hide_panel()

######################################
# PYTHON KEYBOARD FUNCTIONS AND VARS
######################################

panel_shown = False
shortcut_pressed = False

def keyboard_step():
    keyboard_check_shortcut()
    keyboard_update_panel()

def keyboard_check_shortcut():
    global shortcut_pressed
    try:
        shortcut_pressed = False
        for sc in SHORTCUT:
            if keyboard.is_pressed(sc):
                shortcut_pressed = True
    except Exception as e:
        #print(e)
        #break
        pass

def keyboard_update_panel():
    if panel_shown and not shortcut_pressed:
        hide_panel()
    elif not panel_shown and shortcut_pressed:
        show_panel()

######################################
# UTIL FUNCTIONS
######################################

def execute_commands(seq):
    center_x, center_y = get_current_screen_center()
    values = { "center_x": center_x, "center_y": center_y }
    for cmd in seq:
        c = cmd.format_map(values)
        if PRIVILEGES == "root":
            c = CMD_WRAPPER.format(username=USERNAME, cmd=cmd)
        #print(c)
        os.system(c)

def show_panel():
    global panel_shown
    execute_commands(CMD_SHOW)
    panel_shown = True
    #print("Panel shown!")

def hide_panel():
    global panel_shown
    execute_commands(CMD_HIDE)
    panel_shown = False
    #print("Panel hidden!")

######################################
# LOOP FUNCTIONS
######################################

def setup():
    if BOOT_TIME is not None:
        time.sleep(BOOT_TIME)
    if MODE == 'python/keyboard/bg':
        print("Registering keyboard events...")
        for sc in SHORTCUT:
            print(sc)
            try:
                keyboard.on_press_key(sc, lambda e: keyboard_step())
                keyboard.on_release_key(sc, lambda e: keyboard_step())
            except Exception as e:
                pass
    elif MODE == 'python/pynput':
        print("Registering pynput events...")
        listener = pynput.keyboard.Listener(
            on_press=pynput_on_press,
            on_release=pynput_on_release
        )
        listener.start()
    print("Ready!")
    execute_commands(CMD_SETUP)

def loop():
    while True:
        if MODE == 'python/keyboard/fg':
            keyboard_step()
        if SLEEP_TIME is not None:
            #time.sleep(SLEEP_TIME)
            threading.Event().wait(SLEEP_TIME)

if __name__ == "__main__":
    print("Loading Workspace Feedback Script...")
    setup()
    loop()
