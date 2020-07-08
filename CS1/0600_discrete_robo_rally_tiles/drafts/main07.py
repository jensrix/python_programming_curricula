'''
1
2
3
4
5 robots blink before they move?
6 wait is an option
7 sensing environment?
8 add in conveyors
9 make conveyors convey after each move
10 add in L-shaped walls
11 lazers? repairs? health bars?
12
13 boost moves? other special moves
14 put flags on the field, bots have to each collect all flags. flags then display also on the bot like they are being carried.
15 more than one player can occupy a checkpoint by being reset to it. I'm ok with this for now.
'''
import pygame, math, random

pygame.init()
initial_width = 144
initial_height = 144

scaling = 0.5

font = pygame.font.SysFont('Arial', int(48*scaling))

tile_width = int(initial_width*scaling)
tile_height = int(initial_height*scaling)

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
yellow = (255,255,0)

direction_list = ['north', 'east', 'south', 'west']

options = ['move','left','right']


def getPlayerAt(players, row, col):
    '''Returns player at given location or returns None.'''
    for p in players:
        if p.row == row and p.col == col:
            return p
    return None

def outOfBounds(board,row,col):
    return row<0 or col<0 or row>=len(board) or col>=len(board[0])

def canMove(board, players, row, col, direction):
    #Robots can always move out of bounds
    if outOfBounds(board, row, col):
        return True
    #Check indicated direction
    if direction == 0: #north
        #Make sure there is no wall to the north
        if board[row][col] != '1wu ':
            #If there is a player to the north...
            if getPlayerAt(players, row, col) != None:
                #...then recursively check that it can be moved north
                return canMove(board, players, row-1, col, direction)
            else:
                return True
    elif direction == 1: #east
        #Make sure there is no wall to the east
        if board[row][col] != '1wr ':
            #If there is a player to the east...
            if getPlayerAt(players, row, col+1) != None:
                #...then recursively check that it can be moved east
                return canMove(board, players, row, col+1, direction)
            else:
                return True
    elif direction == 2: #south
        #Make sure there is no wall to the south
        if board[row][col] != '1wd ':
            #If there is a player to the south...
            if getPlayerAt(players, row+1, col) != None:
                #...then recursively check that it can be moved south
                return canMove(board, players, row+1, col, direction)
            else:
                return True
    elif direction == 3: #west
        #Make sure there is no wall to the west
        if board[row][col] != '1wl ':
            #If there is a player to the west...
            if getPlayerAt(players, row, col-1) != None:
                #...then recursively check that it can be moved west
                return canMove(board, players, row, col-1, direction)
            else:
                return True
    else:
        print('ERROR This should be impossible.')
        exit()
    return False

class Robot:
    def __init__(self, screen, row, col, color):
        self.screen = screen
        self.row = row
        self.col = col
        self.color = color
        self.sides = 3
        self.radius = 40*scaling
        self.direction = 0
        self.checkpoint = (row,col)
        self.next_action = ''
        self.text = font.render('', True,yellow)
        self.blink = False
    def doAction(self, board, players, action):
        if action == 'left':
            self.rotateLeft()
        elif action == 'right':
            self.rotateRight()
        elif action == 'move':
            self.move(board, players)
        self.next_action = ''
        self.text = font.render('', True,yellow)
    def update(self, board):
        r = random.randint(0,2)
        if r == 0:
            self.next_action = 'left'
        elif r == 1:
            self.next_action = 'right'
        else:
            self.next_action = 'move'
        self.text = font.render(self.next_action, True,yellow)
        return self.next_action
    def rotateLeft(self):
        self.direction -= 1
        if self.direction < 0:
            self.direction = len(direction_list)-1
    def rotateRight(self):
        self.direction = (self.direction+1)%len(direction_list)
    def forceMove(self, players, direction):
        temp_row = self.row
        temp_col = self.col
        if direction == 0: #north
            temp_row -= 1
        elif direction == 1: #east
            temp_col += 1
        elif direction == 2: #south
            temp_row += 1
        elif direction == 3: #west
            temp_col -= 1
        #Check for another player that got shoved and
        #pass the shove down the line.
        p = getPlayerAt(players, temp_row, temp_col)
        if p != None:
            p.forceMove(players, direction)
        #Complete the move
        self.row = temp_row
        self.col = temp_col
        self.eventAtLocation(board)
    def move(self, board, players):
        if canMove(board, players, self.row, self.col, self.direction):
            temp_row = self.row
            temp_col = self.col
            if self.direction == 0: #north
                temp_row -= 1
            elif self.direction == 1: #east
                temp_col += 1
            elif self.direction == 2: #south
                temp_row += 1
            elif self.direction == 3: #west
                temp_col -= 1
            #If someone else is in this space, shove them.
            p = getPlayerAt(players, temp_row, temp_col)
            if p != None:
                p.forceMove(players, self.direction)
            #Complete the move
            self.row = temp_row
            self.col = temp_col
            self.eventAtLocation(board)
    def eventAtLocation(self, board):
        '''Check for and activate any event at current location'''
        #Check for off the board and reset to a checkpoint
        if outOfBounds(board,self.row,self.col):
            self.row, self.col = self.checkpoint
        #Check for falling in a hole
        elif board[self.row][self.col] == 'hole':
            print('Fell in a hole. Reset to last checkpoint')
            self.row, self.col = self.checkpoint
        #Update our checkpoint if we landed on a checkpoint
        elif board[self.row][self.col] == 'chek':
            self.checkpoint = (self.row, self.col)
    def getCenter(self):
        offset_x = self.col*tile_width + tile_width/2
        offset_y = self.row*tile_height + tile_height/2
        return offset_x, offset_y
    def getCorners(self):
        #Returns list of points to draw the ship
        points = []
        offset_x, offset_y = self.getCenter()
        heading = 0
        if self.direction == 0:
            heading = -math.pi/2
        elif self.direction == 2:
            heading = math.pi/2
        elif self.direction == 3:
            heading = math.pi
        #Nose
        angle = heading+math.pi*2
        x = offset_x + math.cos(angle)*self.radius*1.5
        y = offset_y + math.sin(angle)*self.radius*1.5
        points.append([x, y])
        #wing 1
        angle = heading+math.pi*2*(1.2/self.sides)
        x = offset_x + math.cos(angle)*self.radius
        y = offset_y + math.sin(angle)*self.radius
        points.append([x, y])
        #rear
        angle = heading+math.pi
        x = offset_x + math.cos(angle)*self.radius*0.5
        y = offset_y + math.sin(angle)*self.radius*0.5
        points.append([x, y])
        #wing 2
        angle = heading+math.pi*2*(1.8/self.sides)
        x = offset_x + math.cos(angle)*self.radius
        y = offset_y + math.sin(angle)*self.radius
        points.append([x, y])
        return points
    def draw(self):
        c = self.color
        if self.blink:
            c = black
        #Draw outline of ship.
        points = self.getCorners()
        pygame.draw.polygon(self.screen, c,
                            points,int(scaling*8))
        #Draw current action
        offset_x, offset_y = self.getCenter()
        self.screen.blit(self.text, (offset_x, offset_y))

