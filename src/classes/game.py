from map import Map
from player import Player
from dataclasses import dataclass


@dataclass
class Game:
    id: int
    player1: Player
    player2: Player
    map: Map
    player1ChangedTiles: list
    player2ChangedTiles: list
    numOfMove: int
    finished: bool
    winnerTeamName: str
    reasonForEndingGame: str
