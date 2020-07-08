from constants import *
import sprite

def createLevel(level_num):
    if level_num == -1:
        flags = [(2, 3),(5, 5),(6, 1),(6, 3)]
        player_starts = [(0,0),(1,0),(2,0),(3,0)]
        return flags, 'maps/map00.txt', player_starts
    elif level_num == 0:
        flags = [(2, 3),(5, 5),(6, 1),(6, 3)]
        player_starts = [(0,0),(5,5),(5,6),(5,7)]
        return flags, 'maps/map01.txt', player_starts
    elif level_num == 1:
        flags = [(1, 1),(1, 6),(6, 1),(6, 6)]
        player_starts = [(1,0),(2,0),(3,0),(4,0)]
        return flags, 'maps/level050.txt', player_starts
    elif level_num == 2:
        flags = [(1, 3),(8, 3),(1, 13),(8, 13)]
        player_starts = [(1,0),(2,0),(3,0),(4,0)]
        return flags, 'maps/level300.txt', player_starts

def getRowColChange(direction):
    if not(direction in direction_list):
        print('ERROR: Invalid argument to getRowColChange('+str(direction)+')')
        exit()
    temp_row = 0
    temp_col = 0
    if direction == 'north':
        temp_row -= 1
    elif direction == 'east':
        temp_col += 1
    elif direction == 'south':
        temp_row += 1
    else: #if direction == 'west':
        temp_col -= 1
    return temp_row,temp_col

def isConveyor(board, row, col):
    #Returns True if requested tile is a conveyor
    tile = board[row][col]
    return tile in conveyors or tile in left_turn_conveyors or tile in right_turn_conveyors

def conveysTo(board, row, col):
    '''Returns a triple of row change, col change, and
    rotation, indicating how the requested tile would
    move a robot. All non-conveyor tiles return 0,0,0.'''
    if not isConveyor(board,row,col):
        return 0,0,0
    elif board[row][col] in conveyors:
        index = conveyors.index(board[p.row][p.col])
        direction = direction_list[index]
        row_change,col_change = getRowColChange(direction)
        return row_change,col_change,0
    elif board[row][col] in left_turn_conveyors:
        index = left_turn_conveyors.index(board[p.row][p.col])
        direction = direction_list[index]
        row_change,col_change = getRowColChange(direction)
        return row_change,col_change,-1 #left rotation
    elif board[row][col] in right_turn_conveyors:
        index = right_turn_conveyors.index(board[p.row][p.col])
        direction = direction_list[index]
        row_change,col_change = getRowColChange(direction)
        return row_change,col_change,1 #right rotation

def getPlayerAt(players, row, col):
    '''Returns player at given location or returns None.'''
    for p in players:
        if p.row == row and p.col == col:
            return p
    return None

def outOfBounds(board,row,col):
    return row<0 or col<0 or row>=len(board) or col>=len(board[0])

def canMove(board, players, row, col, direction):
    '''Pre: direction is a string'''
    #Robots can always move out of bounds
    if outOfBounds(board, row, col):
        return True
    #Check indicated direction
    if direction == 'north':
        #Make sure there is no wall to the north
        if board[row][col] != '1wu ' and board[row][col] != '2wur' and board[row][col] != '2wlu':
            #If there is a player to the north...
            if getPlayerAt(players, row-1, col) != None:
                #...then recursively check that it can be moved north
                return canMove(board, players, row-1, col, direction)
            else:
                return True
    elif direction == 'east':
        #Make sure there is no wall to the east
        if board[row][col] != '1wr ' and board[row][col] != '2wur' and board[row][col] != '2wrd':
            #If there is a player to the east...
            if getPlayerAt(players, row, col+1) != None:
                #...then recursively check that it can be moved east
                return canMove(board, players, row, col+1, direction)
            else:
                return True
    elif direction == 'south':
        #Make sure there is no wall to the south
        if board[row][col] != '1wd ' and board[row][col] != '2wrd' and board[row][col] != '2wdl':
            #If there is a player to the south...
            if getPlayerAt(players, row+1, col) != None:
                #...then recursively check that it can be moved south
                return canMove(board, players, row+1, col, direction)
            else:
                return True
    elif direction == 'west':
        #Make sure there is no wall to the west
        if board[row][col] != '1wl ' and board[row][col] != '2wdl' and board[row][col] != '2wlu':
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

