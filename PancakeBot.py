# Python 3.8.2
# Last updated 09/11/2020 (MM/DD/YYYY)
# By StrayPyramid

# Implemented task priority
# Implemented drinks machine and drinks order interpretation

import time, os, math, sys
from PIL import ImageOps, ImageGrab
import win32api, win32con, win32gui
import numpy as np
from enum import Enum

from rect import *
from constants import *
from key_codes import *

# Current max rank
# 14
# Reason: Drinking making mechanic not implemented into code.

IngredientSum = {}
ToppingCounts = {}

#Pancake cook time: 33 seconds, 16 seconds for first day

INGREDIENT_FP = "item_sums.txt"

FIRST_DAY_COOK_TIME = 16
DEFAULT_COOK_TIME = 34
cook_time = 0

#Getting the handler of the active python console
console_handle = win32gui.GetForegroundWindow()
IMAGE_SUM_DEBUG = False

STATION = Enum('STATION', 'ORDER GRILL BUILD DRINK')
PHASE = Enum('PHASE', 'WAITING COOKING COOKED BUILT')
current_station = STATION.ORDER

# Code Starts Here.
#------------------------------------------

def grabArea(rect):
    rect = Rect(rect)
    rect.translate(Coor.X_PAD, Coor.Y_PAD)
    
    im = ImageGrab.grab((rect.left(), rect.top(), rect.right(), rect.bottom()))
    return im

def sumArea(rect):
    #rect: Xpos, YPos, Width, Height
    im = ImageOps.grayscale(grabArea(rect))
    a = np.array(im.getcolors())
    a = a.sum()
    if IMAGE_SUM_DEBUG: print(rect, ":", a)
    return a    
    
def saveArea(rect):
    im = grabArea(rect)
    sum = sumArea(rect)
    im.save("./"+str(sum)+".png", 'PNG')

def pressKey(k):
    win32api.keybd_event(VK_CODE[k], 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[k],0 ,win32con.KEYEVENTF_KEYUP ,0)

def holdKey(k):
    win32api.keybd_event(VK_CODE[k], 0)
    time.sleep(.05)
    
def releaseKey(k):
    win32api.keybd_event(VK_CODE[k],0 ,win32con.KEYEVENTF_KEYUP ,0) 
    time.sleep(.05)
    
def upperKey(k):
    win32api.keybd_event(VK_CODE['shift'], 0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE[k], 0)
    win32api.keybd_event(VK_CODE[k],0 ,win32con.KEYEVENTF_KEYUP ,0)
    time.sleep(.05)
    win32api.keybd_event(VK_CODE['shift'],0 ,win32con.KEYEVENTF_KEYUP ,0)

def writeString(string):
    for char in string:
        if char == ' ':
            pressKey('spacebar')
        elif char == '!':
            upperKey('1')
        elif char.isupper():
            upperKey(char.lower())
        else:
            pressKey(char)  
            
def mousePos(cord):
    win32api.SetCursorPos((cord[0] + Coor.X_PAD, cord[1] + Coor.Y_PAD))
    
def leftClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def leftDown():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(.1)

def leftUp():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(.1)

def clickPos(cord):
    #print("CLICK", cord)
    mousePos(cord)
    leftClick()

def set_foreground_window(handle):
    win32gui.SetForegroundWindow(handle)
    

def check_sound():
    
    set_foreground_window(console_handle)
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
        check_sound()

def select_save():
    
    # Select the save number
    set_foreground_window(console_handle)    
    while True:
        save_slot = input("Which slot? (1 - 3)")
        if save_slot not in ('1', '2', '3'):
            print ('Pick a proper slot!')
        else:
            break
    
    # If the slot is empty, start a new game
    if sumArea(Area.mm_delete_slot[save_slot]) == GUISum.empty_slot:
        new_game(save_slot)
        return True
    
    # Slot already has a save
    print ('This slot already has a save')
    while True:
        set_foreground_window(console_handle)
        choice = input("Continue or Delete? \n")
        if choice[0].lower() == 'c':
            return continue_from_save(save_slot)
            
        elif choice[0].lower() == 'd':
            print ('Deleting...')
            clickPos(Coor.mm_delete_slot[save_slot])
            time.sleep(.5)
            clickPos(Coor.mm_erasegmcnfm[save_slot])
            time.sleep(.5)
            clickPos(Coor.mm_slot[save_slot])
            new_game(save_slot)
            return True
        else:
            print ("I don't understand!")
            

