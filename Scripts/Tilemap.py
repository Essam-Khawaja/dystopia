import pygame
import json


class Tilemap:
    def __init__(self, game, tileSize=32):
        self.game = game
        self.tileSize = tileSize
        self.tilemap = {}
        self.offGridTiles = ['props']

        # for i in range(0, 20):
        #     self.tilemap[str(3 + i) + ";10"] = {'type': 'ground_tiles', 'variant': 2, 'position': (3 + i, 10)}
        #     self.tilemap["10;" + str(5 + i)] = {'type': 'ground_tiles', 'variant': 5, 'position': (10, 5 + i)}

    def TilesAround(self, position):
        tiles = []
        tileLocation = ((int(position[0] // self.tileSize)), (int(position[1] // self.tileSize)))
        for offset in NEIGHBOUR_OFFSETS:
            checkLocation = str(tileLocation[0] + offset[0]) + ';' + str(tileLocation[1] + offset[1])
            if checkLocation in self.tilemap:
                tiles.append(self.tilemap[checkLocation])
        return tiles

    def SolidCheck(self, position):
        # Computes the location of the tile from current position
        tileLocation = str(int(position[0] // self.tileSize)) + ';' + str(int(position[1] // self.tileSize))
        # Checks if tile is in tilemap
        if tileLocation in self.tilemap:
            if self.tilemap[tileLocation]['type'] in PHYSICS_TILES:
                return self.tilemap[tileLocation]

    def PhysicsRectsAround(self, position, offset=(0, 0)):
        rectangles = []
        tile_types = []
        for tile in self.TilesAround(position):
            if tile['type'] in PHYSICS_TILES:
                rectangles.append(pygame.Rect(tile['position'][0] * self.tileSize - offset[0],
                                              tile['position'][1] * self.tileSize - offset[1],
                                              self.tileSize, self.tileSize))
                tile_types.append(tile['type'])
        return rectangles, tile_types

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tileSize, 'offgrid': self.offGridTiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tileSize = map_data['tile_size']
        self.offGridTiles = map_data['offgrid']

    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['position'][0] + shift[0]) + ';' + str(tile['position'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def Extract(self, idPairs, keep=False):
        matches = []
        for tile in self.offGridTiles.copy():
            if(tile['type'], tile['variant']) in idPairs:
                matches.append(tile.copy())
                if not keep:
                    self.offGridTiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in idPairs:
                matches.append(tile.copy())
                matches[-1]['position'] = matches[-1]['position'].copy()
                matches[-1]['position'][0] *= self.tileSize
                matches[-1]['position'][1] *= self.tileSize
                if not keep:
                    del self.tilemap[loc]

        return matches

    def Render(self, surface, offset=(0, 0)):
        for tile in self.offGridTiles:
            surface.blit(self.game.assets[tile["type"]][tile["variant"]],
                         (tile["position"][0] - offset[0], tile["position"][1] - offset[1]))
        # Range of (Top left pixel, Top right pixel)
        for x in range(offset[0] // self.tileSize, (offset[0] + surface.get_width()) // self.tileSize + 1):
            for y in range(offset[1] // self.tileSize, (offset[1] + surface.get_height()) // self.tileSize + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surface.blit(self.game.assets[tile['type']][tile['variant']],
                                 (tile["position"][0] * self.tileSize - offset[0],
                                  tile["position"][1] * self.tileSize - offset[1]))
        # rectangles, x = self.PhysicsRectsAround(self.game.player.position, (int(self.game.scroll[0]), int(self.game.scroll[1])))
        # for rectangle in rectangles:
        #     pygame.draw.rect(self.game.display, (0, 255, 0), rectangle)


# main
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOUR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'ground_tiles', 'wall_tiles', 'platform', 'healers', 'level_transition'}
AUTOTILE_TYPES = {'ground_tiles', 'wall_tiles', 'healers'}
