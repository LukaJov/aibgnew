from dataclasses import dataclass

@dataclass
class Player:
    x: int
    y: int
    score: int
    energy: int
    nectar: int
    honey: int
    turnsFrozen: int
    numOfSkipATurnUsed: int
    executedAction: int
    distanceMoved: int
    teamName: str
    skin: int
    hiveX: int
    hiveY: int
    frozen: bool 

    def update(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.score = data["score"]
        self.energy = data["energy"]
        self.nectar = data["nectar"]
        self.honey = data["honey"]
        self.turnsFrozen = data["turnsFrozen"]
        self.numOfSkipATurnUsed = data["numOfSkipATurnUsed"]
        self.executedAction = data["executedAction"]
        self.distanceMoved = data["distanceMoved"]
        self.teamName = data["teamName"]
        self.skin = data["skin"]
        self.hiveX = data["hiveX"]
        self.hiveY = data["hiveY"]
        self.frozen = data["frozen"]