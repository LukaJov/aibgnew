import logging
from src.map import Map, Pos, getMoves, getSkipMoves, ItemType, mergeMoves
from src.lib.decision_logic import BaseBlock, ACT, SEQ, DEC, PPTime
from src.classes.player import Player
import time

FLOWER_VALUE = [ItemType.SUNFLOWER, ItemType.LILAC, ItemType.ROSE, ItemType.CHERRY_BLOSSOM]

class Agent:
    # Map data of enviroment
    map: Map
    logic: BaseBlock
    me: Player
    opp: Player
    # Initialize agent
    def __init__(self, game_state, player): 
        # Create objects
        self.map = Map(game_state["map"])
        self.me_key = player
        self.opp_key = "player2" if player == "player1" else "player1"
        self.me = Player(**game_state[player])
        self.opp = Player(**game_state["player2" if player == "player1" else "player1"])
        self.map.tiles[self.opp.hiveX][self.opp.hiveY].isWalkable = False
        self.min_energy = 50
        self.n_hives_visit = 0
        self.build_logic()
        #print(self.me)
    # Update map and other data on each turn
    def observe(self, state):
        self.me.update(state[self.me_key])
        self.opp.update(state[self.opp_key])
        self.map.update(state["map"])
        self.map.update_opp_pos(Pos(self.opp.x, self.opp.y))
        if self.is_on_hive():
            self.n_hives_visit+=1
            if self.n_hives_visit > 20:
                self.min_energy=62
            #if self.n_hives_visit % 10 == 0:
                #self.min_energy += 10

    def build_logic(self):
        
        self.logic = SEQ([
            ACT(self.getFreezes),
            #ACT(self.getSuperHoney), 
            
            DEC(self.is_energy_low, ACT(self.default), ACT(self.null)),
            ACT(self.getEnergy),
            DEC(self.is_full_necatar, SEQ([ACT(self.get_energy_to_hive), ACT(self.getToHive)]), ACT(self.null)),
            DEC(self.is_on_hive, 
                DEC(self.has_any_nectar,
                    SEQ([
                        ACT(self.convertToEnergy), 
                        ACT(self.convertToHoney)
                        ]), 
                    ACT(self.null)), 
                ACT(self.null)),
            ACT(self.getNearestFlowers),
            #ACT(self.getBestFlower),
            ACT(self.default),
        ])
    
    def null(self):
        return None
    
    def is_energy_low(self):
        return self.me.energy < 5
    
    
    def get_energy_to_hive(self):
        path = self.map.findPathDFS(Pos(self.me.x, self.me.y), Pos(self.me.hiveX,self.me.hiveY ))
        if path is None:
            return None
        moves = getMoves(path)
        if len(moves) * 2 + 1 > self.me.energy:
            return self.default()
        return None
    
    def has_any_nectar(self):
        return self.me.nectar > 0
    
    # QUESTION 100
    def is_full_necatar(self):
        return self.me.nectar >= 100
    
    def is_on_hive(self):
        return self.me.x == self.me.hiveX and self.me.hiveY == self.me.y
    
    # NOT USED
    def need_energy(self):
        return self.me.energy >= 50
    
    def default(self):
        return ["skipATurn", {}]
    # Get next set of actions
    def act(self):
        # time.sleep(0.5)
        # print("PREV_ACTION", self.me.executedAction)
        self.logic.clear()
        out = self.logic()
        print(PPTime(self.logic._time))
        # print(self.logic)
        # print(out)
        # print(max(1-0.0020*self.n_hives_visit,0.95))
        return out[1]
    
    # Use to find best path to specific tile type 
    # Mostly use for FREEZ and SUPER_HONEY
    # TER - turn energy ration 1 use all turn, 0 use all energy saving
    def getTileType(self, tileType, max_turns = 5, min_energy= 1, ter = 1):
        tiles = self.map.find_tiles(tileType)
        if len(tiles) == 0:
            return None
        moves = []
        min = 1e9
        min_eng = 0 # Turns for current minimum path
        min_turns = 0 # Energy for current minimum path
        for tile in tiles:
            path = self.map.findPathDFS(Pos(self.me.x, self.me.y), Pos.from_tile(tile))
            if path is None:
                continue
            tempMoves = getMoves(path) # Energy
            if len(tempMoves)*2 >= self.me.energy - min_energy: # Check if it will not use all energy not checking energy picked
                continue 
            temp = mergeMoves(tempMoves) # Merge moves to turns
            pathingScore = ter * len(temp) + (1-ter) * len(tempMoves)*2
            if pathingScore < min:
                moves = temp
                min = pathingScore
                min_eng = len(tempMoves)*2
                min_turns = len(temp)
        if min_turns >= max_turns:
            return None
        if len(moves) == 0:
            return None
        
        return ["move", {"direction": moves[0]["dir"],"distance":moves[0]["dist"] }]
    
    def getNearestFlowers(self):
        
        ret = self.map.best_line(Pos(self.me.x, self.me.y), self.me.nectar, self.me.energy)
        
        if ret is None:
            return None
        return ret
    
    def getFlowers(self, max_turns = 5, min_energy= 1, ter = 1):
        tiles = self.map.find_walkable()
        if len(tiles) == 0:
            return None
        #if len(tiles) < 25:
        #    ter = 0.9
        moves = []
        min_score = 1e9
        min_eng = 0 # Turns for current minimum path
        min_turns = 0 # Energy for current minimum path
        
        #print("TILES: ", len(tiles))
        for tile in tiles:
            path = self.map.findPathDFS(Pos(self.me.x, self.me.y), Pos.from_tile(tile))
            if path is None:
                continue
            path, expected_score = self.map.fill_nectar_and_cut_path_v2(self.me.nectar, self.me.energy, path)
            #print("TEMP")
            discourage = max([3 - expected_score/50, 0]) # DISOUCRAGE IF NOT 100 HONEY IN PATH 
            #if expected_score >= 100:
            #    discourage = 0
            tempMoves = getMoves(path) # Energy
            if len(tempMoves)*4 >= self.me.energy - min_energy: # Check if it will not use all energy not checking energy picked
                continue 
            temp = mergeMoves(tempMoves) # Merge moves to turns
            # TURNS + ENERGY + DISOUCRAGE 
            pathingScore = ter * len(temp) + (1-ter) * len(tempMoves)*2 + 2*discourage
            #print(pathingScore)
            if pathingScore < min_score:
                moves = temp
                min_score = pathingScore
                min_eng = len(tempMoves)*2
                min_turns = len(temp)
        if min_turns >= max_turns:
            return None
        if len(moves) == 0:
            return None
        #print(moves)
        #print(min_score)
        return ["move", {"direction": moves[0]["dir"],"distance":moves[0]["dist"] }]
    
    def getTwoStep(self):
        pass
    
    
    def getSunFlower(self):
        c = FLOWER_VALUE[0]
        for f in FLOWER_VALUE:
            t = self.map.find_tiles(f)
            c = f
            if len(t) > 0:
                break
        return self.getTileType(c, 10, 10, 0.8)
    
    def getBestFlower(self):
        return self.getFlowers(10, 10, 0.8)
        
    
    def getFreezes(self):
        return self.getTileType(ItemType.FREEZE, 4, 20, 0.5)
    
    
    def getEnergy(self):
        if self.me.energy >= 20:
            return None
        return self.getTileType(ItemType.ENERGY, 2, 10, 1)
        
    def getSuperHoney(self):
        return self.getTileType(ItemType.SUPER_HONEY, 4, 20, 0.5)
    
    def getToHive(self):
        #print(Pos(self.me.x, self.me.y), Pos(self.me.hiveX,self.me.hiveY))
        path = self.map.findPathDFS(Pos(self.me.x, self.me.y), Pos(self.me.hiveX,self.me.hiveY ))
        if path is None or len(path) == 0:
            return None
        moves = getMoves(path)
        if len(moves)*2 + 1 >= self.me.energy:
            return None
        moves = mergeMoves(moves)
        #print(moves)
        if len(moves) == 0:
            return None
        return ["move", {"direction": moves[0]["dir"],"distance":moves[0]["dist"] }]  
    
    # self.me.energy 32
    # fali 18 -> nectar 9
    # koliko cemo uzeti 100 - 9 koliko ce ostati 91
    # da zaokruzimo 91 % 20 -> 11
    # uzmia -> 20
    def convertToEnergy(self):
        fali = self.min_energy - self.me.energy
        if fali<1:
            return None
        nectar = (fali+1) // 2
        zaokruzivanje = (self.me.nectar - nectar) % 20
        return ["feedBeeWithNectar", {"amountOfNectarToFeedWith":zaokruzivanje+nectar }]
    
    
    def convertToHoney(self):
        if self.me.nectar >= 20:
            return ["convertNectarToHoney", {"amountOfHoneyToMake": 5 }]
        return None
    
    
    # -> 
    