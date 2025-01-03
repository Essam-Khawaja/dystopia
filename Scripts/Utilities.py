import pygame
import os

pygame.init()

class Animation:
    def __init__(self, images, imageDuration=5, loop=True):
        self.images = images    # These are all the images in the animation sprite
        self.imageDuration = imageDuration  # How long each frame is supposed to last
        self.loop = loop    # Do we want to loop through the animation
        self.done = False   # Is the animation done?
        self.frame = 0  # This is the current frame of the GAME not the animation

    def Copy(self):
        return Animation(self.images, self.imageDuration, self.loop)  # Returns an exact copy of the same object(BYREF)

    def Image(self):
        return self.images[int(self.frame / self.imageDuration)]

    def IsDone(self):
        return self.done

    def Update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.imageDuration * len(self.images))    # Loops around the frames
        else:
            self.frame = min(self.frame + 1, (self.imageDuration * len(self.images)) - 1)
            if self.frame >= (self.imageDuration * len(self.images)) - 1:
                self.done = True


# Function for loading an image from files
def LoadImage(path, colorkey=(0, 0, 0)):
    image = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    # Set color key removes the black background from a surface
    image.set_colorkey(colorkey)
    return image


def LoadImages(path):
    images = []
    for image_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(LoadImage(path + '/' + image_name))
    return images


# main
BASE_IMAGE_PATH = "Data/Images/"
FONT = pygame.font.Font("Data/Font/PressStart2P-vaV7.ttf", 20)
