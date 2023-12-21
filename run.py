import sys
from src.stations.drink_station import DrinkStation
from src.stations.order_station import OrderStation
from src.sum_area import sum_area
from src.pancake_bot import PancakeBot
from src.stations.build_station import BuildStation

if __name__ == "__main__":
    bot = PancakeBot()

    arg_value = sys.argv[1] if len(sys.argv) > 1 else None

    if arg_value == "build_sauce":
        topping = sys.argv[2]
        BuildStation.spread_sprinkle_or_sauce(topping)
    elif arg_value == "build_topping":
        topping = sys.argv[2]
        count = int(sys.argv[3])
        BuildStation.spread_topping(topping, count)
    elif arg_value == "build_base":
        BuildStation.add_base()
    elif arg_value == "make_drink":
        order_station = OrderStation()
        drink_station = DrinkStation()

        order = order_station.interpret_order()
        drink_station.make_drink(order)

    elif arg_value == "sum_area":
        print("Please enter area coordinates")
        print("FORMAT: LEFT TOP WIDTH HEIGHT")

        coor = input().split(" ")
        if len(coor) != 4:
            print("INVALID")
            sys.exit()

        area = tuple([int(i) for i in coor])
        print(sum_area(area))

    else:
        bot.start(arg_value)
