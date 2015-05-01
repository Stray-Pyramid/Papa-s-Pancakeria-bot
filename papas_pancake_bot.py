import time
import os
import math
from sys import exit
from PIL import ImageOps
import win32api, win32con, win32gui
from numpy import *

from desktopmagic.screengrab_win32 import (getDisplayRects,getScreenAsImage,getRectAsImage)

# Current max day
# 17

# TODO
# --------------
# 1. pancake/waffle mixables (Blueberry)
# 2. Drink making :(
# 3. Finish ingredient coordinates / ingredient sums
# 4. Handle game won scenario

# Globals
# -----------------

x_pad = 480
y_pad = 329

x_limit = x_pad + 640
y_limit = y_pad + 480

#Pancake cook time: 33 seconds, 16 seconds for first day
def_pancake_cook_time = 34
first_day = False

orders = {}
waitingOrders = []

grillGroups = {}
grills = {1:True,2:True,3:True,4:True,5:True,6:True,7:True,8:True}
irons = {1:True,2:True,3:True,4:True}

#Getting the handler of the active python console
console_handle = win32gui.GetForegroundWindow()

class Coor:
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
	
	ordr_active = (560, 20)
	ordr_slot1 = (20, 10)

	#Grill Station controls
	gril_cancel = (60, 385)
	gril_confirm = (565, 390)
	
	#Grill Station grills
	grill = {
		1:(65, 205),
		2:(185, 205),
		3:(305, 205),
		4:(425, 205),
		5:(65, 290),
		6:(185, 290),
		7:(305, 290),
		8:(425, 290)
	}
	
	iron = {
		1:(65, 115),
		2:(185, 115),
		3:(305, 115),
		4:(430, 115)
	}
	
	#Build station controls
	build_base = (93, 305)
	build_center = (310, 225)	
	build_tickt = (170, 335)
	build_finish = (595, 395)
	
	#Day complete
	daycom_continue1 = (310, 445)
	daycom_skipslots = (254, 364)
	daycom_continue2 = (313, 450)
	daycom_continue3 = (570, 460)
	
class Area:
	#Places which need Screengrab for the bot to see
	mm_sound = (x_pad+620, y_pad+358, x_pad+629, y_pad+367)
	mm_play = (x_pad+278, y_pad+338, x_pad+278+56, y_pad+338+28)
	
	#Save Slot delete button
	mm_delete_slot = {
		'1':(x_pad+184, y_pad+61, x_pad+184+29, y_pad+61+21),
		'2':(x_pad+376, y_pad+61, x_pad+376+29, y_pad+61+21),
		'3':(x_pad+568, y_pad+61, x_pad+568+29, y_pad+61+21)
	}
	
	#Menu button in lower left when main game is running. Used as confirmation that a cut-scene has finished
	menu_btn = (x_pad+17, y_pad+451, x_pad+17+41, y_pad+451+12)
	
	#Area of floor where new customers feet will be. Used to detect customers waiting for you to take their order
	order_floor = (x_pad+120, y_pad+365, x_pad+120+20, y_pad+365+30)
	
	#Used to detect when customers have finished reviewing their pancake.
	pancake_tray = (x_pad+300, y_pad+350, x_pad+300+20, y_pad+350+20)
	
	#Used to detect the end of the day
	flipline_logo = (x_pad+14, y_pad+434, x_pad+14+78, y_pad+434+34)
	
	#Used to detect when day summary has finished
	continue1 = (x_pad+245, y_pad+434, x_pad+245+121, y_pad+434+28)
	
	#Day Number, visible during store opening
	day_number = (x_pad+300, y_pad+445, x_pad+300+37, y_pad+445+23)
	
	#Day Title, accompanies day number, used to check when day number is fully visible
	day_title = (x_pad+284, y_pad+418, x_pad+284+66, y_pad+418+4)
	
	#Continue Area on game load, used to detect when the game is finished loading
	load_continue = (x_pad+550, y_pad+440, x_pad+550+4, y_pad+440+35)
	load_screen = (x_pad+480, y_pad+440, x_pad+480+4, y_pad+440+35)
	
