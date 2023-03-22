

from dataclasses import dataclass
from enum import Enum
from collections import deque
from functools import lru_cache

WIDTH = 9
HEIGHT = 27


class ItemType(Enum):
    CHERRY_BLOSSOM = "CHERRY_BLOSSOM"
    ROSE = "ROSE"
    LILAC = "LILAC"
    SUNFLOWER = "SUNFLOWER"
    ENERGY = "ENERGY" 
    BOOSTER_NECTAR_30_PCT = "BOOSTER_NECTAR_30_PCT"
    BOOSTER_NECTAR_50_PCT = "BOOSTER_NECTAR_50_PCT"
    BOOSTER_NECTAR_100_PCT = "BOOSTER_NECTAR_100_PCT"
    HIVE = "HIVE"
    POND = "POND"
    EMPTY = "EMPTY"
    MINUS_FIFTY_PCT_ENERGY = "MINUS_FIFTY_PCT_ENERGY"
    SUPER_HONEY = "SUPER_HONEY"
    FREEZE = "FREEZE"
    HOLE = "HOLE"
    
FLOWER_VALUE = [ItemType.SUNFLOWER, ItemType.LILAC, ItemType.ROSE, ItemType.CHERRY_BLOSSOM]

flowers = {
    ItemType.CHERRY_BLOSSOM : 15,
    ItemType.ROSE : 30,
    ItemType.LILAC : 45,
    ItemType.SUNFLOWER : 60
}

boosters = {
    ItemType.BOOSTER_NECTAR_30_PCT:30,
    ItemType.BOOSTER_NECTAR_50_PCT:50,
    ItemType.BOOSTER_NECTAR_100_PCT:100,
}

specials = {
    ItemType.MINUS_FIFTY_PCT_ENERGY:50,
    ItemType.SUPER_HONEY:150,
    ItemType.FREEZE:100,
}

NECTAR_VALUE = {
    ItemType.SUNFLOWER:60,
    ItemType.LILAC:45, 
    ItemType.ROSE:30, 
    ItemType.CHERRY_BLOSSOM:15,
    ItemType.ENERGY:0,
    ItemType.BOOSTER_NECTAR_30_PCT:0,
    ItemType.BOOSTER_NECTAR_50_PCT:0,
    ItemType.BOOSTER_NECTAR_100_PCT:0,
    ItemType.HIVE:0,
    ItemType.POND:0,
    ItemType.EMPTY:0,
    ItemType.MINUS_FIFTY_PCT_ENERGY:0,
    ItemType.SUPER_HONEY:0,
    ItemType.FREEZE:0,
    ItemType.HOLE:0,
}
@dataclass
class TileContent:
    itemType: ItemType
    numOfItems: int
    
    def update(self, data):
        self.itemType = ItemType[data["itemType"]]
        self.numOfItems = data["numOfItems"]

def IsWalkalbe(type: ItemType):
    return type != ItemType.HOLE and type != ItemType.POND

@dataclass
class Tile:
    x: int
    y: int
    isWalkable:bool
    tileContent: TileContent
    
    def update(self, data):
        self.x = data["row"]
        self.y = data["column"]
        self.tileContent.update(data["tileContent"])
    

@dataclass
class Pos:
    x: int
    y: int     
    
    def from_tile(tile: Tile):
        return Pos(tile.x, tile.y)   
    
    def __hash__(self):
        return self.x<<10+self.y
    
    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y 

