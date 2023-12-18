import sys
from src.pancake_bot import PancakeBot

if __name__ == "__main__":
    bot = PancakeBot()
    
    arg_value = sys.argv[1] if len(sys.argv) > 1 else None
    PancakeBot.Start(arg_value)
