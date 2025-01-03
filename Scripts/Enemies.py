import pygame
import math
import random
from Scripts.Particles import Particle
from Scripts.Sparks import Spark

from Scripts.Entities import PhysicsEntity

class Enemy(PhysicsEntity):
    def __init__(self, game, position, size, hp=100):
        super().__init__(game=game, entityType='enemy', position=position, size=size, hp=hp)
        self.walking = 0    # Timer for how long the enemy will walk for
        self.loadAttack = False
        self.attackTimer = 0
        self.stillAttacking = False
        self.showingHealth = False

        self.currentHealth = hp
        self.healthBarLength = 50
        self.healthRatio = hp / self.healthBarLength
        self.healthChangeSpeed = 0.5

        self.dead = False

    def Update(self, tilemap, movement=(0, 0)):
        if self.walking:    # If the characters walking for more than 0 seconds
            if tilemap.SolidCheck((self.Rectangle().centerx + (-7 if self.flip else 7), self.position[1] + 25)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    if self.flip:
                        movement = (movement[0] - 0.15, movement[1])
                    else:
                        movement = (movement[0] + 0.15, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                distance = (self.game.player.position[0] - self.position[0],
                            self.game.player.position[1] - self.position[1])
                self.Attack(distance)
        elif random.random() < 0.005:
            self.walking = random.randint(30, 120)

        if abs(self.game.player.dashing):
            if self.Rectangle().colliderect(self.game.player.Rectangle()):
                self.game.sfx['player_hit'].play()
                self.GetDamage(3)
                self.game.screenshake = max(10, self.game.screenshake)
                self.showingHealth = True
                for i in range(0, 5):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.Rectangle().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'base', self.Rectangle().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
        if self.currentHealth == 0:
            self.dead = True
        if self.dead:
            for i in range(0, 30):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.Rectangle().center, angle, 2 + random.random()))
                self.game.particles.append(Particle(self.game, 'base', self.Rectangle().center,
                                                    velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                              math.sin(angle + math.pi) * speed * 0.5],
                                                    frame=random.randint(0, 7)))
            self.game.sparks.append(Spark(self.Rectangle().center, 0, 5 + random.random()))
            self.game.sparks.append(Spark(self.Rectangle().center, math.pi, 5 + random.random()))
            return True

        super().Update(tilemap, movement=movement)

        if movement[0] != 0:
            self.SetAction('run')
        else:
            self.SetAction('idle')

    def TakeDamage(self, playerAttackHitbox):
        if self.game.player.hit:
            if playerAttackHitbox.colliderect(self.Rectangle()):
                self.game.sfx['enemy_hit'].play()
                self.GetDamage(25)
                self.game.player.hit = False
                self.showingHealth = True
                self.game.screenshake = max(10, self.game.screenshake)
                for i in range(0, 5):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.Rectangle().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'base', self.Rectangle().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))

    def Attack(self, distance):
        if abs(distance[1]) < 16:
            if self.flip and distance[0] < 0:
                self.game.sfx['shoot'].play()
                self.game.projectiles.append(
                    [[self.Rectangle().centerx - 7, self.Rectangle().centery + 7], self.flip, -1.5, 0])
                for i in range(0, 4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                              2 + random.random())
                    )
            if not self.flip and distance[0] > 0:
                self.game.sfx['shoot'].play()
                self.game.projectiles.append(
                    [[self.Rectangle().centerx - 7, self.Rectangle().centery + 7], self.flip, 1.5, 0])
                for i in range(0, 4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                              2 + random.random())
                    )
                    


    def HealthBar(self, surface, offset=(0, 0)):
        transitionWidth = 0
        transitionColour = (255, 0, 0)

        if self.currentHealth < self.targetHealth:
            self.currentHealth += self.healthChangeSpeed
            transitionWidth = int((self.targetHealth - self.currentHealth) / self.healthRatio)
            transitionColour = (0, 255, 0)
        if self.currentHealth > self.targetHealth:
            self.currentHealth -= self.healthChangeSpeed
            transitionWidth = int((self.targetHealth - self.currentHealth) / self.healthRatio)
            transitionColour = (255, 255, 0)

        healthBarRectangle = pygame.Rect(self.position[0] - offset[0] - 14,
                                         self.position[1] - offset[1] - 32,
                                         self.currentHealth / self.healthRatio, 5)
        transitionBarRectangle = pygame.Rect(healthBarRectangle.right,
                                             self.position[1] - offset[1] - 32,
                                             transitionWidth, 5)
        pygame.draw.rect(surface, (255, 0, 0), healthBarRectangle)
        pygame.draw.rect(surface, transitionColour, transitionBarRectangle)
        pygame.draw.rect(surface, (255, 255, 255), (self.position[0] - offset[0] - 14,
                                                    self.position[1] - offset[1] - 32,
                                                    self.healthBarLength, 5), 1)

    def Render(self, surface, offset=(0, 0)):
        if self.showingHealth:
            self.HealthBar(surface, offset)
        super().Render(surface, offset)

        if self.flip:
            surface.blit(pygame.transform.flip(self.game.assets['gun'], True, False),
                         (self.Rectangle().centerx - 16 - offset[0],
                          self.Rectangle().centery - offset[1] - 15))
        else:
            surface.blit(self.game.assets['gun'], (self.Rectangle().centerx - offset[0],
                                                   self.Rectangle().centery - offset[1] - 15))
