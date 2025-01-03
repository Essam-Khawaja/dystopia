import pygame


class Trap:
    def __init__(self, game, trapType, position, image):
        self.game = game
        self.trapType = trapType
        self.position = list(position)
        self.image = image
        self.imageSurface = pygame.Surface((32, 32))
        self.imageSurface.blit(self.image, (0, 0))

    def Mask(self):
        return pygame.mask.from_surface(self.imageSurface)

    def Update(self, player):
        playerMask = pygame.mask.from_surface(player)
        offset = (player.position[0] - self.position[0],
                  player.position[1] - self.position[1])
        if playerMask.overlap_mask(self.Mask(), offset):
            player.dead += 1
