import time
from typing import List

from src.order import Order, OrderPhase

from src.station_changer import StationChanger, Station
from src.stations.order_station import OrderStation
from src.stations.grill_station import GrillStation
from src.stations.build_station import BuildStation
from src.stations.drink_station import DrinksStation
from src.ticket_line import TicketLine

from src.tutorial_sequence import TutorialSequence


class GameLoop:
    def __init__(self) -> None:
        self._station_changer = StationChanger()
        self._order_station = OrderStation()
        self._grill_station = GrillStation()
        self._build_station = BuildStation()
        self._drink_station = DrinksStation()
        self._ticket_line = TicketLine()

        self._orders: List[Order]
        self._store_open = True
        self._time_prev_check = 0
        self._order_timeout = 0

    def do_tutorial(self):
        TutorialSequence.run(self._order_station, self._grill_station,
                             self._build_station, self._station_changer)

    def _reset(self, is_first_day):
        self._orders = []

        self._store_open = True
        self._time_prev_check = 0
        self._order_timeout = 0

        self._order_station.total_orders_taken = 0

        # One the first day, cooking time is halved due to the tutorial.
        if is_first_day:
            self._grill_station.set_cook_duration(
                GrillStation.AFTER_TUTORIAL_COOK_DURATION)
        else:
            self._grill_station.set_cook_duration(
                GrillStation.DEFAULT_COOK_DURATION)

        # Avoiding the problems of the blue ribbon
        # TODO Add detection for blue ribbon to prevent station switching every single day
        time.sleep(.5)
        self._station_changer.change(Station.GRILL)

    def run(self, is_first_day):
        self._reset(is_first_day)

        # TASK PRIORITY
        #
        # 1. Pancake flipping and finishing on the grill
        # 2. Getting customers orders
        # 3. Drinks
        # 4. Cooking start for orders
        # 5. Pancake building
        # 6. Pancake serving

        while len(self._orders) != 0 or self._store_open:
            # 1. Check grill
            if self._grill_station.order_ready(self._orders):
                self._station_changer.change(Station.GRILL)
                self._grill_station.process_orders(self._orders)

            # 2. Check for new customers
            if not self._store_open and self._time_prev_check + self._order_timeout < time.time():

                self._station_changer.change(Station.ORDER)

                if self._order_station.customer_ready_to_order() and len(self._orders) < 12:
                    print('Customer detected!')

                    # Take order
                    order = self._order_station.take_order()
                    self._orders.append(order)
                    self._ticket_line.add_order(order)
                    self._ticket_line.store(order)

                    print(f'Number of orders: {len(self._orders)}')

                    # Check if the store is now closed, and that there are no more customers
                    # If that is the case, there is no longer a need to check for new customers
                    if self._order_station.store_is_closed() and self._order_station.customer_is_approaching():
                        self._store_open = False

                    self._time_prev_check = time.time()
                    self._order_timeout = 5

                    continue

                # Check if a customer is approaching counter
                if self._order_station.customer_is_approaching():
                    # No customers approaching
                    self._time_prev_check = time.time()
                    self._order_timeout = 8
                else:
                    # Customer approaching
                    self._time_prev_check = time.time()
                    self._order_timeout = 3

            # 3. Make drinks for orders
            drink_made = False
            for order in self._orders:
                if order.has_drink() and not order.drink_made:
                    self._station_changer.change(Station.DRINK)
                    self._drink_station.make_drink(order)
                    self._build_station.add_drink(order)
                    drink_made = True
                    break

            if drink_made:
                continue

            # 4. Start cooking if spaces are available on the grill
            started_order = False
            for order in self._orders:

                # if needed number of grills is available,
                if order.phase == OrderPhase.WAITING:
                    if self._grill_station.can_do_order(order):
                        self._station_changer.change(Station.GRILL)
                        self._grill_station.start_order(order)
                        started_order = True

            if started_order:
                continue

            # 5. Build Pancake
            if self._grill_station.pancakes_ready() and not self._build_station.order_is_built():
                order = self._grill_station.finished_queue.pop(0)
                self._station_changer.change(Station.BUILD)
                self._ticket_line.retrieve(order)
                self._build_station.build_order(order)

            # 6. Serve pancake
            if self._build_station.order_is_built():
                self._station_changer.change(Station.BUILD)
                order = self._build_station.finish_active_order()
                self._ticket_line.dispatch(order)
                self._orders.remove(order)
