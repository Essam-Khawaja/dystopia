import random
import pygame
import math
import time

from Scripts.Utilities import LoadImage, LoadImages, Animation
from Scripts.Tilemap import Tilemap
from Scripts.Particles import Particle
from Scripts.Sparks import Spark
from Scripts.Player import Player
from Scripts.Enemies import Enemy
from Scripts.States.StateManager import State
from Scripts.States.TitleMenu import TitleMenu
from Scripts.States.OptionsMenu import OptionsMenu
from Scripts.States.EndScreen import EndScreen


class Game(State):
    def __init__(self, game):
        pygame.init()
        super().__init__(game)

        self.Fullscreen = False

        # Screen represents the window of the game, while the display is the surface we render on
        self.screen = game.screen
        # Set the size of the surface based on the amount the pixel art will scale up(for display)
        self.display = pygame.Surface((533, 300))
        self.opacityDisplay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        pygame.display.set_caption("Dystopia")

        # To set the frame rate later on in Run()
        self.clock = pygame.time.Clock()
        self.fps = 120

        # All assets, such as images and sound files, will be stored in this dictionary
        self.assetsUI = {
            'health_bar': LoadImage('UI/health_bar.png', colorkey=(255, 255, 255))
        }

        self.assets = {
            'logo': pygame.image.load('Data/Logo/Logo.png'),
            'ground_tiles': LoadImages('Tiles/Dungeon Tileset/Castle Tiles/Ground Tiles'),
            'wall_tiles': LoadImages('Tiles/Dungeon Tileset/Castle Tiles/Wall Tiles'),
            'platform': LoadImages('Tiles/Dungeon Tileset/Castle Tiles/Platform'),
            'props': LoadImages('Tiles/Dungeon Tileset/Castle Tiles/Props'),
            'healers': LoadImages('Tiles/mushroom caves assets/foreground/Healers'),
            'level_transition': LoadImages('Tiles/mushroom caves assets/foreground/Level Transition'),
            'extra_props': LoadImages('Tiles/Dungeon Tileset/Extra Props'),
            'entities': LoadImages('Tiles/mushroom caves assets/foreground/Entities'),
            'ronin': LoadImage('Animation Sprites/Ronin/Player.png'),
            'ronin_idle': Animation(LoadImages('Animation Sprites/Ronin/Idle'), imageDuration=25),
            'ronin_run': Animation(LoadImages('Animation Sprites/Ronin/Running'), imageDuration=8),
            'ronin_jump': Animation(LoadImages('Animation Sprites/Ronin/Jump'), imageDuration=25, loop=False),
            'ronin_wall_slide': Animation(LoadImages('Animation Sprites/Ronin/Wall Slide')),
            'ronin_dash': Animation(LoadImages('Animation Sprites/Ronin/Dash'), imageDuration=5, loop=False),
            'ronin_attack1': Animation(LoadImages('Animation Sprites/Ronin/Attack/Attack 1'), imageDuration=7,
                                       loop=False),
            'ronin_attack2': Animation(LoadImages('Animation Sprites/Ronin/Attack/Attack 2'), imageDuration=7,
                                       loop=False),
            'enemy_idle': Animation(LoadImages('Animation Sprites/Ghost Enemy/Idle'), imageDuration=30),
            'enemy_run': Animation(LoadImages('Animation Sprites/Ghost Enemy/Running'), imageDuration=30),
            'enemy_attack': Animation(LoadImages('Animation Sprites/Ghost Enemy/Attack'), imageDuration=15, loop=False),
            'particle_base': Animation(LoadImages('Particles/particle'), imageDuration=6, loop=False),
            'background': LoadImage('Backgrounds/Dungeon Background.png'),
            'projectile1': LoadImage('Animation Sprites/Projectiles/Type 1/tile046.png'),
            'projectile_dissipate': Animation(LoadImages('Animation Sprites/Projectiles/Type 1'), imageDuration=1,
                                              loop=False),
            'gun': LoadImage('Weapons/Ghost Weapon.png')
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('Data/SFX/jump.wav'),
            'dash': pygame.mixer.Sound('Data/SFX/dash.wav'),
            'player_hit': pygame.mixer.Sound('Data/SFX/hit.wav'),
            'enemy_hit': pygame.mixer.Sound('Data/SFX/sword_hit.mp3'),
            'shoot': pygame.mixer.Sound('Data/SFX/enemy_shoot.mp3'),
            'ambience': pygame.mixer.Sound('Data/SFX/ambience.wav'),
            'sword': pygame.mixer.Sound('Data/SFX/sword.wav'),
            'player_death': pygame.mixer.Sound('Data/SFX/death.mp3'),
            'low_health': pygame.mixer.Sound('Data/SFX/low_health.mp3'),
            'running': pygame.mixer.Sound('Data/SFX/running.mp3'),
        }

        self.sfx['ambience'].set_volume(0.05)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['enemy_hit'].set_volume(0.3)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.3)
        self.sfx['sword'].set_volume(0.3)
        self.sfx['low_health'].set_volume(0.3)
        self.sfx['player_hit'].set_volume(0.4)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['running'].set_volume(0.4)

        # Setting up the player object as well as the movement
        self.player = Player(self, position=(200, 50), size=(20, 25))
        self.movement = [False, False]
        self.dead = 0

        # Setting up the backgrounds to correct size
        # for i in range(0, len(self.assets['background'])):
        #     self.assets['background'][i] = pygame.transform.scale(self.assets['background'][i], self.display.get_size())
        self.assets['background'] = pygame.transform.scale(self.assets['background'], self.display.get_size())

        # Setting up the particles
        self.particles = []

        # Setting up the enemy projectiles
        self.projectiles = []

        # The spark visual effects for hits
        self.sparks = []

        # Sets up all the enemies
        self.enemies = []

        # For setting up the camera
        self.scroll = [0, 0]
        self.backgroundScroll = 0

        # Setting up the tile system for the level design
        self.tilemap = Tilemap(self, tileSize=25)
        self.level = 0
        self.transition = -30   # Sets the screen to black at initial state of transition
        self.LoadLevel(self.level)
        self.changeLevel = False
        self.gameFinish = False

        # Adding screenshake for visual effect:
        self.screenshake = 0

        # Frame rate Independence
        self.deltaTime = 0
        self.previousTime = 0

    def GetDeltaTime(self):
        now = time.time()
        self.deltaTime = now - self.previousTime
        self.previousTime = now

    def LoadLevel(self, level):
        self.changeLevel = False
        self.tilemap.load('Data/Levels/' + str(level) + '.json')

        # Resetting the following things for the new level
        self.player = Player(self, position=(200, 50), size=(20, 25))
        self.movement = [False, False]
        self.enemies = []
        for spawner in self.tilemap.Extract([('entities', 0), ('entities', 1)]):
            if spawner['variant'] == 0:
                self.player.position = spawner['position']
                self.player.airtime = 0
            else:
                self.enemies.append(Enemy(self, spawner['position'], (20, 25)))

        self.projectiles = []
        self.scroll = [0, 0]
        self.sparks = []
        self.particles = []
        self.dead = 0
        self.transition = -50
        self.backgroundScroll = 0

    def Run(self):
        # Setting up the main game loop
        # backgroundScrollLeft = False
        # backgroundScrollRight = False
        pygame.mixer.music.load('Data/Music/Spook_dungeon.wav')
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)

        running = True
        while running:
            # Keeping frame rate independence:
            self.GetDeltaTime()

            # Finds how far away the player is from the display and sets the scroll value (takes 1/30th of the distance)
            self.scroll[0] += (self.player.Rectangle().centerx - self.display.get_width() / 2 - self.scroll[0]) / 10
            self.scroll[1] += (self.player.Rectangle().centery - self.display.get_width() / 3 - self.scroll[1]) / 10
            # To prevent sub-pixel collisions
            renderScroll = (int(self.scroll[0]), int(self.scroll[1]))

            # backgroundTiles = math.ceil(self.display.get_width() / self.assets['background'][0].get_width()) + 1
            # for i in range(0, backgroundTiles):
            #     speed = 1
            #     for background in self.assets['background']:
            #         self.display.blit(background,
            #                           ((i * background.get_width()) - self.backgroundScroll * speed, 0))
            #         speed += 0.25
            # if backgroundScrollLeft and self.backgroundScroll > 0:
            #     self.backgroundScroll -= 0.25
            # if backgroundScrollRight:
            #     self.backgroundScroll += 0.25
            # self.opacityDisplay.fill((0, 0, 0, 100))
            # self.display.blit(self.opacityDisplay, (0, 0))

            self.display.blit(self.assets['background'], (0, 0))

            # Setting all the possible values for the screenshake
            self.screenshake = max(0, self.screenshake - 1)  # Minimum value goes until 0

            if self.changeLevel:       # The base condition for level change
                self.transition += 1
                if self.transition > 30:
                    self.level += 1
                    if self.level < 3:
                        self.LoadLevel(self.level)
                    else:
                        self.gameFinish = True
                        running = False
            # Automatically raises the transition from -10 to 0 each frame, giving a transition effect from black
            if self.transition < 0:
                self.transition += 1

            # If the player has started dying
            if self.dead:
                self.sfx['player_death'].play()
                self.dead += 1      # At every frame add one more to the timer for the players death
                self.sfx['player_death'].set_volume(1 - (self.dead * 0.01))
                if self.dead > 100:          # Once timer reaches 40 frames, reload the level
                    self.transition += 1
                    if self.transition > 50:
                        self.LoadLevel(self.level)

            # Render in the tilemap so with camera scroll
            self.tilemap.Render(self.display, offset=renderScroll)

            # Rendering in and updating the enemy movement
            for enemy in self.enemies.copy():
                hit = enemy.Update(self.tilemap, (0, 0))
                enemy.Render(self.display, offset=renderScroll)
                if hit:
                    enemy.GetDamage(25)
                    if enemy.targetHealth <= 0:
                        self.enemies.remove(enemy)

            # We call the functions from PhysicalEntity to update the players movement and then render them on screen
            if not self.dead:
                self.player.Update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.Render(self.display, offset=renderScroll)

            # The projectile list is arranged as [[x, y]], flip, direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[2]
                projectile[3] += 1
                image = self.assets['projectile1']
                self.display.blit(pygame.transform.flip(image, projectile[1], False),
                                  (projectile[0][0] - 32 / 2 - renderScroll[0],
                                   projectile[0][1] - 28 / 2 - renderScroll[1]))
                if self.tilemap.SolidCheck(projectile[0]):
                    self.projectiles.remove(projectile)     # Removes the projectiles if they hit the wall
                    for i in range(0, 4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[2] > 0 else 0),
                                  2 + random.random())
                        )
                elif projectile[3] > 200:
                    for i in range(0, len(self.assets['projectile_dissipate'].images)):
                        self.display.blit(pygame.transform.flip(self.assets['projectile_dissipate'].Image(),
                                                                projectile[1], False),
                                          (projectile[0][0] - 32 / 2 - renderScroll[0],
                                           projectile[0][1] - 32 / 2 - renderScroll[1]))
                        self.assets['projectile_dissipate'].Update()
                    self.projectiles.remove(
                        projectile)  # Removes the projectiles if they last longer than 6 seconds
                elif abs(self.player.dashing) < 50:     # Checks if the player is not dashing
                    if self.player.Rectangle().collidepoint(projectile[0]):     # If projectile and player collide
                        self.sfx['player_hit'].play()
                        self.projectiles.remove(projectile)
                        self.display.fill((200, 0, 0, 100))
                        pygame.time.wait(50)
                        isDead = self.player.GetDamage(25)
                        if self.player.targetHealth <= 25 and not isDead:
                            self.sfx['low_health'].play()
                        if isDead:
                            self.sfx['low_health'].set_volume(0)
                            self.dead += 1
                            self.screenshake = max(20, self.screenshake)  # Shakes the screen when the player gets hit
                            if self.dead == 1:
                                for i in range(0, 30):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.sparks.append(
                                        Spark(self.player.Rectangle().center, angle, 2 + random.random()))
                                    self.particles.append(Particle(self, 'base', self.player.Rectangle().center,
                                                                   velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                             math.sin(angle + math.pi) * speed * 0.5],
                                                                   frame=random.randint(0, 7)))
                        self.screenshake = max(16, self.screenshake)    # Shakes the screen when the player gets hit
                        for i in range(0, 5):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.Rectangle().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'base', self.player.Rectangle().center,
                                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                     math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.Update()
                spark.Render(self.display, offset=renderScroll)
                if kill:
                    self.sparks.remove(spark)

            for particle in self.particles.copy():
                kill = particle.Update()
                particle.Render(self.display, offset=renderScroll)
                if kill:
                    self.particles.remove(particle)

            # The event handler
            for event in pygame.event.get():
                # if event.type == pygame.VIDEORESIZE:
                #     if not self.Fullscreen:
                #         self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_F11:
                    #     self.Fullscreen = not self.Fullscreen
                    #     if self.Fullscreen:
                    #         self.screen = pygame.display.set_mode((self.screen.get_width(),
                    #                                                self.screen.get_height()), pygame.FULLSCREEN)
                    #     else:
                    #         self.screen = pygame.display.set_mode((self.screen.get_width(),
                    #                                                self.screen.get_height()), pygame.RESIZABLE)
                    # if not self.player.attacking:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = True
                        backgroundScrollLeft = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                        backgroundScrollRight = True
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                        if self.player.Jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_l:
                        self.player.Dash()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_j:
                        if not self.dead:
                            self.player.attackCount += 1
                            thisAttackHitbox = self.player.Attack()
                            for enemy in self.enemies:
                                enemy.TakeDamage(thisAttackHitbox)
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_n:
                        if not self.changeLevel:
                            self.changeLevel = True
                        else:
                            self.changeLevel = False
                    if event.key == pygame.K_b:
                        if not self.changeLevel:
                            self.level -= 1
                            self.changeLevel = True
                        else:
                            self.changeLevel = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = False
                        backgroundScrollLeft = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        backgroundScrollRight = False

            # Setting up all the UI
            # self.display.blit(self.assetsUI['health_bar'], (20, 10))

            # self.display.blit(pygame.transform.scale_by(self.assetsUI['health_bar'], 2), (0, 0))

            # Sets up the transition effect for the death and changing levels
            if self.transition:
                transitionSurface = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transitionSurface, (255, 255, 255), (self.display.get_width() // 2,
                                                                        self.display.get_height() // 2),
                                   (50 - abs(self.transition)) * 8)
                transitionSurface.set_colorkey((255, 255, 255))
                self.display.blit(transitionSurface, (0, 0))

            screenshakeOffset = (random.random() * self.screenshake - self.screenshake / 2,
                                 random.random() * self.screenshake - self.screenshake / 2)

            # Pastes the display onto the window(screen) and ticks the clock at the appropriate FPS
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshakeOffset)
            self.clock.tick(self.fps)
            pygame.display.update()