def continue_from_save(slot):
    print ('Continuing from save...')
    clickPos(Coor.mm_slot[slot])
    time.sleep(1)
    clickPos(Coor.mm_resume_save)
    
    
    #sometimes can skip green continue button for loading
    print ('Loading level...')
    time.sleep(1)
    if sumArea(Area.load_continue) == GUISum.load_loading:
        while sumArea(Area.load_continue) != GUISum.load_continue:
            time.sleep(1)
        clickPos(Coor.preload_continue) 
    
    print("WHILE LOOP")
    
    time.sleep(6)
    dayStart_sum = sumArea(Area.day_number)
    print("NOW")

    if dayStart_sum == GUISum.dayStart_tutorial:
        print ('It is the first day, a tutorial needs completing')
        print ('Waiting for cutscene to finish...')
        while sumArea(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)
        do_tutorial()
        return True
    else:
        print ('It is not the first day')
        print ('Waiting for cutscene to finish...')
        while sumArea(Area.menu_btn) != GUISum.menu_btn:
            time.sleep(2)
        print ("Let's go!")
        return False        


def get_gender():
    while(True):
        gender = input('Male or female?')[0].lower()
        if gender == "m" or gender == 'f':
            return gender
        
def new_game(save_slot):
    clickPos(Coor.mm_slot[save_slot])
    
    set_foreground_window(console_handle)
    gender = get_gender()

    if gender == 'm':
        clickPos(Coor.char_male)
    elif gender == 'f':
        clickPos(Coor.char_female)
            
    while True:
        try:
            set_foreground_window(console_handle)
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
    do_tutorial()



def change_station(station):
    global current_station
    if station == current_station:
        return
    
    if station == STATION.ORDER:
        clickPos(Coor.s_order)
    elif station == STATION.GRILL:
        clickPos(Coor.s_grill)
    elif station == STATION.BUILD:
        clickPos(Coor.s_build)
    elif station == STATION.DRINK:
        clickPos(Coor.s_drink)
    else:
        raise Exception("Tried to switch to non-existent station with ID:", station)
        
    current_station = station
        
    print("Changing to station ", STATION(station).name)
    
    #Time it takes to transition between stations
    time.sleep(.5)
    
def take_order():
    wait_for_order()
    return interpret_order()
    
    
def wait_for_order():
    time.sleep(.4)
    clickPos(Coor.take_order)
    print ('Taking an order...')
    time.sleep(1)
    screen = sumArea(Area.order_wait)
    while sumArea(Area.order_wait) == screen:
        time.sleep(1)
    

def move_order_to_line(order):
    mousePos(Coor.line_active)
    leftDown()
    mousePos((Coor.line_first_slot[0] + (Coor.line_spacing * order.id), Coor.line_first_slot[1]))
    leftUp()
        
