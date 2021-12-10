import os
import pickle
from typing import Dict
from .world import World
from minecraft.world import Model


class Component:

    def __init__(self, model: Model):
        self.model = model


class ComponentManager:
    components: Dict[str, Component]

    def __init__(self):
        self.components = {}
        for fname in os.listdir('minecraft/data/components'):
            with open(f'minecraft/data/components/{fname}', 'rb') as f:
                self.components[fname] = pickle.load(f)

    def get_component(self, name: str) -> Component:
        return self.components[name]
