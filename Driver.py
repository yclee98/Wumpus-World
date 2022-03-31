from World import *

def main():
    rows = 7
    columns = 6
    innerCell = 9
    
    #initializing objects
    map = Map(rows, columns, innerCell)
    npc = NPC(map)
    agent = Agent(map)

    #create map and spawn agent/npc on map
    map.createMap()
    agent.spawnAgent()
    npc.spawnNPC(agent.x, agent.y, rows, columns)

    #absoulte map prinout
    npc.printNPC()
    map.printMap(agent.sensory)

    agent.moveForward()
    agent.moveForward()
    agent.turnRight()
    agent.moveForward()
    agent.shoot(npc)

if __name__== "__main__":
    main()