def do_tutorial():
    
    grill = GrillStation()
    
    #wait until intro sequence is finished
    print ('Waiting for cutscene to finish...')
    while sumArea(Area.menu_btn) != GUISum.menu_btn:
        time.sleep(2)   
        
    print ("Tutorial Time!")
    
    #click on grill station
    change_station(STATION.GRILL)
    
    #click on build station
    change_station(STATION.BUILD)
    
    #click on order station
    change_station(STATION.ORDER)
    
    #take order, wait for order to complete
    print("Waiting for customer...")
    while sumArea(Area.order_floor) == GUISum.order_floor: #empty floor
        time.sleep(1)
    
    print ('Customer is ready!')
    wait_for_order()
        
    #drag ticket to ticket line
    mousePos(Coor.line_active)
    leftDown()
    mousePos(Coor.line_first_slot)
    leftUp()
    
    #click on grill station
    change_station(STATION.GRILL)
    
    #drag order to active order
    mousePos(Coor.line_first_slot)
    leftDown()
    mousePos(Coor.line_active)
    leftUp()
    
    #do pancakes
    grill.place_ingredient('grill', 'pancake', 5)
    time.sleep(.1)
    grill.place_ingredient('grill', 'pancake', 6)
        
    #Wait until 16 seconds have passed, then flip pancakes
    print('Waiting for pancakes to cook...')
    time.sleep(18)
            
    grill.flip('grill', 5)
    time.sleep(.1)
    grill.flip('grill', 6)
    
    print('Pancakes Flipped')
    #Wait until 16 seconds have passed, then drag pancakes to green tick.
    time.sleep(18)
    
    grill.finish_cooking('grill', 5)
    time.sleep(.1)
    grill.finish_cooking('grill', 6)
    
    #click on build station
    change_station(STATION.BUILD)
    
    #drag pancakes to build area
    grill.add_base()
    time.sleep(.5)
    grill.add_base()
    
    #drag 3 butter pads to 3 elliptic points on the pancake
    #maximum distribution.
    grill.spread_topping('butterpad', 3)

    #drag and release blueberries in circle path
    grill.spread_topping('blueberry')

    #blue and release blueberry sauce in circle path
    grill.spread_topping('blueberry_sauce')
    
    #click finish
    time.sleep(1)
    clickPos(Coor.build_finish)
    time.sleep(1)
    
    #drag ticket to finish tray
    mousePos(Coor.line_active)
    leftDown()
    time.sleep(.5)
    mousePos(Coor.build_tray)
    leftUp()
    
    #wait until back at build station
    print ('Waiting for customer...')
    while sumArea(Area.pancake_tray) != GUISum.pancake_tray:
        time.sleep(1)
    
    #click on order station
    change_station(STATION.ORDER)
    
    #END
    print('TUTORIAL COMPLETE!')
       
        
def interpret_order():
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
            drink = interpret_drink()
            continue
        
        # If sum doesn't exist, prompt the user for name and add it
        if sum not in IngredientSum:
            add_ingredient(sum, slot)
        
        # If ticket slot is empty, no action required
        if IngredientSum[sum] == 'empty':
            print('Slot '+str(slot+1)+' is empty')
            continue
  
        # If regular slot, lookup and process
        ingredient = IngredientSum[sum]
        print('Found '+ingredient)
        
        ingred_type = IngredientTypes[ingredient][0]
        
        print(ingred_type)
        if ingred_type == 'topping':
            rect = Rect(Area.ticket_toppingNum)
            rect.translate(0, -Area.ticket_spacing * slot)
            countSum = sumArea(rect)
            print(countSum)
            if countSum in ToppingCounts:
                topping_count = ToppingCounts[countSum]
                print(topping_count, "pieces of", ingredient)
            else:
                print ('Toppping count sum not found for slot ' + str(slot+1) + ', Sum: ' + str(countSum))
                print ('Please write the number of toppings required.')
                topping_count = int(input())
                add_topping_count(countSum, topping_count)
                
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
    
def interpret_drink():
    d_flavour = None
    d_size = None
    d_base = None
    
    # Left slot - drink flavour
    sum = sumArea(Area.t_d_flavour)
    if sum not in IngredientSum:
        print("DRINK FLAVOUR NOT FOUND")
        add_ingredient(sum, 7, drink=True)
    
    d_flavour = IngredientSum[sum]
    
    # Middle slot - drink size
    sum = sumArea(Area.t_d_size)
    if sum not in IngredientSum:
        print("DRINK SIZE NOT FOUND")
        add_ingredient(sum, 7, drink=True)
    
    d_size = IngredientSum[sum]
    
    # Right slot - drink base
    sum = sumArea(Area.t_d_additional)
    if sum not in IngredientSum:
        print("DRINK ADDITIONAL NOT FOUND")
        add_ingredient(sum, 7, drink=True)
    
    d_add = IngredientSum[sum]

    return Drink(d_flavour, d_size, d_add)
    
        
