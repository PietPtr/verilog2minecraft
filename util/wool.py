from enum import Enum

from amulet import Block


class WoolType(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    REPEATER = "repeater"
    WHITE_WOOL = "white_wool"
    ORANGE_WOOL = "orange_wool"
    MAGENTA_WOOL = "magenta_wool"
    LIGHT_BLUE_WOOL = "light_blue_wool"
    YELLOW_WOOL = "yellow_wool"
    LIME_WOOL = "lime_wool"
    PINK_WOOL = "pink_wool"
    GRAY_WOOL = "gray_wool"
    LIGHT_GRAY_WOOL = "light_gray_wool"
    CYAN_WOOL = "cyan_wool"
    PURPLE_WOOL = "purple_wool"
    BLUE_WOOL = "blue_wool"
    BROWN_WOOL = "brown_wool"
    GREEN_WOOL = "green_wool"
    RED_WOOL = "red_wool"
    BLACK_WOOL = "black_wool"

    def to_minecraft(self) -> Block:
        return Block('minecraft', self.value)

    @staticmethod
    def num_to_wool(idx):
        # haha dit is gewoon een array (:
        return num_to_wool[idx % 16]


num_to_wool = {
    0: WoolType.WHITE_WOOL,
    1: WoolType.ORANGE_WOOL,
    2: WoolType.MAGENTA_WOOL,
    3: WoolType.LIGHT_BLUE_WOOL,
    4: WoolType.YELLOW_WOOL,
    5: WoolType.LIME_WOOL,
    6: WoolType.PINK_WOOL,
    7: WoolType.GRAY_WOOL,
    8: WoolType.LIGHT_GRAY_WOOL,
    9: WoolType.CYAN_WOOL,
    10: WoolType.PURPLE_WOOL,
    11: WoolType.BLUE_WOOL,
    12: WoolType.BROWN_WOOL,
    13: WoolType.GREEN_WOOL,
    14: WoolType.RED_WOOL,
    15: WoolType.BLACK_WOOL
}
