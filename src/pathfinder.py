
from dataclasses import dataclass
from map import Map, Pos

WIDTH = 9
HEIGHT = 27

@dataclass
class PathTile:
    parent  = None
    gCost: float = 0  # Distance to start node
    hCost: float = 0  # Distance to goal node
    pos: Pos = Pos(0, 0)
    @property
    def fCost(self):
        return self.gCost + self.hCost
    
    def __hash__(self):
        return self.pos.__hash__()

    def w(self):
        return "O" if self.walkable else "X"


class PathFinding:
    def __init__(self, map: Map, size:int = 32) -> None:
        self.map = map
        self.size = size
        self.tiles: list[list[PathTile]] = []
        for x in range(HEIGHT):
            self.tiles.append([])
            for y in range(WIDTH):
                # Remove walkable
                self.tiles[x].append(PathTile(pos=Pos(x,y)))
                
    def isTileWalkable(self, pos: Pos):
        return self.map.isTileWalkable(pos)
    
    def getAStarTile(self, pos: Pos):
        return self.tiles[pos.x][pos.y]
    
    def getPath(self, start: Pos, end: Pos):

        start_tile = self.getAStarTile(start)
        goal_tile = self.getAStarTile(end)
        open_list: set[PathTile] = set()
        open_list.add(start_tile)
        closed_list: set[PathTile] = set()
        while len(open_list) > 0:
            current_tile = min(open_list, key = lambda tile: tile.fCost )
            open_list.remove(current_tile)
            closed_list.add(current_tile)
            if current_tile.pos == goal_tile.pos:
                return self._reTracePath(start_tile, goal_tile)

            for pos in self.map.getNeighbors(current_tile.pos):
                neigbor = self.getAStarTile(pos)
                # TODO: change to lookup map
                if not self.isTileWalkable(pos) or neigbor in closed_list:
                    continue
                newMovementCostToNeigbor = current_tile.gCost + current_tile.pos.dist(pos)
                if newMovementCostToNeigbor < neigbor.gCost or not neigbor in open_list:
                    neigbor.gCost = newMovementCostToNeigbor
                    neigbor.hCost = goal_tile.pos.dist(pos)
                    neigbor.parent = current_tile
                    if not neigbor in open_list:
                        open_list.add(neigbor)
        return None