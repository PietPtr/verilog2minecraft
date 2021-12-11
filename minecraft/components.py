import os
import pickle
from typing import Dict
from .world import World
from minecraft.world import Model



class ComponentManager:
    models: Dict[str, Model]

    def __init__(self):
        self.models = {}
        for fname in os.listdir('minecraft/data/components'):
            with open(f'minecraft/data/components/{fname}', 'rb') as f:
                self.models[fname] = pickle.load(f)

    def get_model(self, name: str) -> Model:
        return self.models[name]
