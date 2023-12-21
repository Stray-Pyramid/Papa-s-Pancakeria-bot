import time
import math
import numpy as np

from src.topping import Toppings

from ..constants.constants import IngredientTypes, Coor
from ..win_control import click_pos, mouse_pos, left_down, left_up, move_cursor_along_path
from ..order import Order, OrderPhase


class BuildStation():

    def __init__(self):
        self.active_order: Order | None = None
        self.drink_queue = []

    def build_order(self, order: Order):
        if self.active_order:
            print("Cannot make order, one is already being made")
            return

        self.active_order = order

        print(f"Building order {order.id}")
        print(order.ingredients)

        for ingredient in order.ingredients:

            item_name = ingredient[0]
            item_type = IngredientTypes[item_name][0]

            if item_type in ('bread', 'waffle'):
                self.add_base()
            elif item_type == 'piece':
                item_count = ingredient[1]
                self.spread_topping(item_name, item_count)
            else:
                self.spread_sprinkle_or_sauce(item_name)

        # Wait for animations to finish
        time.sleep(.5)
        order.phase = OrderPhase.BUILT

    def finish_order(self, order: Order) -> Order:
        # Finish
        click_pos(Coor.build_finish)
        time.sleep(.2)

        # Place drink
        if order.has_drink() and order.drink_made:
            drink_i = self.drink_queue.index(order.id)
            BuildStation.place_drink(drink_i)
            self.drink_queue.remove(order.id)

        return order

    def finish_active_order(self) -> Order:
        if self.active_order is None:
            raise Exception("Build station has no active order")

        order = self.active_order
        self.active_order = None

        self.finish_order(order)

        return order

    def add_drink(self, order: Order):
        self.drink_queue.append(order.id)

    def order_is_built(self) -> bool:
        if self.active_order is None:
            return False

        return self.active_order.phase is OrderPhase.BUILT

    @staticmethod
    def place_drink(drink_i):
        drink_coor = Coor.drink_rack[drink_i]
        time.sleep(1)
        mouse_pos(drink_coor)
        left_down()
        mouse_pos(Coor.build_tray)
        left_up()

    @staticmethod
    def get_point_in_ellipse(x_center, y_center, theta):
        x = x_center * math.cos(math.radians(theta))
        y = y_center * math.sin(math.radians(theta))
        return int(math.floor(x)), int(math.floor(y))

    @staticmethod
    def get_point_in_flower(r_max, theta):
        r = r_max * math.cos((5/3) * math.radians(theta))
        x = r * math.cos(math.radians(theta))
        y = r * math.sin(math.radians(theta))

        return int(x), int(y)

    @staticmethod
    def get_point_in_spikey_flower(theta):
        petals = 6
        radius = -10

        fx = np.abs(
            (35/np.pi) * (np.mod((petals*theta) - np.pi/2, 2*np.pi) - np.pi)) + 35

        x = (radius + fx) * math.cos(theta)
        y = (radius + fx) * math.sin(theta)

        return int(x), int(y)

    @staticmethod
    def get_points_in_spiral(size, loops):
        points = 250
        theta = (2 * np.pi) / points

        point_list = []
        for i in range(0, points):
            x = size * (theta * i) * math.cos(theta * i * loops) * 0.9
            y = size * (theta * i) * math.sin(theta * i * loops)

            point_list.append((x, y))

        return point_list

    @staticmethod
    def add_base():
        mouse_pos(Coor.build_base)
        time.sleep(.1)
        left_down()
        mouse_pos((Coor.build_center[0] - 20, Coor.build_center[1]))
        time.sleep(.1)
        left_up(delay=0.1)

    @staticmethod
    def spread_topping(ingred_name: str, toppings_num=1):
        topping = Toppings.get(ingred_name)

        if topping.type != 'piece':
            raise Exception(f"{topping.name} is a {topping.type}, not a piece")

        if toppings_num == 1:
            # Place in the center
            mouse_pos(topping.location)
            left_down()
            mouse_pos(topping.center)
            time.sleep(.2)
            left_up()
            time.sleep(.2)
        else:
            increment = 360 / toppings_num
            if toppings_num in (2, 3):
                offset = 90
            else:
                offset = 45

            for i in range(0, toppings_num):
                mouse_pos(topping.location)
                left_down()
                time.sleep(.1)
                x, y = BuildStation.get_point_in_ellipse(
                    40, 40, (i*increment+offset))
                # print ('Placing topping at '+str(x)+', '+str(y)+' from pancake center')
                mouse_pos((topping.center[0]+x, topping.center[1]+y))
                time.sleep(.1)
                left_up()

            time.sleep(.2)

    @staticmethod
    def spread_sprinkle_or_sauce(ingred_name):
        # Sprinkle or Sauce, flower pattern
        topping = Toppings.get(ingred_name)

        if topping.type not in ('sauce', 'sprinkle'):
            raise Exception(
                f"{topping.name} is a {topping.type}, not a sauce or sprinkle")

        points = BuildStation.get_points_in_spiral(topping.size, topping.loops)

        mouse_pos(topping.location)
        left_down()
        mouse_pos((topping.center[0] + points[0][0],
                   topping.center[1] + points[0][1]))
        left_up(delay=0)
        move_cursor_along_path(
            points, speed=topping.speed, offset=topping.center)

        # Buffer
        time.sleep(.2)