class Order():
    
    def __init__(self, ingredients, grillsNeeded, ironsNeeded, drink = None):
        self.ingredients = ingredients
        self.num_of_grills = grillsNeeded
        self.num_of_irons = ironsNeeded
        self.drink = drink
        self.drink_made = False
        
        self.phase = PHASE.WAITING
        self.flipped = False
        self.id = -1
        
        self.cook_start_time = 0
    
    
        self.allocated_grills = []
        self.allocated_irons = []
    
    def has_drink(self):
        return self.drink != None
    
    def ready(self):
        return (self.drink == None or self.drink_made is True) and self.phase is PHASE.BUILT
    

class GrillStation():
    
    grills = [True, True, True, True, True, True, True, True]
    irons = [True, True, True, True]
    finished_queue = []
    
    def __init__(self, cook_time = DEFAULT_COOK_TIME):
        self.cook_time = cook_time
        
    def can_do_order(self, order):
        #if the number of grills and irons available is greater than the required from order info, return true
        if self.grills.count(True) >= order.num_of_grills and self.irons.count(True) >= order.num_of_irons:
            return True
        return False
        
    def do_order(self, order):
        change_station(STATION.GRILL)
        #place batters on grill, and the extras        
        
        self.allocate_grills(order)
        self.allocate_irons(order)
        
        print(order.allocated_grills)
        print(order.allocated_irons)
        
        grill_it = 0
        iron_it  = 0
        
        for ingredient in order.ingredients:
            
            ingredient_name = ingredient[0]
            if ingredient_name not in ('pancake', 'french', 'waffle'):
                continue
                
            if len(ingredient) == 2:
                topping = ingredient[1]
            else:
                topping = None
            
            if ingredient_name in ('pancake', 'french'):
                grill_slot = order.allocated_grills[grill_it]
                grill_it += 1
                self.place_ingredient('grill', ingredient_name, grill_slot)
                if topping is not None:
                    self.place_ingredient('grill', topping, grill_slot)
            
            if ingredient_name in ('waffle'):
                iron_slot = order.allocated_irons[iron_it]
                iron_it += 1
                self.place_ingredient('iron', ingredient_name, iron_slot)
                if topping is not None:
                    self.place_ingredient('iron', topping, iron_slot)
        
        order.cook_start_time = time.time()
        order.phase = PHASE.COOKING
        print("Order %s has started cooking" % order.id)
        
    def check_orders(self, orders):
        for order in orders:
            if order.phase != PHASE.COOKING:
                continue
        
            if order.cook_start_time + self.cook_time <= time.time():
                #Go to grill
                change_station(STATION.GRILL)
                
                if order.flipped == False:
                #Flip Pancakes
                    print ('Flipping order '+str(order.id))
                    for slot in order.allocated_grills:
                        self.flip('grill', slot)
                    for slot in order.allocated_irons:
                        self.flip('iron', slot)
                    order.cook_start_time = time.time()
                    order.flipped = True

                elif order.flipped == True:
                #Pancakes are cooked
                    print("Order", str(order.id), "has finished cooking")
                    for slot in order.allocated_grills:
                        self.finish_cooking('grill', slot)
                        self.grills[slot] = True
                    for slot in order.allocated_irons:
                        self.finish_cooking('iron', slot)
                        self.irons[slot] = True
                        
                    order.phase = PHASE.COOKED
                    self.finished_queue.append(order.id)
                
    def flip(self, type, slot):
        if(type == 'grill'):
            clickPos(Coor.grill[slot])
        elif(type == 'iron'):
            clickPos(Coor.iron[slot])
    
    def allocate_grills(self, order):
        allocated_grills = []
        
        for i in range(0, 8):
            if len(allocated_grills) == order.num_of_grills:
                break
            if self.grills[i] == True:
                allocated_grills.append(i)
                self.grills[i] = False
            
                
        order.allocated_grills = allocated_grills

    def allocate_irons(self, order):
        allocated_irons = []
        
        for i in range(0, 4):
            if len(allocated_irons) == order.num_of_irons:
                break
            if self.irons[i] == True:
                allocated_irons.append(i)
                self.irons[i] = False
            
                
        order.allocated_irons = allocated_irons
    
    @staticmethod
    def place_ingredient(type, ingredient, slot):
        print ('Placing '+ingredient+' on '+type+' at slot '+str(slot))
        mousePos(IngredientTypes[ingredient][1])
        time.sleep(.4)
        leftDown()
        if type == 'grill':
            mousePos(Coor.grill[slot])
        elif type == 'iron':
            mousePos(Coor.iron[slot])
        time.sleep(.1)
        leftUp()    
    
    @staticmethod
    def finish_cooking(type, slot):
        if type == 'grill':
            mousePos(Coor.grill[slot])
        elif type == 'iron':
            mousePos(Coor.iron[slot])
        leftDown()
        time.sleep(.1)
        mousePos(Coor.gril_confirm)
        leftUp()
        time.sleep(.1)
    

    
    def pancakes_ready(self):
        #print("%s pancake orders ready" % len(self.finished_queue))
        return len(self.finished_queue) != 0

