import pickle, sys
from minecraft.world import World

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python load_model.py <world path> <origin coords> <end coords> <name>")
        print("E.g. python load_model.py /home/daan/.minecraft/saves/epic 0,2,0 3,2,2 flipflop")
    world = World()
    start = tuple(map(int, sys.argv[2].split(',')))
    end = tuple(map(int, sys.argv[3].split(',')))
    model = world.read_model(sys.argv[1], start, (end[0] - start[0] + 1, end[1] - start[1] + 1, end[2] - start[2] + 1))
    with open(f'minecraft/data/components/{sys.argv[4]}', 'wb') as f:
        pickle.dump(model, f)
