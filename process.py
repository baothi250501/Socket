import os

def listProcess():
    process = os.popen('wmic process get Name, ProcessId, ThreadCount').read()
    print(process)

def killProcess(pID):
    os.system('wmic process where ProcessId=%a delete'%(pID))

def startProcess(processName):
    processName += '.exe'
    processName = "\'" + processName + "\'"
    os.system('wmic process call create %s'%(processName))

listProcess()