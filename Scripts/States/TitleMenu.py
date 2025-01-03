import pygame
from Scripts.States.StateManager import State
from Scripts.Utilities import LoadImage


class TitleMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        behind = LoadImage('Backgrounds/Title Menu/back.png')
        middle = LoadImage('Backgrounds/Title Menu/middle.png')
        front = LoadImage('Backgrounds/Title Menu/near.png')
        self.backgroundImages = [behind, middle, front]
        self.scroll = 0

        pygame.mixer.music.load('Data/Music/Title_Jingingle.wav')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()

    def Update(self, deltaTime, actions):
        pass

    def Render(self, surface):
        self.scroll += 1
        backgroundWidth = self.backgroundImages[0].get_width()
        for i in range(0, 3):
            self.backgroundImages[i] = pygame.transform.scale(self.backgroundImages[i], surface.get_size())
        for x in range(20):
            speed = 0.5
            for i in self.backgroundImages:
                surface.blit(i, ((x * backgroundWidth) - self.scroll * speed, 0))
                speed += 0.01
        self.game.DrawText(surface, "Dystopia", (255, 255, 255), surface.get_width() // 2, surface.get_height() // 2, 1)
        self.game.DrawText(surface, "Press ENTER to begin", (255, 255, 255),
                           surface.get_width() // 2, surface.get_height() // 2 + 50, 0)
