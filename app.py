import os

def listApp():
    output = os.popen('powershell "gps | where {$_.MainWindowTitle } | select name, id, {$_.Threads.Count}').read()
    print(output)

def killApp(pID):
    os.system('wmic process where ProcessId=%a delete'%(pID))

def startApp(appName):
    appName += '.exe'
    appName = "\'" + appName + "\'"
    os.system('wmic process call create %s'%(appName))

listApp()
startApp('notepad')
listApp()