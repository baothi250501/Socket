from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from functools import partial
from socket import AF_INET, socket, SOCK_STREAM
import json
from io import BytesIO
import os
from tkinter import filedialog
from Client import*
from PIL import ImageTk,Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
sclient = None
check = False

def Line(lines):
    if (len(lines) > 0):
        res = lines[0]
        lines.pop(0)
        res = res.decode("utf8")
        res = res.replace("\n","")
        return res
    else:
        return "QUIT"

def receive(lines):
    buffer = BytesIO()
    try:
        resp = sclient.recv(100)       
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

def receiveLine(lines):
    receive(lines)
    return Line(lines)

def receiveJson(data):
    return
def connectServer(IPVar):
    submittedIP = IPVar.get()
    try:
        try:
            sclient = socket(AF_INET, SOCK_STREAM)
        except socket.error:
            messagebox.showerror("Error", "Lỗi không thể tạo socket")
        ADDR = (submittedIP, 65432)
        sclient.connect(ADDR)
        check = True
    except Exception:
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return
    if (check == True):
        messagebox.showinfo("Info", "Kết nối đến server thành công")
def screenServer():
    return 

#Process Running

##Start Process
def startProcClick(IDVar):
    ID = IDVar.get()
    sclient.sendall(bytes("STARTID \n", "utf8"))
    sclient.sendall(bytes(ID + "\n", "utf8"))
    signal = sclient.recv(1)
    if (signal != b'0'):
        messagebox.showinfo("Process đã được bật")
    else:
        messagebox.showinfo("Bật process không thành công")
def startProcGUI():
    root = Tk()
    root.title ("Start")
    root.geometry("330x50")
    IDVar = StringVar()
    IDEntry = Entry(root,width = 40, textvariable=IDVar).pack(side = LEFT, padx = 5)
    submittedIP = IDVar.get()
    startFunc = partial(startProcClick,IDVar)
    Button(root, text = "Start", width = 8, command = startFunc).pack(side = LEFT)
    root.mainloop()
def startProc():
    sclient.sendall(bytes("START", "utf8"))
    startProcGUI()

##Xem Process
def xemProc(root):
    sclient.sendall(bytes("XEM", "utf8"))
    data = receiveLine()
    lines = data.split('\n') 
    list = []
    idList = -1
    for i in range (2, len(lines), 2):
        comp = lines[i].split('  ')
        comp = [p for p in comp if (p != '' and p != ' ')]
        list.append([])
        idList += 1
        for j in comp:    
            list[idList].append(j)
    cnt = 0
    for record in list:
        root.treev.insert("", 'end', iid = cnt, text ="", 
             values =(record[0], record[1], record[2]))
        cnt += 1

##Xoa Process
def xoaProc(root):
    for record in root.treev.get_children():
        root.treev.delete(record)
    return 

##Kill Process
def killProcClick(IDVar):
    sclient.sendall(bytes("KILLID \n", "utf8"))
    ID = IDVar.get()
    sclient.sendall(bytes(ID + "\n", "utf8"))
    signal = sclient.recv(1)
    if (signal !=  b'0'):
        messagebox.showinfo("Đã diệt process")
    else:
        messagebox.showinfo("Diệt process không thành công")
def killProcGUI():
    root = Tk()
    root.title ("Kill")
    root.geometry("330x50")
    IDVar = StringVar()
    IDEntry = Entry(root,width = 40, textvariable=IDVar).pack(side = LEFT, padx = 5)
    submittedIP = IDVar.get()
    killFunc = partial(killProcClick,IDVar)
    Button(root, text = "Kill", width = 8, command = killFunc).pack(side = LEFT)
    root.mainloop()
def killProc():
    sclient.sendall(bytes("KILL \n", "utf8"))
    killProcGUI()

