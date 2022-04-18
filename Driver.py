from contextlib import nullcontext
import random
import math
from pyswip import Prolog

prolog = Prolog()
prolog.consult('Agent.pl')

####### WHEN REFERENCING THE MAP DO map[y][x], map[row][column]
####### Rows correspond to y coordinates and columns correspond to x coordinates for the map(in manual 2.21)
class Map:
    def __init__(self, rows, columns, innerCell):
        self.rows = rows
        self.columns = columns
        self.innerCell = innerCell
        self.map = []
        self.npc = None
        self.agent = None

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

        #populate the cell 4 of the inner cell with ? 
        #to indicator, no agent, no known wumpus or portal or safe cell
        for i in range(self.rows):
            for j in range(self.columns):
                self.map[i][j][4] = "?"

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

    #initialize npc to map variable
    def initalizeObject(self, npc, agent):
        self.npc = npc
        self.agent = agent

    def restartGame(self):
        self.clearMap()
        self.agent.spawnAgent()
        self.npc.spawnNpc()
        self.spawnNPConMap()
        self.printMap()
        self.agent.rMap.updateOrigin(0,0)
        self.agent.rMap.printMap(self.agent.sensory)


    #clear the map of all symbols printout
    def clearMap(self):
        for i in range(1, self.rows-1):
            for j in range(1, self.columns-1):
                for k in range(self.innerCell):
                    self.map[i][j][k] = "."
        for i in range(1, self.rows-1):
            for j in range(1, self.columns-1):
                self.map[i][j][4] = "?"

    def fillWall(self, x, y):
        for k in range(self.innerCell):
            self.map[y][x][k]="#"

    #update cell with to indicate presence of npc 
    def updateCellNpc(self, npcX, npcY, A):
        #update cell 3 and 5 with "—" 
        self.map[npcY][npcX][3] = "—"
        self.map[npcY][npcX][5] = "—"
        self.map[npcY][npcX][4] = A

    #show the npc on the map;
    def spawnNPConMap(self):
        if(self.npc.wumpus!=None):
            self.updateCellNpc(self.npc.wumpus[0], self.npc.wumpus[1], "W")
        if(self.npc.coin!=None):
            #self.updateCellNpc(self.npc.coin[0], self.npc.coin[1], "C")
            self.map[self.npc.coin[1]][self.npc.coin[0]][6] = "*"
        self.updateCellNpc(self.npc.portal[0][0], self.npc.portal[0][1], "O")
        self.updateCellNpc(self.npc.portal[1][0], self.npc.portal[1][1], "O")
        self.updateCellNpc(self.npc.portal[2][0], self.npc.portal[2][1], "O")
    
    def spawnAgentOnMap(self, x ,y, orientation):
        if(orientation=='north'): self.map[y][x][4]='^'
        elif(orientation=='east'): self.map[y][x][4]='>'
        elif(orientation=='south'): self.map[y][x][4]='v'
        elif(orientation=='west'): self.map[y][x][4]='<'
        self.map[y][x][3]='—'
        self.map[y][x][5]='—'


    #perceive sensory at position x y
    def perceiveSensory(self, agentPosition, bump=False, scream=False):
        #agentPosition in (x, y)
        #confounded, stench, tingle, glitter, bump, scream
        sensory = ["off", "off", "off", "off", "off", "off"] #intialize all sensory to off

        #confounded indicator; agent in the same cell as a confundus
        if(agentPosition in self.npc.portal):
            sensory[0] = "on"

        #glitter indicator; agent in same cell as coin
        if(agentPosition == self.npc.coin):
            sensory[3] = "on"
        
        #bump indicator
        if(bump):
            sensory[4] = "on"
        
        #scream indicator
        if(scream):
            sensory[5] = "on"
        
        #get the up down left right cell of the position agent is in 
        up = (agentPosition[0], agentPosition[1]+1)
        down = (agentPosition[0], agentPosition[1]-1)
        left = (agentPosition[0]-1, agentPosition[1])
        right = (agentPosition[0]+1, agentPosition[1])

        #stench indicator; cell next to one inhibited by wumpus
        if(up==self.npc.wumpus or down==self.npc.wumpus or left==self.npc.wumpus or right==self.npc.wumpus):
            sensory[1] = "on"        

        #tingle indicator; cell next to one inhibited by confundus 
        if(up in self.npc.portal or down in self.npc.portal or left in self.npc.portal or right in self.npc.portal):
            sensory[2] = "on"
        
        return sensory
        

    #print the map
    def printMap(self):
        innerCellColumn = self.innerCell // 3
        innerCellRow = self.innerCell // 3
        print()
        print("=================Absolute Map====================")
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
        print()

    #print the sensory
    def printSensory(self, sensory):
        fullName = ["Confounded", "Stench", "Tingle", "Glitter", "Bump", "Scream"]
        output = ""
        for i in range(len(sensory)):
            if(sensory[i] == "on"): #indicator is on
                output = output + fullName[i] + "—"
            else: #indicator is off
                output = output + fullName[i][0] + "—"
        print("Percepts: " + output)
        print()


