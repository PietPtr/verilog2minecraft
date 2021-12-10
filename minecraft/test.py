from world import World, Model, Block
nand_gate = Model({
    (0, 0, 2): Block.STONE,
    (1, 0, 2): Block.STONE,
    (2, 0, 2): Block.STONE,
    (0, 1, 2): Block.TORCH,
    (2, 1, 2): Block.TORCH,
    (1, 1, 2): Block.REDSTONE,
    (0, 0, 1): Block.REDSTONE,
    (0, 0, 0): Block.REDSTONE,
    (2, 0, 1): Block.REDSTONE,
    (2, 0, 0): Block.REDSTONE,
})

not_gate = Model({
    (0, 0, 0): Block.STONE,
    (0, 1, 0): Block.TORCH,
})

world = World()
world.add_model((0, 2, 0), nand_gate)
world.add_model((0, 2, 5), not_gate)
world.build('/home/daan/.minecraft/saves/epic')
