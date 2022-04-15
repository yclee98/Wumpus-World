from contextlib import nullcontext
import random
import math
from pyswip import Prolog

prolog = Prolog()
prolog.consult('Agent.pl')
#add reborn to end game reset 
bool(list(prolog.query("reborn()"))) 


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

        # #populate the walls on the first and last row with #
        # for i in range(self.columns):
        #     for k in range(self.innerCell):
        #         self.map[0][i][k]="#"
        #         self.map[lastrow][i][k]="#"

        # #populate the walls on the first and last columns with #
        # for i in range(self.rows):
        #     for k in range(self.innerCell):
        #         self.map[i][0][k]="#"
        #         self.map[i][lastcolumn][k]="#"

        #populate the cell 4 of the inner cell with ? 
        #to indicator, no agent, no known wumpus or portal or safe cell
        for i in range(self.rows):
            for j in range(self.columns):
                self.map[i][j][4] = "?"

    #clear the map of all symbols printout
    def clearMap(self):
        for i in range(self.rows):
            for j in range(self.columns):
                for k in range(self.innerCell):
                    self.map[i][j][k] = "."
        for i in range(self.rows):
            for j in range(self.columns):
                self.map[i][j][4] = "?"

    def fillWall(self, x, y):
        for k in range(self.innerCell):
            self.map[y][x][k]="#"

    #initialize npc to map variable
    def setNpc(self, npc):
        self.npc = npc

    #update cell with to indicate presence of npc 
    def updateCellNpc(self, npcX, npcY):
        #update cell 3 and 5 with "—" 
        self.map[npcY][npcX][3] = "—"
        self.map[npcY][npcX][5] = "—"

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
    def perceiveSensory(self, agentPosition, bump=False, scream=False):
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
        #self.spawnNPConMap() #before printing the map, update the relevant cell to indicate presence of npc
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
    def __init__(self, map, RelativeMap):
        self.map = map
        self.rMap= RelativeMap
        self.x = 1
        self.y = 1
        #orientation = north, south, east, west
        self.orientation = "north" 
        #sensory = confounded, stench, tingle, glitter, bump, scream
        #0 for off, 1 for on
        #confounded on at start of the game 
        self.sensory = [1,0,0,0,0,0]
        self.initial_scream_heard = 1

    def start(self):
        while(True):
            self.explore()

    def spawnAgent(self):
        self.x=1
        self.y=1
        self.orientation="north"
        self.initial_scream_heard = 1
        self.sensory = self.map.perceiveSensory((self.x, self.y))
        self.sensory[0] = 1
        bool(list(prolog.query("reborn()")))
        bool(list(prolog.query(f"reposition({self.sensory})")))
        self.queryAgentKnowledge()
        self.map.printMap(self.sensory)
        self.rMap.updateOrigin(0,0)
        self.rMap.printMap(self.sensory)
        

    def moveForward(self):
        bump = False
        print("Action sequence: move forward")
        oldX = self.x
        oldY = self.y

        #depend on orientation move the agent 
        if(self.orientation=='north'): 
            self.y = self.y + 1

        elif(self.orientation=='east'): 
            self.x = self.x + 1 
            
        elif(self.orientation=='south'): self.y = self.y - 1 
        elif(self.orientation=='west'): self.x = self.x - 1 

        #check if bump into wall, valid x is range 1 to 4; valid y is range 1 to 5
        #bump to wall is out of the valid range
        if(self.x <=0 or self.x>=5 or self.y<=0 or self.y>=6):
            #do not let agent move to wall so return to old position
            self.x = oldX
            self.y = oldY
            bump = True
        if(bump==False and (self.orientation=='north'or self.orientation=='south')):
            self.rMap.addrows(2)
        if(bump==False and (self.orientation=='east' or self.orientation=='west')):
            self.rMap.addcolumns(2)
        return bump
    
    def turnLeft(self):
        print("Action sequence: turn left")
        if(self.orientation=='north'): self.orientation='west'
        elif(self.orientation=='east'): self.orientation='north'
        elif(self.orientation=='south'): self.orientation='east'
        elif(self.orientation=='west'): self.orientation='south'


    def turnRight(self):
        print("Action sequence: turn right")
        if(self.orientation=='north'): self.orientation='east'
        elif(self.orientation=='east'): self.orientation='south'
        elif(self.orientation=='south'): self.orientation='west'
        elif(self.orientation=='west'): self.orientation='north'


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
        elif(self.orientation=='south'): aheadY = aheadY - 1
        elif(self.orientation=='west'): aheadX = aheadX - 1

        #check if there is arrow to shoot
        if(bool(list(prolog.query("hasarrow")))):
            #check if wumpus ahead to shoot
            if((aheadX, aheadY) == self.map.npc.wumpus):
                scream = True
                self.map.npc.wumpus = None #remove wumpus from npc
                print("Wumpus killed")
                self.rMap.heardScream()
            else:
                print("Failed to kill wumpus")
        else:
            print("No arrow to shoot")

        return scream

    def move(self, action):
        bump = False
        scream = False
        #naming convention for action is follow from manual 2.1
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

        #when stepping into confoundus portal, relocate agent, clear the map, perceive new sensory and update agent
        if(self.sensory[0]==1):
            self.enterConfundusPortal()
            self.map.clearMap()
            self.sensory = self.map.perceiveSensory((self.x, self.y))
            self.sensory[0] = 1 #mark confoundus indicator as on
            bool(list(prolog.query(f"reposition({self.sensory})")))
        else:
            #call the move on the prolog side 
            bool(list(prolog.query(f"move({action},{self.sensory})")))

        #query the knowledge of the agent to update the map
        self.queryAgentKnowledge()
        #self.map.printMap(self.sensory)
        self.rMap.printMap(self.sensory)

        self.checkEndGame()

    def explore(self):
        actions = list(prolog.query("explore(L)"))[0]['L']
        input()
        for i in actions:
            a = str(i)
            self.move(a)


    def queryAgentKnowledge(self):
        #get relative postion
        current = list(prolog.query("current(X,Y,D)"))[0]
        rx = current['X']
        ry = current['Y']
        rd = current['D']
        print(f"agent relative {rx} {ry} {rd}")
        print(f"agent absolute {self.x} {self.y} {self.orientation}")

        self.querySafeUnvisited(rx, ry)
        listOfConfoundus = self.queryPossibleConfoundus(rx, ry)
        listOfWumpus = self.queryPossibleWumpus(rx, ry)
        self.checkConfoundusWumpus(listOfConfoundus, listOfWumpus)

        self.queryWall(rx, ry)
        self.qeurySensory(rx, ry)
        self.queryVisited(rx, ry, rd)
        self.updateAgentPosition(rd)

    #check for possible cell with both confoundus and wumpus then mark cell as U
    def checkConfoundusWumpus(self, confoundus, wumpus):
        containBoth = confoundus.intersection(wumpus)
        for i in containBoth:
            self.map.map[i[1]][i[0]][4] = 'U'

    def queryPossibleWumpus(self, rx, ry):
        #query agent for wumpus location and use offset to represent in map
        #return a list of all confoundus location
        listOfWumpus = set() 
        offsetX = self.x - rx
        offsetY = self.y - ry
        print("Possible wumpus: ", end=" ")
        #valid game range for x is range 1 to 4; valid y is range 1 to 5
        for i in list(prolog.query("wumpus(X,Y)")):
            possibleX = i['X'] + offsetX
            possibleY = i['Y'] + offsetY
            listOfWumpus.add((possibleX, possibleY))
            print(f"({possibleX}, {possibleY})", end = " ")
            #if(possibleX > 0 and possibleX < 5 and possibleY > 0 and possibleY < 6):
            self.map.map[possibleY][possibleX][4] = 'W'
        print()
        return listOfWumpus

    def queryPossibleConfoundus(self, rx, ry):
        #query agent for confoundus location and use offset to represent in map
        #return a set of all confoundus location
        listOfConfoundus = set()
        offsetX = self.x - rx
        offsetY = self.y - ry
        print("Possible confoundus: ", end=" ")
        #valid game range for x is range 1 to 4; valid y is range 1 to 5
        for i in list(prolog.query("confoundus(X,Y)")):
            possibleX = i['X'] + offsetX
            possibleY = i['Y'] + offsetY
            listOfConfoundus.add((possibleX, possibleY))
            print(f"({possibleX}, {possibleY})", end = " ")
            #if(possibleX > 0 and possibleX < 5 and possibleY > 0 and possibleY < 6):
            self.map.map[possibleY][possibleX][4] = 'O'
        print()
        return listOfConfoundus
    
    def querySafeUnvisited(self, rx, ry):
        #query agent for safe unvisited location and use offset to represent in map
        offsetX = self.x - rx
        offsetY = self.y - ry
        print("Possible unvisited safe: ", end=" ")
        #valid game range for x is range 1 to 4; valid y is range 1 to 5
        for i in list(prolog.query("safe(X,Y)")):
            possibleX = i['X'] + offsetX
            possibleY = i['Y'] + offsetY
            print(f"({possibleX}, {possibleY})", end = " ")
            # if(possibleX > 0 and possibleX < 5 and possibleY > 0 and possibleY < 6):
            self.map.map[possibleY][possibleX][3] = '.'
            self.map.map[possibleY][possibleX][5] = '.'
            self.map.map[possibleY][possibleX][4] = 's'
        print()

    def queryVisited(self, rx, ry, rd):
        #query agent for visited location and use offset to represent in map
        offsetX = self.x - rx
        offsetY = self.y - ry
        print("Visited: ", end=" ")
        #valid game range for x is range 1 to 4; valid y is range 1 to 5
        for i in list(prolog.query("visited(X,Y)")):
            possibleX = i['X'] + offsetX
            possibleY = i['Y'] + offsetY
            print(f"({possibleX}, {possibleY})", end = " ")
            # if(possibleX > 0 and possibleX < 5 and possibleY > 0 and possibleY < 6):
            self.map.map[possibleY][possibleX][3] = '.'
            self.map.map[possibleY][possibleX][5] = '.'
            self.map.map[possibleY][possibleX][4] = 'S'
        print()
    
    def queryWall(self, rx, ry):
        #query agent for wall location and use offset to represent in map
        offsetX = self.x - rx
        offsetY = self.y - ry
        print("Possible wall: ", end=" ")
        #valid game range for x is range 1 to 4; valid y is range 1 to 5
        for i in list(prolog.query("wall(X,Y)")):
            possibleX = i['X'] + offsetX
            possibleY = i['Y'] + offsetY
            print(f"({possibleX}, {possibleY})", end = " ")
            self.map.fillWall(possibleX, possibleY)
        print()

        
    def updateAgentPosition(self, rd):
        #update cell 3 and 5 of the new cell agent is to '-'
        self.map.map[self.y][self.x][3] = '—'
        self.map.map[self.y][self.x][5] = '—'
        #update cell 4 to the relative orientation of the agent
        if(rd=='rnorth'):
            self.map.map[self.y][self.x][4] = '^'
        elif(rd=='rsouth'):
            self.map.map[self.y][self.x][4] = 'v'
        elif(rd=='reast'):
            self.map.map[self.y][self.x][4] = '>'
        elif(rd=='rwest'):
            self.map.map[self.y][self.x][4] = '<'

    def qeurySensory(self, rx, ry):
        #update confoundus, stench, tingle, glitter 
        #query the sensory information
        if bool(list(prolog.query(f"confoundus({rx},{ry})"))):
            self.map.map[self.y][self.x][0] = '%'

        else:
            self.map.map[self.y][self.x][0] = '.'
        if bool(list(prolog.query(f"stench({rx},{ry})"))):
            self.map.map[self.y][self.x][1] = '='
        else:
            self.map.map[self.y][self.x][1] = '.'
        if bool(list(prolog.query(f"tingle({rx},{ry})"))):
            self.map.map[self.y][self.x][2] = 'T'

        else:
            self.map.map[self.y][self.x][2] = '.'
        if bool(list(prolog.query(f"glitter({rx},{ry})"))):
            self.map.map[self.y][self.x][6] = '*'
        else:
            self.map.map[self.y][self.x][6] = '.'

        #update bump
        #query if the first and second current is the same it means it did not move so a bump
        try:
            newPosition = list(prolog.query("current(X,Y,D)"))[0]
            previousPosition = list(prolog.query("current(X,Y,D)"))[1]
            if(newPosition == previousPosition): 
                self.map.map[self.y][self.x][7] = 'B'
            else:
                self.map.map[self.y][self.x][7] = '.'
        except IndexError:
            #no previous position; at the start of the game 
            pass

        #update scream
        wumpus_count = len(list(prolog.query("wumpus(X,Y)")))
        hasarrow = bool(list(prolog.query("hasarrow")))
        if(hasarrow == False and wumpus_count==0 and self.initial_scream_heard == 1):
            self.map.map[self.y][self.x][8] = '@'
            self.initial_scream_heard = 0
        else:
            self.map.map[self.y][self.x][8] = '.'

        

    def enterConfundusPortal(self):
        print("standing on portal")
        listofNPC = set() # get list of npcs
        #typeWumpus = type(self.map.npc.wumpus) is tuple # checking if there is more than 1 wumpus
        typeCoin = type(self.map.npc.coin) is tuple # checking if there is more than 1 coin
        # if (typeWumpus == False):
        #     for i in range(len(self.map.npc.wumpus)):
        #             listofNPC.add(self.map.npc.wumpus[i])
        # else:

        if(self.map.npc.wumpus!=None):
            listofNPC.add(self.map.npc.wumpus)

        for i in range(len(self.map.npc.portal)):
                listofNPC.add(self.map.npc.portal[i])

        if (typeCoin == False):
            for i in range(len(self.map.npc.coin)):
                    listofNPC.add(self.map.npc.coin[i])
        else:
            listofNPC.add(self.map.npc.coin)
        #print("this is listofNPC", listofNPC) # end of getting list of NPCs
        # random while not in the list, set as new location
        #print("this is columns", self.columns)
        #print("this is rows", self.rows)
        flag = False
        while (flag==False):
            newX = random.randint(1,self.map.columns-2)
            newY=random.randint(1,self.map.rows-2)
            #print("this is new x", newX)
            #print("this is new Y", newY)
            newPosition = (newX,newY)
            if newPosition not in listofNPC:
                flag = True
                print("this is new position", newPosition)
                self.x=newX
                self.y=newY
                self.orientation="north"
                self.rMap.enterConfundusPortal(0,0)
                #self.updateAgentPosition('rnorth')
                #self.map.printMap(self.sensory)
        # reflect on the map

    def checkEndGame(self):
        w = self.enterWumpus()
        o = self.returnOrign()
        if (w == True or o == True):
            print("=================================")
            print("============GAME OVER============")
            print("=================================")
            quit()
            self.map.clearMap()
            self.spawnAgent()
            return True

    #when there is no coin and agent return to origin 
    def returnOrign(self):
        if(self.map.npc.coin == None and self.x==1 and self.y==1):
            print("coin collected, returned to origin, ganeover")
            return True
        return False


    def enterWumpus(self):
        if(self.map.npc.wumpus == None): return False

        if((self.x, self.y) == self.map.npc.wumpus):
            print("entered wumpus cell, gameover")
            return True
        else:
            return False

        
