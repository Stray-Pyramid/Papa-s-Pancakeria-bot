# Python 3.8.2
# Last updated 09/14/2020 (MM/DD/YYYY)
# By StrayPyramid

import time
import pygetwindow

from .win_control import *
from .rect import *
from .constants.constants import *
from .sum_area import *

from .station_changer import *

from .stations.grill_station import *
from .stations.build_station import *
from .stations.drink_station import *

class PancakeBot():
    IngredientSum = {}
    ToppingCounts = {}

    # Pancake cook time: 33 seconds, 16 seconds for first day

    INGREDIENT_FP = "./src/constants/item_sums.txt"

    # Getting the handler of the active python console
    CONSOLE_WINDOW: pygetwindow.Win32Window
    PANCAKE_WINDOW: pygetwindow.Win32Window
    IMAGE_SUM_DEBUG = False


    def __init__(self):
        self.CONSOLE_WINDOW = pygetwindow.getActiveWindow()
        self.PANCAKE_WINDOW = pygetwindow.getWindowsWithTitle("Adobe Flash Player 32")[0]
        
        self.load_items()
        
        self.PANCAKE_WINDOW.moveTo(1800, 800)
    
    def Start(self, arg=None):
        if arg is None:
            self.start_game()
        
        if arg == 'io':
            self.interpret_order()
        elif arg == 'continue_first':
            self.main_loop(is_first_day = True)
        elif arg == 'continue':
            self.main_loop()
        elif arg == 'load':
            print(self.IngredientSum)
            print(self.ToppingCounts)
        else:
            print(f"Invalid argument: {arg}")
            exit()
            
    def check_sound(self):
        
        self.CONSOLE_WINDOW.activate()
        sound = input("Would you like sound? (Y/N)\n")[0].lower()
        soundState = sumArea(Area.mm_sound)
        if sound == 'y':
            #Turn sound on
            if soundState == GUISum.sound_muted:
                clickPos(Coor.mm_sound)
            
        elif sound == 'n':
            #Turn sound off
            if soundState == GUISum.sound_active:
                clickPos(Coor.mm_sound)
        else:
            print ("I don't understand '"+sound+"'")
            self.check_sound()

    def select_save(self):
        
        # Select the save number
        self.CONSOLE_WINDOW.activate()
        while True:
            save_slot = input("Which slot? (1 - 3)")
            if save_slot not in ('1', '2', '3'):
                print ('Pick a proper slot!')
            else:
                break
        
        # If the slot is empty, start a new game
        if sumArea(Area.mm_delete_slot[save_slot]) == GUISum.empty_slot:
            self.new_game(save_slot)
            return True
        
        # Slot already has a save
        print ('This slot already has a save')
        while True:
            self.CONSOLE_WINDOW.activate()
            choice = input("Continue or Delete? \n")
            if choice[0].lower() == 'c':
                return self.continue_from_save(save_slot)
                
            elif choice[0].lower() == 'd':
                print ('Deleting...')
                clickPos(Coor.mm_delete_slot[save_slot])
                time.sleep(.5)
                clickPos(Coor.mm_erasegmcnfm[save_slot])
                time.sleep(.5)
                clickPos(Coor.mm_slot[save_slot])
                self.new_game(save_slot)
                return True
            else:
                print ("I don't understand!")
                

    def continue_from_save(self, slot):
        print ('Continuing from save')
        clickPos(Coor.mm_slot[slot])
        time.sleep(1)
        clickPos(Coor.mm_resume_save)
        
        print ('Starting level...')
        
        first_day = False
        while True:
            # Click continue button if loading
            if sumArea(Area.load_continue) == GUISum.load_loading:
                clickPos(Coor.preload_continue) 
                
            # Day 1 is tutorial
            if sumArea(Area.day_number) == GUISum.dayStart_tutorial:
                first_day = True
                break
                
            # When cutscene finishes, start the loop
            if sumArea(Area.order_floor) == GUISum.order_floor:
                break
                
            time.sleep(1)
                
        if first_day:
            print ('It is the first day, a tutorial needs completing')
            while sumArea(Area.menu_btn) != GUISum.menu_btn:
                time.sleep(2)
            self.do_tutorial()
            return True
        else:
            while sumArea(Area.menu_btn) != GUISum.menu_btn:
                time.sleep(2)
            print ("Let's go!")
            return False        


    def get_gender(self):
        while(True):
            gender = input('Male or female?')[0].lower()
            if gender == "m" or gender == 'f':
                return gender
            
    def new_game(self, save_slot):
        clickPos(Coor.mm_slot[save_slot])
        
        self.CONSOLE_WINDOW.activate()
        gender = self.get_gender()

        if gender == 'm':
            clickPos(Coor.char_male)
        elif gender == 'f':
            clickPos(Coor.char_female)
                
        while True:
            try:
                self.CONSOLE_WINDOW.activate()
                name = input("What is your name? \n")
                clickPos(Coor.char_nameField)
                writeString(name)
                break
            except:
                print ("Oops! Try entering a name without special characters.")
                clickPos(Coor.char_nameField)
                time.sleep(0.2)
                clickPos(Coor.char_nameField)
                pressKey('backspace')
        
        clickPos(Coor.char_continue)
        time.sleep(1)
        clickPos(Coor.intro_skip)
        self.do_tutorial()

    def take_order(self):
        self.wait_for_order()
        return self.interpret_order()
        
        
    def wait_for_order(self):
        time.sleep(.4)
        clickPos(Coor.take_order)
        print ('Taking an order...')
        time.sleep(1)
        screen = sumArea(Area.order_wait)
        while sumArea(Area.order_wait) == screen:
            time.sleep(.5)
        
    @staticmethod
    def move_order_to_line(order):
        mousePos(Coor.line_active)
        leftDown()
        mousePos((Coor.line_first_slot[0] + (Coor.line_spacing * order.id), Coor.line_first_slot[1]))
        leftUp()
            
    def do_tutorial(self):
        
        station = StationChanger()
        grill = GrillStation(station)
        
        # Wait until intro sequence is finished
        print ('Waiting for cutscene to finish...')
        while sumArea(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)   
            
        print ("Tutorial Time!")
        
        # Click on grill station
        station.change(STATION.GRILL)
        
        # Click on build station
        station.change(STATION.BUILD)
        
        # Click on order station
        station.change(STATION.ORDER)
        
        # Take order, wait for order to complete
        print("Waiting for customer...")
        while sumArea(Area.order_floor) == GUISum.order_floor: #empty floor
            time.sleep(1)
        
        print ('Customer is ready!')
        self.wait_for_order()
            
        # Drag ticket to ticket line
        mousePos(Coor.line_active)
        leftDown()
        mousePos(Coor.line_first_slot)
        leftUp()
        
        # Click on grill station
        station.change(STATION.GRILL)
        
        # Drag order to active order
        mousePos(Coor.line_first_slot)
        leftDown()
        mousePos(Coor.line_active)
        leftUp()
        
        # Do pancakes
        grill.place_ingredient('grill', 'pancake', 5)
        time.sleep(.1)
        grill.place_ingredient('grill', 'pancake', 6)
            
        # Wait until 16 seconds have passed, then flip pancakes
        print('Waiting for pancakes to cook...')
        time.sleep(18)
                
        grill.flip(GrillStation.GRILL, 5)
        time.sleep(.1)
        grill.flip(GrillStation.GRILL, 6)
        
        print('Pancakes Flipped')
        # Wait until 16 seconds have passed, then drag pancakes to green tick.
        time.sleep(18)
        
        grill.finish_cooking(GrillStation.GRILL, 5)
        time.sleep(.1)
        grill.finish_cooking(GrillStation.GRILL, 6)
        
        # Click on build station
        station.change(STATION.BUILD)
        
        # Drag pancakes to build area
        BuildStation.add_base()
        time.sleep(.5)
        BuildStation.add_base()
        
        # Drag 3 butter pads to 3 elliptic points on the pancake
        # Maximum distribution.
        BuildStation.spread_topping('butterpad', 3)

        # Drag and release blueberries in circle path
        BuildStation.spread_sprinkle_or_sauce('blueberry')

        # Blue and release blueberry sauce in circle path
        BuildStation.spread_sprinkle_or_sauce('blueberry_sauce')
        
        # Click finish
        time.sleep(1)
        clickPos(Coor.build_finish)
        time.sleep(1)
        
        # Drag ticket to finish tray
        mousePos(Coor.line_active)
        leftDown()
        time.sleep(.5)
        mousePos(Coor.build_tray)
        leftUp()
        
        # Wait until back at build station
        print ('Waiting for customer...')
        while sumArea(Area.pancake_tray) != GUISum.pancake_tray:
            time.sleep(1)
        
        # Click on order station
        station.change(STATION.ORDER)
        
        # END
        print('TUTORIAL COMPLETE!')
        
    def interpret_order(self):
        #Returns the type of ingredients and number of pancakes / waffles that can order needs
        grillsNeeded = 0
        ironsNeeded = 0
        ingredients = []
        drink = None
        
        
        for slot in range(0, 8):
            # Get sum for ticket slot
            rect = Rect(Area.ticket_section)
            rect.translate(0, -Area.ticket_spacing * slot)
            sum = sumArea(rect)
            
            # If drinks slot
            if slot == 7:
                drink = self.interpret_drink()
                continue
            
            # If sum doesn't exist, prompt the user for name and add it
            if sum not in self.IngredientSum:
                self.add_ingredient(sum, slot)
            
            # If ticket slot is empty, no action required
            if self.IngredientSum[sum] == 'empty':
                print('Slot '+str(slot+1)+' is empty')
                continue
    
            # If regular slot, lookup and process
            ingredient = self.IngredientSum[sum]
            print('Found '+ingredient)
            
            ingred_type = IngredientTypes[ingredient][0]
            
            print(ingred_type)
            if ingred_type == 'piece':
                rect = Rect(Area.ticket_toppingNum)
                rect.translate(0, -Area.ticket_spacing * slot)
                countSum = sumArea(rect)
                print(countSum)
                if countSum in self.ToppingCounts:
                    topping_count = self.ToppingCounts[countSum]
                    print(topping_count, "pieces of", ingredient)
                else:
                    print ('Toppping count sum not found for slot ' + str(slot+1) + ', Sum: ' + str(countSum))
                    print ('Please write the number of toppings required.')
                    topping_count = int(input())
                    self.add_topping_count(countSum, topping_count)
                    
                ingredients.append([ingredient, topping_count])
                    
            elif ingred_type == 'combo':
                combo_bread = IngredientTypes[ingredient][1]
                combo_bits  = IngredientTypes[ingredient][2]
                if combo_bread in ('pancake', 'french'):
                    grillsNeeded += 1
                elif combo_bread == 'waffle':
                    ironsNeeded += 1
                ingredients.append([combo_bread, combo_bits])
                
            else:
                ingredients.append([ingredient])
                
            if ingred_type == 'bread':
                grillsNeeded += 1
            elif ingred_type == 'waffle':
                ironsNeeded += 1
                    
        
                    
        
        print('Number of grills needed: '+str(grillsNeeded))
        print('Number of irons needed: '+str(ironsNeeded))
        print('Ingredient list')
        print(ingredients)
        print(drink)
        return Order(ingredients, grillsNeeded, ironsNeeded, drink)
        
    def interpret_drink(self):
        d_flavour = None
        d_size = None
        d_base = None
        
        sum = sumArea(Area.t_d_size)
        print(sum)
        if self.IngredientSum[sum] == 'empty':
                print('Drinks slot is empty')
                return None
        
        # Left slot - drink flavour
        sum = sumArea(Area.t_d_flavour)
        if sum not in self.IngredientSum:
            print("DRINK FLAVOUR NOT FOUND")
            self.add_ingredient(sum, 7, drink=True)
        
        d_flavour = self.IngredientSum[sum]
        
        # Middle slot - drink size
        sum = sumArea(Area.t_d_size)
        if sum not in self.IngredientSum:
            print("DRINK SIZE NOT FOUND")
            self.add_ingredient(sum, 7, drink=True)
        
        d_size = self.IngredientSum[sum]
        
        # Right slot - drink base
        sum = sumArea(Area.t_d_additional)
        if sum not in self.IngredientSum:
            print("DRINK ADDITIONAL NOT FOUND")
            self.add_ingredient(sum, 7, drink=True)
        
        d_add = self.IngredientSum[sum]

        return Drink(d_flavour, d_size, d_add)
        
            

        
    def get_ticketLineNum(self, orders):
        for i in range(0, 12):
            if get_order_by_id(orders, i) == None:
                return i
                
    def gameplay_loop(self, is_first_day):

        orders = []
        store_closed = False
        time_prev_check = 0
        order_timeout = 0
        
        #One the first day, cooking time is halved due to the tutorial.
        if is_first_day:
            cook_time = FIRST_DAY_COOK_TIME
        else:
            cook_time = DEFAULT_COOK_TIME
        print ('Cooking time set to %s seconds' % cook_time)
        
        station = StationChanger()
        grill_station = GrillStation(station, cook_time)
        build_station = BuildStation(station)
        drinks_station = DrinksStation(station)
        
        #Main loop goes here.
        print ("MAIN LOOP BEGINNING")
        
        #Avoiding the problems of the blue ribbon
        #TODO Add detection for blue ribbon to prevent station switching every single day
        time.sleep(.5)
        station.change(STATION.GRILL)
        
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
            grill_station.check_orders(orders)
            
            # 2. Check for new customers
            if not store_closed and time_prev_check + order_timeout < time.time():
            
                station.change(STATION.ORDER)
                # If customer is waiting at counter
                if sumArea(Area.order_floor) != GUISum.order_floor and (len(orders) < 12):
                    print ('Customer detected!')
                    
                    #Take order
                    order = self.take_order()
                    order.id = self.get_ticketLineNum(orders)
                    self.move_order_to_line(order)
                    orders.append(order)
                    print ('Number of orders: '+str(len(orders)))
                    
                    # Check if the customer was a closer (CLOSED sign)
                    # If so, no longer need to check for new customers
                    if sumArea(Area.store_sign) == GUISum.closed_sign:
                        store_closed = True
                    
                    time_prev_check = time.time()
                    order_timeout = 5
                    
                    continue
                    
                else:
                    # Check if a customer is approaching counter
                    if sumArea(Area.store_floor) == GUISum.store_floor:
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
                    drinks_station.make_drink(order)
                    build_station.add_drink(order)
                    drink_made = True
                    break
                    
            if drink_made: continue
            
            # 4. Start cooking if spaces are available on the grill
            started_order = False
            for order in orders:
                
                #if needed number of grills is available,
                if order.phase == ORDER_PHASE.WAITING:
                    if grill_station.can_do_order(order):
                        grill_station.do_order(order)
                        started_order = True
                        
            if started_order: continue
            
            # 5. BUILD PANCAKE, YES    
            if grill_station.pancakes_ready() and not build_station.order_ready:
                order_id = grill_station.finished_queue.pop(0)
                order = get_order_by_id(orders, order_id)
                
                build_station.build_pancake(order)
                


            # 6. Serve pancake  
            # Day finishes when the last order is served
            if build_station.order_ready:
                order_id = build_station.serve_pancake()
                
                #wait until back at build station or day finished
                print('Waiting for customer...')
                while sumArea(Area.pancake_tray) != GUISum.pancake_tray:
                    time.sleep(.5)
                    #Check if day end
                    if sumArea(Area.flipline_logo) == GUISum.flipline_logo:
                        print ('Level complete')
                        orders.clear()
                        return
                
                # Remove order from orders
                for order in orders:
                    if order.id == order_id:
                        orders.remove(order)
                        break
            
    def start_next_day(self):

        print('Waiting...')
        while sumArea(Area.continue1) != GUISum.continue1:
            time.sleep(1)
            
        clickPos(Coor.daycom_continue1)
        time.sleep(4)
        clickPos(Coor.daycom_skipslots)
        time.sleep(2)
        clickPos(Coor.daycom_continue2)
        
        print('Waiting for next day to load...')
        while sumArea(Area.load_continue) != GUISum.load_continue:
            time.sleep(1)
            
        clickPos(Coor.daycom_continue3)

        print('Waiting for cutscene to finish...'   )
        while sumArea(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)
        print("Let's go!")
        
        
    def load_items(self):        
        with open(self.INGREDIENT_FP, 'r') as f:
            for line in f:
                i_data = line.strip()
                if(i_data) == '': return # EOF
                
                item_sum, item_name = i_data.split(":")
                item_sum = int(item_sum)
                
                if item_name[:-1] == "item_count_":
                    topping_count = int(item_name[-1])
                    self.ToppingCounts[item_sum] = topping_count
                else:
                    self.IngredientSum[item_sum] = item_name

    def add_topping_count(self, topping_sum: int, topping_count: int):

        with open(self.INGREDIENT_FP, 'a+') as f:
            f.seek(0, 2)
            f.write("%s:item_count_%s\n" % (topping_sum, topping_count))
        
        self.ToppingCounts[topping_sum] = topping_count
        
        
    def add_ingredient(self, item_sum: int, slot: int, drink=False):
        
        print('Found unregisterd ingredient')
        print('Slot: '+str(slot+1))
        print('Sum: '+str(item_sum))    
        print("Please enter ingredient name")
        
        item_name = self.input_console()
        
        if drink is False:
            for _,key in enumerate(IngredientTypes):
                
                if item_name == key or item_name == 'empty':
                    self.IngredientSum[item_sum] = item_name
                        
                    with open(self.INGREDIENT_FP, 'a+') as f:
                        f.seek(0, 2)
                        f.write("%s:%s\n" % (item_sum, item_name))
                    break
            else:
                print("Ingredient name not found.")
                quit()
                
        else:
            self.IngredientSum[item_sum] = item_name
            with open(self.INGREDIENT_FP, 'a+') as f:
                f.seek(0, 2)
                f.write("%s:%s\n" % (item_sum, item_name))
        
        
        
    def input_console(self):
        self.CONSOLE_WINDOW.activate()
        return input()

        
    def start_game(self):

        #Start on preloader screen
        clickPos(Coor.preload_continue)
        
        print('Waiting for intro to finish...')
        print('')
        print('=========')
        print('If the intro has finished but the script does not detect it,')
        print('the window is misaligned. You will need to update the')
        print('X_PAD and Y_PAD game coordinates and restart the script.')
        print('=========')
        print('')
        
        while sumArea(Area.mm_play) != GUISum.play_button:
            time.sleep(2)

        #Check sound
        self.check_sound()
        
        #Click Play
        clickPos(Coor.mm_play)
        
        # Transition delay
        time.sleep(1.2)
        
        #Select save
        is_first_day = self.select_save()
        
        #Game begins here
        self.main_loop(is_first_day)
        
    def main_loop(self, is_first_day = False):
        while True:
            self.gameplay_loop(is_first_day)
            is_first_day = False
            self.start_next_day()