IngredientTypes = {
	# name: type, coordinate, timeToPour
	'pancake':				['bread', (256, 384)],
	'french': 				['bread', (357, 376)],
	'waffle':					['waffle', (256, 384)],
	
	'butterpad':			['topping', (445, 235)],
	'banana':				['topping', (445, 315)],
	'strawberry':			['topping', (445, 275)],
	
	'blueberry':				['sprinkle', (175, 235), 2.1],
	'choc_chip':			['sprinkle', (172, 283), 3],
	'rasberry':				['sprinkle', (177, 326), 2],
	'cinnamon':				['sprinkle', (441, 192), 2.1],
	'sugar':					['sprinkle', (175, 198), 2.2],
	
	'blueberry_sauce':	['sauce', (155, 140), 2],
	'hot_sauce':			['sauce', (420, 140), 2],
	'whipped_cream':	['sauce', (195, 133), 1.7],
	'honey':					['sauce', (467, 133), 2]
	
}

#Time it takes to apply = more points

IngredientSums = {
	# sum : name, type
	14203:'pancake',
	14372:'pancake',
	16683:'pancake',
	
	14087:'french',
	15671:'french',
	
	14170:'waffle',
	14309:'waffle',
	16360:'waffle',
	
	16526:'butterpad',
	17343:'butterpad',
	17360:'butterpad',
	17126:'butterpad',

	16234:'banana',
	16429:'banana',
	17075:'banana',
	
	12145:'strawberry',
	14174:'strawberry',
	
	11967:'blueberry',
	10324:'blueberry',
	
	9468:'choc_chip',
	11157:'choc_chip',

	8495:'rasberry',
	10176:'rasberry',
	
	16764:'sugar',
	
	13827:'cinnamon',
	16045:'cinnamon',
	
	15240:'blueberry_sauce',
	19035:'blueberry_sauce',
	15393:'blueberry_sauce',

	18249:'whipped_cream',
	18988:'whipped_cream',
	
	14213:'hot_sauce',	
	14738:'hot_sauce',
	18600:'hot_sauce',
	
	18086:'honey'
}
	
	
Counts = {
	9838 : 1,
	8511: 1,
	17360 : 1,
	
	13693: 2,
	11560: 2,
	
	12493 : 3,
	16526: 3,
	14421: 3,
	
	9840 : 4,
	11188 : 4
}
	
