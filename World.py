import random

####### WHEN REFERENCING THE MAP DO map[y][x], map[row][column]
####### Rows correspond to y coordinates and columns correspond to x coordinates for the map(in manual 2.21)
class Map:
    def __init__(self, rows, columns, innerCell):
        self.rows = rows
        self.columns = columns
        self.innerCell = innerCell
        self.map = []
        self.npc = None

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

    #initialize npc to map variable
    def setNpc(self, npc):
        self.npc = npc

    #update cell with to indicate presence of npc 
    def updateCellNpc(self, npcX, npcY):
        #update cell 3 and 5 with "—" 
        self.map[npcY][npcX][3] = "—"
        self.map[npcY][npcX][5] = "—"
    
    #update cell after killing wumpus, remove wumpus from the cell
    def updateCellKillWumpus(self, npcX, npcY):
        #wumpus died, print . at that cell instead 
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
    
    #show the npc on the map;
    def spawnNPConMap(self):
        if(self.npc.wumpus!=None):
            self.updateCellNpc(self.npc.wumpus[0], self.npc.wumpus[1])
        if(self.npc.coin!=None):
            self.updateCellNpc(self.npc.coin[0], self.npc.coin[1])
        self.updateCellNpc(self.npc.portal[0][0], self.npc.portal[0][1])
        self.updateCellNpc(self.npc.portal[1][0], self.npc.portal[1][1])
        self.updateCellNpc(self.npc.portal[2][0], self.npc.portal[2][1])
    
    #perceive sensory at position x y
    def perceiveSensory(self, agentPosition, bump, scream):
        #agentPosition in (x, y)
        #confounded, stench, tingle, glitter, bump, scream
        sensory = [0, 0, 0, 0, 0, 0] #intialize all sensory to off

        #confounded indicator; agent in the same cell as a confundus
        if(agentPosition in self.npc.portal):
            sensory[0] = 1

        #glitter indicator; agent in same cell as coin
        if(agentPosition == self.npc.coin):
            sensory[3] = 1
        
        #bump indicator
        if(bump):
            sensory[4] = 1
        
        #scream indicator
        if(scream):
            sensory[5] = 1
        
        #get the up down left right cell of the position agent is in 
        up = (agentPosition[0], agentPosition[1]+1)
        down = (agentPosition[0], agentPosition[1]-1)
        left = (agentPosition[0]-1, agentPosition[1])
        right = (agentPosition[0]+1, agentPosition[1])

        #stench indicator; cell next to one inhibited by wumpus
        if(up==self.npc.wumpus or down==self.npc.wumpus or left==self.npc.wumpus or right==self.npc.wumpus):
            sensory[1] = 1        

        #tingle indicator; cell next to one inhibited by confundus 
        if(up in self.npc.portal or down in self.npc.portal or left in self.npc.portal or right in self.npc.portal):
            sensory[2] = 1
        
        return sensory

    #print the map
    def printMap(self, sensory):
        self.spawnNPConMap() #before printing the map, update the relevant cell to indicate presence of npc
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

