class Coor:
    # Set to the top left pixel of the game window. 
    # Firefox browser with bookmark tab, scrolled to the top.
    X_PAD = 20
    Y_PAD = 347

    X_LIMIT = X_PAD + 640
    Y_LIMIT = Y_PAD + 480
    
    preload_continue = (565, 458)
    
    mm_play = (347, 351)
    mm_sound = (621, 362)
    
    mm_slot = {
        '1' : (129, 334),
        '2' : (319, 334),
        '3' : (513, 334)
    }
    
    mm_delete_slot = {
        '1' : (202, 76),
        '2' : (394, 76),
        '3' : (585, 76)
    }
    
    mm_erasegmcnfm = {
        '1' : (130, 250),
        '2' : (320, 250),
        '3' : (510, 250)
    }
    
    mm_resume_save = (305, 435)
    
    char_male = (215, 330)
    char_female = (414, 330)
    char_nameField = (313, 269)
    char_continue = (400, 315)
    
    intro_skip = (570, 445)
    
    s_order = (160, 455)
    s_grill = (265, 455)
    s_build = (380, 455)
    
    take_order = (150, 145)
    
    line_active = (560, 20)
    line_first_slot = (20, 10)
    line_spacing = 37

    #Grill Station controls
    gril_cancel = (60, 385)
    gril_confirm = (565, 390)
    
    #Grill Station grills
    grill = {
        0:(65, 205),
        1:(185, 205),
        2:(305, 205),
        3:(425, 205),
        4:(65, 290),
        5:(185, 290),
        6:(305, 290),
        7:(425, 290)
    }
    
    iron = {
        0:(65, 115),
        1:(185, 115),
        2:(305, 115),
        3:(430, 115)
    }
    
    #Build station controls
    build_base = (93, 305)
    build_center = (310, 225)   
    build_ticket = (170, 335)
    build_finish = (595, 395)
    
    #Day complete
    daycom_continue1 = (310, 445)
    daycom_skipslots = (254, 364)
    daycom_continue2 = (313, 450)
    daycom_continue3 = (570, 460)
    
class Rect:
    
    def __init__(self, *args, **kwargs):
        if (len(args) == 1) and type(args[0]) == tuple:
            arg = args[0]
            self._x = arg[0]
            self._y = arg[1]
            self._width = arg[2]
            self._height = arg[3]
        elif (len(args) == 4) and all(isinstance(x, int) for x in args):
            self._x = args[0]
            self._y = args[1]
            self._width = args[2]
            self._height = args[3]
        elif (len(args) == 1) and type(args[0]) == Rect:
            self._x = args[0].x()
            self._y = args[0].y()
            self._width = args[0].width()
            self._height = args[0].height()
        else:
            # Invalid input arguments
            types = " ".join([type(x).__name__ for x in args])
            raise Exception("Rect initalized with invalid type(s):", types)
    
    def __repr__(self):
        return "<Rect (%s, %s, %s, %s)>" % (self._x, self._y, self._width, self._height)
    
    def __str__(self):
        return "<Rect (%s, %s, %s, %s)>" % (self._x, self._y, self._width, self._height)
    
    def left(self):
        return self._x
    
    def right(self):
        return self._x + self._width
        
    def top(self):
        return self._y
    
    def bottom(self):
        return self._y + self._height
    
    def width(self):
        return self._width
    
    def height(self):
        return self._height
    
    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def setCoords(self, x1: int, y1: int, x2: int, y2: int):
        self._x = x1
        self._y = y1
        self._width = x2 - x1
        self._height = y2 - y1
        return self
    
    def setHeight(self, height: int):
        self._height = height
        return self
    
    def setRect(self, x: int, y: int, width: int, height: int):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        return self
        
    def setWidth(self, width: int):
        self._width = width
        return self
    
    def setX(self, x: int):
        self._x = x
        return self
    
    def setY(self, y: int):
        self._y = y
        return self
    
    def moveLeft(self, x: int):
        self._x = x
        return self
    
    def moveRight(self, x: int):
        self._x = x - self._width
        return self
    
    def moveTop(self, y: int):
        self._y = y
        return self
    
    def moveBottom(self, y: int):
        self._y = y - self._height
        return self
        
    def translate(self, dx: int, dy: int):
        self._x += dx
        self._y += dy
        return self
    