VK_CODE = {
		   '!':0x2,
		   'backspace':0x08,
           'tab':0x09,
           'clear':0x0C,
           'enter':0x0D,
           'shift':0x10,
           'ctrl':0x11,
           'alt':0x12,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x1B,
           'spacebar':0x20,
           'page_up':0x21,
           'page_down':0x22,
           'end':0x23,
           'home':0x24,
           'left_arrow':0x25,
           'up_arrow':0x26,
           'right_arrow':0x27,
           'down_arrow':0x28,
           'select':0x29,
           'print':0x2A,
           'execute':0x2B,
           'print_screen':0x2C,
           'ins':0x2D,
           'del':0x2E,
           'help':0x2F,
           '0':0x30,
           '1':0x31,
           '2':0x32,
           '3':0x33,
           '4':0x34,
           '5':0x35,
           '6':0x36,
           '7':0x37,
           '8':0x38,
           '9':0x39,
           'a':0x41,
           'b':0x42,
           'c':0x43,
           'd':0x44,
           'e':0x45,
           'f':0x46,
           'g':0x47,
           'h':0x48,
           'i':0x49,
           'j':0x4A,
           'k':0x4B,
           'l':0x4C,
           'm':0x4D,
           'n':0x4E,
           'o':0x4F,
           'p':0x50,
           'q':0x51,
           'r':0x52,
           's':0x53,
           't':0x54,
           'u':0x55,
           'v':0x56,
           'w':0x57,
           'x':0x58,
           'y':0x59,
           'z':0x5A,
           'numpad_0':0x60,
           'numpad_1':0x61,
           'numpad_2':0x62,
           'numpad_3':0x63,
           'numpad_4':0x64,
           'numpad_5':0x65,
           'numpad_6':0x66,
           'numpad_7':0x67,
           'numpad_8':0x68,
           'numpad_9':0x69,
           'multiply_key':0x6A,
           'add_key':0x6B,
           'separator_key':0x6C,
           'subtract_key':0x6D,
           'decimal_key':0x6E,
           'divide_key':0x6F,
           'F1':0x70,
           'F2':0x71,
           'F3':0x72,
           'F4':0x73,
           'F5':0x74,
           'F6':0x75,
           'F7':0x76,
           'F8':0x77,
           'F9':0x78,
           'F10':0x79,
           'F11':0x7A,
           'F12':0x7B,
           'F13':0x7C,
           'F14':0x7D,
           'F15':0x7E,
           'F16':0x7F,
           'F17':0x80,
           'F18':0x81,
           'F19':0x82,
           'F20':0x83,
           'F21':0x84,
           'F22':0x85,
           'F23':0x86,
           'F24':0x87,
           'num_lock':0x90,
           'scroll_lock':0x91,
           'left_shift':0xA0,
           'right_shift ':0xA1,
           'left_control':0xA2,
           'right_control':0xA3,
           'left_menu':0xA4,
           'right_menu':0xA5,
           'browser_back':0xA6,
           'browser_forward':0xA7,
           'browser_refresh':0xA8,
           'browser_stop':0xA9,
           'browser_search':0xAA,
           'browser_favorites':0xAB,
           'browser_start_and_home':0xAC,
           'volume_mute':0xAD,
           'volume_Down':0xAE,
           'volume_up':0xAF,
           'next_track':0xB0,
           'previous_track':0xB1,
           'stop_media':0xB2,
           'play/pause_media':0xB3,
           'start_mail':0xB4,
           'select_media':0xB5,
           'start_application_1':0xB6,
           'start_application_2':0xB7,
           'attn_key':0xF6,
           'crsel_key':0xF7,
           'exsel_key':0xF8,
           'play_key':0xFA,
           'zoom_key':0xFB,
           'clear_key':0xFE,
           '+':0xBB,
           ',':0xBC,
           '-':0xBD,
           '.':0xBE,
           '/':0xBF,
           '`':0xC0,
           ';':0xBA,
           '[':0xDB,
           '\\':0xDC,
           ']':0xDD,
           "'":0xDE,
           '`':0xC0}
 
# Code Starts Here.
#------------------------------------------

def set_foreground_window(handle):
	win32gui.SetForegroundWindow(handle)

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

def grabArea(args):
	im = ImageOps.grayscale(getRectAsImage(args))
	a = array(im.getcolors())
	a = a.sum()
	return a
			
def get_cords():
	x,y = win32api.GetCursorPos()
	x = x - x_pad
	y = y - y_pad
	return x,y
	
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

def mousePos(cord):
	win32api.SetCursorPos((x_pad+cord[0], y_pad+cord[1]))

def clickPos(cord):
	mousePos(cord)
	leftClick()

	
	
	



def check_sound():
	soundOFF = 3414
	
	set_foreground_window(console_handle)
	sound = raw_input("Would you like sound? (Y / N)\n")
	soundState = grabArea(Area.mm_sound)
	if sound.lower() == 'y':
		#Turn sound on
		if soundState == soundOFF:
			clickPos(Coor.mm_sound)
		
	elif sound.lower() == 'n':
		#Turn sound off
		if soundState != soundOFF:
			clickPos(Coor.mm_sound)
	else:
		print "I don't understand '"+sound+"'"
		check_sound()

