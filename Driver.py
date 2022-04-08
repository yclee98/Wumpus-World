from World import *

def main():
    rows = 7
    columns = 6
    innerCell = 9
    
    #initializing objects
    map = Map(rows, columns, innerCell)
    npc = NPC()
    agent = Agent(map)

    #create map and spawn npc
    map.createMap()
    map.setNpc(npc)

    #absolute map prinout 
    npc.printNPC()
    #map.printMap(agent.sensory)

    #spawn the agent which will also query the prolog for knowledge, only confoundus is on at the start
    agent.spawnAgent()
    
    
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
        elif(move=="2"):
            map.clearMap()


if __name__== "__main__":
    main()