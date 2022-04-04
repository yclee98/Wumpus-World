from World import *

def main():
    rows = 7
    columns = 6
    innerCell = 9
    
    #initializing objects
    map = Map(rows, columns, innerCell)
    npc = NPC()
    agent = Agent(map)

    #create map and spawn agent/npc on map
    map.createMap()
    agent.spawnAgent()
    # npc.spawnNPC(agentX, agentY, rows, columns) #if want to random npc location
    map.setNpc(npc)

    #absoulte map prinout
    npc.printNPC()
    # map.showXY()
    map.printMap(agent.sensory)
    
    move = ""
    while(move != "1"):
        move = input("1 to exit; available input (f l r s p): ")
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


if __name__== "__main__":
    main()