##Process
def ProcessGUI():
    root = Tk()
    root.title("Process Running")
    root.geometry("350x270") 
    root.resizable(0, 0)
    topFrame = Frame(root)
    topFrame.pack(side = TOP, fill = X )
    Button(topFrame, text = "Kill", width = 10, command = killProc).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Xem", width = 10, command = xemProc).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Xoá", width = 10, command = xoaProc(root)).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Start", width = 10, command = startProc).pack(side = LEFT, padx = 5)
    treev = ttk.Treeview(root, selectmode ='browse')
    treev.pack(side ='right')
    verscrlbar = ttk.Scrollbar(root, orient ="vertical", command = treev.yview)
    verscrlbar.pack(side ='right', fill ='x')
    treev.configure(xscrollcommand = verscrlbar.set)
    treev["columns"] = ("1", "2", "3")
    treev['show'] = 'headings'
    treev.column("1", width = 110, anchor ='c')
    treev.column("2", width = 110, anchor ='se')
    treev.column("3", width = 110, anchor ='se')
    treev.heading("1", text ="Name Process")
    treev.heading("2", text ="ID Process")
    treev.heading("3", text ="Count Thread")
    root.mainloop()
def ProcessRunning():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return 
    sclient.sendall(bytes("PROCESS \n", "utf8"))
    ProcessGUI()


#App Running 

##Start App
def startAppClick(IDVar):
    ID = IDVar.get()
    sclient.sendall(bytes("STARTID \n", "utf8"))
    sclient.sendall(bytes(ID + "\n", "utf8"))
    signal = sclient.recv(1)
    if (signal != b'0'):
        messagebox.showinfo("App đã được bật")
    else:
        messagebox.showinfo("Bật app không thành công")
def startAppGUI():
    root = Tk()
    root.title ("Start")
    root.geometry("330x50")
    IDVar = StringVar()
    IDEntry = Entry(root,width = 40, textvariable=IDVar).pack(side = LEFT, padx = 5)
    submittedIP = IDVar.get()
    startFunc = partial(startAppClick,IDVar)
    Button(root, text = "Start", width = 8, command = startFunc).pack(side = LEFT)
    root.mainloop()
def startApp():
    sclient.sendall(bytes("START", "utf8"))
    startAppGUI()

##Xem App
def xemApp(root):
    sclient.sendall(bytes("XEM", "utf8"))
    data = receiveLine()
    lines = data.split('\n') 
    list = []
    idList = -1
    for i in range (2, len(lines), 2):
        comp = lines[i].split('  ')
        comp = [p for p in comp if (p != '' and p != ' ')]
        list.append([])
        idList += 1
        for j in comp:    
            list[idList].append(j)
    cnt = 0
    for record in list:
        root.treev.insert("", 'end', iid = cnt, text ="", 
             values =(record[0], record[1], record[2]))
        cnt += 1

##Xoa App
def xoaApp(root):
    for record in root.treev.get_children():
        root.treev.delete(record)
    return 

##Kill App
def killAppClick(IDVar):
    ID = IDVar.get()
    sclient.sendall(bytes("STARTID \n", "utf8"))
    sclient.sendall(bytes(ID + "\n", "utf8"))
    signal = sclient.recv(1)
    if (signal != b'0'):
        messagebox.showinfo("Đã diệt application")
    else:
        messagebox.showinfo("Diệt application không thành công")
def killAppGUI():
    root = Tk()
    root.title ("Kill")
    root.geometry("330x50")
    IDVar = StringVar()
    IDEntry = Entry(root,width = 40, textvariable=IDVar).pack(side = LEFT, padx = 5)
    submittedIP = IDVar.get()
    killFunc = partial(killAppClick,IDVar)
    Button(root, text = "Kill", width = 8, command = killFunc).pack(side = LEFT)
    root.mainloop()  
def killApp():
    sclient.sendall(bytes("KILL \n", "utf8"))
    killAppGUI()

##App
def AppGUI():
    root = Tk()
    root.title("listApp")
    root.geometry("350x270")
    root.resizable(0, 0)
    topFrame = Frame(root)
    topFrame.pack(side = TOP, fill = X )
    Button(topFrame, text = "Kill", width = 10, command = killApp).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Xem", width = 10, command = xemApp).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Xoá", width = 10, command = xoaApp).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Start", width = 10, command = startApp).pack(side = LEFT, padx = 5)
    treev = ttk.Treeview(root, selectmode ='browse')
    treev.pack(side ='right')
    verscrlbar = ttk.Scrollbar(root, orient ="vertical", command = treev.yview)
    verscrlbar.pack(side ='right', fill ='x')
    treev.configure(xscrollcommand = verscrlbar.set)
    treev["columns"] = ("1", "2", "3")
    treev['show'] = 'headings'
    treev.column("1", width = 110, anchor ='c')
    treev.column("2", width = 110, anchor ='se')
    treev.column("3", width = 110, anchor ='se')
    treev.heading("1", text ="Name Application")
    treev.heading("2", text ="ID Application")
    treev.heading("3", text ="Count Thread")
    root.mainloop()
