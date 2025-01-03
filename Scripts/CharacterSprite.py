import pygame


class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def GetImage(self, frame, scale=1, position=(0, 0)):
        image = pygame.Surface((32, 32))
        image.blit(self.sheet, position, area=((frame * 32), 0, 32, 32))
        image = pygame.transform.scale(image, (32 * scale, 32 * scale))
        image.set_colorkey((0, 0, 0))
        return image

    def IdentifyNextFrame(self, last_update, animation_cooldown, frame, total_frames):
        current_time = pygame.time.get_ticks()
        if current_time - last_update >= animation_cooldown:
            frame += 1
            last_update = current_time
            if frame >= total_frames:
                frame = 0
        return last_update, frame
