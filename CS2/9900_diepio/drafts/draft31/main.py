'''TODO next steps:
consider what is minimal to make a competitive game.
what if exp was gained for damaging opponents? This might make
offensive strategies more viable.

2. Differentiated exp bricks.
    two-shot yellow squares
    5 shot red triangles
3. display attribute levels on the screen.
Created levelup_text for this and displayLevels function.
Next step is to tidy the leVEL UP printing and display
the button that will boost this level. ALSO display
the experience progress towards next level up and amount
of level ups ready to spend
4. make player upgrades by key press not mouse click.
5. make level ups cost experience.
6. some powerups are still making this freeze
7. do the powerups all work?
8. should put the enemies back in for testing
9. Is there a way to implement cloaking?
Yes, for each NPC, get all objects within vision radius and only
pass those in. Cloaked ships are either not passed in or must be
closer to be seen.
Only draw the objects seen by camera/perspective ship.
Implement zoom in and zoom out.

Move around picking up energy to stay alive, boost recharges
for quick movement, and ammo to keep shooting. Shoot exp
bricks to gain exp and level up basic attributes. Game is done.
Students write an AI!
-save power ups
-upgrade number of slots in which to save powerups
-larger levels
-sound effects of shots and hits
-constant spawn rate so the environment changes
-different movement? Easier to dodge, circle strafe, lead a target?
-angler fish in diep: creates a super high exp brick that the creator cannot shoot or collide with and then cloaks near it. These super high exp bricks do sometimes spawn randomly.

3 lives.

Exp and upgrades.
Be able to upgrade/downgrade friction, recoil, vision radius.

I like the idea of giving students a list of all the food and a list of
all powerups and of all enemies and letting them do distance
calculations to determine what is nearest and what is a priority.

Charge up shot for extra damage and stamina bar for extra
speed both add another layer of strategy.

-diep ammo limitations and ammo pickups, stamina, burst speed, saveable powerups.
-choose ability set at start then write AI. All abilities come on cooldowns so it's less randomly dependent on landing near powerups?

Tactical item pickups that can be used later. Shove out can be used on
a rammer. Teleport can get you out of a tricky spot. Grenade can be
fired into a cluster of enemies.
Make one of the things you can level up storage for powerups.

Keep this initially separate then make a third project
integrating this with maze navigator or a sort of racing game.
'''

import time, pygame, diep_sprite, player, enemy, funcs, sparkle, powerup, random
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
    levelup_text[i] = font.render(levelup_text[i],True,black)

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
                          200,#x
                          200,#y
                          yellow,
                          35,#radius
                          critter_names[i])
    funcs.insertInOrder(npc_critter, all_sprites)
    all_critters.append(npc_critter)
    leader_list.append(npc_critter)


def makeFood(count,color,shape,radius,hit_radius,all_sprites,xp,hp):
    for i in range(count):
        f = diep_sprite.DiepSprite(screen, 0,0,
                    color, radius, 0,#base level
                    draw_shape=shape,
                    draw_heading=False)
        f.experience = xp
        f.resetHealthbar(screen,hp)
        f.collision_radius = hit_radius
        f.teleport()
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


p=powerup.Powerup(screen, 500, 500, white)
funcs.insertInOrder(p, all_sprites)


#Delete dead sprites
def deleteDead():
    for i in reversed(range(len(all_sprites))):
        if all_sprites[i].xs[HP_INDEX] <= 0:
            if all_sprites[i].sprite_type == TYPE_FOOD:
                #Reset the food
                all_sprites[i].reset()
            else:
                del all_sprites[i]
        elif all_sprites[i].sprite_type == TYPE_BULLET and all_sprites[i].timeout<0:
            del all_sprites[i]

def processInputs():
    global done, camera_index
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            #print(event.key) #Print value of key press
            if event.key == 32:#space bar
                camera_index = (camera_index+1)%len(all_critters)
            elif event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
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
                if all_sprites[i].xs[HP_INDEX] <= 0:
                    xp_receiver = all_sprites[j]
                    #bullet give xp to shooter
                    if xp_receiver.sprite_type == TYPE_BULLET:
                        xp_receiver = xp_receiver.shooter
                    xp_receiver.experience += all_sprites[i].getExperienceGiven()
                if all_sprites[j].xs[HP_INDEX] <= 0:
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

def draw():
    screen.fill((0,0,0)) #fill screen with black
    povx = all_critters[camera_index].x
    povy = all_critters[camera_index].y
    for a in all_sprites:
        if a.sprite_type == TYPE_CRITTER and len(a.expiration)>0:
            #Add sparkle on powered up critters
            randcolor = random.randint(0,255),random.randint(0,255),random.randint(0,255)
            temp = sparkle.Sparkle(screen, a.x+random.randint(-100,100),
                        a.y+random.randint(-100,100), randcolor)
            funcs.insertInOrder(temp, all_sprites)
        a.draw(povx, povy, center_on_screen=(a==all_critters[camera_index]))

def displayLeaderboard():
    screen.blit(leader_text, (screen_width-140, 20))
    for i in range(len(leader_list)):
        screen.blit(font.render(leader_list[i].name+': '+str(int(leader_list[i].experience)),
            True,white), (screen_width-140, 45+i*25))

def displayLevels():
    pygame.draw.rect(screen, white , [0,45,250,230])
    for i in range(len(levelup_text)):
        screen.blit(levelup_text[i], (0, 45+i*25))
        #Draw a star for each level of leveled up
        for j in range(all_critters[camera_index].levels[i]):
            pygame.draw.ellipse(screen, green, [150+j*12, 55+i*25, 10,10])

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