class Drink():
    def __init__(self, flavour, size, additional):
        self.flavour = flavour
        self.size = size
        self.additional = additional
    
    def __repr__(self):
        return "<Drink %s %s %s>" % (self.flavour, self.size, self.additional)
        
    def __str__(self):
        return "<Drink %s %s %s>" % (self.flavour, self.size, self.additional)
    
class DrinksStation():

    def make_drink(self, order):
        is_tutorial = False
        
        if order.drink is None:
            print("Order has no drink!")
            return
    
        drink = order.drink
        change_station(STATION.DRINK)
        time.sleep(1)
        
        if sumArea(Area.drink_check) == GUISum.drinks_tutorial:
            print("TUTORIAL_DETECT")
            is_tutorial = True
        
        # Flavour
        print("FLAVOUR")
        clickPos(Coor.d_flav[drink.flavour]) 
        time.sleep(.3)
        
        # Cup size
        print("CUP SIZE")
        clickPos(Coor.d_size[drink.size])
        time.sleep(.7)
        
        # Timing click
        print("POUR")
        clickPos(Coor.d_pour_btn)
        time.sleep(.2)
        clickPos(Coor.d_pour_btn)
        time.sleep(3)
        
        # Milk
        print("ADDITIONAL")
        clickPos(Coor.d_add[drink.additional])
        time.sleep(.55)
        
        # Timing click
        print("POUR")
        clickPos(Coor.d_pour_btn)
        
        if is_tutorial:
            time.sleep(2)
            clickPos(Coor.d_my_drinks)
            time.sleep(.5)
            clickPos(Coor.d_my_drinks)
        
        order.drink_made = True

