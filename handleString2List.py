def listProcess():
    process = os.popen('wmic process get Name, ProcessId, ThreadCount').read() # process is a string 
    lines = process.split('\n')
    list = []
    idList = -1
    for i in range (2, len(lines), 2):
        comp = lines[i].split('  ')
        comp = [p for p in comp if (p != '' and p != ' ')]
        list.append([])
        idList += 1
        for j in comp:    
            #j = [q for q in j if (q != ' ')]
            list[idList].append(j)
        print(list[idList])
