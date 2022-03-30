from World import *

def main():
    ####### WHEN MAPPING COORDINATES TO WORLD DO map[y][x]
    ####### rows correspond to y coordinates and columns correspond to x coordinates(in manual 2.21)
    rows = 7
    columns = 6
    innerCell = 9
    map = None  #3d map[rows][columns][innerCell]

    agent=[1,1]
    #sensory = confounded, stench, tingle, glitter, bump, scream
    #0 for off, 1 for on
    #confounded on at start of the game 
    sensory = [1,0,0,0,0,0]

    #npc position 
    npc = {
        "wumpus": None,
        "coin": None,
        "portal1": None,
        "portal2": None,
        "portal3": None
    }

    map = createMap(rows, columns, innerCell)
    spawnNPC(npc, agent[0], agent[1], rows, columns)
    showNPC(npc, map)
    # showXY(map) #can use this to see the coordinate for the various grid 

    print(npc)
    printMap(map)

if __name__=="__main__":
    main()