class Sprite:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

def constructMap(filename):
    # Dictionary mapping tileset abbreviations to file names
    image_dict = {'empt': 'tile-clear.png',
                  'hole': 'tile-hole.png',
                  '1wl ': 'tile-wall-1a.png',
                  '1wu ': 'tile-wall-1b.png',
                  '1wr ': 'tile-wall-1c.png',
                  '1wd ': 'tile-wall-1d.png',
                  'chek': 'tile-hammer-wrench.png'}
    # Open file to read in text representation of the map
    file_handle = open(filename, 'r')
    line = file_handle.readline()
    line = line.strip()
    images = []  # 2d array of sprites
    board = []   # 2d array of tile names
    while line:
        array = line.split(',')
        row_array_img = []
        row_array_name = []
        for i in range(len(array)):
            img = pygame.image.load('tiles/'+image_dict[array[i]])
            # Scale image
            img = pygame.transform.scale(img, (tile_width, tile_height))
            row_array_img.append(Sprite(i*tile_width, len(images)*tile_width, img))
            row_array_name.append(array[i])
        images.append(row_array_img)
        board.append(row_array_name)
        line = file_handle.readline()
        line = line.strip()
    return images,board



def drawAll(surface, players):
    surface.fill(black)
    for row in images:
        for col in row:
            col.draw(surface)
    for p in players:
        p.draw()
    pygame.display.flip()
    # Delay to get 10 fps
    clock.tick(10)


#images is a 2d array of images
#board is a 2d array of the names of tiles
images,board = constructMap('maps/map01.txt')

board_width = len(board[0])
board_height = len(board)
map_width = int(board_width*tile_width)
map_height = int(board_height*tile_height)

clock = pygame.time.Clock()
surface = pygame.display.set_mode((map_width, map_height))

player1 = Robot(surface, 0, 0, white)
player2 = Robot(surface, 4, 3, red)
player3 = Robot(surface, 4, 4, red)
player4 = Robot(surface, 4, 5, red)
player_list = [player1, player2, player3, player4]

#Use this list for ordering actions
action_list = []

# Draw all images on the surface
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == 32: #space bar
                #Reset the action list for the next round
                if len(action_list) == 0:
                    #All players decide what they want to do
                    for p in player_list:
                        action_list.append([p, p.update(board)])
                    #Randomize ordering of actions
                    random.shuffle(action_list)
                else:
                    #Take the next action
                    player, action = action_list.pop()
                    #blink to indicate actor
                    for i in range(6):
                        player.blink = not player.blink
                        print('blinking '+str(player.blink))
                        drawAll(surface, player_list) #Draw and pause
                    #Perform action
                    player.doAction(board, player_list, action)
            elif event.key == pygame.K_RIGHT:
                player_list[0].rotateRight()
            elif event.key == pygame.K_LEFT:
                player_list[0].rotateLeft()
            elif event.key == pygame.K_UP:
                player_list[0].move(board, player_list)
    drawAll(surface, player_list) #Draw and pause
pygame.quit()