def getMoveAction(pos1 : Pos, pos2 : Pos):
    difX = pos1.x - pos2.x
    difY = pos1.y - pos2.y


    if difX == 2:    #(x-2, y) -> gore
        return 'w'
    if difX == -2:   #(x+2, y) -> dole 
        return 's'
        
    if pos1.x % 2 == 0:
        if difX == 1 and difY == 1: #(x-1, y-1) -> gore levo
            return 'q'
        if difX == 1 and difY == 0: #(x-1, y) -> gore desno
            return 'e'
        if difX == -1 and difY == 0: #(x+1, y) -> dole desno
            return 'd'
        if difX == -1 and difY == 1: #(x+1, y-1) -> dole levo
            return 'a'
    else:
        if difX == 1 and difY == 0: #(x-1, y) -> gore levo
            return 'q'
        if difX == 1 and difY == -1: #(x-1, y+1) -> gore desno
            return 'e'
        if difX == -1 and difY == -1: #(x+1, y+1) -> dole desno
            return 'd'
        if difX == -1 and difY == 0: #(x+1, y) -> dole levo
            return 'a'

def getMoves(path: list[Pos]):
    moves = []
    if path is None:
        return moves
    for i in range(len(path)-1):
        moves.append(getMoveAction(path[i], path[i+1]))
    return moves

def mergeMoves(moves: list[Pos]):
    skip_moves = []
    active_skip_move = {"dir":"", "dist":1}
    for move in moves:
        if move != active_skip_move["dir"]:
            skip_moves.append(active_skip_move.copy())
            active_skip_move["dir"] = move
            active_skip_move["dist"] = 1
        else:
            active_skip_move["dist"] += 1
    skip_moves.append(active_skip_move)
    return skip_moves[1:]
def getSkipMoves(path: list[Pos]):
    moves = getMoves(path)
    return mergeMoves(moves)
    
    
