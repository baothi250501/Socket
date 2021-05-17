import socket
import os
import tkinter as tk
import winreg
from io import BytesIO

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

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
        resp = sock.recv(100)       # Read in some number of bytes -- balance this
    except:
        return              
    else:
        buffer.write(resp)          # Write to the BytesIO object
        buffer.seek(0)              # Set the file pointer to the SoF
        start_index = 0             # Count the number of characters processed
        for line in buffer:
            start_index += len(line)
            lines.append(line)       # Do something with your line
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

def shutdown():
    os.system('shutdown /s')

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
        return "Lỗi\n"
    try:
        tmp = winreg.QueryValueEx(a, valueName)
        return tmp[0]
    except OSError:
        return "Lỗi\n"

def setValue(link, valueName, value, typeValue):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return "Lỗi\n"
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
        return "Lỗi\n"
    try:
        winreg.SetValueEx(a, valueName, 0, kind, value)
        return "Set value thành công\n"
    except OSError:
        return "Lỗi\n"

def deleteValue(link, valueName):
    try:
        a = baseRegistryKey(link)
        subKey = link[link.index('\\') + 1:len(link)]
        a = winreg.OpenKey(baseRegistryKey(link), subKey, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return "Lỗi\n"
    try:
        winreg.DeleteValue(a, valueName)
        return "Xóa value thành công\n"
    except OSError:
        return "Lỗi\n"

def deleteKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.DeleteKey(key, subKey)
        return "Xóa key thành công\n"
    except OSError:
        return "Lỗi\n"

def createKey(link):
    key = baseRegistryKey(link)
    subKey = link[link.index('\\') + 1:len(link)]
    try:
        winreg.CreateKey(key, subKey)
        return "Tạo key thành công\n"
    except OSError:
        return "Lỗi\n"

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
                sock.sendall("Sửa thành công\n")
            except:
                sock.sendall("Sửa thất bại\n")
        elif (s == "SEND"):
            option = receiveLine(sock, lines)
            print(option)
            link = receiveLine(sock, lines)
            print(link)
            a = baseRegistryKey(link)
            if (a == ""):
                s = "Lỗi\n"
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
                    s = "Lỗi\n"
            sock.sendall(s)
            #print(s)
        else:
            return

"""
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
    sock.sendall(data)

def keylog(sock, lines):
    keys = []
    while (True):
        s = receiveLine(sock, lines)
        data = []
        if (s == "PRINT"):
            printKeys(sock, keys)
            keys.clear()
        elif (s == "HOOK"):
            while (receiveLine(sock, lines) == "QUIT"):
                keyLogger_hook()
            else:
                line -= 1
        elif (s == "UNHOOK"):
            while (receiveLine(sock, lines) == "QUIT"):
                keyLogger_unhook()
            else:
                line -= 1
        else:
            return
"""

def takepic():
    pass

def process(sock, lines):
    while (True):
        s = receiveLine(sock, lines)
        if (s == "XEM"):
            process = os.popen('wmic process get Name, ProcessId, ThreadCount').read()
            sock.sendall((bytes(process + '\n')))
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
                                sock.sendall("Lỗi\n")
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sock.sendall("Đã diệt process\n")
                                #print("Đã diệt process\n")
                        except:
                            sock.sendall("Lỗi\n")
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
                        sock.sendall("Process đã được bật\n")
                        #print("Process đã được bật\n")
                    except:
                        sock.sendall("Lỗi\n")
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
            sock.sendall(listApp + '\n')
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
                                sock.sendall("Lỗi\n")
                                #print("Lỗi\n")
                            else:
                                os.system('wmic process where ProcessId=%a delete'%(id))
                                sock.sendall("Đã diệt chương trình\n")
                                #print("Đã diệt chương trình\n")
                        except:
                            sock.sendall("Lỗi\n")  
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
                        sock.sendall("Chương trình đã được bật\n")
                        #print("Chương trình đã bật\n")
                    except:
                        sock.sendall("Lỗi\n")
                        #print("Lỗi\n")
                else:
                    test = False
        else:
            break
            

def buttonServer_click():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        try:
            print('Connected by', addr)
            lines = []
            str = ""
            while True:
                str = receiveLine(conn, lines)
                if (str == "KEYLOG"):
                    #keylog()
                    pass
                elif (str == "REGISTRY"):
                    registry(conn, lines)
                elif (str == "SHUTDOWN"):
                    shutdown()
                elif (str == "TAKEPIC"):
                    takepic()
                elif (str == "PROCESS"):
                    process(conn, lines)
                elif (str == "APPLICATION"):
                    application(conn, lines)
                else: # str == "QUIT"
                    conn.close()
                    s.close()
        except KeyboardInterrupt:
            conn.close()
            s.close()

def run_server():
    window = tk.Tk()
    window.title("Form1")

    frame1 = tk.Frame(master=window, width=150, height=150)
    frame1.pack()

    button = tk.Button(master=window, text="Mở server", width=10, height=5, command=buttonServer_click)
    button.place(x=35, y=30)

    window.mainloop()

run_server()