import time
from typing import List

from .order import Order
from .win_control import mouse_pos, left_up, left_down
from .constants.constants import Coor


class TicketLine():
    MAXIMUM_TICKETS = 12

    def __init__(self):
        self._active_order = None
        self._slots: List[Order | None] = [None] * 10

    def add_order(self, order: Order):
        self._active_order = order

    # Move order ticket from active to line
    def store(self, order: Order):
        if self._active_order is None:
            raise Exception("No active order ticket")

        if all(self._slots):
            raise Exception("No space found on ticket line")

        for slot_number, order_in_slot in enumerate(self._slots):
            if order_in_slot is not None:
                continue

            print(f"Moving order {order.id} ticket to slot {slot_number}")

            self._slots[slot_number] = order
            self._active_order = None
            self._pickup_active_order()
            self._drop_order_on_line(slot_number)
            return

    def store_active_order(self):
        if self._active_order:
            self.store(self._active_order)

    # Move order ticket from line to active
    def retrieve(self, order: Order):
        if self._active_order is not None:
            raise Exception("There is already an active order ticket")

        for slot_number, order_in_slot in enumerate(self._slots):
            if order_in_slot != order:
                continue

            print(f"Moving order {order.id} ticket to active")

            self._active_order = order
            self._slots[slot_number] = None

            self._pickup_order_on_line(slot_number)
            self._drop_active_order()
            return

    # Move order ticker from line / active to dispatch tray
    def dispatch(self, order: Order):
        order_found = False

        print(f"Dispatching order {order.id}")

        if order == self._active_order:
            self._active_order = None
            self._pickup_active_order()
            order_found = True
        else:
            for slot_number, order_in_slot in enumerate(self._slots):
                if order_in_slot == order:
                    self._slots[slot_number] = None
                    self._pickup_order_on_line(slot_number)
                    order_found = True
                    break

        if order_found is False:
            raise Exception("Could not find order ticket to dispatch")

        self._drop_order_on_dispatch_tray()
        self._wait_for_customer()

    @staticmethod
    def _pickup_active_order():
        mouse_pos(Coor.line_active)
        left_down()

    @staticmethod
    def _drop_active_order():
        mouse_pos(Coor.line_active)
        left_up()

    @staticmethod
    def _pickup_order_on_line(slot_number: int):
        x_pos = Coor.line_first_slot[0] + (Coor.line_spacing * slot_number)
        mouse_pos((x_pos, Coor.line_first_slot[1]))
        left_down()

    @staticmethod
    def _drop_order_on_line(slot_number: int):
        x_pos = Coor.line_first_slot[0] + (Coor.line_spacing * slot_number)
        mouse_pos((x_pos, Coor.line_first_slot[1]))
        left_up()

    @staticmethod
    def _drop_order_on_dispatch_tray():
        mouse_pos(Coor.build_tray)
        left_up()

    @staticmethod
    def _wait_for_customer():
        print("Waiting for customer...")
        time.sleep(9)
        print("Over")
