class Particle:
    def __init__(self, game, particleType, position, velocity=[0, 0], frame=0):
        self.game = game
        self.particleType = particleType
        self.position = list(position)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle_' + particleType].Copy()
        self.animation.frame = frame

    def Update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        self.animation.Update()

        return kill

    def Render(self, surface, offset=(0, 0)):
        image = self.animation.Image()
        surface.blit(image, (self.position[0] - offset[0] - image.get_width() // 2,
                             self.position[1] - offset[1] - image.get_height() // 2))
