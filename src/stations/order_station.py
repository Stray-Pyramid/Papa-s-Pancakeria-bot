import time
from typing import Dict

from ..constants.constants import Area, IngredientTypes, Coor, GUISum
from ..win_control import click_pos
from ..sum_area import sum_area
from ..datatypes.rect import Rect


from ..order import Order
from ..drink import Drink


class OrderStation():
    INGREDIENT_FP = "./src/constants/item_sums.txt"

    def __init__(self):
        self.ingredient_sums: Dict[int, str] = {}
        self.topping_count_sums: Dict[int, int] = {}

        self.total_orders_taken = 0

        self.load_items()

    def customer_ready_to_order(self):
        return sum_area(Area.order_floor) != GUISum.order_floor

    def customer_is_approaching(self):
        return sum_area(Area.store_floor) != GUISum.store_floor

    def store_is_closed(self):
        return sum_area(Area.store_sign) == GUISum.store_closed_sign

    def load_items(self):
        with open(self.INGREDIENT_FP, 'r', encoding="utf-8") as file:
            for line in file:
                if (line) == '':
                    return  # EOF

                item_sum, item_name = line.strip().split(":")
                item_sum = int(item_sum)

                if item_name[:-1] == "item_count_":
                    topping_count = int(item_name[-1])
                    self.topping_count_sums[item_sum] = topping_count
                else:
                    self.ingredient_sums[item_sum] = item_name

    def take_order(self):
        self.wait_for_order()
        order = self.interpret_order()

        self.total_orders_taken += 1
        return order

    def wait_for_order(self):
        time.sleep(.4)
        click_pos(Coor.take_order)
        print('Taking an order...')
        time.sleep(1)
        screen = sum_area(Area.order_wait)
        while sum_area(Area.order_wait) == screen:
            time.sleep(.5)

    # Returns the type of ingredients and number of pancakes / waffles that can order needs
    def interpret_order(self) -> Order:
        grills_needed = 0
        irons_needed = 0
        ingredients = []

        for slot in range(0, 7):
            # Get sum for ticket slot
            rect = Rect(Area.ticket_section)
            rect.translate(0, -Area.ticket_spacing * slot)
            area_sum = sum_area(rect)

            # If sum doesn't exist, prompt the user for name and add it
            if area_sum not in self.ingredient_sums:
                self.add_ingredient_sum(area_sum, slot)

            # If ticket slot is empty, no action required
            if self.ingredient_sums[area_sum] == 'empty':
                break

            # If regular slot, lookup and process
            ingredient = self.ingredient_sums[area_sum]
            ingred_type = IngredientTypes[ingredient][0]

            if ingred_type == 'piece':
                rect = Rect(Area.ticket_toppingNum)
                rect.translate(0, -Area.ticket_spacing * slot)
                area_sum = sum_area(rect)
                if area_sum in self.topping_count_sums:
                    topping_count = self.topping_count_sums[area_sum]
                    print(topping_count, "pieces of", ingredient)
                else:
                    print('Toppping count sum not found for slot ' +
                          str(slot+1) + ', Sum: ' + str(area_sum))
                    print('Please write the number of toppings required.')
                    topping_count = int(input())
                    self.add_topping_count(area_sum, topping_count)

                ingredients.append([ingredient, topping_count])

            elif ingred_type == 'combo':
                combo_bread = IngredientTypes[ingredient][1]
                combo_bits = IngredientTypes[ingredient][2]
                if combo_bread in ('pancake', 'french'):
                    grills_needed += 1
                elif combo_bread == 'waffle':
                    irons_needed += 1
                ingredients.append([combo_bread, combo_bits])

            else:
                ingredients.append([ingredient])

            if ingred_type == 'bread':
                grills_needed += 1
            elif ingred_type == 'waffle':
                irons_needed += 1

        drink = self.interpret_drink()
        order_id = self.total_orders_taken+1

        print(ingredients)
        print(drink)
        return Order(order_id, ingredients, grills_needed, irons_needed, drink)

    def interpret_drink(self):
        area_sum = sum_area(Area.t_d_size)
        print(area_sum)
        if self.ingredient_sums[area_sum] == 'empty':
            print('Drinks slot is empty')
            return None

        # Left slot - drink flavour
        area_sum = sum_area(Area.t_d_flavour)
        if area_sum not in self.ingredient_sums:
            print("DRINK FLAVOUR NOT FOUND")
            self.add_ingredient_sum(area_sum, 7, drink=True)

        d_flavour = self.ingredient_sums[area_sum]

        # Middle slot - drink size
        area_sum = sum_area(Area.t_d_size)
        if area_sum not in self.ingredient_sums:
            print("DRINK SIZE NOT FOUND")
            self.add_ingredient_sum(area_sum, 7, drink=True)

        d_size = self.ingredient_sums[area_sum]

        # Right slot - drink base
        area_sum = sum_area(Area.t_d_additional)
        if area_sum not in self.ingredient_sums:
            print("DRINK ADDITIONAL NOT FOUND")
            self.add_ingredient_sum(area_sum, 7, drink=True)

        d_base = self.ingredient_sums[area_sum]

        return Drink(d_flavour, d_size, d_base)

    def add_topping_count(self, topping_sum: int, topping_count: int):

        with open(self.INGREDIENT_FP, 'a+', encoding="utf-8") as f:
            f.seek(0, 2)
            f.write(f"{topping_sum}:item_count_{topping_count}\n")

        self.topping_count_sums[topping_sum] = topping_count

    def load_ingrediet_sums(self):
        pass

    def add_ingredient_sum(self, item_sum: int, slot: int, drink=False):
        print('Found unregisterd ingredient')
        print('Slot: '+str(slot+1))
        print('Sum: '+str(item_sum))
        print("Please enter ingredient name")

        item_name = self.input_console()

        if drink is False:
            for _, key in enumerate(IngredientTypes):

                if item_name == key or item_name == 'empty':
                    self.ingredient_sums[item_sum] = item_name

                    with open(self.INGREDIENT_FP, 'a+', encoding="utf-8") as f:
                        f.seek(0, 2)
                        f.write(f"{item_sum}:{item_name}\n")
                    break
            else:
                print("Ingredient name not found.")
                quit()

        else:
            self.ingredient_sums[item_sum] = item_name
            with open(self.INGREDIENT_FP, 'a+', encoding="utf-8") as f:
                f.seek(0, 2)
                f.write("item_sum:item_name\n")

    # TODO Put this in the proper place
    def input_console(self):
        self.console_window.activate()
        return input()
