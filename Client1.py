from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from functools import partial
from PIL import ImageTk, Image
from PIL import ImageFile
from socket import AF_INET, socket, SOCK_STREAM
import socket
from io import BytesIO
import os
import pyautogui

ImageFile.LOAD_TRUNCATED_IMAGES = True
check = False
BUFF_SIZE = 1000000

#Create socket
try:
    sclient = socket.socket(AF_INET, SOCK_STREAM)
except socket.error:
    messagebox.showerror("Error", "Lỗi không thể tạo socket")

#Connect to Server
def connectServer(IPVar):
    submittedIP = IPVar.get()
    global check
    global sclient
    try:
        ADDR = (submittedIP, 65432)
        sclient.connect(ADDR)
        check = True
    except Exception:
        messagebox.showerror("Error", "Chưa kết nối đến server")
        return False
    if (check == True):
        messagebox.showinfo("Info", "Kết nối đến server thành công")
        return True

#Receive Data
def receive(): 
    data = b''
    while True:
        while True:
            try:
                part = sclient.recv(BUFF_SIZE)
                data += part
                if len(part) < BUFF_SIZE:
                    # either 0 or end of data
                    break
            except socket.error:
                return
        if data:
            break
    return data.decode().strip()

def receive1(): # nhận bytes
    data = b''
    while True:
        while True:
            try:
                part = sclient.recv(BUFF_SIZE)
                data += part
                if len(part) < BUFF_SIZE:
                    # either 0 or end of data
                    break
            except socket.error:
                return
        if data:
            break
    return data

##########################################################

