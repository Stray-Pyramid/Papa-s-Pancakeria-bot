import time
import pygetwindow

from .win_control import click_pos, press_key, write_string
from .constants.constants import Coor, Area, GUISum
from .sum_area import sum_area


class GameGUI:
    def __init__(self):
        console_window = pygetwindow.getActiveWindow()
        if console_window:
            self.console_window = console_window
        else:
            raise Exception("Could not get console window")

        self.pancake_window = pygetwindow.getWindowsWithTitle(
            "Adobe Flash Player 32")[0]

        self.pancake_window.moveTo(1800, 800)

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

            if choice[0].lower() == 'd':
                print('Deleting...')
                click_pos(Coor.mm_delete_slot[save_slot])
                time.sleep(.5)
                click_pos(Coor.mm_erasegmcnfm[save_slot])
                time.sleep(.5)
                click_pos(Coor.mm_slot[save_slot])
                self.new_game(save_slot)
                return True

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

    def start_game(self) -> bool:

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

        return is_first_day