class GameLoop:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.display = pygame.Surface((640, 360))
        self.Fullscreen = False

        self.running, self.playing = True, True
        self.actions = {'Start_Game': False,
                        "Options": False,
                        "Main_Menu": True,
                        'End_Screen': False}
        self.deltaTime, self.previousTime = 0, 0
        self.states = []

        self.LoadAssets()

        self.titleScreen = TitleMenu(self)  
        self.mainGame = Game(self)
        self.optionsMenu = OptionsMenu(self)
        self.endScreen = EndScreen(self)
        self.states.append(self.titleScreen)
        self.states.append(self.optionsMenu)
        self.states.append(self.endScreen)

    def Update(self):
        if not self.actions["Start_Game"]:
            self.states[-1].Update(self.deltaTime, self.actions)

    def Render(self):
        if not self.actions["Start_Game"]:
            if self.actions["Main_Menu"]:
                self.states[0].Render(self.display)
            elif self.actions["Options"]:
                self.states[1].Run(self.screen)
                self.actions["Options"] = False
                self.actions["Start_Game"] = True
            elif self.actions['End_Screen']:
                self.states[2].Render(self.display)
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size(), ), (0, 0))

    def Run(self):
        pygame.display.set_icon(self.mainGame.assets['logo'])
        while self.playing:
            self.GetDeltaTime()
            self.display.fill((0, 0, 0))
            # self.Update()
            if self.actions['Start_Game']:
                self.mainGame.Run()
                self.actions['End_Screen'] = self.mainGame.gameFinish
                self.actions['Start_Game'] = False
                if not self.mainGame.gameFinish:
                    self.actions['Options'] = True
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    if not self.Fullscreen:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.QUIT:
                    self.playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.Fullscreen = not self.Fullscreen
                        if self.Fullscreen:
                            self.screen = pygame.display.set_mode((self.screen.get_width(),
                                                                   self.screen.get_height()), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((self.screen.get_width(),
                                                                   self.screen.get_height()), pygame.RESIZABLE)
                    if event.key == pygame.K_RETURN:
                        if not self.actions['End_Screen']:
                            self.actions["Main_Menu"] = False
                            self.actions['Start_Game'] = True
                        else:
                            self.playing = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        self.actions["Main_Menu"] = False
            self.Render()
            pygame.display.update()
            self.clock.tick(120)

    def GetDeltaTime(self):
        now = time.time()
        self.deltaTime = now - self.previousTime
        self.previousTime = now

    def DrawText(self, surface, text, colour, x, y, fontOption):
        textSurface = self.fonts[fontOption].render(text, True, colour)
        # textSurface.set_colorkey((0, 0, 0))
        textRectangle = textSurface.get_rect()
        textRectangle.center = (x, y)
        surface.blit(textSurface, textRectangle)

    def LoadAssets(self):
        self.fonts = [pygame.font.Font('Data/Font/PressStart2P-vaV7.ttf', 20),
                      pygame.font.Font('Data/Font/Crang.ttf', 50)]


# main
game = GameLoop()
game.Run()
