import pickle, sys
from world import World

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python load_model.py <world path> <origin coords> <sizes> <name>")
        print("E.g. python load_model.py /home/daan/.minecraft/saves/design 0,2,0 3,2,2 flipflop")
    world = World()
    model = world.read_model(sys.argv[1], tuple(map(int, sys.argv[2].split(','))), tuple(map(int, sys.argv[3].split(','))))
    with open(f'data/components/{sys.argv[4]}', 'wb') as f:
        pickle.dump(model, f)
