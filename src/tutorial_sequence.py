import time

from src.ticket_line import TicketLine

from .sum_area import sum_area
from .constants.constants import GUISum, Area

from .station_changer import Station, StationChanger
from .stations.grill_station import GrillStation
from .stations.build_station import BuildStation
from .stations.order_station import OrderStation


class TutorialSequence():
    @staticmethod
    def run(order_station: OrderStation, grill_station: GrillStation,
            build_station: BuildStation, station_changer: StationChanger):

        ticket_line = TicketLine()

        # Wait until intro sequence is finished
        print('Waiting for cutscene to finish...')
        while sum_area(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)

        # Look at all those stations!
        station_changer.change(Station.GRILL)
        station_changer.change(Station.BUILD)
        station_changer.change(Station.ORDER)

        print("Waiting for customer...")
        while sum_area(Area.order_floor) == GUISum.order_floor:
            time.sleep(1)

        order_station.wait_for_order()
        time.sleep(2)
        order = order_station.interpret_order()

        ticket_line.add_order(order)
        ticket_line.store(order)

        station_changer.change(Station.GRILL)

        ticket_line.retrieve(order)

        # Cooka da pancakes
        grill_station.start_order(order, grills=[5, 6])
        time.sleep(GrillStation.TUTORIAL_COOK_DURATION)
        grill_station.flip_order(order)
        time.sleep(GrillStation.TUTORIAL_COOK_DURATION)
        grill_station.finish_cooking(order)

        # Build the pancake
        station_changer.change(Station.BUILD)

        BuildStation.add_base()
        time.sleep(.5)
        BuildStation.add_base()

        BuildStation.spread_topping('butterpad', 3)
        BuildStation.spread_sprinkle_or_sauce('blueberry')
        time.sleep(.5)
        BuildStation.spread_sprinkle_or_sauce('blueberry_sauce')

        # Give the pancake to the customer
        build_station.finish_order(order)
        ticket_line.dispatch(order)

        station_changer.change(Station.ORDER)

        # END
        print('TUTORIAL COMPLETE!')
