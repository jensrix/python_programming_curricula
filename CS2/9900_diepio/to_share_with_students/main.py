import time, pygame, player, enemy, funcs, animation_manager, powerup, food
import ai_for_testing
from constants import *


pygame.init()

#Initialize variables:
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width,screen_height))
font = pygame.font.SysFont('Arial', 25)
#Create leaderboard text
leader_text = font.render('LEADERBOARD',True,white)
#Create levelup texts
for i in range(len(levelup_text)):
    levelup_text[i] = font.render('('+str(i+1)+')'+levelup_text[i],True,white)

critter = player.PlayerCritter(screen,
                        500,#x
                        500,#y
                        blue,
                        35,#radius
                        "Neal")
funcs.insertInOrder(critter, all_sprites)
#Maintain a list of all critters exclusively.
#Initially this is mostly for the camera
all_critters = [critter]
leader_list = [critter]
camera_index = 0
critter_names = ['Bill', 'Ted', 'Socrates']

for i in range(enemy_count):
    npc_critter = enemy.EnemyCritter(screen,
                          200*i,#x
                          200,#y
                          yellow,
                          35,#radius
                          critter_names[i])
    funcs.insertInOrder(npc_critter, all_sprites)
    all_critters.append(npc_critter)
    leader_list.append(npc_critter)


#Create an AI for testing
from random import randint
npc_critter = ai_for_testing.AI(screen,
                          randint(0,2000),#x
                          randint(0,2000),#y
                          red,
                          35,#radius
                          'aggro')
npc_critter.ai_type = 0
funcs.insertInOrder(npc_critter, all_sprites)
all_critters.append(npc_critter)
leader_list.append(npc_critter)


def makeFood(count,color,shape,radius,hit_radius,all_sprites,xp,hp):
    for i in range(count):
        f = food.Food(screen, color,radius,
                    hp, xp, hit_radius, shape)
        funcs.insertInOrder(f, all_sprites)

#Lowest xp food
makeFood(red_food_count,red,SHAPE_TRI,
        red_food_radius,red_food_hit_radius,
        all_sprites,red_food_xp,red_food_hp)
#Medium xp food
makeFood(yellow_food_count,yellow,SHAPE_RECT,
        yellow_food_radius,yellow_food_hit_radius,
        all_sprites,yellow_food_xp,yellow_food_hp)
#Largest xp food
makeFood(blue_food_count,blue,SHAPE_PENTA,
        blue_food_radius,blue_food_hit_radius,
        all_sprites,blue_food_xp,blue_food_hp)


#Make one powerup
#p=powerup.Powerup(screen, 500, 500, white)
#p.teleport()
#funcs.insertInOrder(p, all_sprites)

#Testing all powerups
for i in range(len(powerup_options)):
    p=powerup.Powerup(screen, i*200, 500, white)
    p.power = powerup_options[i]
    p.text = font.render(p.power, True, white)
    funcs.insertInOrder(p, all_sprites)


am = animation_manager.AnimationManager()

#Delete dead sprites
def deleteDead():
    for i in reversed(range(len(all_sprites))):
        if all_sprites[i].hit_points <= 0:
            if all_sprites[i].sprite_type == TYPE_FOOD:
                #Reset the food
                all_sprites[i].reset()
            else:
                del all_sprites[i]
        elif all_sprites[i].sprite_type == TYPE_BULLET and all_sprites[i].timeout<0:
            del all_sprites[i]