class BuildStation():
    
    def __init__(self):
        self.order_ready = False
        self.active_order = None
        self.drink_queue = []
    
    
    def build_pancake(self, order):
        if self.order_ready:
            print("Cannot make pancake, another is ready to serve")
            return
        
        print("Building Pancake for order %s" % order.id)
        
        #Go to build station
        change_station(STATION.BUILD)

        #build pancake
        for ingredient in order.ingredients:
            
            item_name = ingredient[0]
            item_count = ingredient[1] if len(ingredient) == 2 else None
            item_type = IngredientTypes[item_name][0]
            
            if item_type == 'bread' or item_type == 'waffle':
                self.add_base()
                time.sleep(.1)
            elif item_type == 'topping':
                self.spread_topping(item_name, item_count)
            else:
                self.spread_topping(item_name)
        
        #Wait for animations to finish
        time.sleep(.5)
        order.phase = PHASE.BUILT
        self.order_ready = True
        self.active_order = order
        
    
    def serve_pancake(self):        
        
        order_id = self.active_order.id
        
        change_station(STATION.BUILD)

        # Finish
        clickPos(Coor.build_finish)
        time.sleep(.2)
        
        # Place drink
        if self.active_order.has_drink() and self.active_order.drink_made:
            drink_i = self.drink_queue.index(order_id)
            drink_coor = Coor.drink_rack[drink_i]
            self.drink_queue.remove(order_id)
            
            time.sleep(1)
            mousePos(drink_coor)
            leftDown()
            mousePos(Coor.build_tray)
            leftUp()
        
        # Give to customer
        self.move_ticket_to_tray(order_id)

        #wait until back at build station
        print('Waiting for customer...')
        while sumArea(Area.pancake_tray) != GUISum.pancake_tray:
            time.sleep(1)
            #Check if day end
            if sumArea(Area.flipline_logo) == GUISum.flipline_logo:
                return 0, True
        
        
        self.active_order = None
        self.order_ready = False
        
        return order_id, False

    def move_ticket_to_tray(self, order_id):
        mousePos((Coor.line_first_slot[0] + (Coor.line_spacing * order_id), Coor.line_first_slot[1]))
        leftDown()
        mousePos(Coor.build_tray)
        leftUp()
        
    def add_drink(self, order):
        self.drink_queue.append(order.id)
    
    @staticmethod
    def get_point_in_ellipse(x,y,deg):
        # xPos = x cos t
        # yPos = y sin t
        xPos = x * (math.cos(math.radians(deg)))
        yPos = y * (math.sin(math.radians(deg)))
        return (int(math.floor(xPos)), int(math.floor(yPos)))
    
    @staticmethod
    def add_base():
        mousePos(Coor.build_base)
        leftDown()
        mousePos((Coor.build_center[0] - 20, Coor.build_center[1]))
        leftUp()
            
    def spread_topping(self, name, points=20):
        
        if IngredientTypes[name][0] == 'topping':
            #Step 1: Get number of toppings
            toppings_num = points
            if toppings_num == 1:
                mousePos(IngredientTypes[name][1])
                leftDown()
                mousePos(Coor.build_center)
                time.sleep(.2)
                leftUp()
            else:
                #Step 2: Divide 360 degrees by number of toppings
                increment = 360 / toppings_num
                #Step 3: Hope.
                for x in range(1, toppings_num+1):
                    mousePos(IngredientTypes[name][1])
                    leftDown()
                    time.sleep(.1)
                    x, y = self.get_point_in_ellipse(45, 45, x*increment)
                    #print ('Placing topping at '+str(x)+', '+str(y)+' from pancake center')
                    mousePos((Coor.build_center[0]+x, Coor.build_center[1]+y))
                    time.sleep(.1)
                    leftUp()
                
        else:
            points  = int(IngredientTypes[name][2] / 0.1)
            increment = 360 / points
            mousePos(IngredientTypes[name][1])
            leftDown()
            for x in range(1, points+1):
                time.sleep(.1)
                x, y = self.get_point_in_ellipse(45, 45, x*increment)
                #print ('Placing sprinkle/sauce at '+str(x)+', '+str(y)+' from pancake center')
                mousePos((Coor.build_center[0]+x, Coor.build_center[1]+y))
                leftUp()
            #Buffer
            time.sleep(.2)
    
def get_order_by_id(orders, id):
    for order in orders:
        if order.id == id:
            return order
    
    return None
    
def get_ticketLineNum(orders):
    for i in range(0, 12):
        if get_order_by_id(orders, i) == None:
            return i
            
