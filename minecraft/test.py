import amulet
from amulet.api.block import Block

# load the level
level = amulet.load_level("data/flat")
game_version = ("bedrock", (1, 18, 1))

block = Block("minecraft", "stone")
level.set_version_block(
    0,  # x location
    4,  # y location
    0,  # z location
    "overworld",  # dimension
    game_version,
    block,
)

level.save()
level.close()