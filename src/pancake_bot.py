# Python 3.8.2
# Last updated 09/14/2020 (MM/DD/YYYY)
# By StrayPyramid

import time
from typing import List
import pygetwindow

from src.order import Order, OrderPhase
from src.ticket_line import TicketLine

from .win_control import click_pos, mouse_pos, left_down, left_up, press_key, write_string
from .constants.constants import Coor, Area, GUISum
from .sum_area import sum_area

from .station_changer import Station, StationChanger

from .stations.order_station import OrderStation
from .stations.grill_station import GrillStation
from .stations.build_station import BuildStation
from .stations.drink_station import DrinksStation


class PancakeBot():
    # Pancake cook time: 33 seconds, 16 seconds for first day

    # Getting the handler of the active python console
    IMAGE_SUM_DEBUG = False

    def __init__(self):
        console_window = pygetwindow.getActiveWindow()
        if console_window:
            self.console_window = console_window
        else:
            raise Exception("Could not get console window")

        self.pancake_window = pygetwindow.getWindowsWithTitle(
            "Adobe Flash Player 32")[0]

        self.station_changer = StationChanger()
        self.order_station = OrderStation()
        self.grill_station = GrillStation()
        self.build_station = BuildStation()
        self.drink_station = DrinksStation()
        self.ticket_line = TicketLine()

        self.pancake_window.moveTo(1800, 800)

    def start(self, arg=None):
        if arg is None:
            self.start_game()

        if arg == 'io':
            self.order_station.interpret_order()
        elif arg == 'continue_first':
            self.main_loop(is_first_day=True)
        elif arg == 'continue':
            self.main_loop()
        elif arg == 'load':
            print(self.order_station.ingredient_sums)
            print(self.order_station.topping_count_sums)
        else:
            print(f"Invalid argument: {arg}")
            exit()

    def check_sound(self):

        self.console_window.activate()
        sound = input("Would you like sound? (Y/N)\n")[0].lower()
        sound_state = sum_area(Area.mm_sound)
        if sound == 'y':
            # Turn sound on
            if sound_state == GUISum.sound_muted:
                click_pos(Coor.mm_sound)

        elif sound == 'n':
            # Turn sound off
            if sound_state == GUISum.sound_active:
                click_pos(Coor.mm_sound)
        else:
            print("I don't understand '"+sound+"'")
            self.check_sound()

    def select_save(self):

        # Select the save number
        self.console_window.activate()
        while True:
            save_slot = input("Which slot? (1 - 3)")
            if save_slot not in ('1', '2', '3'):
                print('Pick a proper slot!')
            else:
                break

        # If the slot is empty, start a new game
        if sum_area(Area.mm_delete_slot[save_slot]) == GUISum.empty_slot:
            self.new_game(save_slot)
            return True

        # Slot already has a save
        print('This slot already has a save')
        while True:
            self.console_window.activate()
            choice = input("Continue or Delete? \n")
            if choice[0].lower() == 'c':
                return self.continue_from_save(save_slot)

            elif choice[0].lower() == 'd':
                print('Deleting...')
                click_pos(Coor.mm_delete_slot[save_slot])
                time.sleep(.5)
                click_pos(Coor.mm_erasegmcnfm[save_slot])
                time.sleep(.5)
                click_pos(Coor.mm_slot[save_slot])
                self.new_game(save_slot)
                return True
            else:
                print("I don't understand!")

    def continue_from_save(self, slot):
        print('Continuing from save')
        click_pos(Coor.mm_slot[slot])
        time.sleep(1)
        click_pos(Coor.mm_resume_save)

        print('Starting level...')

        first_day = False
        while True:
            # Click continue button if loading
            if sum_area(Area.load_continue) == GUISum.load_loading:
                click_pos(Coor.preload_continue)

            # Day 1 is tutorial
            if sum_area(Area.day_number) == GUISum.dayStart_tutorial:
                first_day = True
                break

            # When cutscene finishes, start the loop
            if sum_area(Area.order_floor) == GUISum.order_floor:
                break

            time.sleep(1)

        if first_day:
            print('It is the first day, a tutorial needs completing')
            while sum_area(Area.menu_btn) != GUISum.menu_btn:
                time.sleep(2)
            self.do_tutorial()
            return True

        while sum_area(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)
        print("Let's go!")
        return False

    def get_gender(self):
        while True:
            gender = input('Male or female?')[0].lower()
            if gender == "m" or gender == 'f':
                return gender

    def new_game(self, save_slot):
        click_pos(Coor.mm_slot[save_slot])

        self.console_window.activate()
        gender = self.get_gender()

        if gender == 'm':
            click_pos(Coor.char_male)
        elif gender == 'f':
            click_pos(Coor.char_female)

        while True:
            try:
                self.console_window.activate()
                name = input("What is your name? \n")
                click_pos(Coor.char_nameField)
                write_string(name)
                break
            except Exception:
                print("Oops! Try entering a name without special characters.")
                click_pos(Coor.char_nameField)
                time.sleep(0.2)
                click_pos(Coor.char_nameField)
                press_key('backspace')

        click_pos(Coor.char_continue)
        time.sleep(1)
        click_pos(Coor.intro_skip)
        self.do_tutorial()

    def do_tutorial(self):

        self.grill_station.set_cook_duration(
            GrillStation.TUTORIAL_COOK_DURATION)

        # Wait until intro sequence is finished
        print('Waiting for cutscene to finish...')
        while sum_area(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)

        print("Tutorial Time!")

        # Click on grill station
        self.station_changer.change(Station.GRILL)

        # Click on build station
        self.station_changer.change(Station.BUILD)

        # Click on order station
        self.station_changer.change(Station.ORDER)

        # Take order, wait for order to complete
        print("Waiting for customer...")
        while sum_area(Area.order_floor) == GUISum.order_floor:  # empty floor
            time.sleep(1)

        print('Customer is ready!')
        self.order_station.wait_for_order()

        # Drag ticket to ticket line
        mouse_pos(Coor.line_active)
        left_down()
        mouse_pos(Coor.line_first_slot)
        left_up()

        # Click on grill station
        self.station_changer.change(Station.GRILL)

        # Drag order to active order
        mouse_pos(Coor.line_first_slot)
        left_down()
        mouse_pos(Coor.line_active)
        left_up()

        # Do pancakes
        self.grill_station.place_ingredient('grill', 'pancake', 5)
        time.sleep(.1)
        self.grill_station.place_ingredient('grill', 'pancake', 6)

        # Wait until 16 seconds have passed, then flip pancakes
        print('Waiting for pancakes to cook...')
        time.sleep(18)

        click_pos(Coor.grill[5])
        time.sleep(.1)
        click_pos(Coor.grill[6])

        print('Pancakes Flipped')
        # Wait until 16 seconds have passed, then drag pancakes to green tick.
        time.sleep(18)

        self.grill_station._move_to_output(Coor.grill[5])
        time.sleep(.1)
        self.grill_station._move_to_output(Coor.grill[6])

        # Click on build station
        self.station_changer.change(Station.BUILD)

        # Drag pancakes to build area
        BuildStation.add_base()
        time.sleep(.5)
        BuildStation.add_base()

        # Drag 3 butter pads to 3 elliptic points on the pancake
        # Maximum distribution.
        BuildStation.spread_topping('butterpad', 3)

        # Drag and release blueberries in circle path
        BuildStation.spread_sprinkle_or_sauce('blueberry')

        # Blue and release blueberry sauce in circle path
        BuildStation.spread_sprinkle_or_sauce('blueberry_sauce')

        # Click finish
        time.sleep(1)
        click_pos(Coor.build_finish)
        time.sleep(1)

        # Drag ticket to finish tray
        mouse_pos(Coor.line_active)
        left_down()
        time.sleep(.5)
        mouse_pos(Coor.build_tray)
        left_up()

        # Wait until back at build station
        print('Waiting for customer...')
        while sum_area(Area.pancake_tray) != GUISum.pancake_tray:
            time.sleep(1)

        # Click on order station
        self.station_changer.change(Station.ORDER)

        # END
        print('TUTORIAL COMPLETE!')

    def gameplay_loop(self, is_first_day):

        orders: List[Order] = []

        store_closed = False
        time_prev_check = 0
        order_timeout = 0

        # One the first day, cooking time is halved due to the tutorial.
        if is_first_day:
            self.grill_station.set_cook_duration(
                GrillStation.TUTORIAL_COOK_DURATION)
        else:
            self.grill_station.set_cook_duration(
                GrillStation.DEFAULT_COOK_DURATION)

        # Main loop goes here.
        print("MAIN LOOP BEGINNING")

        # Avoiding the problems of the blue ribbon
        # TODO Add detection for blue ribbon to prevent station switching every single day
        time.sleep(.5)
        self.station_changer.change(Station.GRILL)

        # TASK PRIORITY
        #
        # 1. Pancake flipping and finishing on the grill
        # 2. Getting customers orders
        # 3. Drinks
        # 4. Cooking start for orders
        # 5. Pancake building
        # 6. Pancake serving

        while True:
            # 1. Check grill
            if self.grill_station.order_ready(orders):
                self.station_changer.change(Station.GRILL)
                self.grill_station.process_orders(orders)

            # 2. Check for new customers
            if not store_closed and time_prev_check + order_timeout < time.time():

                self.station_changer.change(Station.ORDER)
                # If customer is waiting at counter
                if sum_area(Area.order_floor) != GUISum.order_floor and (len(orders) < 12):
                    print('Customer detected!')

                    # Take order
                    order = self.order_station.take_order()
                    orders.append(order)
                    self.ticket_line.add_order(order)
                    self.ticket_line.store(order)

                    print(f'Number of orders: {len(orders)}')

                    # Check if the customer was a closer (CLOSED sign)
                    # If so, no longer need to check for new customers
                    if sum_area(Area.store_sign) == GUISum.closed_sign:
                        store_closed = True

                    time_prev_check = time.time()
                    order_timeout = 5

                    continue

                else:
                    # Check if a customer is approaching counter
                    if sum_area(Area.store_floor) == GUISum.store_floor:
                        # No customers approaching
                        time_prev_check = time.time()
                        order_timeout = 8
                    else:
                        # Customer approaching
                        time_prev_check = time.time()
                        order_timeout = 3

            # 3. Make drinks for orders
            drink_made = False
            for order in orders:
                if order.has_drink() and not order.drink_made:
                    self.station_changer.change(Station.DRINK)
                    self.drink_station.make_drink(order)
                    self.build_station.add_drink(order)
                    drink_made = True
                    break

            if drink_made:
                continue

            # 4. Start cooking if spaces are available on the grill
            started_order = False
            for order in orders:

                # if needed number of grills is available,
                if order.phase == OrderPhase.WAITING:
                    if self.grill_station.can_do_order(order):
                        self.station_changer.change(Station.GRILL)
                        self.grill_station.do_order(order)
                        started_order = True

            if started_order:
                continue

            # 5. Build Pancake
            if self.grill_station.pancakes_ready() and not self.build_station.order_is_built():
                order = self.grill_station.finished_queue.pop(0)
                self.station_changer.change(Station.BUILD)
                self.ticket_line.retrieve(order)
                self.build_station.build_pancake(order)

            # 6. Serve pancake
            # Day finishes when the last order is served
            if self.build_station.order_is_built():
                self.station_changer.change(Station.BUILD)
                order = self.build_station.finish_active_order()
                self.ticket_line.dispatch(order)
                orders.remove(order)

                # wait until back at build station or day finished
                print('Waiting for customer...')
                while sum_area(Area.pancake_tray) != GUISum.pancake_tray:
                    time.sleep(.5)
                    # Check if day end
                    if sum_area(Area.flipline_logo) == GUISum.flipline_logo:
                        self.order_station.total_orders_taken = 0
                        print('Level complete')
                        return

    def start_next_day(self):

        print('Waiting...')
        while sum_area(Area.continue1) != GUISum.continue1:
            time.sleep(1)

        click_pos(Coor.daycom_continue1)
        time.sleep(4)
        click_pos(Coor.daycom_skipslots)
        time.sleep(2)
        click_pos(Coor.daycom_continue2)

        print('Waiting for next day to load...')
        while sum_area(Area.load_continue) != GUISum.load_continue:
            time.sleep(1)

        click_pos(Coor.daycom_continue3)

        print('Waiting for cutscene to finish...')
        while sum_area(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)
        print("Let's go!")

    def start_game(self):

        # Start on preloader screen
        click_pos(Coor.preload_continue)

        print('Waiting for intro to finish...')
        print('')
        print('=========')
        print('If the intro has finished but the script does not detect it,')
        print('the window is misaligned. You will need to update the')
        print('X_PAD and Y_PAD game coordinates and restart the script.')
        print('=========')
        print('')

        while sum_area(Area.mm_play) != GUISum.play_button:
            time.sleep(2)

        # Check sound
        self.check_sound()

        # Click Play
        click_pos(Coor.mm_play)

        # Transition delay
        time.sleep(1.2)

        # Select save
        is_first_day = self.select_save()

        # Game begins here
        self.main_loop(is_first_day)

    def main_loop(self, is_first_day=False):
        while True:
            self.gameplay_loop(is_first_day)
            is_first_day = False
            self.start_next_day()
