#!/usr/bin/python3

# Created by Jared Dunbar, April 4th, 2020
# Use this as an example for a basic game.

import pyxel, random
import os.path
from os import path

# Width and height of game screen, in tiles
WIDTH = 16
HEIGHT = 12

# Width and height of the game level
GL_WIDTH = 32
GL_HEIGHT = 32

# Entities (should not) be able to walk through structures,
#   unless they have "allow" set to True
structures = []

# Window offsets for the panning feature.
windowOffsetX = 0
windowOffsetY = 0

# Entities can move all over the place and stand in the same cube, but not walk
#   into structures unless the structure has "allow" set to True
entities = []

# Sound mappings
sounds = {}

# These are the texture maps for 8x8 and 16x16
texture8 = {}
texture16 = {}

# Information about the image map:

# Image maps are 256x256. This allows for 256 16x16 textures in one tilemap,
#   or 1024 8x8 textures in one tilemap

# Image Map 0: 16x16 textures
# Image Map 1: 8x8 textures
# Image Map 2: <unused>

# This sets up all the rendering code for ya. Give it a image,
#   and it will remember the thing for you.
#   NOTE: transparent is a color key. If -1, doesn't do transparent stuff.
class Drawn():
    def __init__(self, name, size=16, texture="invalid16.png", transparent=-1):
        if (size != 8) and (size != 16):
            print("CRITICAL FAIL! Texture is not of correct size!")
            exit(1)
        self.trans = transparent
        if size == 16:
            # Only register if we're not in the 16x16 texturemap
            if name not in texture16:
                if not path.exists(texture):
                    texture = "invalid16.png"
                # 16x16 is in bank 0
                self.bank = 0
                self.xLoc = int(len(texture16)/16)*16
                self.yLoc = (len(texture16)%16) * 16
                pyxel.image(self.bank).load(self.xLoc, self.yLoc, texture)
                texture16[name] = self
        elif size == 8:
            # Only register if we're not in the 8x8 texturemap
            if name not in texture8:
                if not path.exists(texture):
                    texture = "invalid8.png"
                # 8x8 is in bank 1
                self.bank = 1
                self.xLoc = int(len(texture8)/32)*8
                self.yLoc = (len(texture8)%32)*8
                pyxel.image(self.bank).load(self.xLoc, self.yLoc, texture)
                texture8[name] = self

    def draw(self, x, y, trans=None, fX=False, fY=False):
        if (trans == None):
            trans = self.trans
        # Default texture size is 16x16
        ts = 16
        # If we're in Bank 1, texture size is 8x8
        if self.bank == 1:
            ts = 8
        xf = ts
        yf = ts
        if fX:
            xf = -ts
        if fY:
            yf = -ts
        pyxel.blt(x*abs(ts), y*abs(ts), self.bank, self.xLoc, self.yLoc, xf, yf, trans)

class Sounded():
    def __init__(self, name, notes, tone="s", volume="4", effect=("n" * 4 + "f"), speed=7):
        if name not in sounds:
            self.id = len(sounds)
            pyxel.sound(self.id).set(note=notes, tone=tone, volume=volume, effect=effect, speed=speed)
            sounds[name] = self

    # There are 4 streams - 0 through 3
    def play(self, stream=0):
        pyxel.play(stream, self.id)

# This is the base class of any thing that renders to the screen and ticks.
class Entity():
    def __init__(self, name, texture=["invalid16.png"], x=0, y=0):
        self.name = name
        self.x = x
        self.y = y
        self.allow = False
        self.frameNum = 0
        self.dir = "N"
        self.texName = [x.rsplit(".",1)[0] for x in texture]
        for tex in texture:
            texName = tex.rsplit(".",1)[0] # remove file extension
            Drawn(texName, 16, tex)

    def update(self):
        pass

    def draw(self):
        drawX = self.x + windowOffsetX
        drawY = self.y + windowOffsetY
        if (drawX >= 0 and drawX < WIDTH) and (drawY >=0 and drawY < HEIGHT):
            texture16[self.texName[self.frameNum]].draw(drawX, drawY)

class Floor(Entity):
    def __init__(self, name, x, y):
        super(Floor, self).__init__(name, ["floor.png"], x, y)
        self.allow = True

