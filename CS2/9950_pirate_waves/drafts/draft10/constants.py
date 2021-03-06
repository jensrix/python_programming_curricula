
black=0,0,0
blue=(0,0,255)
sky_blue=(200,200,255)
red=(255,0,0)
green=(0,255,0)
screen_width = 1000
screen_height = 600

#Spacing between water height locations
spacing = 10 #pixels
sea_level = 200
friction = 0.02
surface_tension = 0.3

#For scaling down the image
scaling = 0.2

#Buffer of empty pixels around boat image to make the boat
#sink down in the water more.
buffer = 7

#Upward pressure from being under water. Is a function of depth
bouyancy = 0.2
#Constant downward acceleration
gravity = 0.8
air_friction = 0.01
water_friction = 0.1

#Use to oscillate the right-most water_heights value
amplitude = 150
period = 25

#Controls for the player's boat
jump_power = 27 #instantaneous change to dy when jumping
speed = 3 #shift left or right in pixels per frame

rum_scroll_speed_min = 5
rum_scroll_speed_max = 10
rum_respawn_min = 15
rum_respawn_max = 45
rum_collision_distance = 40

sword_respawn_min = 45
sword_respawn_max = 75

#How far above sea level to spawn swords and rum
spawn_above_sea_level = 100

#Speed of cannon ball shot
cannon_ball_speed=20
cannon_ball_arc=3.1415/3

#Depth at which the boat causes a splash in the water.
splash_depth = 45
splash_delay = 15 #delay in frames before the boat can cause another splash.
splash_adjust = 15 #adjustment to reduce magnitude of splash. Unit is pixels

#This determines how long to dwell on each frame of the cannon shot explosions
dwell_sequence = []
for _ in range(27):
    dwell_sequence.append(0)
for _ in range(9):
    dwell_sequence.append(3)
for _ in range(3):
    dwell_sequence.append(0)

#Drift for the smoke from cannon shots
smoke_dx = -2