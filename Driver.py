from World import *

def main():
    rows = 7
    columns = 6
    innerCell = 9
    
    #initializing objects
    map = Map(rows, columns, innerCell)
    npc = NPC()
    #store map inside Agent class
    agent = Agent(map)

    #create map and spawn npc
    map.createMap()
    #store NPC inside map cass
    map.setNpc(npc)

    agent.spawnAgent()

    #if u want random npc location uncomment
    #npc.spawnNPC(agent.x, agent.y, rows, columns)
    npc.printNPC()

    #make agent explore automatically
    #agent.start()
    
    
    move = ""
    while(move != "1"):
        move = input("1 to exit; available input (f l r s p e): ")
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
            agent.explore()


if __name__== "__main__":
    main()