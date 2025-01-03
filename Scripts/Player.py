import pygame
import math
import random
from Scripts.Particles import Particle
from Scripts.Sparks import Spark
from Scripts.Utilities import LoadImage
from Scripts.Entities import PhysicsEntity


class Player(PhysicsEntity):
    def __init__(self, game, position, size, hp=100):
        super().__init__(game=game, entityType='ronin', position=position, size=size, hp=hp)
        self.airtime = 0
        self.jumps = 2
        self.wallSlide = False
        self.dashing = 0    # Timer for how long the player can dash
        self.dashDone = True

        self.hit = False
        self.attacking = False
        self.attackCount = 1
        self.attackType = [False, False]

        self.currentHealth = hp
        self.healthBarLength = 250
        self.healthRatio = hp / self.healthBarLength
        self.healthChangeSpeed = 0.5

        self.healthBarImage = LoadImage('UI/health_bar.png', colorkey=(255, 255, 255))
        self.healthBarTopLeft = (54, 39)
        self.barMaxWidth = 152
        self.barHeight = 4

    def Update(self, tilemap, movement=(0, 0)):
        super().Update(tilemap, movement=movement)

        self.airtime += 1

        if self.airtime > 1000:
            self.game.dead += 1

        if self.collisions['down']:
            self.airtime = 0
            self.jumps = 2

        self.wallSlide = False
        if (self.collisions['right'] or self.collisions['left']) and self.airtime > 4 and not self.attacking:
            self.wallSlide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
        if not self.attacking:
            if not self.wallSlide:
                if self.dashDone:
                    if self.airtime > 4:
                        self.SetAction('jump')
                    elif movement[0] != 0:
                        self.SetAction('run')
                    else:
                        self.SetAction('idle')
            else:
                self.SetAction('wall_slide')
        else:
            if self.attackType[0]:
                self.SetAction('attack1')
            if self.attackType[1]:
                self.SetAction('attack2')
            if self.animation.IsDone():
                self.attacking = False

        # Working on the particle effect of the dash
        if abs(self.dashing) in {70, 50}:   # 70 represents the start of dash and 50 represents the end
            for i in range(0, 10):
                if abs(self.dashing) == 70:
                    angle = random.random() * math.pi * 2   # Generates a random angle in radians
                    speed = random.random() * 0.5 + 0.5     # Generates a random speed
                    # Calculates the particles velocity
                    particleVelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                    self.game.particles.append(Particle(self.game, 'base', self.Rectangle().center,
                                                        velocity=particleVelocity, frame=random.randint(0, 7)))
                else:
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.Rectangle().center, angle, 2 + random.random(),
                                                  colour=(242, 15, 52)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.dashDone = False
            self.velocity[0] = abs(self.dashing) / self.dashing * 4
            self.SetAction('dash')
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
                self.dashDone = True
                # Does particle for stream of dash
                particleVelocity = [abs(self.dashing) / self.dashing * 2 * random.random(), 0]
                self.game.particles.append(Particle(self.game, 'base', self.Rectangle().center,
                                                    velocity=particleVelocity, frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def Attack(self):
        self.game.sfx['sword'].play()
        self.attacking = True
        if self.flip:
            attackHitbox = pygame.Rect(self.Rectangle().centerx, self.Rectangle().y,
                                       -1*self.Rectangle().width, self.Rectangle().height)
        else:
            attackHitbox = pygame.Rect(self.Rectangle().centerx, self.Rectangle().y,
                                       1*self.Rectangle().width, self.Rectangle().height)
        if self.attackCount >= 2:
            self.attackCount = 0
        if self.attackCount % 2 == 0:
            self.attackType[0] = True
            self.attackType[1] = False
        else:
            self.attackType[0] = False
            self.attackType[1] = True
        for enemy in self.game.enemies:
            if attackHitbox.colliderect(enemy.Rectangle()):
                self.hit = True
        return attackHitbox

    def Jump(self):
        if self.wallSlide:
            if self.flip and self.lastMovement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.airtime = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.lastMovement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.airtime = 5
                self.jumps = max(0, self.jumps - 1)
                return True

        elif self.jumps:
            self.velocity[1] = -3.5
            self.jumps -= 1
            self.airtime = 5
            return True

    def Dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -70
            else:
                self.dashing = 70

    def HealthBar(self, surface, offset=(0, 0)):
        # transitionWidth = 0
        # transitionColour = (255, 0, 0)
        #
        # if self.currentHealth < self.targetHealth:
        #     self.currentHealth += self.healthChangeSpeed
        #     transitionWidth = int((self.targetHealth - self.currentHealth) / self.healthRatio)
        #     transitionColour = (0, 255, 0)
        # if self.currentHealth > self.targetHealth:
        #     self.currentHealth -= self.healthChangeSpeed
        #     transitionWidth = int((self.targetHealth - self.currentHealth) / self.healthRatio)
        #     transitionColour = (255, 255, 0)
        #
        # healthBarRectangle = pygame.Rect(5, 15, self.currentHealth / self.healthRatio, 15)
        # transitionBarRectangle = pygame.Rect(healthBarRectangle.right, 45, transitionWidth, 25)
        # pygame.draw.rect(surface, (255, 0, 0), healthBarRectangle)
        # # pygame.draw.rect(surface, transitionColour, transitionBarRectangle)
        # pygame.draw.rect(surface, (255, 255, 255), (5, 15, self.healthBarLength, 15), 4)
        surface.blit(self.healthBarImage, (20, 10))
        currentHealthRatio = self.targetHealth / self.hitPoints
        currentBarWidth = self.barMaxWidth * currentHealthRatio
        healthBarRectangle = pygame.Rect(self.healthBarTopLeft, (currentBarWidth, self.barHeight))
        pygame.draw.rect(surface, (255, 0, 0), healthBarRectangle)


    def Render(self, surface, offset=(0, 0)):
        self.HealthBar(surface, offset)
        super().Render(surface, offset)
