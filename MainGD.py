import pygame
import neat
import random
import os

pygame.font.init()

gen_number = -1
VEL = 10

WIN_WIDTH = 800
WIN_HEIGHT = 680
CUBE = pygame.transform.scale(pygame.image.load(os.path.join("images", "esse2.png")), (75, 75))
BLOCK = pygame.transform.scale(pygame.image.load(os.path.join("images", "block.png")), (75, 75))
SPIKE = pygame.transform.scale(pygame.image.load(os.path.join("images", "a1.png")), (50, 50))
BG = pygame.image.load(os.path.join("images", "bg1.jpg"))
BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base1.png")))
FONT = pygame.font.SysFont("freesansbold.ttf", 50)


class Cube:
    ROTATION_VEL = 6

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick = 0
        self.vel = 0
        self.height = self.y
        self.img = CUBE
        self.rot = 0
        self.subiu = False
        self.distance_spike = 0
        self.distance_block = 0

    def could_jump(self):

        if self.y == WIN_HEIGHT - BASE.get_height() - self.img.get_height() + 5 or self.y == WIN_HEIGHT - BASE.get_height() - BLOCK.get_height() - CUBE.get_height():
            return True
        else:
            return False

    def jump(self):

        self.vel = -10.5
        self.tick = 0
        self.height = self.y

        self.rot += 1
        if self.rot == 5:
            self.rot = 1
            self.tilt = 0

    def move(self, blocks):
        # CUBE PHYSICS
        self.tick += 1
        self.y += self.vel * self.tick + 1.0 * self.tick ** 2

        # CUBE AND BASE INTERACTION
        if self.y > WIN_HEIGHT - BASE.get_height() - self.img.get_height() + 5:
            self.y = WIN_HEIGHT - BASE.get_height() - self.img.get_height() + 5
            self.vel = 0
        # CUBE AND BLOCKS INTERACTION

        for block in blocks:
            if self.x + CUBE.get_width() > block.x and self.x < block.x + BLOCK.get_width() and self.y + CUBE.get_height() < block.y:
                self.subiu = True
            if self.subiu is True and self.y + CUBE.get_height() > block.y:
                self.y = block.y - CUBE.get_height()
                # self.subiu = True
            if self.x > block.x + BLOCK.get_width() and self.subiu is True:
                self.subiu = False
                if self.y + CUBE.get_height() == block.y:
                    self.tick = 0

        # CUBE ROTATION AFTER JUMP
        if self.tilt > -90 * self.rot:
            self.tilt -= self.ROTATION_VEL

    def draw(self, win):
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Base:
    WIDTH = BASE.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.img = BASE

    def move(self):
        self.x1 -= VEL
        self.x2 -= VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


class Bg:
    WIDTH = BG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.img1 = BG
        self.img2 = pygame.transform.flip(BG, True, False)

    def move(self):
        self.x1 -= VEL
        self.x2 -= VEL
        # self.x3 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.img1, (self.x1, self.y))
        win.blit(self.img2, (self.x2, self.y))


class Spike:

    def __init__(self, y):
        self.x = 0
        self.y = y
        self.img = SPIKE
        self.passed = False
        self.distance_b = 0
        self.set_spike()

    def set_spike(self):
        self.x = 800  # = random.randrange(600, 900)

    def move(self):
        self.x -= VEL

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collision(self, cube):
        cube_mask = cube.get_mask()
        spike_mask = pygame.mask.from_surface(self.img)
        offset = (round(self.x - cube.x), round(self.y - cube.y))
        point = cube_mask.overlap(spike_mask, offset)

        if point:
            return True

        return False


class Block:

    def __init__(self, y):
        self.x = 0
        self.y = y
        self.img = BLOCK
        self.passed = False
        self.set_block()

    def set_block(self):
        self.x = 1200  # random.randrange(1300, 1600)

    def move(self):
        self.x -= VEL

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collision(self, cube):
        cube_mask = cube.get_mask()
        block_mask = pygame.mask.from_surface(self.img)
        offset = (round(self.x - cube.x), round(self.y - cube.y))
        point = cube_mask.overlap(block_mask, offset)

        if point:
            return True

        return False