class RelativeMap(Map):
    def __init__(self,rows,columns,innerCell):
        self.rows = rows
        self.columns = columns
        self.innerCell = innerCell
        self.x =0
        self.y=0
        self.initial_scream_heard = 0

        self.map = []
    
    def printMap(self, sensory):
        #self.spawnNPConMap() #before printing the map, update the relevant cell to indicate presence of npc
        #print("this is x origin", self.x)
        #print("this is y origin", self.y)
        xmodifier= math.floor(self.columns/2)
        #print ("this is xmodifier", xmodifier)
        startingX= self.x - xmodifier
       # print("this is starting x",startingX) #starting from most left
        ymodifier=math.floor(self.rows/2)
        #print("this is ymodifier", ymodifier) 
        startingY=self.y+ymodifier#starting for the top
       # print("this is starting y",startingY)
       # print("in loop")
        for i in range (self.rows):
            #print("this is x", startingX, "this is y", startingY)
            self.printRow(startingX,startingY,self.columns)
            startingY=startingY-1

        self.printSensory(sensory)

    def getrows(self):
        return self.rows

    def getcolumns(self):
        return self.columns

    def setrows(self,value):
        self.rows=value
    def setcolumns(self,value):
        self.columns=value
    def addrows(self, value):
        self.rows = self.getrows()+ value
    def addcolumns(self, value):
        self.columns = self.getcolumns()+ value
    def enterConfundusPortal(self, newX, newY):
        self.setrows(3)
        self.setcolumns(3)
        self.updateOrigin(newX,newY)

    def updateOrigin(self,x,y):
        self.x=x
        self.y=y


    def printRow(self,x, y, numOfRoom):
        print("|", end=" ")
        #query first row of symbols
        for k in range(numOfRoom):
            x1 = x + k
            if(bool(list(prolog.query(f"wall({x1}, {y})")))): 
                print("# # #", end=" ")
                print("|", end=" ")
                continue
            if(bool(list(prolog.query(f"confoundus({x1}, {y})"))) and bool(list(prolog.query(f"visited({x1}, {y})")))): print("%", end =" ")
            else: print(".", end =" ")
            if(bool(list(prolog.query(f"stench({x1}, {y})")))): print("=", end =" ")
            else: print(".", end =" ")
            if(bool(list(prolog.query(f"tingle({x1}, {y})")))): print("T", end =" ")
            else:
                print(".", end =" ")
            print("|", end=" ")
        print()

        #query second row of symbols
        print("|", end=" ")
        for k in range(numOfRoom):
            x1 = x + k
            if(bool(list(prolog.query(f"wall({x1}, {y})")))): 
                print("# # #", end=" ")
                print("|", end=" ")
                
                continue
            wumpus = bool(list(prolog.query(f"wumpus({x1},{y})")))
            confoundus = bool(list(prolog.query(f"confoundus({x1},{y})"))) and not(x1==0 and y==0)
            agent = list(prolog.query(f"current({x1},{y},D)"))
            if(wumpus or confoundus or bool(agent)):
                print("—", end =" ")
                if(bool(agent)):
                    d = agent[0]['D']
                    if(d == "rnorth"): print("^", end=" ")
                    elif(d == "reast"): print(">", end=" ")
                    elif(d == "rsouth"): print("V", end=" ")
                    elif(d == "rwest"): print("<", end=" ")
                elif(wumpus and confoundus): print("U", end =" ")
                elif(wumpus): print("W", end =" ")
                elif(confoundus):print("O", end =" ")
                print("—", end =" ")
            else:
                print(".", end =" ")
                if(bool(list(prolog.query(f"visited({x1},{y})")))): print("S", end =" ") 
                elif(bool(list(prolog.query(f"safe({x1},{y})")))): print("s", end =" ")
                else: print("?", end =" ")  
                print(".", end =" ")
            print("|", end=" ")
        print()

        #query third row of symbols
        print("|", end=" ")
        for k in range(numOfRoom):
            x1 = x + k
            if(bool(list(prolog.query(f"wall({x1}, {y})")))): 
                print("# # #", end=" ")
                print("|", end=" ")
                continue
            if(bool(list(prolog.query(f"glitter({x1}, {y})")))): print("*", end =" ")
            else: print(".", end =" ")
            agent = bool(list(prolog.query(f"current({x1},{y},D)")))
            if(agent):
                try:
                    cur = list(prolog.query("current(X,Y,D)"))
                    if(cur[0] == cur[1]): print("B", end=" ")
                    else: print(".", end=" ")
                except IndexError:
                    print(".", end=" ")

                wumpus_count = len(list(prolog.query("wumpus(X,Y)")))
                hasarrow = bool(list(prolog.query("hasarrow")))
                if(agent and hasarrow == False and wumpus_count==0 and self.initial_scream_heard==1):
                    print("@", end=" ")
                    self.initial_scream_heard = 0
                else:
                    print(".", end=" ")
            else:
                print(".", end=" ")
                print(".", end=" ")

            print("|", end=" ")
        print()

    def heardScream(self):
        self.initial_scream_heard=1
    


        




