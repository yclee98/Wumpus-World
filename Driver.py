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
    map.spawnNPConMap(npc, agent.x, agent.y)

    #absoulte map prinout
    npc.printNPC()
    # map.showXY()
    map.printMap(agent.sensory)
    
    move = ""
    while(move != "1"):
        move = input("available input (f l r s p): ")
        if(move == "f"):
            agent.moveForward()
        elif (move =="l"):
            agent.turnLeft()
        elif (move =="r"):
            agent.turnRight()
        elif (move=="s"):
            agent.shoot()
        elif(move=="p"):
            agent.pickUp()


if __name__== "__main__":
    main()