def select_save():
	empty_slot = 7790
	menu_btn = 12564
	day_one_sum = 4521
	day_title_sum = 2274
	
	set_foreground_window(console_handle)
	save = raw_input("Which slot? (1 - 3)")[:1]
	if save == '1' or save == '2' or save == '3':
		
		#Check if slot already has save
		if grabArea(Area.mm_delete_slot[save]) != empty_slot:
			print 'This slot already has a save'
			while True:
				set_foreground_window(console_handle)
				choice = raw_input("Continue or Delete? \n")
				if choice[:8].lower() == 'continue':
					print 'Continuing from save...'
					clickPos(Coor.mm_slot[save])
					time.sleep(1)
					clickPos(Coor.mm_resume_save)
					
					#or grabArea(Area.load_continue) == 5365
					time.sleep(1)
					if grabArea(Area.load_screen) == 140:
						print 'Loading level...'
						while grabArea(Area.load_continue) != 5365:
							time.sleep(1)
						clickPos(Coor.daycom_continue3)

					print 'Waiting...'						
					while grabArea(Area.day_title) != day_one_sum:
						time.sleep(.2)
					time.sleep(1)
					dayNumSum = grabArea(Area.day_number)
					if dayNumSum == day_title_sum:
						print 'It is the first day, a tutorial needs completing'
						print 'Waiting for cutscene to finish...'
						while grabArea(Area.menu_btn) != menu_btn:
							time.sleep(2)
						do_tutorial()
						return True
					else:
						print 'It is not the first day'
						print 'Waiting for cutscene to finish...'
						while grabArea(Area.menu_btn) != menu_btn:
							time.sleep(2)
						print "Let's go!"
						return False
					
				elif choice[:6].lower() == 'delete':
					print 'Deleting...'
					clickPos(Coor.mm_delete_slot[save])
					time.sleep(.5)
					clickPos(Coor.mm_erasegmcnfm[save])
					time.sleep(.5)
					clickPos(Coor.mm_slot[save])
					new_game()
					return True
				else:
					print "I don't understand!"
		else:
			clickPos(Coor.mm_slot[save])
			new_game()
			return True

	else:
		print 'Pick a proper slot!'
		select_save()
		
def new_game():
	gender = get_gender()

	if gender == 'male':
		clickPos(Coor.char_male)
	elif gender == 'female':
		clickPos(Coor.char_female)
			
	while True:
		try:
			set_foreground_window(console_handle)
			name = raw_input("What is your name? \n")
			clickPos(Coor.char_nameField)
			writeString(name)
			break
		except:
			print "Oops! Try entering a name without special characters."
			clickPos(Coor.char_nameField)
			time.sleep(0.2)
			clickPos(Coor.char_nameField)
			pressKey('backspace')
	
	clickPos(Coor.char_continue)
	time.sleep(1)
	clickPos(Coor.intro_skip)
	do_tutorial()



def change_station(station):
	#!!! A Fourth station is yet to be unlocked in the game.
	if station == 'order':
		clickPos(Coor.s_order)
	elif station == 'grill':
		clickPos(Coor.s_grill)
	elif station == 'build':
		clickPos(Coor.s_build)
	else:
		print 'ERROR: Unknown station '+str(station)
		#V Stops the script without closing the console.
		sys.exit()
		
	#Time it takes to transition between stations
	time.sleep(.5)
	
def take_order():
	time.sleep(.4)
	clickPos(Coor.take_order)
	time.sleep(2)
	screen = grabArea((x_pad+540, y_pad+360, x_pad+540+60, y_pad+360+30))
	print 'Reading order...'
	while grabArea((x_pad+540, y_pad+360, x_pad+540+60, y_pad+360+30)) == screen:
		time.sleep(1)


		
