import pygame, math, random

#Setup
pygame.init()
width = 900
height = 600
screen = pygame.display.set_mode((width,height))
clock = pygame.time.Clock()
large_font = pygame.font.SysFont('Arial', 48)
small_font = pygame.font.SysFont('Arial', 24)
black = 0,0,0
white = 255,255,255
red = 255,0,0


class Line:
	def __init__(self, screen, x1, y1, x2, y2, dx, dy):
		self.screen = screen
		#Get the length of the line
		self.length = math.sqrt((x1-x2)**2+(y1-y2)**2)
		#Get the midpoint of the line. We do this so we can draw the line
		#based on an angle, which makes it possible to more easily rotate the line.
		self.x = (x2+x1)/2
		self.y = (y2+y1)/2
		#Get the velocity of the line
		self.dx = dx
		self.dy = dy
		#Get the angle of the line
		self.angle = math.atan2(y2-y1, x2-x1)
		#Randomly rotate +-math.pi/256 per frame
		self.rotation_rate = random.random()*math.pi/128
		self.rotation_rate = self.rotation_rate-math.pi/256
	
	def move(self, border_right, border_bottom):
		self.angle = self.angle + self.rotation_rate
		self.x = self.x + self.dx
		self.y = self.y + self.dy
		if self.x < 0:
			self.x += border_right
		elif self.x > border_right:
			self.x -= border_right
		if self.y < 0:
			self.y += border_bottom
		elif self.y > border_bottom:
			self.y -= border_bottom
		
	def draw(self):
		#Calculate the coordinates of both ends of the line
		coord1 = [self.x+math.cos(self.angle)*self.length/2,
				  self.y+math.sin(self.angle)*self.length/2]
		coord2 = [self.x-math.cos(self.angle)*self.length/2,
				  self.y-math.sin(self.angle)*self.length/2]
		pygame.draw.line(self.screen, white, coord1, coord2, 3)


class GameManager:
	def __init__(self, screen, level):
		self.screen = screen
		self.level = level
		#Create player
		self.player = Ship(screen, self.screen.get_width()/2, self.screen.get_height()/2)
		#Create bullet list
		self.bullet_list = []
		#Create randomized asteroids. Asteroids get faster as level progresses
		self.asteroid_list = self.spawnAsteroids(0,0, 3+level, -1.7-0.1*level, 1.7+0.1*level, 40, 60, at_random=True)
		#List of intangible animation objects
		self.animation_list = []
	
	def spawnAsteroids(self, x, y, count, min_dx, max_dx, min_radius, max_radius, at_random=False):
		temp = []
		for i in range(count):
			if at_random:
				x = random.randint(0, self.screen.get_width())
				y = random.randint(0, self.screen.get_height())
			dx = random.random()*(max_dx-min_dx)+min_dx
			dy = random.random()*(max_dx-min_dx)+min_dx
			temp.append(Asteroid(self.screen,x,y,dx,dy,min_radius,max_radius))
		return temp
	
	def update(self):
		#Move and draw
		for item in self.asteroid_list:
			item.move(self.screen.get_width(), self.screen.get_height())
			item.draw()
		for item in self.bullet_list:
			item.move(self.screen.get_width(), self.screen.get_height())
			item.draw()
		for item in self.animation_list:
			item.move(self.screen.get_width(), self.screen.get_height())
			item.draw()
		#Draw the player if the player is still alive
		if self.player.lives > 0:
			self.player.move(self.screen.get_width(), self.screen.get_height())
			self.player.draw()
		#Check collisions
		self.checkCollisions()
		#Remove dead items
		for i in reversed(range(len(self.asteroid_list))):
			if self.asteroid_list[i].remove:
				del self.asteroid_list[i]
		for i in reversed(range(len(self.bullet_list))):
			if self.bullet_list[i].remove:
				del self.bullet_list[i]
	
	def checkCollisions(self):
		#Check for collisions between asteroids and the player
		for a in self.asteroid_list:
			#If there was a collision and the player is not already dead
			if a.collidedWith(self.player) and self.player.lives>0:
				self.player.lives = self.player.lives - 1
				#Add dead player lines to simulate ship breaking apart.
				corners = self.player.getCorners()
				for i in range(len(corners)):
					x1 = corners[i][0]
					y1 = corners[i][1]
					dx = self.player.dx+random.random()-0.5
					dy = self.player.dy+random.random()-0.5
					if i<len(corners)-1:
						x2 = corners[i+1][0]
						y2 = corners[i+1][1]
					else: #This else wraps end of the list to the start.
						x2 = corners[0][0]
						y2 = corners[0][1]
					self.animation_list.append(Line(self.screen, x1,y1, x2,y2, dx, dy))
		#Check for collisions between asteroids and bullets
		extra_asteroids = []
		for a in self.asteroid_list:
			for b in self.bullet_list:
				if a.collidedWith(b):
					a.remove = True
					b.remove = True
					#Spawn smaller asteroids
					if a.min_radius > 10:
						extra_asteroids = extra_asteroids + self.spawnAsteroids(a.x, a.y, 4, -4, 4, a.min_radius/2, a.max_radius/2)
		self.asteroid_list = self.asteroid_list + extra_asteroids
	
	def shoot(self):
		#Shoot if the player is alive
		if self.player.lives>0:
			x = self.player.x+math.cos(self.player.angle)*self.player.radius
			y = self.player.y+math.sin(self.player.angle)*self.player.radius
			b = Bullet(self.screen, x, y, self.player.angle)
			self.bullet_list.append(b)