def AppRunning():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return 
    sclient.sendall(bytes("APPLICATION \n", "utf8"))
    AppGUI()


#Keystroke

##Xoa Keystroke
def xoa(T):
    T.configure(state="normal")
    T.delete("1.0", END)
    T.configure(state="disabled")
    return

##In Phim Keystroke
def inPhim(T):
    sclient.sendall(bytes("INPHIM \n", "utf8"))
    data = receiveLine()
    T.configure(state="normal")
    T.insert(END,data)
    T.configure(state="disabled")
    return

##UnHook Keystroke
def unHook():
    sclient.sendall(bytes("UNHOOK \n", "utf8"))
    signal = sclient.recv(1)
    if (signal != b'0'):
        return True
    else:
        return False

##Hook Keystroke
def hook():
    sclient.sendall(bytes("HOOK \n", "utf8"))
    signal = sclient.recv(1)
    if (signal != b'0'):
        return True
    else:
        return False

##Keystroke   
def KeystrokeGUI():
    root = Tk()
    root.title("keystroke")
    root.geometry("350x270") 
    root.resizable(0, 0)
    topFrame = Frame(root)
    topFrame.pack(side = TOP, fill = X )
    T = Text(root, height = 15, width = 52)
    inPhimFunc = partial(inPhim,T)
    Button(topFrame, text = "Hook", width = 10, command = hook).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "UnHook", width = 10, command = unHook).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "In phím", width = 10, command = inPhimFunc).pack(side = LEFT, padx = 5)
    Button(topFrame, text = "Xoá", width = 10, command = xoa).pack(side = LEFT, padx = 5)
    T.pack()
    root.mainloop()
def Keystroke():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return 
    sclient.sendall(bytes("KEYSTROKE", "utf8"))
    KeystrokeGUI()


#Registry

#Browser
def browser(T1, LinkVar1):
    linkFile = filedialog.askopenfilename(title="Open File", 
                                            filetypes=(("REG Files", "*.reg"),
                                                        ("All Files", "*.*")))
    file = open(linkFile, 'r')
    stuff = file.read()
    T1.delete("1.0", END)
    T1.insert(END, stuff)
    LinkVar1.set(linkFile)
    file.close()
    return

#Gởi nội dung
def goiND(T1):
    sclient.sendall(bytes("REG \n", "utf8"))
    sclient.sendall(bytes(T1),"utf8")
    signal = sclient.recv(1)
    if (signal != b'0'):
        messagebox.showinfo("Sửa thành công")
        return True
    else:
        messagebox.showinfo("Sửa không thành công")
        return False



#ghiT2
def ghiT2(T2, s):
    string= s
    T2.configure(state="normal")
    T2.insert(END,s)
    T2.configure(state="disabled")
    return

#Xoa
def xoa(T2):
    T2.configure(state="normal")
    T2.delete("1.0", END)
    T2.configure(state="disabled")
    return



def fixmsg(self, s):
    if s=='':
        return 'None'
    return s

    