def processInputs(): #handle events handleEvents
    global done, camera_index
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            print(event.key) #Print value of key press
            if event.key == 32:#space bar
                camera_index = (camera_index+1)%len(all_critters)
                #Skip dead critters
                while all_critters[camera_index].hit_points<=0:
                    camera_index = (camera_index+1)%len(all_critters)
            elif event.key == pygame.K_ESCAPE:
                done = True
            elif 49 <= event.key <= 57: #Level up
                all_critters[camera_index].levelUp(event.key-49)
            elif event.key == 99: #c key
                #Testing ship type change: revert to default
                player = all_critters[camera_index]
                player.revertToBaseline = player.revertAll
                player.revertToBaseline()
            elif event.key == 118: #v key
                #Testing ship type change: fire seeking bullets
                player = all_critters[camera_index]
                player.revertToBaseline = player.becomeSeekerShooter
                player.revertToBaseline()
            elif event.key == 98: #b key
                #Testing ship type change
                player = all_critters[camera_index]
                player.revertToBaseline = player.becomeRammer
                player.revertToBaseline()
            elif event.key == 110: #n key
                #Testing ship type change
                player = all_critters[camera_index]
                player.revertToBaseline = player.becomeMachineGun
                player.revertToBaseline()
            elif event.key == 109: #m key
                #Testing ship type change
                player = all_critters[camera_index]
                player.revertToBaseline = player.becomeSniper
                player.revertToBaseline()

    if pygame.mouse.get_pressed()[0]:
        critter.shoot()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        critter.dy -= critter.xs[ACCEL_INDEX]
    if keys[pygame.K_DOWN]:
        critter.dy += critter.xs[ACCEL_INDEX]
    if keys[pygame.K_LEFT]:
        critter.dx -= critter.xs[ACCEL_INDEX]
    if keys[pygame.K_RIGHT]:
        critter.dx += critter.xs[ACCEL_INDEX]

#Sorting pass of all_sprites
def sortSprites():
    for i in range(len(all_sprites)-1):
        if all_sprites[i].rect.left > all_sprites[i+1].rect.left:
            temp = all_sprites[i]
            all_sprites[i] = all_sprites[i+1]
            all_sprites[i+1] = temp

#Collision check between sprites
def checkCollisions():
    for i in range(len(all_sprites)-1):
        for j in range(i+1,len(all_sprites)):
            #For efficiency abort loop if nothing more is in range
            if all_sprites[i].rect.right < all_sprites[j].rect.left:
                break
            #check for collision
            if all_sprites[i].collidedWith(all_sprites[j]):
                #Prevent bullet on bullet damage when the bullets
                #are fired by the same person
                if all_sprites[i].sprite_type==TYPE_BULLET and all_sprites[j].sprite_type==TYPE_BULLET and all_sprites[i].shooter==all_sprites[j].shooter:
                    continue
                #Shove each other out
                all_sprites[i].shoveOut(all_sprites[j])
                all_sprites[j].shoveOut(all_sprites[i])
                #Prevent food on food damage
                if all_sprites[i].sprite_type == TYPE_FOOD and all_sprites[j].sprite_type == TYPE_FOOD:
                    continue
                #Check for NPC collision with powerup
                elif (all_sprites[i].sprite_type == TYPE_CRITTER and all_sprites[j].sprite_type == TYPE_POWERUP):
                    all_sprites[j].applyPower(all_sprites[i])
                    break
                elif (all_sprites[i].sprite_type == TYPE_POWERUP and all_sprites[j].sprite_type == TYPE_CRITTER):
                    all_sprites[i].applyPower(all_sprites[j])
                    break
                #Deal damage
                all_sprites[i].takeDamage(all_sprites[j].xs[COLLISION_DAMAGE_INDEX])
                all_sprites[j].takeDamage(all_sprites[i].xs[COLLISION_DAMAGE_INDEX])
                #If anyone died, give experience to the other.
                if all_sprites[i].hit_points <= 0:
                    xp_receiver = all_sprites[j]
                    #bullet give xp to shooter
                    if xp_receiver.sprite_type == TYPE_BULLET:
                        xp_receiver = xp_receiver.shooter
                    xp_receiver.experience += all_sprites[i].getExperienceGiven()
                if all_sprites[j].hit_points <= 0:
                    xp_receiver = all_sprites[i]
                    #bullet give xp to shooter
                    if xp_receiver.sprite_type == TYPE_BULLET:
                        xp_receiver = xp_receiver.shooter
                    xp_receiver.experience += all_sprites[j].getExperienceGiven()

def update():
    for a in all_sprites:
        if a.sprite_type == TYPE_CRITTER:
            #Implement vision by only providing information
            #on sprites that are within the vision radius
            visible_sprites = funcs.getSpritesInRange(all_sprites, a.xs[VISION_RADIUS_INDEX], a.x,a.y)
            a.update(visible_sprites)
        else:
            a.update()
    am.update()