class Bullet:
	def __init__(self, surface, x, y, angle):
		self.surface = surface
		self.x = x
		self.y = y
		speed = 10
		self.dx = math.cos(angle)*speed
		self.dy = math.sin(angle)*speed
		self.radius = 8
		self.timeout = 90 #frames the bullet will last for
		self.remove = False
	
	def move(self, border_right, border_bottom):
		#Move dx and dy
		self.x += self.dx
		self.y += self.dy
		#Screen wrap
		if self.x+self.radius < 0:
			self.x += border_right
		elif self.x > border_right:
			self.x -= border_right
		if self.y+self.radius < 0:
			self.y += border_bottom
		elif self.y > border_bottom:
			self.y -= border_bottom
	
	def draw(self):
		r = pygame.Rect(self.x-self.radius,
						self.y-self.radius,
						self.radius/2,self.radius/2)
		pygame.draw.ellipse(self.surface, white, r)
		#countdown to removal of bullets
		self.timeout -= 1
		self.remove = self.timeout <= 0




class Ship:
	def __init__(self, surface, x, y):
		self.surface = surface
		self.x = x
		self.y = y
		self.dx = 0
		self.dy = 0
		self.speed = 0.3
		self.sides = 3
		self.radius = 20
		self.angle = 0
		self.rotation_rate = math.pi/16
		self.thrust_on = False
		self.lives = 1
		self.remove = False
	
	def rotateLeft(self):
		self.angle -= self.rotation_rate
	
	def rotateRight(self):
		self.angle += self.rotation_rate
	
	def thrust(self):
		self.dx += math.cos(self.angle)*self.speed
		self.dy += math.sin(self.angle)*self.speed
		self.thrust_on = True
	
	def move(self, border_right, border_bottom):
		#Move dx and dy
		self.x += self.dx
		self.y += self.dy
		#print(self.x)
		if self.x+self.radius < 0:
			self.x += border_right
		elif self.x > border_right:
			self.x -= border_right
		if self.y+self.radius < 0:
			self.y += border_bottom
		elif self.y > border_bottom:
			self.y -= border_bottom
	
	def getCorners(self):
		#Returns list of points to draw the ship
		points = []
		#Nose
		angle = self.angle+math.pi*2
		x = self.x + math.cos(angle)*self.radius*1.5
		y = self.y + math.sin(angle)*self.radius*1.5
		points.append([x, y])
		#wing 1
		angle = self.angle+math.pi*2*(1.2/self.sides)
		x = self.x + math.cos(angle)*self.radius
		y = self.y + math.sin(angle)*self.radius
		points.append([x, y])
		#rear
		angle = self.angle+math.pi
		x = self.x + math.cos(angle)*self.radius*0.5
		y = self.y + math.sin(angle)*self.radius*0.5
		points.append([x, y])
		#wing 2
		angle = self.angle+math.pi*2*(1.8/self.sides)
		x = self.x + math.cos(angle)*self.radius
		y = self.y + math.sin(angle)*self.radius
		points.append([x, y])
		return points
	
	def draw(self):
		#Draw thrust
		if self.thrust_on:
			angle = self.angle+math.pi
			x = self.x + math.cos(angle)*self.radius*0.7
			y = self.y + math.sin(angle)*self.radius*0.7
			radius = 10
			r = pygame.Rect(x-radius/2,y-radius/2,radius,radius)
			pygame.draw.ellipse(self.surface, red, r)
		#Reset thrust
		self.thrust_on = False
		#Draw outline of ship. Note: 3 is line thickness.
		points = self.getCorners()
		pygame.draw.polygon(self.surface, white, points,3)