def registryGUI():
    root = Tk() 
    root.title("Registry") 
    root.geometry("340x350") 
    root.resizable(0, 0)
    topFrame1 = Frame(root)
    topFrame1.pack(side = TOP, fill = X, pady = 2 )
    LinkVar1 = StringVar()
    LinkVar1.set("Đường dẫn...")
    LinkEntry1 = Entry(topFrame1,width = 40, textvariable=LinkVar1, state = "disabled").pack(side = LEFT, padx = 5)
    submittedIP1 = LinkVar1.get()
    topFrame2 = Frame(root)
    topFrame2.pack(side = TOP, fill = X, pady = 2)
    scroll_bar = Scrollbar(topFrame2, orient=VERTICAL)
    T1 = Text(topFrame2, height = 5, width = 26, yscrollcommand=scroll_bar.set)
    browserFunc = partial(browser, T1, LinkVar1)
    Button(topFrame1, text = "Browser", width = 10, command = browserFunc).pack(side = LEFT)
    scroll_bar.pack( side = LEFT, padx = 5)
    scroll_bar.config(command=T1.yview)
    T1.pack(side = LEFT, padx = 5)
    goiNDFunc = partial (goiND, T1)
    Button(topFrame2, text = "Gởi nội dung", width = 10, height = 5, command = goiNDFunc).pack(side = LEFT)
    topFrame3 = Frame(root)
    topFrame3.pack(side = TOP, fill = X, pady = 2)
    Label(topFrame3, text = "Sửa giá trị trực tiếp").pack(side = TOP, fill = X, pady = 2)
    ######
    optionsFunc = ["Get value", "Set value", "Delete value", "Create key", "Delete key"]
    FuncChoosen = ttk.Combobox(topFrame3, value = optionsFunc)
    def comboclick(event):
        ch = FuncChoosen.get()
        if (ch == optionsFunc[0]):
            ValueEntry.pack_forget()
            FuncChoosen.pack_forget()
            '''elif (ch == optionsFunc[1]):
                elif (ch == optionsFunc[2]):'''

    clicked1 = StringVar()
    clicked1.set("Chọn chức năng")
    FuncChoosen.pack(side = TOP,fill = X, pady = 2)
    FuncChoosen.current(0)
    FuncChoosen.bind("<<ComboboxSelected>>", comboclick)
    LinkVar2 = StringVar()
    LinkVar2.set("Đường dẫn")
    LinkEntry2 = Entry(topFrame3,width = 40, textvariable=LinkVar2).pack(side = TOP, fill = X, padx = 2)
    submittedIP2 = LinkVar2.get()
    topFrame4 = Frame(root)
    topFrame4.pack(side = TOP, fill = X, pady = 2)
    NameVar = StringVar()
    NameVar.set("Name value")
    NameEntry = Entry(topFrame4,width = 15, textvariable=NameVar).pack(side = LEFT, padx = 2)
    submittedName = NameVar.get()
    ValueVar = StringVar()
    ValueVar.set("Value")
    ValueEntry = Entry(topFrame4,width = 15, textvariable=ValueVar).pack(side = LEFT, padx = 2)
    submittedValue = ValueVar.get()
    optionsData = ["String", "Binary","DWORD","QWORD","Multi-String", "Expandable String"]
    DataChoosen = ttk.Combobox(topFrame3, value = optionsFunc)
    clicked2 = StringVar()
    clicked2.set("Chọn kiểu dữ liệu")
    DataChoosen.pack(side = TOP,fill = X, pady = 2)
    DataChoosen.current(0)
    #Gởi
    def goi():
        sclient.sendall(bytes("SEND \n", "utf8"))
        sig=''
        T=''
        if FuncChoosen.get()== optionsFunc[0]:
            sig ="Get value"
        elif FuncChoosen.get()== optionsFunc[1]:
            sig ="Set value"
        elif FuncChoosen.get()== optionsFunc[2]:
            sig ="Delete value"
        elif FuncChoosen.get()== optionsFunc[3]:
            sig ="Create key"
        elif FuncChoosen.get()== optionsFunc[4]:
            sig ="Delete key"
        # type of data
        if DataChoosen.get()== optionsData[0]:
            T ="String"
        elif DataChoosen.get()== optionsData[1]:
            T ="Binary"
        elif DataChoosen.get()== optionsData[2]:
            T ="DWORD"
        elif DataChoosen.get()== optionsData[3]:
            T = "QWORD"
        elif DataChoosen.get()== optionsData[4]:
            T="Multi-String"
        elif DataChoosen.get()== optionsData[5]:
            T="Expandable String"

        #SendReg
        sclient.sendall(bytes(fixmsg(sig) + "\n", "utf8"))
        sclient.sendall(bytes(fixmsg(submittedIP2) + "\n", "utf8"))
        sclient.sendall(bytes(fixmsg(submittedName) + "\n", "utf8"))
        sclient.sendall(bytes(fixmsg(submittedValue) + "\n", "utf8"))
        sclient.sendall(bytes(fixmsg(T) + "\n", "utf8"))
        signal = sclient.recv(1)
        s = ''
        if (signal != b'0'):
            if (sig == "Get value"):
                s = submittedValue + " = " + submittedValue + "\n"
            elif (sig == "Set value"):
                s =  "Set value thành công \n"
            elif (sig == "Delete value"):
                s =  "Xóa value thành công \n"
            elif (sig == "Create key"):
                s = "Tạo key thành công \n"
            elif (sig == "Delete key"):
                s =  "Xóa key thành công \n"
            else:
                s = "Hieu \n"
        else:
            s = "Lỗi \n"
        ghiT2(T2,s)
    DataChoosen.bind("<<ComboboxSelected>>", goi)
    topFrame5 = Frame(root)
    topFrame5.pack(side = TOP, fill = X, pady = 2 )
    T2 = Text(topFrame5, height = 5, width = 30, state = "disabled")
    T2.pack(side = TOP, fill = X)
    topFrame6 = Frame(root)
    topFrame6.pack(side = TOP, fill = X, pady = 2 )
    xoaFunc = partial(xoa, T2)
    Button(topFrame6, text = "Gởi", width = 20, command = root.destroy).pack(side = LEFT, padx = 10)
    Button(topFrame6, text = "Xoá", width = 20, command = xoaFunc).pack(side = LEFT, padx = 5)
    root.mainloop()
   