def draw():
    screen.fill((0,0,0)) #fill screen with black
    povx = all_critters[camera_index].x
    povy = all_critters[camera_index].y
    for a in all_sprites:
        if a.sprite_type == TYPE_CRITTER and len(a.expiration)>0:
            #Add sparkle on powered up critters
            am.addSpark(screen,a.x,a.y)
        a.draw(povx, povy, center_on_screen=(a==all_critters[camera_index]))
    am.draw(povx, povy)

def displayLeaderboard():
    screen.blit(leader_text, (screen_width-160, 20))
    for i in range(len(leader_list)):
        x = screen_width-140
        y = 45+i*25
        screen.blit(font.render(leader_list[i].name+': '+str(int(leader_list[i].experience)),
            True,white), (x,y))
        #Dead players get a line through their name
        if leader_list[i].hit_points<= 0:
             pygame.draw.line(screen,white,(x,y+15),(screen_width,y+15),2)

def displayLevels():
    #pygame.draw.rect(screen, white , [0,45,250,230])
    for i in range(len(levelup_text)):
        x = 0
        y = 45+i*25 #55+i*26
        #Draw a star for each level of leveled up
        for j in range(all_critters[camera_index].levels[i]):
            x = j*12
            pygame.draw.ellipse(screen, green, [x,y+10,10,10])
        #Draw the name of the level up
        screen.blit(levelup_text[i], (x+10,y))

def displayExperience():
    '''Display an experience bar and numbers at top of the
    screen'''
    selected = all_critters[camera_index]
    current_level = selected.getCurrentLevel()
    overflow, potential_level = selected.getOverflowExperience()
    exp_to_next_level = level_cutoffs[potential_level]

    x=screen_width/2-100

    #Display unspent level up points
    temp = potential_level-current_level
    if temp > 0:
        text=font.render('Unspent:'+str(temp),True,yellow)
        screen.blit(text,(x,22))

    #Display experience bar
    total_width = 300
    y=2
    border = 2
    height = 22
    pygame.draw.rect(screen, yellow, (x,y,total_width,height), border)
    width = int(total_width*overflow/exp_to_next_level)
    pygame.draw.rect(screen, mid_blue, (x+border,y+border,width,height-2*border+1))

    #Display current experience and amount to next level
    text=font.render(str(overflow)+'/'+str(exp_to_next_level),True,yellow)
    screen.blit(text,(x+4,-1))

def sortLeaderboard():
    for i in range(len(leader_list)-1):
        if leader_list[i].experience < leader_list[i+1].experience:
            temp=leader_list[i]
            leader_list[i]=leader_list[i+1]
            leader_list[i+1]=temp


#These are for seeing what's eating up all the processor time
sort_time = 0
collision_time = 0
delete_dead_time = 0
update_time = 0
draw_time = 0
leaderboard_time = 0

#Main program loop
done = False
while not done:
    processInputs()
    #Sorting pass of all_sprites. If we do one bubble sort per frame,
    #sprites ought to stay roughly sorted.
    start = time.time()
    sortSprites()
    sort_time+= time.time()-start
    #Collision check between sprites
    start = time.time()
    checkCollisions()
    collision_time+= time.time()-start
    #Delete dead sprites
    start = time.time()
    deleteDead()
    delete_dead_time+= time.time()-start
    #Update all sprites
    start = time.time()
    update()
    update_time+= time.time()-start
    #Draw all sprites
    start = time.time()
    draw()
    draw_time+= time.time()-start
    #Sort the leaderboard
    start = time.time()
    sortLeaderboard()
    #Display leaderboard and levels
    displayLeaderboard()
    displayLevels()
    displayExperience()
    leaderboard_time+= time.time()-start
    pygame.display.flip()
    #Delay to get 60 fps
    clock.tick(60)
pygame.quit()

total = sort_time+collision_time+delete_dead_time+update_time+draw_time+leaderboard_time
print('Sorting time: '+str(int(100*sort_time/total)))
print('Collision time: '+str(int(100*collision_time/total)))
print('Delete dead time: '+str(int(100*delete_dead_time/total)))
print('Update time: '+str(int(100*update_time/total)))
print('Draw time: '+str(int(100*draw_time/total)))
print('Leaderboard time: '+str(int(100*leaderboard_time/total)))