def place_batter(grill, name):
	mousePos(IngredientTypes[name][1])
	leftDown()
	mousePos(Coor.grill[grill])
	leftUp()
	
def flip_pancake(grill):
	clickPos(Coor.grill[grill])
		
def finish_pancake(grill):
	mousePos(Coor.grill[grill])
	leftDown()
	mousePos(Coor.gril_confirm)
	leftUp()


	
def place_waffle(iron):
	mousePos(IngredientTypes['pancake'][1])
	leftDown()
	mousePos(Coor.iron[iron])
	leftUp()
	
def flip_waffle(iron):
	clickPos(Coor.iron[iron])
		
def finish_waffle(iron):
	mousePos(Coor.iron[iron])
	leftDown()
	mousePos(Coor.gril_confirm)
	leftUp()
	

	
def get_point_in_ellipse(x,y,deg):
	# xPos = x cos t
	# yPos = y sin t
	xPos = x * (math.cos(math.radians(deg)))
	yPos = y * (math.sin(math.radians(deg)))
	return (int(math.floor(xPos)), int(math.floor(yPos)))
	
def add_base():
	mousePos(Coor.build_base)
	leftDown()
	mousePos(Coor.build_center)
	leftUp()
		
def spread_topping(name, points=20):
	
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
				x, y = get_point_in_ellipse(45, 45, x*increment)
				print 'Placing topping at '+str(x)+', '+str(y)+' from pancake center'
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
			x, y = get_point_in_ellipse(45, 45, x*increment)
			print 'Placing sprinkle/sauce at '+str(x)+', '+str(y)+' from pancake center'
			mousePos((Coor.build_center[0]+x, Coor.build_center[1]+y))
			leftUp()
		#Buffer
		time.sleep(.4)




def move_order_to_line(slot):
	mousePos(Coor.ordr_active)
	leftDown()
	mousePos((20+(slot*37), 10))
	leftUp()
		
def move_order_to_tray(slot):
	mousePos((20+(slot*37), 10))
	leftDown()
	mousePos(Coor.build_tickt)
	leftUp()
		
		
def do_tutorial():
	menu_btn = 12564
	order_floor = 1444
	pancake_tray = 1513
	
	#wait until intro sequence is finished
	while grabArea(Area.menu_btn) != menu_btn:
		print 'Waiting for cutscene to finish...'
		time.sleep(2)	
	print "Let's go!"
	
	#click on grill station
	change_station('grill')
	
	#click on build station
	change_station('build')
	
	#click on order station
	change_station('order')
	
	#take order, wait for order to complete
	while grabArea(Area.order_floor) == order_floor: #empty floor
		print 'No new customers.'
	
	print 'Customer is ready!'
	take_order()
	
	#drag ticket to ticket line
	mousePos(Coor.ordr_active)
	leftDown()
	mousePos(Coor.ordr_slot1)
	leftUp()
	
	#click on grill station
	change_station('grill')
	
	#drag order to active order
	mousePos(Coor.ordr_slot1)
	leftDown()
	mousePos(Coor.ordr_active)
	leftUp()
	
	#do pancakes
	place_batter(6, 'pancake')
	time.sleep(.1)
	place_batter(7, 'pancake')
	
	currentTime = int(time.time())
	print('Pancakes placed at '+str(currentTime))
	
	#loop until 17 seconds have advanced, flip pancakes
	while currentTime+16 >= int(time.time()):
		print 'Waiting for pancakes to cook...'
		time.sleep(2)
	
	flip_pancake(6)
	time.sleep(.1)
	flip_pancake(7)
	
	currentTime = int(time.time())
	print('Pancakes placed at '+str(currentTime))
	#loop until 17 seconds have passed, drag pancakes to green tick.
	while currentTime+16 >= int(time.time()):
		print 'Waiting for pancakes to cook...'
		time.sleep(2)
	
	finish_pancake(6)
	time.sleep(.1)
	finish_pancake(7)
	
	#click on build station
	change_station('build')
	
	#drag pancakes to build area
	add_base()
	time.sleep(.5)
	add_base()
	
	#drag 3 butter pads to 3 elliptic points on the pancake
	#maximum distribution.
	spread_topping('butterpad', 3)

	#drag and release blueberries in circle path
	spread_topping('blueberry')

	#blue and release blueberry sauce in circle path
	spread_topping('blueberry_sauce')
	
	#click finish
	time.sleep(1)
	clickPos(Coor.build_finish)
	time.sleep(1)
	
	#drag ticket to finish tray
	mousePos(Coor.ordr_active)
	leftDown()
	time.sleep(.5)
	mousePos(Coor.build_tickt)
	leftUp()
	
	#wait until back at build station
	while grabArea(Area.pancake_tray) != pancake_tray:
		print 'Waiting for customer...'
		time.sleep(1)
	
	#click on order station
	change_station('order')
	
	#END
	print 'TUTORIAL COMPLETE!'
		
		
