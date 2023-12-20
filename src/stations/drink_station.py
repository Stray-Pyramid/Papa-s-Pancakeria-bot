import time

from ..constants.constants import Coor, Area, GUISum
from ..win_control import click_pos
from ..sum_area import sum_area


class DrinksStation():

    def make_drink(self, order):
        is_tutorial = False

        if order.drink is None:
            print("Order has no drink!")
            return

        drink = order.drink
        time.sleep(1)

        if sum_area(Area.drink_check) == GUISum.drinks_tutorial:
            print("TUTORIAL_DETECT")
            is_tutorial = True

        # Flavour
        print("FLAVOUR")
        click_pos(Coor.d_flav[drink.flavour])
        time.sleep(.3)

        # Cup size
        print("CUP SIZE")
        click_pos(Coor.d_size[drink.size])
        time.sleep(.7)

        # Timing click
        print("POUR")
        click_pos(Coor.d_pour_btn)
        time.sleep(.2)
        click_pos(Coor.d_pour_btn)
        time.sleep(3)

        # Milk
        print("ADDITIONAL")
        click_pos(Coor.d_add[drink.additional])
        time.sleep(.55)

        # Timing click
        print("POUR")
        click_pos(Coor.d_pour_btn)

        if is_tutorial:
            time.sleep(2)
            click_pos(Coor.d_my_drinks)
            time.sleep(.5)
            click_pos(Coor.d_my_drinks)

        order.drink_made = True
