import time, math
import numpy as np
from scipy.integrate import quad, solve_ivp

from src.topping import Toppings

from ..constants.constants import *
from ..win_control import *
from ..sum_area import *
from ..order import *
from ..station_changer import *

class BuildStation():
    
    def __init__(self, station_chngr):
        self.order_ready = False
        self.active_order = None
        self.drink_queue = []
        self.station = station_chngr
    
    
    def build_pancake(self, order):
        if self.order_ready:
            print("Cannot make pancake, another is ready to serve")
            return
        
        print("Building Pancake for order %s" % order.id)
        print(order.ingredients)
        
        #Go to build station
        self.station.change(STATION.BUILD)

        #build pancake
        for ingredient in order.ingredients:
            
            item_name = ingredient[0]
            item_type = IngredientTypes[item_name][0]
            
            if item_type in ('bread', 'waffle'):
                self.add_base()
            elif item_type == 'piece':
                item_count = ingredient[1]
                self.spread_topping(item_name, item_count)
            else:
                self.spread_sprinkle_or_sauce(item_name)
        
        #Wait for animations to finish
        time.sleep(.5)
        order.phase = ORDER_PHASE.BUILT
        self.order_ready = True
        self.active_order = order
        
    
    def serve_pancake(self):        
        
        order_id = self.active_order.id
        
        self.station.change(STATION.BUILD)

        # Finish
        clickPos(Coor.build_finish)
        time.sleep(.2)
        
        # Place drink
        if self.active_order.has_drink() and self.active_order.drink_made:
            drink_i = self.drink_queue.index(order_id)
            BuildStation.place_drink(drink_i)
            self.drink_queue.remove(order_id)

        # Give to customer
        BuildStation.move_ticket_to_tray(order_id)
        
        self.active_order = None
        self.order_ready = False
        
        return order_id
 
    def add_drink(self, order):
        self.drink_queue.append(order.id)
 
    @staticmethod
    def place_drink(drink_i):
        drink_coor = Coor.drink_rack[drink_i]
        time.sleep(1)
        mousePos(drink_coor)
        leftDown()
        mousePos(Coor.build_tray)
        leftUp()
    
    @staticmethod
    def move_ticket_to_tray(order_id):
        mousePos((Coor.line_first_slot[0] + (Coor.line_spacing * order_id), Coor.line_first_slot[1]))
        leftDown()
        mousePos(Coor.build_tray)
        leftUp()
        
    
    @staticmethod
    def get_point_in_ellipse(x, y, theta):
        xPos = x * math.cos(math.radians(theta))
        yPos = y * math.sin(math.radians(theta))
        return int(math.floor(xPos)), int(math.floor(yPos))
        
    @staticmethod
    def get_point_in_flower(r_max, theta):
        r = r_max * math.cos((5/3) * math.radians(theta))
        x = r * math.cos(math.radians(theta))
        y = r * math.sin(math.radians(theta))
        
        return int(x), int(y)
    
    @staticmethod
    def get_point_in_spikey_flower(theta):
        petals = 6
        radius = -10
        
        fx = np.abs((35/np.pi) * (np.mod((petals*theta) - np.pi/2, 2*np.pi) - np.pi)) + 35

        x = (radius + fx) * math.cos(theta)
        y = (radius + fx) * math.sin(theta)
        
        return int(x), int(y)
    
    @staticmethod 
    def get_points_in_spiral(size, loops):
        points = 250
        theta = (2 * np.pi) / points
        
        point_list = []
        for i in range(0, points):
            x = size * (theta * i) * math.cos(theta * i * loops) * 0.9
            y = size * (theta * i) * math.sin(theta * i * loops)
            
            point_list.append((x, y))
        
        return point_list
    
    @staticmethod
    def add_base():
        mousePos(Coor.build_base)
        time.sleep(.1)
        leftDown()
        mousePos((Coor.build_center[0] - 20, Coor.build_center[1]))
        time.sleep(.1)
        leftUp(delay=0.1)
            
    @staticmethod
    def spread_topping(ingred_name: str, toppings_num=1):
        topping = Toppings.get(ingred_name)
        
        if(topping.type != 'piece'):
            raise Exception(f"{topping.name} is a {topping.type}, not a piece")
        
        if toppings_num == 1:
            # Place in the center
            mousePos(topping.location)
            leftDown()
            mousePos(topping.center)
            time.sleep(.2)
            leftUp()
            time.sleep(.2)
        else:
            increment = 360 / toppings_num
            if(toppings_num == 2 or toppings_num == 3):
                offset = 90
            elif(toppings_num == 4):
                offset = 45
            
            for i in range(0, toppings_num):
                mousePos(topping.location)
                leftDown()
                time.sleep(.1)
                x, y = BuildStation.get_point_in_ellipse(40, 40, (i*increment+offset))
                #print ('Placing topping at '+str(x)+', '+str(y)+' from pancake center')
                mousePos((topping.center[0]+x, topping.center[1]+y))
                time.sleep(.1)
                leftUp()
                
            time.sleep(.2)
    
    @staticmethod
    def spread_sprinkle_or_sauce(ingred_name):
        # Sprinkle or Sauce, flower pattern
        topping = Toppings.get(ingred_name)
            
        if(topping.type not in ('sauce', 'sprinkle')):
            raise Exception(f"{topping.name} is a {topping.type}, not a sauce or sprinkle")
        
        points = BuildStation.get_points_in_spiral(topping.size, topping.loops)
        
        mousePos(topping.location)
        leftDown()
        mousePos((topping.center[0] + points[0][0], topping.center[1] + points[0][1]))
        leftUp(delay=0)
        move_cursor_along_path(points, speed=topping.speed, offset=topping.center)
                    
        #Buffer
        time.sleep(.2)