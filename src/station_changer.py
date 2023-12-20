import time
from enum import Enum, auto

from .win_control import click_pos
from .constants.constants import Coor


class Station(Enum):
    ORDER = auto()
    GRILL = auto()
    BUILD = auto()
    DRINK = auto()


class StationChanger():
    def __init__(self):
        self.current_station = Station.ORDER

    def change(self, station: Station):
        # No need to change station if we are already there
        if station == self.current_station:
            return

        if station == Station.ORDER:
            click_pos(Coor.s_order)
        elif station == Station.GRILL:
            click_pos(Coor.s_grill)
        elif station == Station.BUILD:
            click_pos(Coor.s_build)
        elif station == Station.DRINK:
            click_pos(Coor.s_drink)
        else:
            raise Exception(
                "Tried to switch to non-existent station with ID:", station)

        self.current_station = station

        print(f"Changing to station {Station(station).name}")

        # Time it takes to transition between stations
        time.sleep(.5)