class Map:
    def __init__(self, map_state):
        self.tiles: list[list[Tile]] = []
        self.width: int = map_state["width"]
        self.height: int = map_state["height"]
        self.init_tiles(map_state["tiles"])
        
        self.opp_pos = None
    
    def update_opp_pos(self, pos: Pos):
        self.tiles[pos.x][pos.y].isWalkable = False
        if self.opp_pos is not None:
            self.tiles[self.opp_pos.x][self.opp_pos.y].isWalkable = True
        self.opp_pos = pos
    
    def init_tiles(self, tile_state):
        for x in range(HEIGHT):
            self.tiles.append([])
            for y in range(WIDTH):
                temp = tile_state[x][y]
                self.tiles[x].append(Tile(temp["row"], temp["column"], IsWalkalbe(ItemType[temp["tileContent"]["itemType"]]),
                                        TileContent(ItemType[temp["tileContent"]["itemType"]], 
                                                    temp["tileContent"]["numOfItems"])))
                
    def update(self, map_state):
        tile_state = map_state["tiles"]
        for x in range(HEIGHT):
            for y in range(WIDTH):
                self.tiles[x][y].update(tile_state[x][y])
    
    def getNeighborForOneDir(self, pos : Pos, dir:int): 
        if pos.x%2 == 1:
            if pos.x > 0 and dir==0:
                return (Pos(pos.x-1,pos.y))      # Gore Levo -> q
            if pos.x > 1 and dir==1:
                return (Pos(pos.x-2,pos.y))      # Gore -> w
            if pos.x > 0 and pos.y < 8 and dir==2:
                return (Pos(pos.x-1,pos.y+1))    # Gore Desno -> e 
            if pos.x < 26 and pos.y < 8 and dir==3:
                return (Pos(pos.x+1,pos.y+1))    # Dole Desno -> d 
            if pos.x < 25 and dir==4:
                return (Pos(pos.x+2,pos.y))      # Dole -> s
            if pos.x < 26 and dir==5:
                return (Pos(pos.x+1,pos.y))      # Dole levo -> a
        else:
            if pos.x > 0 and pos.y >0  and dir==0:
                return (Pos(pos.x-1,pos.y-1))    # Gore Levo -> q
            if pos.x > 1  and dir==1:    
                return (Pos(pos.x-2,pos.y))      # Gore -> w
            if pos.x > 0  and dir==2:
                return (Pos(pos.x-1,pos.y))      # Gore Desno -> e 
            if pos.x < 26  and dir==3:
                return (Pos(pos.x+1,pos.y))      # Dole Desno -> d 
            if pos.x < 25  and dir==4:
                return (Pos(pos.x+2,pos.y))      # Dole -> s
            if pos.x < 26 and pos.y >0  and dir==5:
                return (Pos(pos.x+1,pos.y-1))    # Dole levo -> a
        return None
     
                
    def getNeighbors(self, pos : Pos): 
        neighbors = list()
        if pos.x%2 == 1:
            if pos.x > 0:
                neighbors.append(Pos(pos.x-1,pos.y))      # Gore Levo -> q
            if pos.x > 1:
                neighbors.append(Pos(pos.x-2,pos.y))      # Gore -> w
            if pos.x > 0 and pos.y < 8:
                neighbors.append(Pos(pos.x-1,pos.y+1))    # Gore Desno -> e 
            if pos.x < 26 and pos.y < 8:
                neighbors.append(Pos(pos.x+1,pos.y+1))    # Dole Desno -> d 
            if pos.x < 25:
                neighbors.append(Pos(pos.x+2,pos.y))      # Dole -> s
            if pos.x < 26:
                neighbors.append(Pos(pos.x+1,pos.y))      # Dole levo -> a
        else:
            if pos.x > 0 and pos.y >0:
                neighbors.append(Pos(pos.x-1,pos.y-1))    # Gore Levo -> q
            if pos.x > 1:    
                neighbors.append(Pos(pos.x-2,pos.y))      # Gore -> w
            if pos.x > 0:
                neighbors.append(Pos(pos.x-1,pos.y))      # Gore Desno -> e 
            if pos.x < 26:
                neighbors.append(Pos(pos.x+1,pos.y))      # Dole Desno -> d 
            if pos.x < 25:
                neighbors.append(Pos(pos.x+2,pos.y))      # Dole -> s
            if pos.x < 26 and pos.y >0:
                neighbors.append(Pos(pos.x+1,pos.y-1))    # Dole levo -> a
        return neighbors
    
    def getNeighborsAll(self, pos : Pos): 
        neighbors = list()
        if pos.x%2 == 1:
            if pos.x > 0:
                neighbors.append(Pos(pos.x-1,pos.y))  # Gore Levo -> q
            else: 
                neighbors.append(None)
            if pos.x > 1:
                neighbors.append(Pos(pos.x-2,pos.y))      # Gore -> w
            else: 
                neighbors.append(None)
            if pos.x > 0 and pos.y < 8:
                neighbors.append(Pos(pos.x-1,pos.y+1))    # Gore Desno -> e 
            else: 
                neighbors.append(None)
            if pos.x < 26 and pos.y < 8:
                neighbors.append(Pos(pos.x+1,pos.y+1))    # Dole Desno -> d 
            else: 
                neighbors.append(None)
            if pos.x < 25:
                neighbors.append(Pos(pos.x+2,pos.y))      # Dole -> s
            else: 
                neighbors.append(None)
            if pos.x < 26:
                neighbors.append(Pos(pos.x+1,pos.y))      # Dole levo -> a
            else: 
                neighbors.append(None)
        else:
            if pos.x > 0 and pos.y >0:
                neighbors.append(Pos(pos.x-1,pos.y-1))    # Gore Levo -> q
            else: 
                neighbors.append(None)
            if pos.x > 1:    
                neighbors.append(Pos(pos.x-2,pos.y))      # Gore -> w
            else: 
                neighbors.append(None)
            if pos.x > 0:
                neighbors.append(Pos(pos.x-1,pos.y))      # Gore Desno -> e 
            else: 
                neighbors.append(None)
            if pos.x < 26:
                neighbors.append(Pos(pos.x+1,pos.y))      # Dole Desno -> d 
            else: 
                neighbors.append(None)
            if pos.x < 25:
                neighbors.append(Pos(pos.x+2,pos.y))      # Dole -> s
            else: 
                neighbors.append(None)
            if pos.x < 26 and pos.y >0:
                neighbors.append(Pos(pos.x+1,pos.y-1))    # Dole levo -> a
            else: 
                neighbors.append(None)
        return neighbors
    
    def getTile(self, pos:Pos):
        return self.tiles[pos.x][pos.y]
    def isTileWalkable(self, pos:Pos):
        return self.tiles[pos.x][pos.y].isWalkable
    @lru_cache(8)
    def floodFill(self, pos: Pos, depth: int = -1):
        if depth == -1:
            depth = 2*HEIGHT
        queue = deque()
        mat = [[-1 for i in range(WIDTH)] for j in range(HEIGHT)]
        mat[pos.x][pos.y] = 0
        queue.append(pos)
        while len(queue) > 0:
            curr_pos = queue.popleft()
            for pos in self.getNeighbors(curr_pos):
                #print(pos)
                if (mat[pos.x][pos.y] == -1 or mat[pos.x][pos.y] > mat[curr_pos.x][curr_pos.y] + 1) and self.isTileWalkable(pos):
                    mat[pos.x][pos.y] = mat[curr_pos.x][curr_pos.y] + 1
                    if mat[pos.x][pos.y] == depth:
                        continue
                    queue.append(pos)

        return mat
    
    
    def findPath(self, start: Pos, end: Pos):
        if start == end:
            return None
        dist_map = self.floodFill(start)
        if dist_map[end.x][end.y] == -1:
            return None
        curr = end
        path = [end]
        while curr != start:
            #print(hist)
            around = self.getNeighbors(curr)
            for pos in around:
                
                if dist_map[pos.x][pos.y] + 1 == dist_map[curr.x][curr.y]:
                    path.append(pos)
                    curr = pos
                    break 
        return path[::-1]
    
    def floodFillDFS(self, start:Pos, end:Pos):
        if start == end:
            return None
        dist_map = self.floodFill(start)
        if dist_map[end.x][end.y] == -1:
            return None
        pointers = [[-1 for i in range(WIDTH)] for j in range(HEIGHT)]
        hist = [[99 for i in range(WIDTH)] for j in range(HEIGHT)]
        queue = deque()
        hist[end.x][end.y] = 0
        queue.append(end)
        while len(queue) > 0:
            #print(queue)
            curr_pos = queue.popleft() 
            #print("CURR:: ", curr_pos)
            for i, pos in enumerate(self.getNeighborsAll(curr_pos)):
                
                #print(i, "NEI: ", pos)
                if pos is None:
                    # Maybe error
                    # add slight priprity to tile that hit wall or edge
                    #hist[curr_pos.x][curr_pos.y]-=0.01
                    continue
                if (pointers[pos.x][pos.y] == -1 or hist[pos.x][pos.y] >= hist[curr_pos.x][curr_pos.y]) and self.isTileWalkable(pos) and dist_map[pos.x][pos.y] + 1 == dist_map[curr_pos.x][curr_pos.y] :
                    if i == pointers[curr_pos.x][curr_pos.y]:
                        queue.appendleft(pos)
                        pointers[pos.x][pos.y] = i
                        #print(curr_pos, "->", pos)
                        #print(hist[pos.x][pos.y], "->", hist[curr_pos.x][curr_pos.y])
                        hist[pos.x][pos.y] = hist[curr_pos.x][curr_pos.y]
                    elif hist[pos.x][pos.y] >= hist[curr_pos.x][curr_pos.y] + 1:
                        queue.append(pos)
                        pointers[pos.x][pos.y] = i
                        #print(curr_pos, "->", pos)
                        #print(hist[pos.x][pos.y], "->", hist[curr_pos.x][curr_pos.y]+1)
                        hist[pos.x][pos.y] = hist[curr_pos.x][curr_pos.y] + 1
        return pointers#, hist
    
    
    def findPathDFS(self, start:Pos, end:Pos):
        pointers = self.floodFillDFS(start, end)
        if pointers is None:
            return None
        rev_pointer_to_pointer = [3,4,5,0,1,2]
        curr = start
        path = [start]
        while curr != end:
            #moves.append(rev_pointer_to_dir[pointers[curr.x][curr.y]])
            curr = self.getNeighborForOneDir(curr, rev_pointer_to_pointer[pointers[curr.x][curr.y]])
            path.append(curr)
            if curr is None:
                return None
        return path
    
    def find_tiles(self, itemType: ItemType):
        ret_tiles = []
        for row in self.tiles:
            for tile in row:
                if tile.tileContent.itemType == itemType:
                    ret_tiles.append(tile)
        return ret_tiles
    
    def find_flowers(self):
        ret_tiles = []
        for row in self.tiles:
            for tile in row:
                if tile.tileContent.itemType in FLOWER_VALUE:
                    ret_tiles.append(tile)
        return ret_tiles
    
    def find_walkable(self):
        ret_tiles = []
        for row in self.tiles:
            for tile in row:
                if tile.isWalkable and tile.tileContent.itemType not in [ItemType.EMPTY, ItemType.HIVE]:
                    ret_tiles.append(tile)
        return ret_tiles
    
    def fill_nectar_and_cut_path(self, my_nectar, path: list[Pos]):
        nectar = my_nectar
        for i, pos in enumerate(path):
            temp = self.getTile(pos)
            nectar += NECTAR_VALUE[temp.tileContent.itemType]
            if nectar >= 100:
                return path[:i+1], nectar
        return path, nectar
    
    def fill_nectar_and_cut_path_v2(self, my_nectar, energy, path: list[Pos]):
        nectar = my_nectar
        score = 0
        for i, pos in enumerate(path):
            temp = self.getTile(pos)
            nectar += self.caluculate_tile_nectar(nectar, pos)
            score += self.caluculate_tile_score(energy, pos)
            if nectar >= 100:
                return path[:i+1], nectar - my_nectar + 0.5*score
        return path, nectar - my_nectar + 0.5*score
    
    def caluculate_tile_score(self, energy, pos: Pos):
        added_value = 0
        tile = self.getTile(pos)
        tile_type = tile.tileContent.itemType
        if tile_type == ItemType.ENERGY:
            if energy > 80:
                added_value = 100 - energy
            else:
                added_value = 20
        elif tile_type in specials.keys():
            added_value = specials[tile_type]
        return added_value


    def caluculate_tile_nectar(self, nectar, tile_type: ItemType):
        added_nectar = 0
        if tile_type in flowers.keys():
            if nectar < 100:
                added_nectar = flowers[tile_type]
        elif tile_type in boosters.keys():
            added_nectar = int(nectar * boosters[tile_type] / 100)
            if 100 - nectar < added_nectar:
                added_nectar = 100 - nectar
        return added_nectar
    
    def find_up(self, pos:Pos):
        positions = []
        curr_pos = pos
        while True:
            if pos.x - 2 < 0:
                break
            curr_pos = Pos(curr_pos.x-2, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
        return positions

    def find_down(self, pos: Pos):
        positions = []
        curr_pos = pos
        while True:
            if pos.x + 2 > 26:
                break
            curr_pos = Pos(curr_pos.x+2, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
        return positions
        
    def find_up_left(self, pos: Pos):
        positions = []
        curr_pos = pos
        while True:
            if (curr_pos.x - 1 < 0) or (curr_pos.x%2==0 and curr_pos.y - 1 < 0):
                break
            if curr_pos.x%2==0:
                curr_pos = Pos(curr_pos.x-1, curr_pos.y-1)
            else:
                curr_pos = Pos(curr_pos.x-1, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
        return positions

    def find_down_left(self, pos: Pos):
        positions = []
        curr_pos = pos
        while True:
            if (curr_pos.x + 1 > 8) or (curr_pos.x%2==0 and curr_pos.y - 1 < 0):
                break
            if curr_pos.x%2==0:
                curr_pos = Pos(curr_pos.x+1, curr_pos.y-1)
            else:
                curr_pos = Pos(curr_pos.x+1, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
        return positions

    def find_up_right(self, pos: Pos):
        positions = []
        curr_pos = pos
        while True:
            if (curr_pos.x - 1 < 0) or (curr_pos.x%2!=0 and curr_pos.y + 1 > 8):
                break
            if curr_pos.x%2!=0:
                curr_pos = Pos(curr_pos.x-1, curr_pos.y+1)
            else:
                curr_pos = Pos(curr_pos.x-1, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
            
        return positions

    def find_down_right(self, pos: Pos):
        positions = []
        curr_pos = pos
        while True:
            if (curr_pos.x + 1 > 26) or (curr_pos.x%2!=0 and curr_pos.y + 1 > 8) or (curr_pos.y == 8 and curr_pos.x%2==0):
                break
            if curr_pos.x%2!=0:
                curr_pos = Pos(curr_pos.x+1, curr_pos.y+1)
            else:
                curr_pos = Pos(curr_pos.x+1, curr_pos.y)
            if self.isTileWalkable(curr_pos) is False:
                break
            positions.append(curr_pos)
        return positions

    def find_lines(self, pos:Pos):
        up = self.find_up(pos)
        down = self.find_down(pos)
        up_left = self.find_up_left(pos)
        down_left = self.find_down_left(pos)
        up_right = self.find_up_right(pos)
        down_right = self.find_down_right(pos)
        return {'q' : up_left, 'w' : up, 'e': up_right, 'd' : down_right, 's' : down, 'a' : down_left}
        
    """def caluculate_tile_score(self, energy, tile_type):
        added_value = 0
        if tile_type == "ENERGY":
            if energy > 80:
                added_value = 100 - energy
            else:
                added_value = 20
        elif tile_type in specials.keys():
            added_value = specials[tile_type]
        return added_value"""


    def caluculate_tile_nectar(self, nectar, pos:Pos):
        added_nectar = 0
        tile = self.getTile(pos)
        tile_type = tile.tileContent.itemType
        if tile_type in flowers.keys():
            if nectar < 100:
                added_nectar = flowers[tile_type]
        return added_nectar

    def count_steps(self, line, nectar, energy):
        res_index = -1
        curr_nectar = 0
        found = False
        for index, pos in enumerate(line):
            curr_nectar += self.caluculate_tile_nectar(nectar, pos)
            nectar += self.caluculate_tile_nectar(nectar, pos)
            #print(nectar)
            if nectar >= 100:
                res_index = index + 1
                found = True
                break
        if found:
            line.reverse()
            
            score = 0
            curr_score = 0
            for index, pos in enumerate(line):
                score += self.caluculate_tile_score(energy, pos)
                if score != 0 and len(line) - index - 1 > res_index:
                    
                    res_index = len(line) - index - 1
                    break        
            line.reverse()
            
            for i in range(0, res_index):
                curr_score += self.caluculate_tile_score(energy, line[i])
            
            return nectar + curr_score, res_index + 1

        
        return 0, -1

    def best_line(self, pos, nectar, energy):
        max_value = 0
        lines = self.find_lines(pos)
        #print(pos)
        print(lines)
        move1, steps1, move2, steps2 = '/', 0, '/', 0
        for key, value in lines.items():
            score, steps = self.count_steps(value, nectar, energy)
            #print(score, steps)
            if score > max_value:
                max_value = score
                move1 = key
                steps1 = steps
                #print(key, steps, score)
        if max_value >= 100:
            #print("jedan", move1, steps1, max_value)
            return ["move", {"direction": move1,"distance":steps1 }]
        for key, value in lines.items():
            for index, v in enumerate(value):
                lines2 = self.find_lines(v)
                for key2, value2 in lines2.items():
                    score, steps = self.count_steps(value2, nectar, energy)
                    if score > max_value:
                        max_value = score
                        move1, steps1, move2, steps2 = key, index + 1, key2, steps
                        #print("dva", move1, steps1, move2, steps2, max_value)
        if max_value >= 100:
            return ["move", {"direction": move1,"distance":steps1 }]
        return None