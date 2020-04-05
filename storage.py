    rooms = roomSetup
    #rooms += [item for sublist in [[x[0] for y in range(x[1])] for x in roomSetup] for item in sublist]
    map = []
    roommap = []
    for x in range(0,15):
        map.append([])
        roommap.append([])
        for y in range(0,9):
            map[x].append(0)
            roommap[x].append(None)
    x = 1
    y = 1
    while len(rooms) > 1:
        map[x][y] = 1
        roommap[x][y] = rooms.pop(random.randrange(0,len(rooms)))
        n = random.randrange(1,5)
        direction = 0
        not_this_way = 0
        while n > 0:
            while direction == not_this_way:
                direction = random.randrange(1,4)
            if direction == 1: # Left
                if x > 0:
                    not_this_way = 3
                    x = x - 1
                else:
                    not_this_way = 1
                    x = x + 1
                if map[x][y] == 0:
                    map[x][y] = 2
            elif direction == 2: # Up
                if y > 0:
                    not_this_way = 4
                    y = y - 1
                else:
                    not_this_way = 2
                    y = y + 1
                if map[x][y] == 0:
                    map[x][y] = 2
            elif direction == 3: # Right
                if x < 14:
                    not_this_way = 1
                    x = x + 1
                else:
                    not_this_way = 3
                    x = x - 1
                if map[x][y] == 0:
                    map[x][y] = 2
            elif direction == 4: # Down
                if y < 8:
                    not_this_way = 2
                    y = y + 1
                else:
                    not_this_way = 4
                    y = y - 1
                if map[x][y] == 0:
                    map[x][y] = 2
            if roommap[x][y] == None or n > 1:
                n = n - 1
    map[x][y] = 1
    roommap[x][y] = rooms.pop(random.randrange(0,len(rooms)))
    for x in range(0,15):
        for y in range(0,9):
            mxy = map[x][y]
            if mxy == 0:
                continue
            mxyl = False
            mxyu = False
            mxyd = False
            mxyr = False
            if y > 0:
                if map[x][y-1] != 0:
                    mxyu = True
            if y < 8:
                if map[x][y+1] != 0:
                    mxyd = True
            if x > 0:
                if map[x-1][y] != 0:
                    mxyl = True
            if x < 14:
                if map[x+1][y] != 0:
                    mxyr = True
            if mxy == 1:
                roomobj = Room(mxyu,mxyd,mxyl,mxyr)
            elif mxy == 2:
                roomobj = Hallway(mxyu,mxyd,mxyl,mxyr)
            roomobj.generateInWorld(x,y)
