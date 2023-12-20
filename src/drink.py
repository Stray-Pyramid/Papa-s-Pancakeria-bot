class Drink():
    def __init__(self, flavour, size, additional):
        self.flavour = flavour
        self.size = size
        self.additional = additional

    def __repr__(self):
        return f"<Drink {self.flavour} {self.size} {self.additional}>"

    def __str__(self):
        return f"<Drink {self.flavour} {self.size} {self.additional}>"