def interpret_order():
	#Returns the type of ingredients and number of pancakes / waffles that can order needs
	grillsNeeded = 0
	ironsNeeded = 0
	ingredients = []
	
	for x in range(0, 8):
		box = (x_pad+493, y_pad+267-(x*30), x_pad+493+66, y_pad+267-(x*30)+18)
		sum = grabArea(box)
		if sum == 3220 or sum == 4880:
			print 'Slot '+str(x+1)+' is empty'
		else:
			try:
				ingredient = IngredientSums[sum]
				print 'Found '+ingredient
				if IngredientTypes[IngredientSums[sum]][0] == 'topping':
					countSum = grabArea((x_pad+562, y_pad+267-(x*30), x_pad+562+66, y_pad+267-(x*30)+18))
					try:
						toppingCount = Counts[countSum]
					except:
						print 'Toppping count not found for slot '+str(x+1)
						print countSum
						print 'Please write the number of toppings required.'
						toppingCount = int(raw_input())
						
					ingredients.append([ingredient, toppingCount])
				else:
					ingredients.append([ingredient])
				if IngredientTypes[IngredientSums[sum]][0] == 'bread':
					grillsNeeded += 1
				elif IngredientTypes[IngredientSums[sum]][0] == 'waffle':
					ironsNeeded += 1
				
			except:
				print 'Found unregisterd ingredient'
				print 'Slot: '+str(x+1)
				print 'Sum: '+str(sum)
	
	print 'Number of grills needed: '+str(grillsNeeded)
	print 'Number of irons needed: '+str(ironsNeeded)
	print 'Ingredient list'
	print ingredients
	return ingredients, grillsNeeded, ironsNeeded
	
	
def get_ticketLineNum():
	#Find first available spot on line
	for x in range(0, 12):
		try:
			orders[x]
			print 'Spot Taken'
		except:
			print 'Spot in line found'
			return x
		
		
def allocate_grills(number):
	availGrills = list()
	if number == 0:
		print 'No grills to allocate'
		return []
	
	for grill in grills:
		if grills[grill] == True:
			print 'Grill '+str(grill)+' is available'
			availGrills.append(grill)
			grills[grill] = False
			if len(availGrills) == number:
				break
		else:
			print 'Grill '+str(grill)+' not available'
	print availGrills
	return availGrills
	
def allocate_irons(number):
	availIrons = list()
	if number == 0:
		print 'No irons to allocate'
		return []
	
	for iron in irons:
		if irons[iron] == True:
			print 'Iron '+str(iron)+' is available'
			availIrons.append(iron)
			irons[iron] = False
			if len(availIrons) == number:
				break
		else:
			print 'Iron '+str(iron)+' not available'
	print availIrons
	return availIrons

	
def availableGrills_count():
	count = 0
	for grill in grills:
		if grills[grill] == True:
			count += 1
	print 'Available grills: '+str(count)
	return count

