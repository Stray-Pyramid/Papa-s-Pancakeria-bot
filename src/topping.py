import json
from dataclasses import dataclass
from typing import List

@dataclass
class Topping:
    name: str
    type: str
    location: List[float]
    center: List[float]
    size: float
    loops: float
    speed: float = 0.0

class Toppings:
    @staticmethod
    def get(topping_name: str) -> Topping:
        toppings_list = Toppings._load_toppings('./src/constants/toppings.json')
            
        for topping in toppings_list:
            if topping.name == topping_name:
                return topping
            
        raise Exception(f"Topping not found: {topping_name}")
            
    @staticmethod
    def _load_toppings(filepath: str) -> List[Topping]:
        with open(filepath, 'r') as file:
            json_data = json.load(file)

            toppings_list = []

            for topping_data in json_data:
                # If "speed" attribute is missing, set it to the default value (0.0)
                if "speed" not in topping_data:
                    topping_data["speed"] = 0.0

                topping_instance = Topping(**topping_data)
                toppings_list.append(topping_instance)
                
            return toppings_list