#Process Running
class ProcessGUI(object):

    #Process Init
    def __init__(self, master):
        self.master = Toplevel(master)
        self.master.title("Process Running")
        self.master.geometry("350x270") 
        self.master.resizable(0, 0)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, fill = X )
        Button(self.topFrame, text = "Kill", width = 10, command = self.killProc).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Xem", width = 10, command = self.xemProc).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Xoá", width = 10, command = self.xoaProc).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Start", width = 10, command = self.startProc).pack(side = LEFT, padx = 5)
        self.treev = ttk.Treeview(self.master, selectmode ='browse')
        self.treev.pack(side ='right')
        verscrlbar = ttk.Scrollbar(self.master, orient ="vertical", command = self.treev.yview)
        verscrlbar.pack(side ='right', fill ='x')
        self.treev.configure(xscrollcommand = verscrlbar.set)
        self.treev["columns"] = ("1", "2", "3")
        self.treev['show'] = 'headings'
        self.treev.column("1", width = 110, anchor ='c')
        self.treev.column("2", width = 110, anchor ='se')
        self.treev.column("3", width = 110, anchor ='se')
        self.treev.heading("1", text ="Name Process")
        self.treev.heading("2", text ="ID Process")
        self.treev.heading("3", text ="Count Thread")
        self.master.protocol("WM_DELETE_WINDOW", self.closeProcess)
        self.master.mainloop()
    
    #Close ProcessGUI
    def closeProcess(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()
    
    #Close app or kill GUI
    def Closing(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master1.destroy()
    
    #Kill Process
    def killProcClick(self):
        global sclient
        sclient.sendall(bytes("KILLID", "utf8"))
        ID = self.IDKillEntry.get()
        print(ID)
        sclient.sendall(bytes(ID, "utf8"))
        signal = receive()
        if (signal != '0'):
            messagebox.showinfo("Info", "Đã diệt process")
            return True
        else:
            messagebox.showinfo("Info", "Diệt process không thành công")
            return False
    def killProcGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title ("Kill")
        self.master1.geometry("330x50")
        self.IDKillVar = StringVar()
        self.IDKillEntry = Entry(self.master1,width = 40 , textvariable=self.IDKillVar)
        self.IDKillEntry.pack(side = LEFT, padx = 5)
        Button(self.master1, text = "Kill", width = 8, command = self.killProcClick).pack(side = LEFT)
        self.master1.protocol("WM_DELETE_WINDOW", self.Closing)
        self.master1.mainloop()
    def killProc(self):
        global sclient
        sclient.sendall(bytes("KILL", "utf8"))
        self.killProcGUI()

    #Start Process
    def startProcClick(self):
        global sclient
        ID = self.IDStartEntry.get()
        print(ID)
        sclient.sendall(bytes("STARTID", "utf8"))
        sclient.sendall(bytes(ID, "utf8"))
        signal = receive()
        if (signal != '0'):
            messagebox.showinfo("Info","Process đã được bật")
            return True
        else:
            messagebox.showinfo("Info","Bật process không thành công")
            return False
    def startProcGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title ("Start")
        self.master1.geometry("330x50")
        self.IDStartVar = StringVar()
        self.IDStartEntry = Entry(self.master1,width = 40, textvariable=self.IDStartVar)
        self.IDStartEntry.pack(side = LEFT, padx = 5)
        Button(self.master1, text = "Start", width = 8, command = self.startProcClick).pack(side = LEFT)
        self.master1.protocol("WM_DELETE_WINDOW", self.Closing)
        self.master1.mainloop()
    def startProc(self):
        global sclient
        sclient.sendall(bytes("START", "utf8"))
        self.startProcGUI()

    #Xem Process
    def xemProc(self):
        self.xoaProc()
        global sclient
        sclient.sendall(bytes("XEM", "utf8"))
        data =''
        data = receive()
        lines = data.split('\n') 
        list = []
        idList = -1
        for i in range (0, len(lines)):
            comp = lines[i].split('  ')
            comp = [p for p in comp if (p != '' and p != ' ')]
            list.append([])
            idList += 1
            for j in comp:    
                list[idList].append(j)
        cnt = 0
        for record in list:
            if (len(record) == 3):
                self.treev.insert("", 'end', iid = cnt, text ="", 
                    values =(record[0], record[1], record[2]))
            cnt += 1
        return
    
    #Xóa Process
    def xoaProc(self):
        for record in self.treev.get_children():
            self.treev.delete(record)
        return 

##########################################################

#App Running
class AppGUI(object):

    #App Init
    def __init__(self, master):
        self.master = Toplevel(master)
        self.master.title("listApp")
        self.master.geometry("350x270")
        self.master.resizable(0, 0)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, fill = X )
        Button(self.topFrame, text = "Kill", width = 10, command = self.killApp).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Xem", width = 10, command = self.xemApp).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Xoá", width = 10, command = self.xoaApp).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Start", width = 10, command = self.startApp).pack(side = LEFT, padx = 5)
        self.treev = ttk.Treeview(self.master, selectmode ='browse')
        self.treev.pack(side ='right')
        verscrlbar = ttk.Scrollbar(self.master, orient ="vertical", command = self.treev.yview)
        verscrlbar.pack(side ='right', fill ='x')
        self.treev.configure(xscrollcommand = verscrlbar.set)
        self.treev["columns"] = ("1", "2", "3")
        self.treev['show'] = 'headings'
        self.treev.column("1", width = 110, anchor ='c')
        self.treev.column("2", width = 110, anchor ='se')
        self.treev.column("3", width = 110, anchor ='se')
        self.treev.heading("1", text ="Name Application")
        self.treev.heading("2", text ="ID Application")
        self.treev.heading("3", text ="Count Thread")
        self.master.protocol("WM_DELETE_WINDOW", self.closeApp)
        self.master.mainloop()
    
    #Close AppGUI
    def closeApp(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()

    #Close app or kill GUI
    def Closing(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master1.destroy()

    #Kill App
    def killAppClick(self):
        global sclient
        ID = self.IDKillEntry.get()
        sclient.sendall(bytes("KILLID", "utf8"))
        sclient.sendall(bytes(ID, "utf8"))
        signal = receive()
        if (signal != '0'):
            messagebox.showinfo("Info", "Đã diệt application")
            return True
        else:
            messagebox.showinfo("Info", "Diệt application không thành công")
            return False
    def killAppGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title ("Kill")
        self.master1.geometry("330x50")
        self.IDKillVar = StringVar()
        self.IDKillEntry = Entry(self.master1,width = 40, textvariable=self.IDKillVar)
        self.IDKillEntry.pack(side = LEFT, padx = 5)
        Button(self.master1, text = "Kill", width = 8, command = self.killAppClick).pack(side = LEFT)
        self.master1.protocol("WM_DELETE_WINDOW", self.Closing)
        self.master1.mainloop()  
    def killApp(self):
        global sclient
        sclient.sendall(bytes("KILL", "utf8"))
        self.killAppGUI()
    
    #Start App
    def startAppClick(self):
        global sclient
        ID = self.IDStartEntry.get()
        sclient.sendall(bytes("STARTID", "utf8"))
        sclient.sendall(bytes(ID, "utf8"))
        signal = receive()
        if (signal != '0'):
            messagebox.showinfo("Info", "App đã được bật")
            return True
        else:
            messagebox.showinfo("Info", "Bật app không thành công")
            return False
    def startAppGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title ("Start")
        self.master1.geometry("330x50")
        self.IDStartVar = StringVar()
        self.IDStartEntry = Entry(self.master1,width = 40, textvariable=self.IDStartVar)
        self.IDStartEntry.pack(side = LEFT, padx = 5)
        Button(self.master1, text = "Start", width = 8, command = self.startAppClick).pack(side = LEFT)
        self.master1.protocol("WM_DELETE_WINDOW", self.Closing)
        self.master.mainloop()
    def startApp(self):
        global sclient
        sclient.sendall(bytes("START", "utf8"))
        self.startAppGUI()
    
    #Xem App
    def xemApp(self):
        self.xoaApp()
        global sclient
        sclient.sendall(bytes("XEM", "utf8"))
        data =''
        data = receive()
        lines = data.split('\n') 
        list = []
        idList = -1
        for i in range (0, len(lines)):
            comp = lines[i].split('  ')
            comp = [p for p in comp if (p != '' and p != ' ')]
            list.append([])
            idList += 1
            for j in comp:    
                list[idList].append(j)
        cnt = 0
        for record in list:
            if (len(record) == 3):
                self.treev.insert("", 'end', iid = cnt, text ="", 
                    values =(record[0], record[1], record[2]))
            cnt += 1
        return
    
    #Xoa
    def xoaApp(self):
        for record in self.treev.get_children():
            self.treev.delete(record)
        return 

##########################################################

#Keystoke
class KeystrokeGUI(object):

    #Keystroke Init
    def __init__(self, master):
        self.master = Toplevel(master)
        self.master.title("keystroke")
        self.master.geometry("350x270") 
        self.master.resizable(0, 0)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, fill = X )
        self.T = Text(self.master, height = 15, width = 52)
        Button(self.topFrame, text = "Hook", width = 10, command = self.hook).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "UnHook", width = 10, command = self.unHook).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "In phím", width = 10, command = self.inPhim).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Xoá", width = 10, command = self.xoa).pack(side = LEFT, padx = 5)
        self.T.pack()
        self.master.protocol("WM_DELETE_WINDOW", self.closeKeystroke)
        self.master.mainloop()
    
    #Close KeystrokeGUI
    def closeKeystroke(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()

    #Xoa Keystroke
    def xoa(self):
        self.T.configure(state="normal")
        self.T.delete("1.0", END)
        self.T.configure(state="disabled")
        return

    #In Phím Keystroke
    def inPhim(self):
        global sclient
        sclient.sendall(bytes("PRINT", "utf8"))
        data =''
        data = receive()
        if (data == "0"):
            return
        self.T.configure(state="normal")
        self.T.insert(END,data)
        self.T.configure(state="disabled")
        return

    #UnHook Keystroke
    def unHook(self):
        global sclient
        sclient.sendall(bytes("UNHOOK", "utf8"))
        signal = receive()
        if (signal != '0'):
            return True
        else:
            return False

    ##Hook Keystroke
    def hook(self):
        global sclient
        sclient.sendall(bytes("HOOK", "utf8"))
        signal = receive()
        if (signal != '0'):
            return True
        else:
            return False

##########################################################

#Registry
class RegistryGUI(object):

    #Registry init
    def __init__(self, master):
        self.master = Toplevel(master) 
        self.master.title("Registry") 
        self.master.geometry("340x350") 
        self.master.resizable(0, 0)
        self.topFrame1 = Frame(self.master)
        self.topFrame1.pack(side = TOP, fill = X, pady = 2 )
        self.LinkVar1 = StringVar()
        self.LinkVar1.set("Đường dẫn...")
        self.LinkEntry1 = Entry(self.topFrame1,width = 40, textvariable= self.LinkVar1, state = "disabled").pack(side = LEFT, padx = 5)
        self.topFrame2 = Frame(self.master)
        self.topFrame2.pack(side = TOP, fill = X, pady = 2)
        self.scroll_bar = Scrollbar(self.topFrame2, orient=VERTICAL)
        self.T1 = Text(self.topFrame2, height = 5, width = 26, yscrollcommand= self.scroll_bar.set)
        Button(self.topFrame1, text = "Browser", width = 10, command = self.browser).pack(side = LEFT)
        self.scroll_bar.pack( side = LEFT, padx = 5)
        self.scroll_bar.config(command=self.T1.yview)
        self.T1.pack(side = LEFT, padx = 5)
        Button(self.topFrame2, text = "Gởi nội dung", width = 10, height = 5, command = self.goiND).pack(side = LEFT)
        self.topFrame3 = Frame(self.master)
        self.topFrame3.pack(side = TOP, fill = X, pady = 2)
        Label(self.topFrame3, text = "Sửa giá trị trực tiếp").pack(side = TOP, fill = X, pady = 2)
        self.optionsFunc = ["Get value", "Set value", "Delete value", "Create key", "Delete key"]
        self.choose1 = StringVar()
        self.choose1.set("Chọn chức năng")
        self.FuncChoosen = ttk.Combobox(self.topFrame3, value = self.optionsFunc, textvariable = self.choose1)
        self.FuncChoosen.pack(side = TOP,fill = X, pady = 2)
        self.FuncChoosen.bind("<<ComboboxSelected>>", self.option)
        self.LinkVar2 = StringVar()
        self.LinkVar2.set("Đường dẫn")
        self.LinkEntry2 = Entry(self.topFrame3,width = 40, textvariable=self.LinkVar2)
        self.LinkEntry2.pack(side = TOP, fill = X, padx = 2)
        self.topFrame4 = Frame(self.master)
        self.topFrame4.pack(side = TOP, fill = X, pady = 2)
        self.NameVar = StringVar()
        self.NameVar.set("Name value")
        self.NameEntry = Entry(self.topFrame4,width = 15, textvariable=self.NameVar)
        self.NameEntry.pack(side = LEFT, padx = 2)
        self.ValueVar = StringVar()
        self.ValueVar.set("Value")
        self.ValueEntry = Entry(self.topFrame4,width = 15 , textvariable= self.ValueVar)
        self.ValueEntry.pack(side = LEFT, padx = 2)
        self.choose2 = StringVar()
        self.choose2.set("Chọn kiểu dữ liệu")
        self.optionsData = ["String", "Binary","DWORD","QWORD","Multi-String", "Expandable String"]
        self.DataChoosen = ttk.Combobox(self.topFrame4, value = self.optionsData, textvariable = self.choose2)
        self.DataChoosen.pack(side = LEFT, padx = 2)
        self.topFrame5 = Frame(self.master)
        self.topFrame5.pack(side = TOP, fill = X, pady = 2 )
        self.T2 = Text(self.topFrame5, height = 5, width = 30, state = "disabled")
        self.T2.pack(side = TOP, fill = X)
        self.topFrame6 = Frame(self.master)
        self.topFrame6.pack(side = TOP, fill = X, pady = 2 )
        Button(self.topFrame6, text = "Gởi", width = 20, command = self.goi).pack(side = LEFT, padx = 10)
        Button(self.topFrame6, text = "Xoá", width = 20, command = self.xoa).pack(side = LEFT, padx = 5)
        self.master.protocol("WM_DELETE_WINDOW", self.closeRegistry)
        self.master.mainloop()

    #Close RegistryGUI
    def closeRegistry(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()

    #Option
    def option(self,event):
        ch = self.FuncChoosen.get()
        if (ch == self.optionsFunc[0] or ch == self.optionsFunc[2]):
            self.NameEntry.pack(side = LEFT, padx = 2)
            self.ValueEntry.pack(side = LEFT, padx = 2)
            self.DataChoosen.pack(side = LEFT, padx = 2)
            self.ValueEntry.pack_forget()
            self.DataChoosen.pack_forget()
        elif (ch == self.optionsFunc[1]):
            self.NameEntry.pack(side = LEFT, padx = 2)
            self.ValueEntry.pack(side = LEFT, padx = 2)
            self.DataChoosen.pack(side = LEFT, padx = 2)
        else:
            self.NameEntry.pack(side = LEFT, padx = 2)
            self.ValueEntry.pack(side = LEFT, padx = 2)
            self.DataChoosen.pack(side = LEFT, padx = 2)
            self.NameEntry.pack_forget()
            self.ValueEntry.pack_forget()
            self.DataChoosen.pack_forget()
        return


    #Browser
    def browser(self):
        linkFile = filedialog.askopenfilename(title="Open File", 
                                                filetypes=(("REG Files", "*.reg"),
                                                            ("All Files", "*.*")))
        file = open(linkFile, 'r')
        stuff = file.read()
        self.T1.delete("1.0", END)
        self.T1.insert(END, stuff)
        self.LinkVar1.set(linkFile)
        file.close()
        return

    #Gởi nội dung
    def goiND(self):
        global sclient
        sclient.sendall(bytes("REG", "utf8"))
        text = str.encode(self.T1.get("1.0", END))
        sclient.sendall(text)
        signal = receive()
        if (signal != '0'):
            messagebox.showinfo("Info", "Sửa thành công")
            return True
        else:
            messagebox.showinfo("Info", "Sửa không thành công")
            return False

    #ghiT2
    def ghiT2(self, s):
        self.T2.configure(state="normal")
        self.T2.insert(END,s)
        self.T2.configure(state="disabled")
        return

    #Gởi
    def fixmsg(self, s):
        if s=='':
            return 'no'
        return s
    def goi(self):
        global sclient
        sclient.sendall(bytes("SEND", "utf8"))
        sig=''
        T=''
        if self.FuncChoosen.get()== self.optionsFunc[0]:
            sig ="Get value"
        elif self.FuncChoosen.get()== self.optionsFunc[1]:
            sig ="Set value"
        elif self.FuncChoosen.get()== self.optionsFunc[2]:
            sig ="Delete value"
        elif self.FuncChoosen.get()== self.optionsFunc[3]:
            sig ="Create key"
        elif self.FuncChoosen.get()== self.optionsFunc[4]:
            sig ="Delete key"
        # type of data
        if self.DataChoosen.get()== self.optionsData[0]:
            T ="String"
        elif self.DataChoosen.get()== self.optionsData[1]:
            T ="Binary"
        elif self.DataChoosen.get()== self.optionsData[2]:
            T ="DWORD"
        elif self.DataChoosen.get()== self.optionsData[3]:
            T = "QWORD"
        elif self.DataChoosen.get()== self.optionsData[4]:
            T="Multi-String"
        elif self.DataChoosen.get()== self.optionsData[5]:
            T="Expandable String"

        #SendReg
        msg = self.fixmsg(sig) + "\n" + self.fixmsg(self.LinkEntry2.get()) + "\n" + self.fixmsg(self.NameEntry.get()) + "\n" + self.fixmsg(self.ValueEntry.get()) + "\n" + self.fixmsg(T)
        sclient.sendall(bytes(msg, "utf8"))
        signal = receive()
        s = ''
        if (signal != '0'):
            if (sig == "Get value"):
                s = "Value: " + signal + "\n"
            elif (sig == "Set value"):
                s =  "Set value thành công \n"
            elif (sig == "Delete value"):
                s =  "Xóa value thành công \n"
            elif (sig == "Create key"):
                s = "Tạo key thành công \n"
            elif (sig == "Delete key"):
                s =  "Xóa key thành công \n"
            else:
                s = "Không tồn tại \n"
        else:
            s = "Lỗi \n"
        self.ghiT2(s)
        return
    
    #Xóa
    def xoa(self):
        self.T2.configure(state="normal")
        self.T2.delete("1.0", END)
        self.T2.configure(state="disabled")
        return

##########################################################

#Print Screen
class PicGUI(object):

    #Pic init
    def __init__(self, master):
        self.master = Toplevel(master)
        self.master.geometry("400x300")
        self.data = receive1()
        #print(len(self.data))
        self.img = Image.open(BytesIO(self.data))
        img1=self.img.resize((350, 230), Image.ANTIALIAS)
        self.img2 = ImageTk.PhotoImage(img1)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, fill = X, pady = 10)
        Button(self.topFrame, text = "Take", width = 23, command = self.take).pack(side = LEFT, padx = 15)
        Button(self.topFrame, text = "Save", width = 23, command = self.save).pack(side = LEFT)
        self.label = Label(self.master,image=self.img2)
        self.label.place(x = 20, y = 40)
        self.master.protocol("WM_DELETE_WINDOW", self.closePic)
        self.master.mainloop()

    #Close PicGUI
    def closePic(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()

    #save
    def save(self):
        file = filedialog.asksaveasfile( mode = 'wb',
                                        defaultextension="*.png",
                                        filetypes=[
                                            ("PNG file","*.png"),
                                            ("JPQ file", "*.jpg"),
                                            ("All files", "*.*"),
                                        ])
        if file is None:
            return
        self.img.save(file)
        file.close()
        return

    #take
    def take(self):
        sclient.sendall(bytes("TAKE", "utf8"))
        #print("TAKE")
        self.data = receive1()
        #print(len(self.data))
        #print(1)
        self.img = Image.open(BytesIO(self.data))
        img1=self.img.resize((350, 230), Image.ANTIALIAS)
        self.img2 = ImageTk.PhotoImage(img1)
        self.label = Label(self.master,image=self.img2)
        self.label.place (x = 20, y = 40)
        return

##########################################################

#Client
class ClientGUI(object):
    def __init__(self,master):
        self.master = master
        self.master.title("Client") 
        self.master.geometry("250x270") 
        self.master.resizable(0, 0)
        hostVar = StringVar()
        hostEntry = Entry(self.master,textvariable=hostVar).pack(side = TOP,fill = X, pady = 2)
        submittedHost = hostVar.get()
        connectFunc = partial(connectServer,hostVar)
        Button(self.master, text = "Connect to Server", command = connectFunc).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Process Running", command = self.ProcessRunning).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "App Running", command = self.AppRunning).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Keystroke", command = self.Keystroke).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Registry", command = self.Registry).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Print Screen", command = self.PrintScreen).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Shut down", command = self.ShutDown).pack(side = TOP,fill = X, pady = 2)
        Button(self.master, text = "Quit", command = self.Quit).pack(side = TOP,fill = X, pady = 2)
        self.master.protocol("WM_DELETE_WINDOW", self.Closing)
        self.master.mainloop()

    #Close client
    def Closing(self):
        global sclient
        sclient.sendall(bytes("QUIT", "utf8"))
        self.master.destroy()

    #Process Running Button
    def ProcessRunning(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        sclient.sendall(bytes("PROCESS", "utf8"))
        PRG = ProcessGUI(self.master)
        #self.master.wait_window(PRG.master)

    #App Running Button
    def AppRunning(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        sclient.sendall(bytes("APPLICATION", "utf8"))
        AG = AppGUI(self.master)
        #self.master.wait_window(AG.master)

    #Keystroke Button
    def Keystroke(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        sclient.sendall(bytes("KEYLOG", "utf8"))
        KeystrokeGUI(self.master)

    #Registry Button
    def Registry(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        sclient.sendall(bytes("REGISTRY", "utf8"))
        RG = RegistryGUI(self.master)
        #self.master.wait_window(RG.master)
        

    #PrintScreen Button
    def PrintScreen(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return
        sclient.sendall(bytes("TAKEPIC", "utf8"))
        PG = PicGUI(self.master)
        #self.master.wait_window(PG.master)

    #Shut Down Button
    def ShutDown(self):
        global check
        global sclient
        if (not check):
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        sclient.sendall(bytes("SHUTDOWN", "utf8"))
        sclient.close()
        sclient = None
        check = False

    #Quit Button
    def Quit(self):
        global check
        global sclient
        if (check):
            sclient.sendall(bytes("QUIT", "utf8"))
            sclient.close()
        self.master.destroy()
        return


##########################################################

#Main
if __name__ == "__main__":
    root = Tk()
    window = ClientGUI(root)
    root.mainloop()