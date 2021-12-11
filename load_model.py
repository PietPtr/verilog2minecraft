import pickle, sys
from minecraft.world import World

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python load_model.py <world path> <origin coords> <end coords> <name> <yosys_name>")
        print("E.g. python load_model.py /home/daan/.minecraft/saves/epic 0,2,0 3,2,2 flipflop \\$_DFFE_PP0N_")
    world = World()
    start = tuple(map(int, sys.argv[2].split(',')))
    end = tuple(map(int, sys.argv[3].split(',')))
    model = world.read_model(sys.argv[1],
                             (min(start[0], end[0]), min(start[1], end[1]), min(start[2], end[2])),
                             (max(start[0], end[0]), max(start[1], end[1]), max(start[2], end[2])),
                             sys.argv[5], sys.argv[4])
    with open(f'minecraft/data/components/{sys.argv[4]}', 'wb') as f:
        pickle.dump(model, f)