class NPC:
    def __init__(self):
        #position of npc store as tuple(x, y)
        #access using self.wumpus[0] and self.wumpus[1]
        self.wumpus = None
        self.coin = None
        self.portal = [None, None, None]
    
    def spawnNpc(self):
        self.wumpus = (1,3)
        self.coin = (2,3)
        self.portal = [(3,1), (3,3), (4,4)]
        

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
        self.sensory = ["on", "off","off","off", "off", "off"]
        self.initial_scream_heard = 1
        self.origin = (1,1)
        self.endGame = False

    def spawnAgent(self):
        self.endGame = False
        self.x=1
        self.y=1
        self.orientation="north"
        self.origin = (1,1)
        self.initial_scream_heard = 1
        self.sensory = self.map.perceiveSensory((self.x, self.y))
        self.sensory[0] = "on"
        bool(list(prolog.query("reborn()")))
        bool(list(prolog.query(f"reposition({self.sensory})")))
        self.map.spawnAgentOnMap(self.x, self.y, self.orientation)
        

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
            self.rMap.addrows(2, self.orientation)
        if(bump==False and (self.orientation=='east' or self.orientation=='west')):
            self.rMap.addcolumns(2, self.orientation)
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

        bool(list(prolog.query(f"move({action},{self.sensory})")))

        #when stepping into confundus portal, relocate agent, clear the map, perceive new sensory and update agent
        if(self.sensory[0]=="on"):
            self.enterConfundusPortal()
            # self.map.clearMap()
            self.sensory = self.map.perceiveSensory((self.x, self.y))
            self.sensory[0] = "on" #mark confundus indicator as on
            bool(list(prolog.query(f"reposition({self.sensory})")))
            
        self.rMap.printMap(self.sensory)

        self.checkEndGame()

    def explore(self):
        while(self.endGame == False):
            actions = list(prolog.query("explore(L)"))[0]['L']
            for i in actions:
                a = str(i)
                self.move(a)
       

    def enterConfundusPortal(self):
        print("===================================")
        print("===========ENTERED PORTAL==========")
        print("===================================")
        listofNPC = set() # get list of npcs
        typeCoin = type(self.map.npc.coin) is tuple # checking if there is more than 1 coin

        if(self.map.npc.wumpus!=None):
            listofNPC.add(self.map.npc.wumpus)

        for i in range(len(self.map.npc.portal)):
                listofNPC.add(self.map.npc.portal[i])

        if (typeCoin == False):
            for i in range(len(self.map.npc.coin)):
                    listofNPC.add(self.map.npc.coin[i])
        else:
            listofNPC.add(self.map.npc.coin)
        flag = False
        while (flag==False):
            newX = random.randint(1,self.map.columns-2)
            newY=random.randint(1,self.map.rows-2)
            newPosition = (newX,newY)
            if newPosition not in listofNPC:
                flag = True
                print("this is new position", newPosition)
                self.x=newX
                self.y=newY
                self.orientation="north"
                self.origin = (newX, newY)
                self.rMap.enterconfundusPortal(0,0)
                self.map.clearMap()
                self.map.spawnNPConMap()
                self.map.spawnAgentOnMap(self.x, self.y, self.orientation)
                self.map.printMap()
        # reflect on the map

    def checkEndGame(self):
        w = self.enterWumpus()
        o = self.returnOrign()
        if (w == True or o == True):
            print("=================================")
            print("============GAME OVER============")
            print("=================================")
            # self.map.restartGame()
            self.endGame = True
            return True

    #when there is no coin and agent return to origin 
    def returnOrign(self):
        if(self.map.npc.coin == None and (self.x, self.y) == self.origin):
            print("Coin collected, returned to origin, ganeover")
            return True
        return False


    def enterWumpus(self):
        if(self.map.npc.wumpus == None): return False

        if((self.x, self.y) == self.map.npc.wumpus):
            print("Entered wumpus cell, gameover")
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
        self.IX = 0
        self.IY = 0
        self.maxX = False
        self.maxY = False

        # self.map = []
    
    def printMap(self, sensory):
        xmodifier= math.floor(self.columns/2)
        startingX= self.x - xmodifier
        ymodifier=math.floor(self.rows/2)
        startingY=self.y+ymodifier#starting for the top
        for i in range (self.rows):
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

    def addrows(self, value, direction):
        if(self.maxY == True): return
        if(direction == "north"):
            self.IY = self.IY + 1
            if(self.IY >= 4): 
                self.maxY = True
            if(self.IY<=0 or self.IY>4):
                return
        elif(direction == "south"):
            self.IY = self.IY -1
            if(self.IY <= -4): 
                self.maxY = True
            if(self.IY>=0 or self.IY<-4):
                return
        self.rows = self.getrows()+ value

    def addcolumns(self, value, direction):
        if(self.maxX == True): 
            return
        if(direction == "east"):
            self.IX = self.IX + 1
            if(self.IX >= 3): 
                self.maxX = True
            if(self.IX<=0 or self.IX>3):
                return
        elif(direction == "west"):
            self.IX = self.IX -1
            if(self.IX <= -3): 
                self.maxX = True
            if(self.IX>=0 or self.IX<-3):
                return
        self.columns = self.getcolumns()+ value

    def enterconfundusPortal(self, newX, newY):
        self.updateOrigin(newX,newY)

    def updateOrigin(self,x,y):
        self.setrows(3)
        self.setcolumns(3)
        self.x=x
        self.y=y
        self.IX=0
        self.IY=0
        self.maxX = False
        self.maxY = False


    def printRow(self,x, y, numOfRoom):
        print("|", end=" ")
        #query first row of symbols
        for k in range(numOfRoom):
            x1 = x + k
            if(bool(list(prolog.query(f"wall({x1}, {y})")))): 
                print("# # #", end=" ")
                print("|", end=" ")
                continue
            if(bool(list(prolog.query(f"confundus({x1}, {y})"))) and bool(list(prolog.query(f"visited({x1}, {y})")))): print("%", end =" ")
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
            confundus = bool(list(prolog.query(f"confundus({x1},{y})"))) and not(x1==0 and y==0)
            agent = list(prolog.query(f"current({x1},{y},D)"))
            if(wumpus or confundus or bool(agent)):
                print("—", end =" ")
                if(bool(agent)):
                    d = agent[0]['D']
                    if(d == "rnorth"): print("^", end=" ")
                    elif(d == "reast"): print(">", end=" ")
                    elif(d == "rsouth"): print("V", end=" ")
                    elif(d == "rwest"): print("<", end=" ")
                elif(wumpus and confundus): print("U", end =" ")
                elif(wumpus): print("W", end =" ")
                elif(confundus):print("O", end =" ")
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

import sys


class Test:
    def __init__(self, agent, map):
        self.agent = agent
        self.map = map

    def run_test(self):
        self.correctness_of_explore()

    def correctness_of_explore(self):
        self.map.restartGame()
        self.agent.explore()


def main():
    rows = 7
    columns = 6
    innerCell = 9
    Rrows=3
    Rcolumns=3

    filename = "TeamPatience-testPrintout-Self-Self.txt"
    sys.stdout = open(file=filename, mode="w+", encoding="utf8")

    #initializing objects
    map = Map(rows, columns, innerCell)
    rMap= RelativeMap(Rrows, Rcolumns, innerCell)
    npc = NPC()
    agent = Agent(map, rMap)
    test = Test(agent, map)

    #create map and spawn npc
    map.createMap()
    #store NPC inside map cass
    map.initalizeObject(npc, agent)

    test.run_test()

if __name__== "__main__":
    main()