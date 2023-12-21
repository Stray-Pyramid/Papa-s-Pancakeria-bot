import sys

from src.game_gui import GameGUI
from src.game_loop import GameLoop


class PancakeBot():
    IMAGE_SUM_DEBUG = False

    def __init__(self):
        self.game_loop = GameLoop()
        self.game_gui = GameGUI()

    def start(self, arg=None):
        if arg is None:
            is_first_day = self.game_gui.start_game()
            if is_first_day:
                self.game_loop.do_tutorial()

            self.main_loop(is_first_day)

        if arg == 'continue_first':
            self.main_loop(is_first_day=True)
        elif arg == 'continue':
            self.main_loop()
        else:
            print(f"Invalid argument: {arg}")
            sys.exit()

    def main_loop(self, is_first_day=False):
        while True:
            self.game_loop.run(is_first_day)
            is_first_day = False
            self.game_gui.start_next_day()