def blockedByWall(board, row, col, direction):
    '''Pre: direction is a string
    Post: returns row and column right before the wall or where out of bounds'''
    #Robots can always move out of bounds
    if outOfBounds(board, row, col):
        return row,col
    #Check indicated direction
    if direction == 'north' and board[row][col] != '1wu ' and board[row][col] != '2wur' and board[row][col] != '2wlu':
        return blockedByWall(board, row-1, col, direction)
    elif direction == 'east' and board[row][col] != '1wr ' and board[row][col] != '2wur' and board[row][col] != '2wrd':
        return blockedByWall(board, row, col+1, direction)
    elif direction == 'south' and board[row][col] != '1wd ' and board[row][col] != '2wrd' and board[row][col] != '2wdl':
        return blockedByWall(board, row+1, col, direction)
    elif direction == 'west' and board[row][col] != '1wl ' and board[row][col] != '2wdl' and board[row][col] != '2wlu':
        return blockedByWall(board, row, col-1, direction)
    return row,col

def constructMap(filename):
    # Dictionary mapping tileset abbreviations to file names
    image_dict = {'empt': 'tile-clear.png',
                  'hole': 'tile-hole.png',
                  '1wl ': 'tile-wall-1a.png',
                  '1wu ': 'tile-wall-1b.png',
                  '1wr ': 'tile-wall-1c.png',
                  '1wd ': 'tile-wall-1d.png',
                  'chek': 'tile-hammer-wrench.png',
                  'cv1d': 'tile-conveyor-1a.png',
                  'cv1l': 'tile-conveyor-1b.png',
                  'cv1u': 'tile-conveyor-1c.png',
                  'cv1r': 'tile-conveyor-1d.png',

                  'cvlr': 'tile-conveyor-1-turnleft_a.png',
                  'cvld': 'tile-conveyor-1-turnleft_b.png',
                  'cvll': 'tile-conveyor-1-turnleft_c.png',
                  'cvlu': 'tile-conveyor-1-turnleft_d.png',
                  'cvrr': 'tile-conveyor-1-turnright_a.png',
                  'cvrd': 'tile-conveyor-1-turnright_b.png',
                  'cvrl': 'tile-conveyor-1-turnright_c.png',
                  'cvru': 'tile-conveyor-1-turnright_d.png',

                  '2wur': 'tile-wall-2a.png',
                  '2wrd': 'tile-wall-2b.png',
                  '2wdl': 'tile-wall-2c.png',
                  '2wlu': 'tile-wall-2d.png'
                  }
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
            row_array_img.append(sprite.Sprite(i*tile_width, len(images)*tile_width, img))
            row_array_name.append(array[i])
        images.append(row_array_img)
        board.append(row_array_name)
        line = file_handle.readline()
        line = line.strip()
    return images,board

def boardActions(board, players, flags):
    #Convey any players on conveyors
    for p in players:
        if board[p.row][p.col] in conveyors:
            index = conveyors.index(board[p.row][p.col])
            direction = direction_list[index]
            p.forceMove(board, players, direction, flags)
        elif board[p.row][p.col] in left_turn_conveyors:
            index = left_turn_conveyors.index(board[p.row][p.col])
            direction = direction_list[index]
            p.forceMove(board, players, direction, flags)
            p.rotateLeft()
        elif board[p.row][p.col] in right_turn_conveyors:
            index = right_turn_conveyors.index(board[p.row][p.col])
            direction = direction_list[index]
            p.forceMove(board, players, direction, flags)
            p.rotateRight()

def drawAll(surface, images, players, flags, clock):
    surface.fill(black)
    for row in images:
        for col in row:
            col.draw(surface)
    for p in players:
        p.draw()
    for f in flags:
        f.draw()
    pygame.display.flip()
    # Delay to get desired fps
    clock.tick(fps)

