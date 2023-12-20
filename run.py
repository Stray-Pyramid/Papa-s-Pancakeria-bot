import sys
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
    else:
        bot.start(arg_value)
