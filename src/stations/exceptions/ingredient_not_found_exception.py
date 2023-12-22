class IngredientNotFoundException(Exception):
    def __init__(self, ingredient_sum: int):
        self.message = f"Could not find ingredient with sum {ingredient_sum}"
        super().__init__(self.message)
