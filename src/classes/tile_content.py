from item_type import ItemType
from dataclasses import dataclass

@dataclass
class TileContent:
    itemType: ItemType
    numOfItems: int
