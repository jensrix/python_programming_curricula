import diep_sprite, math, funcs, random, bullet
from constants import *

class Ship(diep_sprite.DiepSprite):
    def __init__(self, screen, x, y, color, radius, name):
        super().__init__(screen, x, y, color, radius, 1,#base level
                        sprite_type=TYPE_CRITTER,
                        draw_healthbar=True)
        self.name=name
        #Delay between shots
        self.refire_count = 0
        #List of timeouts after which some value needs
        #to revert to default. This is used for implementing
        #many of the powerups.
        #self.expiration will be a list of lists. Inner lists will
        #be countdown,stat_index pairs.
        self.expiration = []
        #Use this to limit movement to once per turn so
        #student programmers can't spam the movement commands
        self.can_move = True

    def shootAt(self, x,y):
        if self.refire_count <= 0:
            self.angle = self.angleTo(x,y)
            self.shoot()

    def shootAt(self, target):
        if target is None:
            print('ERROR in shootAt. You cannot shoot at None.')
            return
        if self.refire_count <= 0:
            self.angle = self.angleToSprite(target)
            self.shoot()

    def shoot(self):
        if self.refire_count <= 0:
            self.refire_count = self.xs[REFIRE_DELAY_INDEX]
            if self.xs[BULLET_COUNT_INDEX] == 1:
                self.shootOneBullet(self.angle)
            else:
                spread = math.pi/4
                interval = spread/(self.xs[BULLET_COUNT_INDEX]-1)
                for i in range(self.xs[BULLET_COUNT_INDEX]):
                    self.shootOneBullet(self.angle-spread/2+i*interval)

    def shootOneBullet(self, angle):
        #Shoot a bullet
        spread = self.xs[BULLET_SPREAD_INDEX]
        r = (random.random()-0.5)*2*spread
        dx = math.cos(angle+r)
        r = (random.random()-0.5)*2*spread
        dy = math.sin(angle+r)
        size = self.xs[BULLET_SIZE_INDEX]
        speed = self.xs[BULLET_SPEED_INDEX]
        hp = self.xs[BULLET_HP_INDEX] #penetration
        timeout = self.xs[BULLET_LONGEVITY_INDEX]
        damage = self.xs[BULLET_DAMAGE_INDEX]
        b = bullet.Bullet(self.screen, self.x, self.y, red,
                    size, dx*speed, dy*speed, hp, damage,
                    timeout, self)
        global all_sprites
        funcs.insertInOrder(b, all_sprites)
        #Recoil
        self.dx -= dx*self.xs[RECOIL_INDEX]
        self.dy -= dy*self.xs[RECOIL_INDEX]

    def revert(self,index):
        '''Revert the index stat to default levels.'''
        self.xs[index] = self.getDefault(index)

    def update(self):
        #Cooldown guns and powerups
        self.refire_count -= 1
        #Regen health by taking negative damage
        self.takeDamage( -self.xs[HP_REGEN_INDEX] )
        #Expire temporary stats and abilities
        for i in reversed(range(len(self.expiration))):
            self.expiration[i][0] -= 1
            if self.expiration[i][0] < 0:
                self.revert(self.expiration[i][1])
                del self.expiration[i]
        self.can_move = True #Reset
        super().update()

    def getClosestSprite(self, sprites_in_range, type_list):
        '''Takes a list of sprites in range and a list of
        sprite types. Only returns sprites of the given type.'''
        #Select closest sprite as target
        closest = None
        distance = 2**28
        for s in sprites_in_range:
            #Skip self or self-shot bullets
            if s==self or (s.sprite_type==TYPE_BULLET and s.shooter==self):
                continue
            #Skip sprites other than the desired type
            if s.sprite_type not in type_list:
                continue
            #Update closest
            temp_dist = self.distanceTo(s)
            if temp_dist<distance:
                distance = temp_dist
                closest = s
        return closest

    def getClosestPlayer(self,sprites_in_range):
        return self.getClosestSprite(sprites_in_range, [TYPE_CRITTER])
    def getClosestBullet(self,sprites_in_range):
        return self.getClosestSprite(sprites_in_range, [TYPE_BULLET])
    def getClosestFood(self,sprites_in_range):
        return self.getClosestSprite(sprites_in_range, [TYPE_FOOD])
    def getClosestPowerup(self,sprites_in_range):
        return self.getClosestSprite(sprites_in_range, [TYPE_POWERUP])

    def getAllSpritesInRange(self, sprites_in_range, type_list):
        '''Gets all the sprites of a certain type in range.
        Skips self and self-shot bullets.'''
        to_return = []
        for s in sprites_in_range:
            #Skip self or self-shot bullets
            if s==self or (s.sprite_type==TYPE_BULLET and s.shooter==self):
                continue
            if s.sprite_type in type_list:
                to_return.append(s)
        return to_return

    def getPlayersInRange(self,sprites_in_range):
        return self.getAllSpritesInRange(sprites_in_range,[TYPE_CRITTER])
    def getBulletsInRange(self,sprites_in_range):
        return self.getAllSpritesInRange(sprites_in_range,[TYPE_BULLET])
    def getFoodsInRange(self,sprites_in_range):
        return self.getAllSpritesInRange(sprites_in_range,[TYPE_FOOD])
    def getPowerupsInRange(self,sprites_in_range):
        return self.getAllSpritesInRange(sprites_in_range,[TYPE_POWERUP])

    def moveToward(self, target):
        if target is None:
            print('ERROR in moveToward: target is None')
            return
        self.moveTowardLocation(target.x,target.y)

    def moveTowardLocation(self,x,y):
        if not self.can_move:
            print('WARNING in moveTowardLocation: you already moved once this turn')
            return
        self.can_move = False
        angle = self.angleTo(x,y)
        accel = self.xs[ACCEL_INDEX]
        self.dx += math.cos(angle)*accel
        self.dy += math.sin(angle)*accel

    def fleeFrom(self, target):
        if target is None:
            print('ERROR in fleeFrom: target is None')
            return
        self.fleeFromLocation(target.x,target.y)

    def fleeFromLocation(self,x,y):
        if not self.can_move:
            print('WARNING in fleeFromLocation: you already moved once this turn')
            return
        self.can_move = False
        angle = self.angleTo(x,y)
        accel = self.xs[ACCEL_INDEX]
        self.dx -= math.cos(angle)*accel
        self.dy -= math.sin(angle)*accel

    def moveTowardDirection(self,direction):
        '''direction must be in degrees between 0 and 360'''
        if not self.can_move:
            print('WARNING in moveTowardDirection: you already moved once this turn')
            return
        self.can_move = False
        #Convert direction to an angle in degrees and
        #remember that the world is upside down
        angle = (360-direction)*math.pi/180
        accel = self.xs[ACCEL_INDEX]
        self.dx += math.cos(angle)*accel
        self.dy += math.sin(angle)*accel

