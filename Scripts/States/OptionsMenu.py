import pygame, os
from Scripts.States.StateManager import State
from Scripts.Utilities import LoadImage


class ExtraOptions:
    def __init__(self):
        self.menuImage = LoadImage('Menus/Extra Options.png')
        self.menuRectangle = self.menuImage.get_rect()
        self.menuRectangle.center = (640, 310)
        self.display = pygame.surface.Surface((1280, 720))

        self.menuOptions = {0: "Video Settings", 1: "Audio Settings", 2: "Key Bindings", 3: "Back"}
        self.index = 0

        self.cursorImage = LoadImage('Menus/cursor_2.png')
        self.cursorImage = pygame.transform.scale_by(self.cursorImage, 4)
        self.cursorRectangle = self.cursorImage.get_rect()
        self.cursorPosY = self.menuRectangle.y + 130
        self.cursorRectangle.x, self.cursorRectangle.y = self.menuRectangle.x + 350, self.cursorPosY

        self.buttonClick = pygame.mixer.Sound('Data/SFX/Button click.mp3')

    def Run(self, surface):
        run = True
        pygame.mouse.set_visible(False)
        while run:
            self.display.blit(self.menuImage, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    if event.key == pygame.K_RETURN:
                        self.buttonClick.play()
                        if self.index == 0:
                            pass
                        elif self.index == 1:
                            pass
                        elif self.index == 2:
                            pass
                        elif self.index == 3:
                            run = False
                    if event.key == pygame.K_DOWN:
                        self.index = (self.index + 1) % len(self.menuOptions)
                    if event.key == pygame.K_UP:
                        self.index = (self.index - 1) % len(self.menuOptions)
            self.cursorRectangle.y = self.cursorPosY + (self.index * 125)
            self.display.blit(self.cursorImage, self.cursorRectangle)
            surface.blit(pygame.transform.scale(self.display, surface.get_size()), (0, 0))
            pygame.display.update()


class OptionsMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.menuImage = LoadImage('Menus/Options Menu.png')
        self.menuRectangle = self.menuImage.get_rect()
        self.menuRectangle.center = (640, 310)
        self.display = pygame.surface.Surface((1280, 720))

        self.menuOptions = {0: "Resume", 1: "Options", 2: "Quit"}
        self.index = 0
        self.options = ExtraOptions()

        self.cursorImage = LoadImage('Menus/cursor_2.png')
        self.cursorImage = pygame.transform.scale_by(self.cursorImage, 4)
        self.cursorRectangle = self.cursorImage.get_rect()
        self.cursorPosY = self.menuRectangle.y + 180
        self.cursorRectangle.x, self.cursorRectangle.y = self.menuRectangle.x + 400, self.cursorPosY

        self.buttonClick = pygame.mixer.Sound('Data/SFX/Button click.mp3')

    def Run(self, surface):
        run = True
        pygame.mouse.set_visible(False)
        while run:
            self.display.blit(self.menuImage, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    if event.key == pygame.K_RETURN:
                        self.buttonClick.play()
                        if self.index == 0:
                            run = False
                        elif self.index == 1:
                            self.options.Run(surface)
                        elif self.index == 2:
                            pygame.quit()
                    if event.key == pygame.K_DOWN:
                        self.index = (self.index + 1) % len(self.menuOptions)
                    if event.key == pygame.K_UP:
                        self.index = (self.index - 1) % len(self.menuOptions)
            self.cursorRectangle.y = self.cursorPosY + (self.index * 150)
            self.display.blit(self.cursorImage, self.cursorRectangle)
            surface.blit(pygame.transform.scale(self.display, surface.get_size()), (0, 0))
            pygame.display.update()
