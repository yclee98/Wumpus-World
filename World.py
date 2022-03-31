import random

####### WHEN REFERENCING THE MAP DO map[y][x], map[row][column]
####### Rows correspond to y coordinates and columns correspond to x coordinates for the map(in manual 2.21)
class Map:
    def __init__(self, rows, columns, innerCell):
        self.rows = rows
        self.columns = columns
        self.innerCell = innerCell
        self.map = []

    #create a 3d map of row x columns x innerCell
    #populate outer wall with #
    def createMap(self):
        self.map = []
        #create the map in a 3d array
        for i in range(self.rows):
            self.map.append([])
            for j in range(self.columns):
                self.map[i].append([])
                for k in range(self.innerCell):
                    self.map[i][j].append(".")
        lastrow = self.rows-1
        lastcolumn = self.columns-1

        #populate the walls on the first and last row with #
        for i in range(self.columns):
            for k in range(self.innerCell):
                self.map[0][i][k]="#"
                self.map[lastrow][i][k]="#"

        #populate the walls on the first and last columns with #
        for i in range(self.rows):
            for k in range(self.innerCell):
                self.map[i][0][k]="#"
                self.map[i][lastcolumn][k]="#"

        #populate the cell 4 of the inner cell with ? 
        #to indicator, no agent, no known wumpus or portal or safe cell
        for i in range(1, self.rows-1):
            for j in range(1, self.columns-1):
                self.map[i][j][4] = "?"

    #print the map
    def printMap(self, sensory):
        innerCellColumn = self.innerCell // 3
        innerCellRow = self.innerCell // 3
        print("-------------------------------------------------")
        for i in range(self.rows-1, -1, -1): #to display such that lower row is at the bottom of map
            for j in range(innerCellRow):
                print("|", end="")
                for k in range(self.columns):
                    print(" ", end="")
                    for l in range(innerCellColumn):
                        print(self.map[i][k][j*innerCellRow+l]+" ", end = "")
                    print("|", end="")
                print()
            print("-------------------------------------------------")
        self.printSensory(sensory)

    #print the sensory
    def printSensory(self, sensory):
        fullName = ["Confounded", "Stench", "Tingle", "Glitter", "Bump", "Scream"]
        output = ""
        for i in range(len(sensory)):
            if(sensory[i] == 1): #indicator is on
                output = output + fullName[i] + "—"
            else: #indicator is off
                output = output + fullName[i][0] + "—"
        print("Percepts: " + output)
        print()

    #show x y coordinates on the map; not needed just to see the placement of x y
    def showXY(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.map[i][j][0] = str(j) # x = column
                self.map[i][j][1] = str(i) # y = row

    #update cell with npc location 
    def updateCellNpc(self, npcX, npcY):
        #update cell 3 and 5 with "—" to indicate presence of NPC
        self.map[npcY][npcX][3] = "—"
        self.map[npcY][npcX][5] = "—"
    
    #update cell after killing wumpus
    def updateCellKillWumpus(self, npcX, npcY):
        #wumpus died, print . at that cell
        self.map[npcY][npcX][3] = "."
        self.map[npcY][npcX][5] = "."

    #update cell sensory indicator with symbols at position x y 
    def updateCellSensory(self, sensory, x, y):
        sensorySymbol = ["%", "=", "T", "*", "B", "@"] #confounded, stench, tingle, glitter, bump, scream
        #cell 0 to 2
        for i in range(0,3,1): #confounded, stench, tingle
            if(sensory[i] == 1): 
                self.map[y][x][i] = sensorySymbol[i]
            else:
                self.map[y][x][i] = "."
        #cell 6 to 8
        for i in range(6,9,1): #glitter, bump, scream
            if(sensory[i-3] == 1):
                self.map[y][x][i] = sensorySymbol[i-3]
            else:
                self.map[y][x][i] = "."

    #when moving the agent, update the old cell and new cell
    def updateCellAgent(self, oldX, oldY, newX, newY, orientation):
        #update cell 3 and 5 of the previous cell agent is to '.' 
        #update cell 4 of the previous cell to S (visited safe map cell)
        self.map[oldY][oldX][3] = '.'
        self.map[oldY][oldX][5] = '.'
        self.map[oldY][oldX][4] = 'S'
        
        #update cell 3 and 5 of the new cell agent is to '-'
        self.map[newY][newX][3] = '—'
        self.map[newY][newX][5] = '—'
        #update cell 4 to the orientation of the agent
        #this is the absolute orientation 
        if(orientation=='north'):
            self.map[newY][newX][4] = '^'
        elif(orientation=='south'):
            self.map[newY][newX][4] = 'v'
        elif(orientation=='east'):
            self.map[newY][newX][4] = '>'
        elif(orientation=='west'):
            self.map[newY][newX][4] = '<'

class NPC:
    def __init__(self, map):
        self.map = map
        #position of npc store as tuple(x, y)
        #access using self.wumpus[0] and self.wumpus[1]
        self.wumpus = (3,3)
        self.coin = None
        self.portal1 = None
        self.portal2 = None
        self.portal3 = None

    #spawn the npc location
    def spawnNPC(self, agentX, agentY, rows, columns):
        #x y should not be repeated, use a set to prevent repeation of coordinates
        coordinates = set()
        coordinates.add((agentX, agentY)) #add agent position to set so that it will not be repeated
        
        while(len(coordinates) != 6):
            x=random.randint(1,columns-2) # X correspond to columns
            y=random.randint(1,rows-2) # Y correspond to row
            coordinates.add((x,y))
        coordinates.remove((agentX, agentY)) #remove agent postion from set so that it will not be assigned to npc

        # self.wumpus = coordinates.pop()
        self.coin = coordinates.pop()
        self.portal1 = coordinates.pop()
        self.portal2 = coordinates.pop()
        self.portal3 = coordinates.pop()

        self.map.updateCellNpc(self.wumpus[0], self.wumpus[1])
        self.map.updateCellNpc(self.coin[0], self.coin[1])
        self.map.updateCellNpc(self.portal1[0], self.portal1[1])
        self.map.updateCellNpc(self.portal2[0], self.portal2[1])
        self.map.updateCellNpc(self.portal3[0], self.portal3[1])
    
    def printNPC(self):
        print(f"Wumpus: {self.wumpus}", end=", ")
        print(f"Coin: {self.coin}", end=", ")
        print(f"Portal1: {self.portal1}", end=", ")
        print(f"Portal2: {self.portal2}", end=", ")
        print(f"Portal3: {self.portal3}")


class Agent:
    def __init__(self, map):
        self.map = map
        self.x = 1
        self.y = 1
        #orientation = north, south, east, west
        self.orientation = "north" 
        #sensory = confounded, stench, tingle, glitter, bump, scream
        #0 for off, 1 for on
        #confounded on at start of the game 
        self.sensory = [1,0,0,1,0,0]

    def spawnAgent(self):
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)
        self.map.updateCellSensory(self.sensory, self.x, self.y)

    def moveForward(self):
        print("Action sequence: move forward")
        #depend on orientation move the agent 
        #agent[x,y,orientation]
        oldX = self.x
        oldY = self.y

        if(self.orientation=='north'): self.y = self.y + 1
        elif(self.orientation=='east'): self.x = self.x + 1 
        elif(self.orientation=='south'): self.y = self.y - 1 
        elif(self.orientation=='west'): self.x = self.x - 1 

        #update the position on the map and print the map
        self.map.updateCellAgent(oldX, oldY, self.x, self.y, self.orientation)
        self.map.updateCellSensory(self.sensory, self.x, self.y)
        self.map.printMap(self.sensory)
    
    def turnLeft(self):
        print("Action sequence: turn left")
        if(self.orientation=='north'): self.orientation='west'
        elif(self.orientation=='east'): self.orientation='north'
        elif(self.orientation=='south'): self.orientation='east'
        elif(self.orientation=='west'): self.orientation='south'

        #update the orientation on the map and print the map
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)
        self.map.printMap(self.sensory)

    def turnRight(self):
        print("Action sequence: turn right")
        if(self.orientation=='north'): self.orientation='east'
        elif(self.orientation=='east'): self.orientation='south'
        elif(self.orientation=='south'): self.orientation='west'
        elif(self.orientation=='west'): self.orientation='north'

        #update the orientation on the map and print the map
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)
        self.map.printMap(self.sensory)

    def pickUp(self, npc):
        print("Action sequence: pickup")
        #pickup the coin and turn off the glitter in sensory
        #remove the coin from npc
        self.sensory[3] = 0
        npc.coin = None
        self.map.updateCellSensory(self.sensory, self.x, self.y)
        self.map.printMap(self.sensory)
    
    def shoot(self, npc):
        print("Action sequence: shoot")
        #check if wumpus is ahead and in direction of agent to shoot
        #turn on scream if it manage to kill the wumpus
        aheadX = self.x
        aheadY = self.y
        
        #identify the ahead cell
        if(self.orientation=='north'): aheadY = aheadY + 1
        elif(self.orientation=='east'): aheadX = aheadX + 1
        elif(self.orientation=='south'): aheadY = aheadX - 1
        elif(self.orientation=='west'): aheadX = aheadX - 1

        #check if wumpus ahead to shoot
        if(aheadX == npc.wumpus[0] and aheadY == npc.wumpus[1]):
            self.sensory[5] = 1 
            npc.wumpus = None
            self.map.updateCellKillWumpus(aheadX, aheadY) #location of wumpus is at aheadX and aheadY
            print("Wumpus kill")
        else:
            print("Failed to kill wumpus")
        
        self.map.updateCellSensory(self.sensory, self.x, self.y)
        self.map.printMap(self.sensory)

    