class Area:
    #Places which need Screengrab for the bot to see
    mm_sound = (620, 358, 9, 9)
    mm_play = (278, 338, 56, 28)
    
    #Save Slot delete button
    mm_delete_slot = {
        '1':(184, 61, 29, 21),
        '2':(376, 61, 29, 21),
        '3':(568, 61, 29, 21)
    }
    
    #Menu button in lower left when main game is running. Used as confirmation that a cut-scene has finished
    menu_btn = (17, 451, 41, 12)
    
    #Area of floor where new customers feet will be. Used to detect customers waiting for you to take their order
    order_floor = (120, 365, 20, 30)
    
    #Used to detect when customers have finished reviewing their pancake.
    pancake_tray = (300, 350, 20, 20)
    
    #Used to detect the end of the day
    flipline_logo = (14, 434, 78, 34)
    
    #Used to detect when day summary has finished
    continue1 = (245, 434, 121, 28)
    
    #Day Number, visible during store opening
    day_number = (300, 445, 37, 23)
    
    #Day Title, accompanies day number, used to check when day number is fully visible
    day_title = (284, 418, 66, 4)
    
    # Used to detect when a customer has finished ordering
    order_wait = (540, 360, 60, 30)
    
    #Continue Area on game load, used to detect when the game is finished loading
    load_continue = (550, 440, 4, 35)
    load_screen = (480, 440, 4, 35)
    
    # Order ticket box, and spacing between them
    ticket_section = (513, 267, 45, 10)
    ticket_toppingNum = (562, 267, 45, 10)
    ticket_spacing = 30
    
IngredientTypes = {
    # name: type, coordinate, timeToPour
    
    'pancake':              ['bread', (256, 384)],
    'french':               ['bread', (357, 376)],
    'waffle':                   ['waffle', (256, 384)],
        
    'blueberry_pancake':['combo', 'pancake', 'blueberry_mix'],
    'blueberry_french': ['combo', 'french', 'blueberry_mix'],
    'blueberry_waffle': ['combo', 'waffle', 'blueberry_mix'],
        
    'chocolate_pancake':['combo', 'pancake', 'chocolate_mix'],
    'chocolate_french': ['combo', 'french', 'chocolate_mix'],
    'chocolate_waffle': ['combo', 'waffle', 'chocolate_mix'],
    
    'pecan_pancake':        ['combo','pancake','pecan_mix'],
    'pecan_french':     ['combo','french','pecan_mix'],
    'pecan_waffle':     ['combo','waffle','pecan_mix'],
    
    #Bacon. What? Who puts bacon in their pancakes?
    'bacon_pancake':        ['combo','pancake','bacon_mix'],
    'bacon_french':     ['combo','french','bacon_mix'],
    'bacon_waffle':     ['combo','waffle','bacon_mix'],
    
    'blueberry_mix':        ['mix', (435, 395)],
    'chocolate_mix':        ['mix', (180, 398)],
    'pecan_mix':            ['mix', (462, 355)],
    'bacon_mix':            ['mix', (149, 355)],
    
    'butterpad':            ['topping', (445, 235)],
    'banana':               ['topping', (445, 315)],
    'strawberry':           ['topping', (445, 275)],
    
    'blueberry':                ['sprinkle', (175, 235), 2.1],
    'choc_chip':            ['sprinkle', (172, 283), 3],
    'raspberry':             ['sprinkle', (177, 326), 2],
    'cinnamon':             ['sprinkle', (441, 192), 2.1],
    'sugar':                    ['sprinkle', (175, 198), 2.2],
    
    'blueberry_sauce':  ['sauce', (155, 140), 2],
    'hot_sauce':            ['sauce', (420, 140), 2],
    'whipped_cream':    ['sauce', (195, 133), 1.7],
    'honey':                    ['sauce', (467, 133), 2]
    
}
# IngredientType, (CoorX, CoorY), TimeToApply
#Time it takes to apply = more points on circle