class NPC:
    def __init__(self):
        #position of npc store as tuple(x, y)
        #access using self.wumpus[0] and self.wumpus[1]
        self.wumpus = (1,3)
        self.coin = (2,3)
        self.portal = [(3,1), (3,3), (4,4)]
        
    #spawn the npc location randomly 
    def spawnNPC(self, agentX, agentY, rows, columns):
        #x y should not be repeated, use a set to prevent repeation of coordinates
        coordinates = set()
        coordinates.add((agentX, agentY)) #add agent position to set so that it will not be repeated
        
        while(len(coordinates) != 6):
            x=random.randint(1,columns-2) # X correspond to columns
            y=random.randint(1,rows-2) # Y correspond to row
            coordinates.add((x,y))
        coordinates.remove((agentX, agentY)) #remove agent postion from set so that it will not be assigned to npc

        self.wumpus = coordinates.pop()
        self.coin = coordinates.pop()
        self.portal[0] = coordinates.pop()
        self.portal[1] = coordinates.pop()
        self.portal[2] = coordinates.pop()
    
    def printNPC(self):
        print(f"Wumpus: {self.wumpus}", end=", ")
        print(f"Coin: {self.coin}", end=", ")
        print(f"Portal1: {self.portal[0]}", end=", ")
        print(f"Portal2: {self.portal[1]}", end=", ")
        print(f"Portal3: {self.portal[2]}")


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
        self.sensory = [1,0,0,0,0,0]

    def spawnAgent(self):
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)
        self.map.updateCellSensory(self.sensory, self.x, self.y)     

    def moveForward(self):
        bump = False
        print("Action sequence: move forward")
        oldX = self.x
        oldY = self.y

        #depend on orientation move the agent 
        if(self.orientation=='north'): self.y = self.y + 1
        elif(self.orientation=='east'): self.x = self.x + 1 
        elif(self.orientation=='south'): self.y = self.y - 1 
        elif(self.orientation=='west'): self.x = self.x - 1 

        #check if bump into wall, valid x is range 1 to 4; valid y is range 1 to 5
        #bump to wall is out of the valid range
        if(self.x <=0 or self.x>=5 or self.y<=0 or self.y>=6):
            #do not let agent move to wall so return to old position
            self.x = oldX
            self.y = oldY
            bump = True

        #update the position on the map and print the map
        self.map.updateCellAgent(oldX, oldY, self.x, self.y, self.orientation)
        return bump
    
    def turnLeft(self):
        print("Action sequence: turn left")
        if(self.orientation=='north'): self.orientation='west'
        elif(self.orientation=='east'): self.orientation='north'
        elif(self.orientation=='south'): self.orientation='east'
        elif(self.orientation=='west'): self.orientation='south'

        #update the orientation on the map and print the map, x y no change
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)

    def turnRight(self):
        print("Action sequence: turn right")
        if(self.orientation=='north'): self.orientation='east'
        elif(self.orientation=='east'): self.orientation='south'
        elif(self.orientation=='south'): self.orientation='west'
        elif(self.orientation=='west'): self.orientation='north'

        #update the orientation on the map and print the map, x y no change
        self.map.updateCellAgent(self.x, self.y, self.x, self.y, self.orientation)

    def pickUp(self):
        print("Action sequence: pickup")
        #if there is coin in current cell
        if((self.x, self.y) == self.map.npc.coin):
            self.map.npc.coin = None #remove coin from npc
            print("Successfully pickup the coin")
        else:
            print("No coin to pickup")
            
    def shoot(self):
        scream = False #when wumpus killed, set scream to true
        print("Action sequence: shoot")
        #check if wumpus is ahead and in direction of agent to shoot
        aheadX = self.x
        aheadY = self.y
        
        #identify the ahead cell
        if(self.orientation=='north'): aheadY = aheadY + 1
        elif(self.orientation=='east'): aheadX = aheadX + 1
        elif(self.orientation=='south'): aheadY = aheadX - 1
        elif(self.orientation=='west'): aheadX = aheadX - 1

        #check if wumpus ahead to shoot
        if((aheadX, aheadY) == self.map.npc.wumpus):
            scream = True 
            self.map.npc.wumpus = None #remove wumpus from npc
            self.map.updateCellKillWumpus(aheadX, aheadY) #location of wumpus is at aheadX and aheadY, need to remove from cell
            print("Wumpus killed")
        else:
            print("Failed to kill wumpus")

        return scream

    def move(self, action):
        bump = False
        scream = False
        if(action == "moveforward"):
            bump = self.moveForward() #will teturn true if bump to wall
        elif(action == "turnleft"):
            self.turnLeft()
        elif(action == "turnright"):
            self.turnRight()
        elif(action == "pickup"):
            self.pickUp()
        elif(action == "shoot"):
            scream = self.shoot() #will return true if kill wumpus, there is a scream
        
        #bump and scream indicator are taken from the moveforward and shoot action then pass to percieveSensory to update the sensory list
        self.sensory = self.map.perceiveSensory((self.x, self.y), bump, scream)
        self.map.updateCellSensory(self.sensory, self.x, self.y)
        #TODO call to prolog to assert action and pass the sensory
        self.map.printMap(self.sensory)