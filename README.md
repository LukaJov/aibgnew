- Recommended is using virtual environment, by running command python -m venv env and activating it with command env/Scripts/activate
- Then install requirements, run: pip install -r requirements.txt
- Command to run train: python .\main.py  --playerId 179380
- Different arguments to call in terminal:
```
    - --train, default is True, need to set --no-train to not be in train mode
    - --meFirst, default is True, need to set --no-meFirst to be second player
    - --join, game id to join game
    - --playerId, id of player
    - --spot, when in training mode pick a spot to be, default is 1
```
- To run: 
```
    - as player1: python main.py --no-train --join=[gameid] --playerId 179380
    - as player2: python main.py --no-train --join=[gameid] --playerId 179380 --no-meFirst
```