def draw_game(win, cubes, background, spikes, blocks, base, gener, alive):
    background.draw(win)
    base.draw(win)
    for cube in cubes:
        cube.draw(win)
    for spike in spikes:
        spike.draw(win)
    for block in blocks:
        block.draw(win)
    for cube in cubes:
        for spike in spikes:
            if len(spikes) > 0:
                pygame.draw.line(win, (65, 154, 255), (cube.x + cube.img.get_width() / 2, cube.y + cube.img.get_height() / 2), (cube.x + cube.img.get_width() / 2 + cube.distance_spike - 5, spike.y + spike.img.get_height() / 2), 5)
        for block in blocks:
            if len(blocks) > 0:
                pygame.draw.line(win, (100, 100, 100), (cube.x + cube.img.get_width() / 2, cube.y + cube.img.get_height() / 2), (cube.x + cube.img.get_width() / 2 + cube.distance_block - 5, block.y + block.img.get_height() / 2), 3)
    text = FONT.render("Generation: " + str(gener), True, (255, 255, 0))
    win.blit(text, (770 - text.get_width(), 30))
    text1 = FONT.render("Alive: " + str(alive), True, (255, 0, 0))
    win.blit(text1, (770 - text.get_width(), 60))

    pygame.display.update()


def main(genomes, config):
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    base = Base(WIN_HEIGHT - BASE.get_height())
    background = Bg(0)
    spikes = [Spike(WIN_HEIGHT - BASE.get_height() - SPIKE.get_height())]
    blocks = [Block(WIN_HEIGHT - BASE.get_height() - BLOCK.get_height())]
    distances = list()
    # NEAT
    cubes = list()
    nets = list()
    ge = list()
    for _, g in genomes:
        net = neat.nn.feed_forward.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cubes.append(Cube(200, 200))
        g.fitness = 0
        ge.append(g)

    global gen_number
    gen_number += 1
    choice = 0
    alive = 200

    timer = pygame.time.Clock()
    flag = True
    while flag:
        timer.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                flag = False
                pygame.quit()
                quit()
            # JUMP TEST WITH SPACE-BAR
            # if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            #   cube.jump()

        # NEAT CUBES

        for cube in cubes:
            for spike in spikes:
                    d = spike.x - cube.x
                    if d > 0:
                        distances.append(d)
            if len(distances) > 0:
                cube.distance_spike = min(distances)
            else:
                cube.distance_spike = 800
            distances.clear()
            for block in blocks:
                    d = block.x - cube.x
                    if d > 0:
                        distances.append(d)
            if len(distances) > 0:
                cube.distance_block = min(distances)
            else:
                cube.distance_block = 800
            distances.clear()

        if len(cubes) > 0:
            pass
        else:
            flag = False
            break

        for x, cube in enumerate(cubes):
            cube.move(blocks)
            ge[x].fitness += 0.1
            # print(cube.tick, cube.could_jump(), cube.distance_spike, cube.distance_block)
            output = nets[x].activate((cube.tick, cube.distance_spike, cube.distance_block))  # NEAT EDIT HERE --------
            if output[0] > 0.5 and cube.could_jump():
                cube.jump()
                # ge[x].fitness += 2

        # END OF NEAT CUBES

        background.move()
        base.move()
        remove_spikes = list()
        remove_blocks = list()
        # SPIKES
        add_fit = False
        for spike in spikes:
            for x, cube in enumerate(cubes):
                if spike.collision(cube):
                    # ge[x].fitness -= 1
                    cubes.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    alive -= 1

                if cube.x > spike.x + SPIKE.get_width():
                    spike.passed = True
                    add_fit = True
                    # ge[x].fitness += 20

            if spike.x + spike.img.get_width() < 0:
                remove_spikes.append(spike)

            spike.move()

        if add_fit:
            add_fit = False
            for g in ge:
                g.fitness += 8
        # BLOCKS
        for block in blocks:
            for x, cube in enumerate(cubes):

                # BLOCK COLLISION TEST
                if block.collision(cube):
                    # ge[x].fitness -= 1.5
                    cubes.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    alive -= 1
                # BLOCK COLLISION TEST

                if cube.x > block.x + BLOCK.get_width():
                    block.passed = True
                    add_fit = True
                    # ge[x].fitness += 20

            if block.x + block.img.get_width() < 0:
                remove_blocks.append(block)

            block.move()

        if add_fit:
            for g in ge:
                g.fitness += 8

        # ADD A RANDOM SETUP
        while (len(spikes) + len(blocks)) <= 1:
            # spikes.append(Spike(WIN_HEIGHT - BASE.get_height() - SPIKE.get_height()))

            choice += 1
            if choice == 3:
                blocks.append(Block(WIN_HEIGHT - BASE.get_height() - BLOCK.get_height()))
                choice = 0
            else:
                spikes.append(Spike(WIN_HEIGHT - BASE.get_height() - SPIKE.get_height()))

        # REMOVE
        for r in remove_spikes:
            spikes.remove(r)
        for r in remove_blocks:
            blocks.remove(r)

        draw_game(win, cubes, background, spikes, blocks, base, gen_number, alive)


def run(conf_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, conf_path)
    pop = neat.Population(config)

    # Set a report
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    # End of report

    winner = pop.run(main, 200)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEATconfig.txt")
    run(config_path)
