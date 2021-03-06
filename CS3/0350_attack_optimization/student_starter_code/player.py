import pygame, physics_object, math, bullet

speed = 10
white = 255,255,255
#Width of each action ring that determines which action gets
#taken based on distance from the target.
action_radius = 100

class Player(physics_object.PhysicsObject):
    #Create a player
    def __init__(self, screen, x, y):
        #              x,y,radius, angle, rotation rate
        super().__init__(x, y, 11, 0, math.pi/32)
        self.screen = screen
        #Firing controls
        self.burst_reset = 5 #frames between shots in a burst
        self.burst_countdown = 0 #countdown to next shot
        self.burst_count = 0 #number of shots fired so far in this burst
        self.burst_limit = 3 #number of shots in a burst
        self.cooldown_reset = 120 #frames between bursts
        self.cooldown = 0 #countdown to next burst

        #Use for drawing thrust
        self.accelerate_forward = False
        self.accelerate_backward = False
        self.accelerate_left = False
        self.accelerate_right = False
        #Use for drawing action circles around the target
        self.target_center = (0,0)

        #Attack pattern variables
        self.attack_pattern = [
            #Distance first action_radius pixels
            0, #shoot
            -1, #forward or backward
            -1, #yaw closer 1 or further -1
            -1, #turn toward, away, or neither
            #Distance second action_radius pixels
            0, #shoot
            0, #forward or backward
            -1, #yaw closer 1 or further -1
            -1, #turn toward, away, or neither
            #2
            1, #shoot
            0, #forward or backward
            -1, #yaw closer or further
            1, #turn toward, away, or neither
            #3
            0, #shoot
            0, #forward or backward
            0, #yaw closer or further
            1, #turn toward, away, or neither
            #4
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1, #turn toward, away, or neither
            #5
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1, #turn toward, away, or neither
            #6
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1, #turn toward, away, or neither
            #7
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1, #turn toward, away, or neither
            #8
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1, #turn toward, away, or neither
            #9
            0, #shoot
            1, #forward or backward
            1, #yaw closer or further
            1 #turn toward, away, or neither
        ]

    def update(self, target, bullets):
        #Reset acceleration booleans for drawing
        self.accelerate_forward = False
        self.accelerate_backward = False
        self.accelerate_left = False
        self.accelerate_right = False
        self.target_center = (int(target.x),int(target.y))

        #Cooldown
        self.cooldown-=1
        self.burst_countdown-=1

        #Get target information
        goal_angle = self.angleTo(target.x,target.y)
        turn = self.getSmallestTurnAngle(goal_angle)
        d = self.distanceTo(target)

        #Get action profile index based on distance
        #The 4's are for the 4 actions in each set: shoot, forward/back, yaw, turn toward/away
        #action_radius defines the distance between nested rings for different actions
        index = 4*int(min(d/action_radius, (len(self.attack_pattern)/4)-1))

        #Testing:
        #print(d)
        #print(index) #TODO
        #print(self.attack_pattern[index:index+4])

        if self.attack_pattern[index]==1: #shoot
            self.shoot(bullets)

        if self.attack_pattern[index+1]==1: #forward or backward
            self.accelerateForward()
            self.accelerate_forward = True
        elif self.attack_pattern[index+1]==-1: #forward or backward
            self.accelerateBackward()
            self.accelerate_backward = True

        if self.attack_pattern[index+2]==1: #yaw closer or further
            if turn>0:
                self.accelerateRight()
                self.accelerate_right = True
            else:
                self.accelerateLeft()
                self.accelerate_left = True
        if self.attack_pattern[index+2]==-1: #yaw closer or further
            if turn>0:
                self.accelerateLeft()
                self.accelerate_left = True
            else:
                self.accelerateRight()
                self.accelerate_right = True

        if self.attack_pattern[index+3]==1: #turn toward, away, or neither
            self.turnToward(target.x,target.y,close_enough=math.pi/64)
        elif self.attack_pattern[index+3]==-1: #turn toward, away, or neither
            self.turnFrom(target.x,target.y)



    def shoot(self, bullets):
        if self.cooldown<=0 and self.burst_countdown<=0:
            #Count another shot fired in this burst
            self.burst_count += 1
            #Reset burst countdown
            self.burst_countdown = self.burst_reset
            #If we have fired the limit for this burst, reset the cooldown
            if self.burst_count >= self.burst_limit:
                self.cooldown = self.cooldown_reset
                self.burst_count = 0
            #Create new bullet
            b = bullet.Bullet(self.screen, self.x,self.y,self.angle)
            #Add new bullet to list
            bullets.append(b)


    def draw(self):
        #Angles and radii to determine shape of the player
        angles = [0,135,-135] #in degrees
        radii = [18,10,10] #in pixels
        #Draw outline of player.
        points = self.getCorners(radii, angles)
        #5 is line thickness.
        pygame.draw.polygon(self.screen, white, points,1)
        #Draw a "vision" arc
        dist = 40
        green = 0,255,0
        for i in range(-5,6,1):
            x = self.x+math.cos(self.angle+i*math.pi/60)*dist
            y = self.y+math.sin(self.angle+i*math.pi/60)*dist
            pygame.draw.line(self.screen, green, (self.x,self.y),(x,y))
        #Display thrust
        red = 255,0,0
        radius = 3
        dist = 20
        if self.accelerate_forward:
            x = int(self.x+math.cos(self.angle+math.pi)*dist)
            y = int(self.y+math.sin(self.angle+math.pi)*dist)
            pygame.draw.circle(self.screen, red, (x,y), radius)
        if self.accelerate_backward:
            x = int(self.x+math.cos(self.angle)*dist)
            y = int(self.y+math.sin(self.angle)*dist)
            pygame.draw.circle(self.screen, red, (x,y), radius)
        if self.accelerate_left:
            x = int(self.x+math.cos(self.angle+math.pi/2)*dist)
            y = int(self.y+math.sin(self.angle+math.pi/2)*dist)
            pygame.draw.circle(self.screen, red, (x,y), radius)
        if self.accelerate_right:
            x = int(self.x+math.cos(self.angle-math.pi/2)*dist)
            y = int(self.y+math.sin(self.angle-math.pi/2)*dist)
            pygame.draw.circle(self.screen, red, (x,y), radius)
        #Draw the rings defining different actions to take
        for i in range(1, int(len(self.attack_pattern)/4)):
            pygame.draw.circle(self.screen, white, self.target_center, i*action_radius,1)


    def getCorners(self, radii, angles):
        #Returns list of points to draw the Player
        points = []
        for i in range(len(angles)):
            a = angles[i]*math.pi/180+self.angle
            x = self.x+radii[i]*math.cos(a)
            y = self.y+radii[i]*math.sin(a)
            points.append((x,y))
        return points