class Asteroid:
	def __init__(self, surface, x, y, dx, dy, min_radius, max_radius):
		self.surface = surface
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.sides = random.randint(5,12)
		self.min_radius = min_radius
		self.max_radius = max_radius
		self.radii = []
		for i in range(self.sides):
			temp = random.randint(self.min_radius,self.max_radius)
			self.radii.append(temp)
		self.line_thickness = 2
		self.angle = 0
		#Randomly rotate +-math.pi/256 per frame
		self.rotation_rate = random.random()*math.pi/128
		self.rotation_rate = self.rotation_rate-math.pi/256
		self.remove = False
	
	def collidedWith(self, other):
		distance = math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
		radius_sum = other.radius + self.min_radius
		return distance < radius_sum
		
	def move(self, border_right, border_bottom):
		#Rotate a little
		self.angle = (self.angle + self.rotation_rate) % (math.pi*2)
		#Move dx and dy
		self.x += self.dx
		self.y += self.dy
		#print(self.x)
		if self.x+self.max_radius < 0:
			self.x += border_right
		elif self.x > border_right:
			self.x -= border_right
		if self.y+self.max_radius < 0:
			self.y += border_bottom
		elif self.y > border_bottom:
			self.y -= border_bottom
	
	def draw(self):
		point_list = []
		for i in range(self.sides):
			angle = self.angle+math.pi*2*(i/self.sides)
			x = self.x + math.cos(angle)*self.radii[i]
			y = self.y + math.sin(angle)*self.radii[i]
			point_list.append([x, y])
		pygame.draw.polygon(self.surface, white, point_list, self.line_thickness)



def userInputToPlayer(player):
	keys = pygame.key.get_pressed()
	if keys[pygame.K_UP]:
		player.thrust()
	if keys[pygame.K_LEFT]:
		player.rotateLeft()
	if keys[pygame.K_RIGHT]:
		player.rotateRight()



#Create game manager object to manage updating and moving everything
gm = GameManager(screen, 0) #Start on level 0


#Main loop
done = False
while not done:
	#Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			if event.key == pygame.K_SPACE:
				gm.shoot()
			#Press enter to reset game after death
			if event.key == pygame.K_RETURN and gm.player.lives <= 0:
				gm = GameManager(screen, 0) #Reset to level 0
	#Send user input to the player if it's alive
	if gm.player.lives > 0:
		userInputToPlayer(gm.player)
	#fill screen with black
	screen.fill(black)
	gm.update()
	#Check for victory and advance to next level
	if len(gm.asteroid_list) == 0:
		gm = GameManager(screen, gm.level+1)
	#Display level
	position = (width-150, 10)
	screen.blit(small_font.render("Level "+str(gm.level),True,white),position)
	#Check for game over
	if gm.player.lives <= 0:
		position = (width/2-100, height/2-20)
		screen.blit(large_font.render("Game Over",True,white),position)
		position = (width/2-75, height/2+40)
		screen.blit(small_font.render("[ENTER] to reset",True,white),position)
	#Update the screen
	pygame.display.flip()
	pygame.display.update()
	#Delay to get 30 fps
	clock.tick(30)
