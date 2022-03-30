import random

#create a 3d map
def createMap(rows, columns, innerCell):
    map = []
    #create the map in a 3d array
    for i in range(rows):
        map.append([])
        for j in range(columns):
            map[i].append([])
            for k in range(innerCell):
                map[i][j].append(".")
    lastrow = rows-1
    lastcolumn = columns-1
    #populate the walls on the first and last row with #
    for i in range(columns):
        for k in range(innerCell):
            map[0][i][k]="#"
            map[lastrow][i][k]="#"
    #populate the walls on the first and last columns with #
    for i in range(rows):
        for k in range(innerCell):
            map[i][0][k]="#"
            map[i][lastcolumn][k]="#"
    return map
    
def spawnNPC(npc:dict, agentX, agentY, rows, columns):
    #spawn the position of npc
    #x y should not be repeted, use a set to prevent repeation of coordinates
    coordinates = set()
    coordinates.add((agentX, agentY)) #add agent position to set so that it will not be repeated
    
    while(len(coordinates) != len(npc)+1):
        x=random.randint(1,columns-2) # X correspond to columns
        y=random.randint(1,rows-2) # Y correspond to row
        coordinates.add((x,y))
    coordinates.remove((agentX, agentY)) #remove agent postion from set so that it will not be assigned to npc

    npc['wumpus'] = coordinates.pop()
    npc['coin'] = coordinates.pop()
    npc['portal1'] = coordinates.pop()
    npc['portal2'] = coordinates.pop()
    npc['portal3'] = coordinates.pop()

def printMap(map):
    rows = len(map)
    columns = len(map[0])
    innerCell = len(map[0][0])

    innerCellColumn = innerCell // 3
    innerCellRow = innerCell // 3
    print("-------------------------------------------------")
    for i in range(rows-1, -1, -1): #to display such that lower row is at the bottom of map
        for j in range(innerCellRow):
            print("|", end="")
            for k in range(columns):
                print(" ", end="")
                for l in range(innerCellColumn):
                    print(map[i][k][j*innerCellRow+l]+" ", end = "")
                print("|", end="")
            print()
        print("-------------------------------------------------")

#show NPC value on the map; not needed just to test if correctly placed 
def showNPC(npc, map):
    x=npc['wumpus'][0]
    y=npc['wumpus'][1]
    map[y][x][3] = "W"
    map[y][x][5] = "W"

    x=npc['coin'][0]
    y=npc['coin'][1]
    map[y][x][3] = "C"
    map[y][x][5] = "C"

    x=npc['portal1'][0]
    y=npc['portal1'][1]
    map[y][x][3] = "O"
    map[y][x][5] = "O"

    x=npc['portal2'][0]
    y=npc['portal2'][1]
    map[y][x][3] = "O"
    map[y][x][5] = "O"

    x=npc['portal3'][0]
    y=npc['portal3'][1]
    map[y][x][3] = "O"
    map[y][x][5] = "O"

#show x y coordinates on the map; not needed just to see the placement of x y
def showXY(map):
    rows = len(map)
    columns = len(map[0])
    for i in range(rows):
        for j in range(columns):
            map[i][j][0] = str(j) # x = column
            map[i][j][1] = str(i) # y = row
        
