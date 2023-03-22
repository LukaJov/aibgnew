import requests
import argparse
import json
import time
from src.agent import Agent

URL = "http://localhost:8082/"


headers = {'Content-Type': 'application/json'}
#localhost:8080/train/makeGame
def make_game(playerId, spot):
    res = requests.post(URL+"makeGame", data=json.dumps({  
        "playerId": playerId,
        "playerSpot": spot
    }), headers=headers)
    return res.json()
def join_game(gameId, playerId):
    res = requests.get(URL+"joinGame?playerId=%d&gameId=%d" % (playerId, gameId))
    print(res.json())
    return res.json()

def get(url):
    r = requests.get(url)
    res = r.json()
    return res

def initialize(game_state, player):
    return Agent(game_state, player)

def run(gameId:int, playerId:int, game_state, agent:Agent):
    turn = 0
    time.sleep(0.5)
    while game_state["finished"] == False:
        turn+=1
        # SLOW DOWN
        time.sleep(1)
        print("TURN", turn)
        agent.observe(game_state)
        action = agent.act()
        game_state = do_action(playerId, gameId, action[0], action[1])
        
def do_action(playerId, gameId, action, queryDict):
    data = {
        "playerId": playerId,
        "gameId": gameId
    }
    data.update(queryDict)
    #print(data)
    res = requests.post(URL+action, data=json.dumps(data), headers=headers)
    #print("STATUS_CODE::", res.status_code)
    #print(res.json())
    return res.json()

parser = argparse.ArgumentParser(description='INFTN bot')
parser.add_argument('--train', type=bool, action=argparse.BooleanOptionalAction, default=True)
parser.add_argument('--meFirst', type=bool, action=argparse.BooleanOptionalAction, default=True)
parser.add_argument('--spot', type=int, default=1)
parser.add_argument('--join', type=int)
parser.add_argument('--playerId', type=int, required=True)
args = parser.parse_args()

player = "player1" if args.meFirst else "player2"
if args.train:
    URL+="train/"
    
if args.join == None:
    print("Creating game.")
    game_state = make_game(args.playerId, args.spot)

    print("GAME_ID:",game_state["gameId"])
    agent = initialize(game_state, player)
    run(game_state["gameId"], args.playerId, game_state, agent)
else:
    game_state = join_game(args.playerId, args.join)
    agent = initialize(game_state, player)
    run(args.join,args.playerId, game_state, agent)
    