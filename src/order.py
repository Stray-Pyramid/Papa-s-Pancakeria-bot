from enum import Enum, auto


class OrderPhase(Enum):
    WAITING = auto()
    COOKING = auto()
    COOKED = auto()
    BUILT = auto()


class Order():

    def __init__(self, order_id, ingredients, grills_needed, irons_needed, drink=None):
        self.ingredients = ingredients
        self.num_of_grills = grills_needed
        self.num_of_irons = irons_needed
        self.drink = drink
        self.drink_made = False

        self.phase = OrderPhase.WAITING
        self.flipped = False

        self.id = order_id
        self.ticket_line_slot = -1

        self.cook_start_time = 0.0

    def __repr__(self):
        return f"<Order {self.id}>"

    def __str__(self):
        return f"<Order {self.id}>"

    def has_drink(self):
        return self.drink is not None

    def ready(self):
        is_built = self.phase is OrderPhase.BUILT
        drink_ready = self.drink is None or self.drink_made is True

        return is_built and drink_ready
