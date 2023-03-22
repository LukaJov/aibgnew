from tile_content import TileContent
from dataclasses import dataclass

@dataclass
class Tile:
    row: int
    column: int
    tileContent: TileContent