def availableIrons_count():
	count = 0
	for iron in irons:
		if irons[iron] == True:
			count += 1
	print 'Available irons: '+str(count)
	return count		
	

	
def main_loop(first_day):
	print first_day
	if first_day:
		pancake_cook_time = 16
	else:
		pancake_cook_time = def_pancake_cook_time
	print 'Cooking time set to '+str(pancake_cook_time)+' seconds'
	
	pancake_tray = 1513
	
	#Main loop goes here.
	print "MAIN LOOP BEGINNING"
	
	#Avoiding the problems of the blue ribbon
	change_station('build')
	change_station('order')
	
	order_floor = grabArea(Area.order_floor)
	
	while True:
		time.sleep(.1)
		#If customer is present and a slot on the line is available,
		if grabArea(Area.order_floor) != order_floor and (len(orders)+len(waitingOrders)) < 12:
			print 'Customer detected!'
			#Take order
			take_order()

			#Interpret order
			ingredients, grillsNeeded, ironsNeeded = interpret_order()
			
			#Get ticketLineNum
			ticketLineNum = get_ticketLineNum()
			
			#if needed number of grills is available,
			if availableGrills_count() >= grillsNeeded or availableIrons_count() >= ironsNeeded:		
				print 'Making order...'
				
				#Put order in order[]
				orders[ticketLineNum] = ingredients
				
				#get list of available grills
				grillsAllocated = allocate_grills(grillsNeeded)
				
				#get list of available irons
				ironsAllocated = allocate_irons(ironsNeeded)
				
				#Go to grill station
				change_station('grill')
				
				#Create Grill group
				grillGroups[ticketLineNum] = [(time.time()+pancake_cook_time), False, grillsAllocated, ironsAllocated]
				
				#place pancakes
				grillNum = 0
				ironNum = 0
				for ingredient in ingredients:
					if IngredientTypes[ingredient[0]][0] == 'bread':
						place_batter(grillsAllocated[grillNum], ingredient[0])
						grillNum += 1
					if IngredientTypes[ingredient[0]][0] == 'waffle':
						place_waffle(ironsAllocated[ironNum])
						ironNum += 1
				
			else:
				#Add order to waiting orders
				print 'Order added to waiting orders'
				waitingOrders.append([ticketLineNum, grillsNeeded, ironsNeeded, ingredients])
			
			#Move order ticket to topline, record position
			move_order_to_line(ticketLineNum)
			
		
			print 'Number of orders: '+str(len(orders))
			print 'Number of grill groups: '+str(len(grillGroups))
			print 'Number of waiting orders: '+str(len(waitingOrders))
			change_station('order')
				
		#If any pancakes need to be flipped or at completion
		#Avoiding a runtime error: dictionary changed size during iteration
		grillGroupsCopy = {k:v for k,v in grillGroups.items()}
		
		for orderID in grillGroupsCopy:
			if grillGroups[orderID][0] <= int(time.time()):
				print 'Grill group '+str(orderID)+' is ready'
				
				#Go to grill
				change_station('grill')
				
				if grillGroups[orderID][1] == False:
				#Flip Pancakes!!!!!!!!!!!!!!!!!!!!!!!!
					for grillSlot in grillGroups[orderID][2]:
						flip_pancake(grillSlot)
					for ironSlot in grillGroups[orderID][3]:
						flip_waffle(ironSlot)
					grillGroups[orderID][0] += pancake_cook_time
					grillGroups[orderID][1] = True
					
					change_station('order')

				elif grillGroups[orderID][1] == True:
				#Pancakes are cooked
					for grillSlot in grillGroups[orderID][2]:
						finish_pancake(grillSlot)
						grills[grillSlot] = True
					for ironSlot in grillGroups[orderID][3]:
						finish_waffle(ironSlot)
						irons[ironSlot] = True
					del grillGroups[orderID]
					
					#Any orders waiting for grill slots?
					while len(waitingOrders) > 0:
						if waitingOrders[0][1] > availableGrills_count() or waitingOrders[0][2] > availableIrons_count():
							print 'Not enough grills/irons for order that needs '+str(waitingOrders[0][1])+' grills and '+str(waitingOrders[0][2])+' irons'
							break

						print 'Resuming order'
						
						#Get order info
						ticketLineNum = waitingOrders[0][0]
						grillsNeeded = waitingOrders[0][1]
						ironsNeeded = waitingOrders[0][2]
						ingredients = waitingOrders[0][3]
						del waitingOrders[0]
						
						#Put order in orders[]
						orders[ticketLineNum] = ingredients
						
						#get list of available grills
						grillsAllocated = allocate_grills(grillsNeeded)
						
						#get list of available irons
						ironsAllocated = allocate_irons(ironsNeeded)
						
						#Go to grill station
						change_station('grill')
						
						#Create Grill group
						grillGroups[ticketLineNum] = [(time.time()+pancake_cook_time), False, grillsAllocated]
						
						#place pancakes
						grillNum = 0
						ironNum = 0
						for ingredient in ingredients:
							if IngredientTypes[ingredient[0]][0] == 'bread':
								place_batter(grillsAllocated[grillNum], ingredient[0])
								grillNum += 1
							if IngredientTypes[ingredient[0]][0] == 'waffle':
								place_waffle(ironsAllocated[ironNum])
								ironNum += 1
					

					#Go to build station
					change_station('build')
					
