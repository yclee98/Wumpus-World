from World import *

def main():
    rows = 7
    columns = 6
    innerCell = 9
    Rrows=3
    Rcolumns=3
    
    
    #initializing objects
    map = Map(rows, columns, innerCell)
    rMap= RelativeMap(Rrows, Rcolumns, innerCell)
    npc = NPC()
    #store map inside Agent class
    agent = Agent(map, rMap)

    #create map and spawn npc
    map.createMap()
    #store NPC inside map cass
    map.initalizeObject(npc, agent)
    map.restartGame()
    
    
    move = ""
    print("Exit: 1")
    print("Forward: f")
    print("Turn left: l")
    print("turn right: r")
    print("Shoot: s")
    print("Pickup: p")
    print("Explore: e")
    while(move != "1"):
        move = input("Available Inputs : f l r s p e 1): ")
        if(move == "f"):
            agent.move("moveforward")
        elif (move =="l"):
            agent.move("turnleft")
        elif (move =="r"):
            agent.move("turnright")
        elif (move=="s"):
            agent.move("shoot")
        elif(move=="p"):
            agent.move("pickup")
        elif(move=="e"):
            agent.endGame=False
            while(agent.endGame==False):
                agent.explore()


if __name__== "__main__":
    main()