import time
from typing import List

from ..constants.constants import Coor, IngredientTypes
from ..win_control import click_pos, mouse_pos, left_down, left_up
from ..order import Order, OrderPhase


class GrillStation():
    TUTORIAL_COOK_DURATION = 16
    AFTER_TUTORIAL_COOK_DURATION = 18
    DEFAULT_COOK_DURATION = 34

    IRON = 0
    GRILL = 1

    def __init__(self):
        self.cook_duration = GrillStation.DEFAULT_COOK_DURATION

        self.grills: List[Order | None] = [None] * 8
        self.irons: List[Order | None] = [None] * 4

        self.finished_queue = []

    def set_cook_duration(self, cook_duration: int):
        print(f'Cooking time set to {cook_duration} seconds')
        self.cook_duration = cook_duration

    def can_do_order(self, order: Order):
        # if the number of grills and irons available is
        # greater than the required from order info, return true
        if self.grills.count(None) >= order.num_of_grills:
            if self.irons.count(None) >= order.num_of_irons:
                return True

        return False

    def start_order(self, order: Order,
                    grills: List[int] | None = None, irons: List[int] | None = None):

        if irons is None:
            irons = []

        if grills is None:
            grills = []

        # place batters on grill, and the extras
        for ingredient in order.ingredients:
            ingredient_name = ingredient[0]
            if ingredient_name not in ('pancake', 'french', 'waffle'):
                continue

            if len(ingredient) == 2:
                topping = ingredient[1]
            else:
                topping = None

            if ingredient_name in ('pancake', 'french'):
                if len(grills) != 0:
                    grill_slot = grills.pop(0)
                    self.grills[grill_slot] = order
                else:
                    grill_slot = self.allocate_grill(order)

                self.place_ingredient(self.GRILL, ingredient_name, grill_slot)
                if topping:
                    self.place_ingredient(self.GRILL, topping, grill_slot)

            if ingredient_name in ('waffle'):
                if len(irons) != 0:
                    iron_slot = irons.pop(0)
                    self.irons[iron_slot] = order
                else:
                    iron_slot = self.allocate_iron(order)

                self.place_ingredient(self.IRON, ingredient_name, iron_slot)
                if topping:
                    self.place_ingredient(self.IRON, topping, iron_slot)

        order.cook_start_time = time.time()
        order.phase = OrderPhase.COOKING
        print(f"Order {order.id} has started cooking")

    # If an order is ready to be flipped or has finished cooking
    def order_ready(self, orders: List[Order]):
        for order in orders:
            if order.phase != OrderPhase.COOKING:
                continue

            if order.cook_start_time + self.cook_duration <= time.time():
                return True

        return False

    def process_orders(self, orders: List[Order]):
        for order in orders:
            if order.phase is not OrderPhase.COOKING:
                continue

            if order.cook_start_time + self.cook_duration > time.time():
                continue

            if order.flipped is False:
                self.flip_order(order)

            elif order.flipped is True:
                print(f"Order {order.id} has finished cooking")

                self.finish_cooking(order)

                order.phase = OrderPhase.COOKED
                self.finished_queue.append(order)
                time.sleep(.4)

    def flip_order(self, order: Order):
        print(f'Flipping order {order.id}')

        for slot, order_on_grill in enumerate(self.grills):
            if order_on_grill == order:
                self._flip_grill(slot)

        for slot, order_on_iron in enumerate(self.irons):
            if order_on_iron == order:
                self._flip_iron(slot)

        order.cook_start_time = time.time()
        order.flipped = True

    def finish_cooking(self, order: Order):
        for slot, order_on_grill in enumerate(self.grills):
            if order_on_grill == order:
                self.grills[slot] = None
                self._finish_grill(slot)

        for slot, order_on_iron in enumerate(self.irons):
            if order_on_iron == order:
                self.irons[slot] = None
                self._finish_iron(slot)

    def allocate_grill(self, order: Order):
        for slot, order_on_grill in enumerate(self.grills):
            if order_on_grill is None:
                self.grills[slot] = order
                return slot

    def allocate_iron(self, order: Order):
        for slot, order_on_iron in enumerate(self.irons):
            if order_on_iron is None:
                self.irons[slot] = order
                return slot

    def place_ingredient(self, type, ingredient, slot):
        print(f'Placing {ingredient} at slot {slot}')
        mouse_pos(IngredientTypes[ingredient][1])
        time.sleep(.4)
        left_down()
        if type == self.GRILL:
            mouse_pos(Coor.grill[slot])
        elif type == self.IRON:
            mouse_pos(Coor.iron[slot])
        time.sleep(.1)
        left_up()

    def pancakes_ready(self):
        return len(self.finished_queue) != 0

    @staticmethod
    def _flip_grill(grill_index: int):
        click_pos(Coor.grill[grill_index])

    @staticmethod
    def _flip_iron(iron_index: int):
        click_pos(Coor.iron[iron_index])

    @staticmethod
    def _finish_grill(grill_index: int):
        GrillStation._move_to_output(Coor.grill[grill_index])

    @staticmethod
    def _finish_iron(iron_index: int):
        GrillStation._move_to_output(Coor.iron[iron_index])

    @staticmethod
    def _move_to_output(position):
        mouse_pos(position)
        time.sleep(.1)
        left_down()
        mouse_pos(Coor.grill_output)
        time.sleep(.1)
        left_up()
