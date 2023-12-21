import time

from src.ticket_line import TicketLine

from .sum_area import sum_area
from .constants.constants import GUISum, Area

from .station_changer import Station, StationChanger
from .stations.grill_station import GrillStation
from .stations.build_station import BuildStation
from .stations.order_station import OrderStation


class TutorialSequence():
    PANCAKE_COOK_TIME = 18

    def __init__(self, order_station: OrderStation, grill_station: GrillStation,
                 build_station: BuildStation, station_changer: StationChanger):

        self.order_station = order_station
        self.grill_station = grill_station
        self.build_station = build_station
        self.station_changer = station_changer

        self.grill_station.set_cook_duration(self.PANCAKE_COOK_TIME)

        self.ticket_line = TicketLine()

    def run(self):
        # Wait until intro sequence is finished
        print('Waiting for cutscene to finish...')
        while sum_area(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)

        # Look at all those stations!
        self.station_changer.change(Station.GRILL)
        self.station_changer.change(Station.BUILD)
        self.station_changer.change(Station.ORDER)

        print("Waiting for customer...")
        while sum_area(Area.order_floor) == GUISum.order_floor:
            time.sleep(1)

        self.order_station.wait_for_order()
        time.sleep(2)
        order = self.order_station.interpret_order()

        self.ticket_line.add_order(order)
        self.ticket_line.store(order)

        self.station_changer.change(Station.GRILL)

        self.ticket_line.retrieve(order)

        # Cooka da pancakes
        self.grill_station.start_order(order, grills=[5, 6])
        time.sleep(self.PANCAKE_COOK_TIME)
        self.grill_station.flip_order(order)
        time.sleep(self.PANCAKE_COOK_TIME)
        self.grill_station.finish_cooking(order)

        # Build the pancake
        self.station_changer.change(Station.BUILD)

        BuildStation.add_base()
        time.sleep(.5)
        BuildStation.add_base()

        BuildStation.spread_topping('butterpad', 3)
        BuildStation.spread_sprinkle_or_sauce('blueberry')
        time.sleep(.5)
        BuildStation.spread_sprinkle_or_sauce('blueberry_sauce')

        # Give the pancake to the customer
        self.build_station.finish_order(order)
        self.ticket_line.dispatch(order)

        self.station_changer.change(Station.ORDER)

        # END
        print('TUTORIAL COMPLETE!')