def main_loop(is_first_day):

    orders = []
    store_closed = False
    
    #One the first day, cooking time is halved due to the tutorial.
    if is_first_day:
        cook_time = FIRST_DAY_COOK_TIME
    else:
        cook_time = DEFAULT_COOK_TIME
    print ('Cooking time set to %s seconds' % cook_time)
    
    grill_station = GrillStation(cook_time)
    build_station = BuildStation()
    drinks_station = DrinksStation()
    
    #Main loop goes here.
    print ("MAIN LOOP BEGINNING")
    
    #Avoiding the problems of the blue ribbon
    #TODO Add detection for blue ribbon to prevent station switching every single day
    time.sleep(.5)
    change_station(STATION.GRILL)
    
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
        if not store_closed:
            change_station(STATION.ORDER)
            if sumArea(Area.order_floor) != GUISum.order_floor and (len(orders) < 12):
                print ('Customer detected!')
                
                #Take order
                order = take_order()
                order.id = get_ticketLineNum(orders)
                move_order_to_line(order)
                orders.append(order)
                print ('Number of orders: '+str(len(orders)))
                
                # Check if the customer was a closer (CLOSED sign)
                # If so, no longer need to check for new customers
                if sumArea(Area.store_sign) == GUISum.closed_sign:
                    store_closed = True
                
                continue
        
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
            if order.phase == PHASE.WAITING:
                if grill_station.can_do_order(order):
                    grill_station.do_order(order)
                    started_order = True
                    
        if started_order: continue
        
        # 5. BUILD PANCAKE, YES    
        if grill_station.pancakes_ready() and not build_station.order_ready:
            order_id = grill_station.finished_queue.pop(0)
            order = get_order_by_id(orders, order_id)
            
            build_station.build_pancake(order)
            
            continue

        # 6. Serve pancake  
        # Day finishes when the last order is served
        if build_station.order_ready:
            order_id, day_finished = build_station.serve_pancake()
            
            if day_finished:
                print ('Level complete')
                orders.clear()
                return
                
            # Remove order from orders
            for order in orders:
                if order.id == order_id:
                    orders.remove(order)
                    break
        
def start_next_day():

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
    
    
    
def startBot():

    #Start on preloader screen
    clickPos(Coor.preload_continue)
    
    print('Waiting for intro to finish...')
    while sumArea(Area.mm_play) != GUISum.play_button:
        time.sleep(2)

    #Check sound
    check_sound()
    
    #Click Play
    clickPos(Coor.mm_play)
    
    #Select save
    is_first_day = select_save()
    
    #Game begins here, at the point where customers are coming into your store
    game_loop(is_first_day)
    
def game_loop(is_first_day = False):
    while True:
        main_loop(is_first_day)
        is_first_day = False
        start_next_day()
    
def load_items():
    global IngredientSum
    global ToppingCounts
    
    with open(INGREDIENT_FP, 'r') as f:
        for line in f:
            i_data = line.strip()
            if(i_data) == '': return # EOF
            
            item_sum, item_name = i_data.split(":")
            item_sum = int(item_sum)
            
            if item_name[:-1] == "item_count_":
                topping_count = int(item_name[-1])
                ToppingCounts[item_sum] = topping_count
            else:
                IngredientSum[item_sum] = item_name

def add_topping_count(topping_sum: int, topping_count: int):
    global ToppingCounts

    with open(INGREDIENT_FP, 'a+') as f:
        f.seek(0, 2)
        f.write("%s:item_count_%s\n" % (topping_sum, topping_count))
    
    ToppingCounts[topping_sum] = topping_count
    
    
def add_ingredient(item_sum: int, slot: int, drink=False):
    global IngredientSum
    
    print('Found unregisterd ingredient')
    print('Slot: '+str(slot+1))
    print('Sum: '+str(item_sum))    
    print("Please enter ingredient name")
    
    item_name = input_console()
    
    if drink is False:
        for _,key in enumerate(IngredientTypes):
            
            if item_name == key or item_name == 'empty':
                IngredientSum[item_sum] = item_name
                    
                with open(INGREDIENT_FP, 'a+') as f:
                    f.seek(0, 2)
                    f.write("%s:%s\n" % (item_sum, item_name))
                break
        else:
            print("Ingredient name not found.")
            quit()
            
    else:
        IngredientSum[item_sum] = item_name
        with open(INGREDIENT_FP, 'a+') as f:
            f.seek(0, 2)
            f.write("%s:%s\n" % (item_sum, item_name))
    
    
    
def input_console():
    set_foreground_window(console_handle)
    return input()
   
if __name__ == "__main__":
    load_items()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'io':
            interpret_order()
        elif sys.argv[1] == 'continue_first':
            game_loop(is_first_day = True)
        elif sys.argv[1] == 'continue':
            game_loop()
        elif sys.argv[1] == 'load':
            print(IngredientSum)
            print(ToppingCounts)
    
    else:
        startBot()



    

    