# The player class extends Entity by listening for keyboard events.
class Player(Entity):
    def __init__(self, name, x=WIDTH/2, y=HEIGHT/2):
        super(Player, self).__init__(name, ["player/char_H{}.png".format(x) for x in range(0,12)] + ["player/char_V{}.png".format(x) for x in range(0,12)], x, y)
        self.cooldown = 0
        self.cooldownTime = 2
        self.frameNum = 1
        self.texHnames = [x for x in self.texName if "H" in x]
        self.texVnames = [x for x in self.texName if "V" in x]

    def update(self):
        self.cooldown -= 1
        if (self.cooldown <= 0):
            wantGoX = 0
            wantGoY = 0
            if pyxel.btn(pyxel.KEY_UP):
                wantGoY -= 1
                self.dir = "N"
            if pyxel.btn(pyxel.KEY_DOWN):
                wantGoY += 1
                self.dir = "S"
            if pyxel.btn(pyxel.KEY_LEFT):
                wantGoX -= 1
                self.dir = "E"
            if pyxel.btn(pyxel.KEY_RIGHT):
                wantGoX += 1
                self.dir = "W"

            if (wantGoX != 0 or wantGoY != 0):
                if canGo(self.x, self.y, wantGoX, wantGoY):
                    global windowOffsetX, windowOffsetY
                #if canGo(self.x + wantGoX, self.y + wantGoY, self.x, self.y):
                    self.x = self.x + wantGoX
                    self.y = self.y + wantGoY
                    self.cooldown = self.cooldownTime
                    windowOffsetX -= wantGoX
                    windowOffsetY -= wantGoY

    def draw(self):
        drawX = self.x + windowOffsetX
        drawY = self.y + windowOffsetY

        fX = False
        fY = False
        ch = self.texHnames

        if self.dir == "N":
            fX = True
            fY = True
            ch = self.texVnames
        if self.dir == "S":
            fX = False
            fY = False
            ch = self.texVnames
        if self.dir == "E":
            fX = False
            fY = False
            ch = self.texHnames
        if self.dir == "W":
            fX = True
            fY = True
            ch = self.texHnames

        print(ch)

        if (drawX >= 0 and drawX < WIDTH) and (drawY >=0 and drawY < HEIGHT):
            texture16[ch[self.frameNum - 1]].draw(drawX, drawY, 0, fX=fX, fY=fY)
        self.frameNum += 1
        if (self.frameNum >= 12):
            self.frameNum = 0

# This tells you if an entity is permitted to go somewhere.
# From x,y with velocity a,b
def canGo(x, y, a, b):
    # Don't allow to exit past the edges of the screen
    if ((x+a) < 0 or (x+a) >= GL_WIDTH):
        sounds["collide"].play(0)
        return False
    if ((y+b) < 0 or (y+b) >= GL_HEIGHT):
        sounds["collide"].play(0)
        return False

    # Basic structure checks in direction
    for s in structures:
        if (s.x == (x+a)) and (s.y == (y+b)):
            if s.allow:
                return True
            sounds["collide"].play(0)
            return False

    # Advanced structure checks on diagonals
    if not (x == a or y == b):
        xCheck = False
        yCheck = False
        for s in structures:
            if (s.x == (x+a) and (s.y == y)):
                xCheck = not s.allow
            if (s.x == x) and (s.y == (y+b)):
                yCheck = not s.allow
        if xCheck and yCheck:
            sounds["collide"].play(0)
            return False

    return True

# This sets up the game
def setup():
    # Register with Pyxel
    pyxel.init(WIDTH * 16, HEIGHT * 16, caption="smolgame", palette=[0xff00e5, 0xaaa9ad, 0x5b676d, 0x1f262a, 0x9cff78, 0x44ff00, 0x2ca600, 0x7cff00, 0xff8b00, 0xff0086, 0x6f00ff, 0x0086ff, 0x00ff9a, 0x1f0000, 0x49afff, 0xe2e1ff], scale=4, fps=20)

    # Register sounds
    Sounded("collide", "c2c1", speed=4)
    Sounded("level", "c3e3g3c4c4")

    # Register our player
    player = Player("player")
    entities.append(player)

    # Invalid texture test code
    #random = Entity("random", "random.png")
    #entities.append(random)

# Generate the world! You can use this to generate levels or whatever
def worldgen():
    # Insert the walls and such
    for a in range(0, 64):
        x = random.randrange(0, GL_WIDTH - 1)
        y = random.randrange(0, GL_HEIGHT - 1)
        wall = Entity("wall", ["wall.png"], x, y)
        structures.append(wall)

    # last step: Make the floor. NOTE: This alg is terrible and is O(n^3) at worst.
    floorList = []
    for x in range(0, GL_WIDTH):
        for y in range(0, GL_HEIGHT):
            hasItem = False
            for s in structures:
                if (s.x == x and s.y == y):
                    hasItem = True
            if not hasItem:
                floor = Floor("floor", x, y)
                floorList.append(floor)
    # Insert the floor.
    for a in floorList:
        structures.append(a)

# This is called by Pyxel every tick, and handles all game inputs
def update():
    # Clear the screen
    pyxel.cls(col=0)

    # Quit if Q
    if pyxel.btn(pyxel.KEY_Q):
        pyxel.quit()

    # Play a sound if Space
    if pyxel.btn(pyxel.KEY_SPACE):
        sounds["level"].play(1)

    # Tick all entites and structures. The player movement is included randomly
    #   somewhere in this list but you can do a list comprehension to make it
    #   go first or last if you want (examples provided with no warranty)
    # for x in [x for x in entities if x is Player]
    # for x in [x for x in entities if x is not Player]

    for x in structures:
        x.update()
    for x in entities:
        x.update()

# This is called by Pyxel every time the screen needs a redraw, which can be
#   more than once per tick, but really depends on the FPS?
def draw():
    for x in structures:
        x.draw()
    for x in entities:
        x.draw()

# This is where the game setup logic is
def run():
    setup()
    worldgen()
    pyxel.run(update, draw)

# This is the entry point for our file.
run()
