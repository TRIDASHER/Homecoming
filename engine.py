import os
import sys
import pygame
from random import random, choice, randint
from PIL import Image

pygame.init()
height = 900
width = 1200
canvas = pygame.display.set_mode((width, height))
font = pygame.font.Font(None, 40)

player_hit_boxes = pygame.sprite.Group()
solids = pygame.sprite.Group()
objects = pygame.sprite.Group()
everything = pygame.sprite.Group()
entities = pygame.sprite.Group()
targets = pygame.sprite.Group()
bullets = pygame.sprite.Group()
groups = [player_hit_boxes, solids, objects, everything, entities, targets, bullets]
STARTED = pygame.event.Event(pygame.USEREVENT)
PLAYER_THERE = pygame.event.Event(pygame.USEREVENT + 2)
NEXT_LEVEL = pygame.event.Event(pygame.USEREVENT + 1)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"File not found: {fullname}")
        sys.exit(-1)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.mouse.set_cursor((23, 23), load_image("cursor.png", colorkey=-1))


class Player(pygame.sprite.Sprite):
    image = load_image("cube.png")
    image2 = load_image("cube_side.png", colorkey=-1)
    image4 = load_image("cube_shooting.png")
    image3 = pygame.transform.flip(image2, True, False)

    def __init__(self, *group, x, y):
        super().__init__(*group)
        objects.add(self)
        everything.add(self)
        targets.add(self)
        self.alive = True
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.accel = complex(0, 1)
        self.speed = complex(0, 0)
        self.tp_hit_box = HitBox(player_hit_boxes, x + 7, y + 85, 76, 5)
        self.down_hit_box = HitBox(player_hit_boxes, x + 7, y + 86, 76, 5)
        self.head_hit_box = HitBox(player_hit_boxes, x + 10, y, 70, 1)
        self.hp = 100
        self.damage_cooldown = 0
        self.shoot_cooldown = 60
        player_hit_boxes.add(self.tp_hit_box, self.head_hit_box, self.down_hit_box, self)

    def update(self, *args):
        self.speed += self.accel
        keys = pygame.key.get_pressed()

        self.down_hit_box.set_pos(self.rect.x + 7, self.rect.y + 86)
        self.tp_hit_box.set_pos(self.rect.x + 7, self.rect.y + 85)
        self.head_hit_box.set_pos(self.rect.x + 10, self.rect.y)

        for s in solids:
            if pygame.sprite.collide_rect(self.head_hit_box, s):
                self.speed = self.speed.real + 0j
                self.rect.y -= self.rect.y - s.rect.y - s.rect.h
            if pygame.sprite.collide_rect(self, s):
                self.speed = self.speed.imag * 1j + 0
                if self.rect.x - s.rect.x > 0:
                    self.rect.x += 1
                    self.speed = self.speed if self.speed.real > 0 else 0 + self.speed.imag * 1j
                else:
                    self.rect.x -= 1
                    self.speed = self.speed if self.speed.real > 0 else 0 + self.speed.imag * 1j

            if pygame.sprite.collide_rect(s, self.down_hit_box):
                self.speed = self.speed.real + 0j
                if pygame.key.get_pressed()[pygame.K_w]:
                    self.speed += -21j
            if pygame.sprite.collide_rect(s, self.tp_hit_box):
                self.rect.y += s.rect.y - self.rect.y - 90
            if pygame.sprite.spritecollide(s, player_hit_boxes, False) and s.__class__ in [Fire, DangerousOrb]:
                self.hurt(25)
                if s.__class__ == DangerousOrb:
                    s.speed = complex(*s.rect.center) - complex(*self.rect.center)
            if pygame.sprite.spritecollide(s, player_hit_boxes, False) and s.__class__ in [Spikes, BadWall]:
                self.hurt(100)
            if pygame.sprite.spritecollide(s, player_hit_boxes, False) and s.__class__ in [BadTriangle]:
                self.hurt(50)
            if pygame.sprite.spritecollide(s, player_hit_boxes, False) and s.__class__ == Ending:
                pygame.event.post(NEXT_LEVEL)
        if abs(self.speed) >= 150:
            self.hurt(100)

        if keys[pygame.K_d]:
            self.accel = self.accel.imag * 1j + 0.5
            self.image = Player.image2

        elif keys[pygame.K_a]:
            self.accel = self.accel.imag * 1j - 0.5
            self.image = Player.image3

        else:
            self.accel = self.accel.imag * 1j + 0
            self.image = Player.image
            if pygame.mouse.get_pressed(3)[0]:
                if self.shoot_cooldown <= 0:
                    Fireball(x=self.rect.x + 22, y=self.rect.y + 20)
                    self.shoot_cooldown = 60
                self.image = Player.image4

        if pygame.sprite.groupcollide(player_hit_boxes, entities, False, False):
            sprites = pygame.sprite.groupcollide(player_hit_boxes, entities, False, False)
            ent = [i[0] for i in list(sprites.values())]
            classes = list(map(lambda z: z.__class__, ent))
            if Health in classes:
                self.heal(25)
            for i in ent:
                i.remove(everything, entities, objects)

        self.rect.x += self.speed.real
        self.rect.y += self.speed.imag
        self.speed = self.speed.real / 1.05 + self.speed.imag * 1j
        self.speed = round(self.speed.real, 3) + round(self.speed.imag, 3) * 1j
        self.damage_cooldown -= 1
        self.shoot_cooldown -= 1
        if -0.2 <= self.speed.real < 0:
            self.speed = 0 + self.speed.imag * 1j
        if self.hp <= 0:
            self.alive = False

    def debug(self):
        for i in player_hit_boxes:
            pygame.draw.rect(canvas, rect=i.rect, color="red")
        text = font.render(f"accel:{self.accel}, speed:{self.speed}, pos:{self.rect}", True, (255, 0, 0))
        canvas.blit(text, (0, 0))

    def hurt(self, hp):
        if self.damage_cooldown <= 0:
            self.hp -= hp
            self.damage_cooldown = 30

    def heal(self, hp):
        self.hp += hp if self.hp + hp <= 100 else 100 - self.hp

    def draw_hud(self):
        pygame.draw.rect(canvas, (255 * (1 - self.hp / 100), 255 * (self.hp / 100), 0), (25, 25, self.hp, 20))


