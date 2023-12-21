import time
from src.drink import Drink

from src.order import Order

from ..constants.constants import Coor, Area, GUISum
from ..win_control import click_pos
from ..sum_area import sum_area


class DrinkStation():

    def make_drink(self, order: Order):
        if order.drink is None:
            print("Order has no drink!")
            return

        drink: Drink = order.drink

        is_tutorial = False
        if sum_area(Area.drink_check) == GUISum.drinks_tutorial:
            print("Drinks Tutorial detected")
            is_tutorial = True

        # Flavour
        click_pos(Coor.d_flav[drink.flavour])
        time.sleep(.30)

        # Cup size
        click_pos(Coor.d_size[drink.size])
        if drink.size == 'small':
            time.sleep(3.2)
        elif drink.size == 'large':
            time.sleep(3.6)

        # Milk
        click_pos(Coor.d_add[drink.additional])

        # Timing click
        time.sleep(.55)
        click_pos(Coor.d_pour_btn, interval=0)

        if is_tutorial:
            time.sleep(2)
            click_pos(Coor.d_my_drinks)
            time.sleep(.5)
            click_pos(Coor.d_my_drinks)

        order.drink_made = True