def Registry():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return 
    sclient.sendall(bytes("REGISTRY \n", "utf8"))
    registryGUI()

#Print Screen

##Save
def save(img):
    file = filedialog.asksaveasfile( mode = 'wb',
                                    defaultextension="*.png",
                                    filetypes=[
                                        ("PNG file","*.png"),
                                        ("JPQ file", "*.jpg"),
                                        ("All files", "*.*"),
                                    ])
    
    if file is None:
        return
    img.save(file)
    file.close()

##Take
def take(root,img):
    img = screenServer()
    img1 = img.resize((320,230), Image.ANTIALIAS)
    img2 = ImageTk.PhotoImage(img1)
    Label(root, image=img2).pack(side = BOTTOM, fill = X)
    return

##Pic
def picGUI():
    root = Tk()
    root.title("Pic")
    root.geometry("350x270") 
    root.resizable(0, 0)
    img = screenServer()
    topFrame = Frame(root)
    topFrame.pack(side = TOP, fill = X )
    saveFunc = partial(save,img)
    takeFunc = partial(take,root,img)
    Button(topFrame, text = "Take", width = 20, command = takeFunc).pack(side = LEFT, padx = 10)
    Button(topFrame, text = "Save", width = 20, command = saveFunc).pack(side = LEFT, padx = 5)
    temp= img.resize((320,230), Image.ANTIALIAS)
    img1 = ImageTk.PhotoImage(temp)
    Label(root, image=img1).pack(side = BOTTOM, fill = X)
    root.mainloop()
def PrintScreen():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return
    sclient.sendall(bytes("TAKEPIC \n", "utf8"))
    picGUI()


#Shut Down
def ShutDown():
    if (not check):
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return 
    sclient.sendall(bytes("SHUTDOWN \n", "utf8"))
    sclient.close()
    sclient = None
    check = False


#Quit
def Quit():
    if (check):
        sclient.sendall(bytes("QUIT \n", "utf8"))
        sclient.close()
    return


#ClientGUI
def clientGUI():
    root = Tk() 
    root.title("Client") 
    root.geometry("250x270") 
    root.resizable(0, 0)
    hostVar = StringVar()
    hostEntry = Entry(root,textvariable=hostVar).pack(side = TOP,fill = X, pady = 2)
    submittedHost = hostVar.get()
    connectFunc = partial(connectServer,hostVar)
    Button(root, text = "Connect to Server", command = connectFunc).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Process Running", command = ProcessRunning).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "App Running", command = AppRunning).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Keystroke", command = Keystroke).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Registry", command = Registry).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Print Screen", command = PrintScreen).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Shut down", command = ShutDown).pack(side = TOP,fill = X, pady = 2)
    Button(root, text = "Quit", command = Quit).pack(side = TOP,fill = X, pady = 2)
    root.mainloop()

clientGUI()

