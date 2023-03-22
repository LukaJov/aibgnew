from src.agent import Agent
from src.map import Pos, getMoveAction, getMoves, getSkipMoves
import json

WIDTH = 9
HEIGHT = 27

f = open("game_state.json")
state = json.load(f)
f.close()
a = Agent(state, "player1")
#mat = a.map.floodFill(Pos(0,0))
#print(mat)
pointers, hist = a.map.floodFillDFS(Pos(6,2),Pos(0,0))
#print(path)
#print(getSkipMoves(path))
#print(getSkipMoves(mat))
def printMAT(pointers):
  print("\n".join([" ".join( ["  "] +["%5.2f"%pointers[i][j] for j in range(WIDTH)] if i%2 else ["%5.2f"%pointers[i][j] for j in range(WIDTH)]) for i in range(HEIGHT)]))


printMAT(pointers)
printMAT(hist)


rev_pointer_to_dir = ["d","s","a","q","w","e"]
rev_pointer_to_pointer = [3,4,5,0,1,2]
dir_to_pointer = {
  "q":0,
  "w":1,
  "e":2,
  "d":3,
  "s":4,
  "a":5,
}

path = a.map.findPathDFS(Pos(6,2),Pos(0,0))
print(getSkipMoves(path))
#around = [1,2,3,4,5,6]
#print( around[3:]+around[:3])