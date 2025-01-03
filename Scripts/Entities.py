import pygame


# Class for all objects that follow physics
class PhysicsEntity:
    # Initialising all the data for the class
    def __init__(self, game, entityType, position, size, hp=100):
        self.game = game
        self.entityType = entityType
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.animationOffset = (-3, -3)
        self.flip = False
        self.SetAction('idle')

        self.lastMovement = [0, 0]

        self.hitPoints = hp
        self.targetHealth = hp
        self.dead = False

    # Creates a rectangle around the entity
    def Rectangle(self, offset=(0,0)):
        return pygame.Rect(self.position[0] - offset[0], self.position[1] - offset[1], self.size[0], self.size[1])

    def SetAction(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.entityType + '_' + self.action].Copy()

    def Update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        # Calculates the current frames movement by taking the movement array
        # and adding it to the velocity of the player
        frameMovement = [movement[0] + self.velocity[0], movement[1] + self.velocity[1]]

        # Updates the movement of entity after calculating the frames movement as well as setup collisions
        self.position[0] += frameMovement[0] * 2.5
        entityRectangle = self.Rectangle()
        rectangles, tileTypes = tilemap.PhysicsRectsAround(self.position)
        for i in range(len(rectangles)):
            if entityRectangle.colliderect(rectangles[i]):
                if frameMovement[0] > 0 and tileTypes[i] != 'platform':  # If the entity is moving right
                    entityRectangle.right = rectangles[i].left  # Snap the right of the entity to the left of the block
                    self.collisions['right'] = True
                    if tileTypes[i] == 'level_transition' and self.entityType == 'ronin' and not len(self.game.enemies):
                        self.game.changeLevel = True
                if frameMovement[0] < 0 and tileTypes[i] != 'platform':  # If the entity is moving left
                    entityRectangle.left = rectangles[i].right  # Snap the left of the entity to the right of the block
                    self.collisions['left'] = True
                    if tileTypes[i] == 'level_transition' and self.entityType == 'ronin' and not len(self.game.enemies):
                        self.game.changeLevel = True
                self.position[0] = entityRectangle.x  # Set the players position to the x position of block

        self.position[1] += frameMovement[1]
        entityRectangle = self.Rectangle()
        for i in range(len(rectangles)):
            if entityRectangle.colliderect(rectangles[i]):
                if frameMovement[1] > 0:  # If the entity is moving down
                    entityRectangle.bottom = rectangles[i].top  # Snap the bottom of the entity to the top of the block
                    self.collisions['down'] = True
                    if tileTypes[i] == 'healers' and self.entityType == 'ronin':
                        self.Heal(0.1)
                    if tileTypes[i] == 'level_transition' and self.entityType == 'ronin' and not len(self.game.enemies):
                        self.game.changeLevel = True
                if frameMovement[1] < 0 and tileTypes[i] != 'platform':  # If the entity is moving up
                    entityRectangle.top = rectangles[i].bottom  # Snap the top of the entity to the bottom of the block
                    self.collisions['up'] = True
                    if tileTypes[i] == 'level_transition' and self.entityType == 'ronin' and not len(self.game.enemies):
                        self.game.changeLevel = True
                self.position[1] = entityRectangle.y  # Set the players position to the y position of block

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.lastMovement = movement

        # Adding gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        # Resets the gravity after collision
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.Update()

    def GetDamage(self, amount):
        if self.targetHealth > 0:
            self.targetHealth -= amount
        if self.targetHealth <= 0:
            self.targetHealth = 0
        if not self.dead and self.targetHealth == 0:
            self.dead = True
        return self.dead

    def Heal(self, amount):
        if self.targetHealth < self.hitPoints:
            self.targetHealth += amount
        if self.targetHealth > self.hitPoints:
            self.targetHealth = self.hitPoints

    def Render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.Image(), self.flip, False),
                     (self.position[0] - offset[0] + self.animationOffset[0],
                      self.position[1] - offset[1] + self.animationOffset[1])
                     )
        # Renders the entity onto the current surface
        # surface.blit(self.game.assets['ronin'], (self.position[0] - offset[0], self.position[1] - offset[1]))
