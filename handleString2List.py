def handleString(process):
    lines = process.split('\n') # process is a string
    list = []
    idList = -1
    for i in range (2, len(lines), 2):
        comp = lines[i].split('  ')
        comp = [p for p in comp if (p != '' and p != ' ')]
        list.append([])
        idList += 1
        for j in comp:    
            list[idList].append(j)
        print(list[idList])
