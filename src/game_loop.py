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
        self.station_changer = StationChanger()
        self.order_station = OrderStation()
        self.grill_station = GrillStation()
        self.build_station = BuildStation()
        self.drink_station = DrinksStation()
        self.ticket_line = TicketLine()

    def do_tutorial(self):
        TutorialSequence.run(self.order_station, self.grill_station,
                             self.build_station, self.station_changer)

    def run(self, is_first_day):

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

                if self.order_station.customer_ready_to_order() and len(orders) < 12:
                    print('Customer detected!')

                    # Take order
                    order = self.order_station.take_order()
                    orders.append(order)
                    self.ticket_line.add_order(order)
                    self.ticket_line.store(order)

                    print(f'Number of orders: {len(orders)}')

                    # Check if the customer was a closer (CLOSED sign)
                    # If so, no longer need to check for new customers
                    if self.order_station.store_is_closed() and self.order_station.customer_is_approaching():
                        store_closed = True

                    time_prev_check = time.time()
                    order_timeout = 5

                    continue

                # Check if a customer is approaching counter
                if self.order_station.customer_is_approaching():
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
                        self.grill_station.start_order(order)
                        started_order = True

            if started_order:
                continue

            # 5. Build Pancake
            if self.grill_station.pancakes_ready() and not self.build_station.order_is_built():
                order = self.grill_station.finished_queue.pop(0)
                self.station_changer.change(Station.BUILD)
                self.ticket_line.retrieve(order)
                self.build_station.build_order(order)

            # 6. Serve pancake
            if self.build_station.order_is_built():
                self.station_changer.change(Station.BUILD)
                order = self.build_station.finish_active_order()
                self.ticket_line.dispatch(order)
                orders.remove(order)

                # Day finishes when the last order is served
                if len(orders) == 0 and store_closed:
                    self.order_station.total_orders_taken = 0
                    print('Level complete')
                    return