class SolidObject(pygame.sprite.Sprite):
    image = load_image("wall.png")

    def __init__(self, *group, x, y):
        super().__init__(*group)
        everything.add(self)
        solids.add(self)
        objects.add(self)
        self.image = SolidObject.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Ending(SolidObject):
    image = load_image("ending.png")

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.image = Ending.image


class Fire(SolidObject):
    image = load_image("fire.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.image = Fire.image


class Spikes(Fire):
    image = load_image("spikes.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.image = Spikes.image


class UnstableWall(SolidObject):
    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)

    def update(self):
        if random() * 120 > 117:
            self.remove(*groups)
            BadWall(x=self.rect.x, y=self.rect.y)


class BadWall(SolidObject):
    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.timer = 0
        self.image = pygame.Surface((0, 0))

    def update(self):
        self.timer += 1
        if self.timer >= randint(10, 40):
            self.remove(*groups)
            UnstableWall(x=self.rect.x, y=self.rect.y)
        for _ in range(40):
            pygame.draw.rect(canvas, choice(["blue", "black"]), pygame.Rect(self.rect.x + random() * 120 - 26,
                                                                            self.rect.y + random() *
                                                                            120 - 26, 20, 10))


class DangerousOrb(pygame.sprite.Sprite):
    image = load_image("orb.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group)
        objects.add(self)
        everything.add(self)
        solids.add(self)
        self.image = DangerousOrb.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.accel = complex(0, 0)
        self.speed = complex(0, 0)
        self.target = targets.sprites()[0]

    def update(self):
        self.speed += self.accel
        self.speed -= self.speed / 4
        self.rect.x += self.speed.real
        self.rect.y += self.speed.imag
        target_pos = complex(self.target.rect.x, self.target.rect.y)
        pos = complex(self.rect.x, self.rect.y)
        self.accel = (target_pos - pos) * (1 / abs(target_pos - pos))


class BadTriangle(pygame.sprite.Sprite):
    image = load_image("triangle.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group)
        self.image = BadTriangle.image
        self.rect = self.image.get_rect()
        self.add(everything, objects, solids)
        self.rect.x = x
        self.rect.y = y
        self.accel = complex(0, 0)
        self.speed = complex(5, 0)
        self.hit_boxes = pygame.sprite.Group()
        self.right_box = HitBox(self.hit_boxes, self.rect.x + 91, self.rect.y + 5, 1, 70)
        self.left_box = HitBox(self.hit_boxes, self.rect.x - 1, self.rect.y + 5, 1, 70)
        self.right_down_box = HitBox(self.hit_boxes, self.rect.x + 90, self.rect.y + 90, 1, 1)
        self.left_down_box = HitBox(self.hit_boxes, self.rect.x - 1, self.rect.y + 90, 1, 1)
        self.hp = 100

    def update(self):
        self.speed += self.accel
        self.rect.x += self.speed.real
        self.right_box.set_pos(self.rect.x + 91, self.rect.y + 5)
        self.left_box.set_pos(self.rect.x - 1, self.rect.y + 5)
        self.right_down_box.set_pos(self.rect.x + 91, self.rect.y + 91)
        self.left_down_box.set_pos(self.rect.x - 1, self.rect.y + 91)
        blockers = pygame.sprite.Group(*player_hit_boxes.sprites(), *solids.sprites())
        if pygame.sprite.spritecollide(self.left_box, blockers, False) or \
                not pygame.sprite.spritecollide(self.left_down_box, blockers, False):
            self.speed = -self.speed
        if pygame.sprite.spritecollide(self.right_box, blockers, False) or \
                not pygame.sprite.spritecollide(self.right_down_box, blockers, False):
            self.speed = -self.speed
        if self.hp <= 0:
            self.remove(*groups)
        pygame.draw.rect(canvas, (255 * (1 - self.hp / 100), 255 * (self.hp / 100), 0),
                         (self.rect.x, self.rect.y - 20, self.hp, 10))


class Fireball(DangerousOrb):
    image = load_image("fireball.png", -1)

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        bullets.add(self)
        self.remove(solids)
        self.image = Fireball.image
        self.rect.size = Fireball.image.get_size()
        target_pos = complex(*pygame.mouse.get_pos())
        pos = complex(self.rect.x, self.rect.y)
        self.speed = (target_pos - pos) * (1 / abs(target_pos - pos)) * 20

    def update(self):
        self.rect.x += self.speed.real
        self.rect.y += self.speed.imag
        collided = pygame.sprite.spritecollide(self, solids, False)
        if collided:
            self.remove(*groups)
        for i in collided:
            if i.__class__ == DangerousOrb:
                i.remove(*groups)
            elif i.__class__ == BadTriangle:
                i.hp -= 25


class HitBox(pygame.sprite.Sprite):
    def __init__(self, group, x, y, w, h):
        super().__init__(group)
        everything.add(self)
        self.rect = pygame.rect.Rect(x, y, w, h)

    def set_pos(self, x, y):
        self.rect.x, self.rect.y = x, y


class Platform(SolidObject):
    image = load_image("platform.png")

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.image = Platform.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class FakePlatform(Platform):
    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)

    def update(self):
        if pygame.sprite.spritecollide(self, player_hit_boxes, False):
            self.remove(everything, objects, solids)
            self.kill()


class Entity(pygame.sprite.Sprite):
    def __init__(self, *group, x, y):
        super().__init__(*group, everything, objects, entities)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Health(Entity):
    image = load_image("health.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group, everything, objects, x=x, y=y)


class Button(pygame.sprite.Sprite):
    image = pygame.surface.Surface((0, 0))

    def __init__(self, x, y, w, h, color, line_width, rad, text, action, parameter, *group):
        super().__init__(*group)
        objects.add(self)
        everything.add(self)
        self.image = Button.image
        self.rect = pygame.rect.Rect(x, y, w, h)
        self.color = color
        self.width = line_width
        self.rad = rad
        self.text = text
        self.action = action
        self.parameter = parameter
        self.result = None
        self.is_pressed = False

    def update(self):
        pygame.draw.rect(canvas, self.color, self.rect, self.width, self.rad)
        text = font.render(self.text, False, "black")
        canvas.blit(text, (self.rect.x, self.rect.centery))
        if pygame.mouse.get_pressed(3)[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.clicked()
                self.is_pressed = True
        else:
            self.is_pressed = False

    def clicked(self):
        self.result = self.action(self.parameter)

    def get_result(self):
        res = self.result
        self.result = None
        return res


object_colors = {
    "(34, 177, 76)": SolidObject,
    "(255, 242, 0)": Player,
    "(237, 28, 36)": Fire,
    "(127, 127, 127)": Platform,
    "(195, 195, 195)": FakePlatform,
    "(255, 174, 201)": Health,
    "(163, 73, 164)": Ending,
    "(136, 0, 21)": Spikes,
    "(185, 122, 87)": DangerousOrb,
    "(0, 162, 232)": UnstableWall,
    "(200, 191, 231)": BadTriangle
}


# noinspection PyUnresolvedReferences
def convert_map(picture, map_file_name):
    with Image.open(os.path.join("data", picture)) as im:
        with open(os.path.join("data", map_file_name), "w+", encoding="utf8") as map_file:
            sx, sy = im.size
            pixels = im.load()
            for x in range(sx):
                for y in range(sy):
                    if str(pixels[x, y]) in object_colors.keys():
                        color = f"{pixels[x, y]}"
                        print(object_colors[color], x, y)
                        map_file.write(f"{color};{x};{y}\n")
                    elif pixels[x, y] not in ((255, 255, 255), (0, 0, 0)):
                        sys.stderr.write("Warning: unknown color!\n")


def open_map(map_file_name):
    owner = None
    for g in groups:
        g.empty()
    with open(os.path.join("data", map_file_name)) as map_file:
        for i in map_file.read().split("\n")[:-1]:
            line = i.split(";")
            if object_colors[line[0]] == Player:
                owner = object_colors[line[0]](x=int(line[1]), y=int(line[2]))
            else:
                object_colors[line[0]](x=int(line[1]), y=int(line[2]))
    return owner


if __name__ == '__main__':
    num_map = int(input("Map number:"))
    convert_map(f"map{num_map}.png", f"map{num_map}.hcm")
