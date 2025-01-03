import pygame
from Scripts.Buttons import Buttons
from Scripts.States.StateManager import State


class OptionsMenu(State):
    def __init__(self, game):
        super().__init__(game)

        self.Fullscreen = self.game.Fullscreen

        self.game = game

        self.assets = {
            'resume_img': pygame.image.load("Data/Images/Buttons/button_resume.png").convert_alpha(),
            'options_img': pygame.image.load("Data/Images/Buttons/button_options.png").convert_alpha(),
            'quit_img': pygame.image.load("Data/Images/Buttons/button_quit.png").convert_alpha(),
            'video_img': pygame.image.load('Data/Images/Buttons/button_video.png').convert_alpha(),
            'audio_img': pygame.image.load('Data/Images/Buttons/button_audio.png').convert_alpha(),
            'keys_img': pygame.image.load('Data/Images/Buttons/button_keys.png').convert_alpha(),
            'back_img': pygame.image.load('Data/Images/Buttons/button_back.png').convert_alpha(),
            'cursor': pygame.image.load('Data/Images/UI/Cursor.png')
        }

        # create button instances
        self.resume_button = Buttons(590, 145, self.assets['resume_img'], 1)
        self.options_button = Buttons(583, 270, self.assets['options_img'], 1)
        self.quit_button = Buttons(622, 395, self.assets['quit_img'], 1)
        self.video_button = Buttons(512, 95, self.assets['video_img'], 1)
        self.audio_button = Buttons(511, 220, self.assets['audio_img'], 1)
        self.keys_button = Buttons(532, 345, self.assets['keys_img'], 1)
        self.back_button = Buttons(618, 470, self.assets['back_img'], 1)

        self.gameDisplay = pygame.Surface((1280, 720))

    def Run(self):
        screen = self.game.screen
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        pygame.display.set_caption("Dystopia")
        menu_state = "main"

        # game loop
        run = True
        while run:
            self.gameDisplay.fill((52, 78, 91))

            mousePosition = pygame.mouse.get_pos()
            mousePosition = (mousePosition[0] / 2, mousePosition[1] / 2)
            cursorPosition = (int((mousePosition[0]) // 32), int((mousePosition[1]) // 32))
            self.gameDisplay.blit(self.assets['cursor'], mousePosition)

            # event handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                # if event.type == pygame.VIDEORESIZE:
                #     if not self.Fullscreen:
                #         self.gameDisplay = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # if event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_F11:
                #         self.Fullscreen = not self.Fullscreen
                #         if self.Fullscreen:
                #             self.gameDisplay = pygame.display.set_mode((self.gameDisplay.get_width(),
                #                                                         self.gameDisplay.get_height()), pygame.FULLSCREEN)
                #         else:
                #             self.gameDisplay = pygame.display.set_mode((self.gameDisplay.get_width(),
                #                                                         self.gameDisplay.get_height()), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False

            # check if game is paused

            if menu_state == "main":
                # draw pause screen buttons
                if self.resume_button.draw(self.gameDisplay):
                    run = False
                if self.options_button.draw(self.gameDisplay):
                    menu_state = "options"
                if self.quit_button.draw(self.gameDisplay):
                    pygame.quit()
            # check if the options menu is open
            if menu_state == "options":
                # draw the different options buttons
                if self.video_button.draw(self.gameDisplay):
                    print("Video Settings")
                if self.audio_button.draw(self.gameDisplay):
                    print("Audio Settings")
                if self.keys_button.draw(self.gameDisplay):
                    print("Change Key Bindings")
                if self.back_button.draw(self.gameDisplay):
                    menu_state = "main"

            screen.blit(pygame.transform.scale(self.gameDisplay, screen.get_size()), (0, 0))

            pygame.display.update()