#-------------------------------------------- Shit happens here
					#build pancake

					for ingredient in orders[orderID]:
						print ingredient
						print IngredientTypes[ingredient[0]]
						if IngredientTypes[ingredient[0]][0] == 'bread' or IngredientTypes[ingredient[0]][0] == 'waffle':
							add_base()
							time.sleep(.1)
						elif IngredientTypes[ingredient[0]][0] == 'topping':
							spread_topping(ingredient[0],ingredient[1])
						else:
							spread_topping(ingredient[0])
					
					#Wait for animations to finish
					time.sleep(.5)
					#Give to customer
					clickPos(Coor.build_finish)
					time.sleep(.2)
					move_order_to_tray(orderID)
					
					#wait until back at build station
					print 'Waiting for customer...'
					while grabArea(Area.pancake_tray) != pancake_tray:
						time.sleep(1)
						#Check if day end
						if grabArea(Area.flipline_logo) == 34737:
							print 'Level complete'
							del orders[orderID]
							return
					

					
					#Delete order from orders[]
					del orders[orderID]	
					change_station('order')
			

		
def start_next_day():
	menu_btn = 12564
	
	print 'Waiting...'
	while grabArea(Area.continue1) != 25029:
		time.sleep(1)
	clickPos(Coor.daycom_continue1)
	time.sleep(4)
	clickPos(Coor.daycom_skipslots)
	time.sleep(2)
	clickPos(Coor.daycom_continue2)
	
	print 'Waiting for next day to load...'
	while grabArea(Area.load_continue) != 5365:
		time.sleep(1)
		
	clickPos(Coor.daycom_continue3)

	print 'Waiting for cutscene to finish...'	
	while grabArea(Area.menu_btn) != menu_btn:
		time.sleep(2)
	print "Let's go!"
	
def startGame():
	play_button_sum = 19410
	
	#Start on preloader screen
	clickPos(Coor.preload_continue)
	
	#Wait for play button to appear
	print 'Waiting for intro to finish...'
	while grabArea(Area.mm_play) != play_button_sum:
		time.sleep(2)

	#Check sound
	check_sound()
	
	#Click Play
	clickPos(Coor.mm_play)
	
	#Select save
	first_day = select_save()
	
	#Game begins here, at the point where customers are coming into your store
	while True:
		main_loop(first_day)
		first_day = False
		start_next_day()
	
#startGame()
	
	

	

