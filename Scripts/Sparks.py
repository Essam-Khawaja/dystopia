import pygame
import math


class Spark:
    def __init__(self, position, angle, speed, colour=(255, 255, 255)):
        self.position = list(position)
        self.angle = angle
        self.speed = speed
        self.colour = colour

    def Update(self):
        self.position[0] += math.cos(self.angle) * self.speed
        self.position[1] += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)
        return not self.speed

    def Render(self, surface, offset=(0, 0)):
        renderPoints = [
            (self.position[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
             self.position[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),

            (self.position[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0],
             self.position[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),

            (self.position[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0],
             self.position[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),

            (self.position[0] + math.cos(self.angle + math.pi * 1.5) * self.speed * 0.5 - offset[0],
             self.position[1] + math.sin(self.angle + math.pi * 1.5) * self.speed * 0.5 - offset[1])
        ]
        pygame.draw.polygon(surface, self.colour, renderPoints)
