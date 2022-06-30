# Flappy bird AI game, This program is written with the help of youtuber tech with tim
# Author : Tarun Chawla
# Date : 25/06/2022

# Important Imports
from json import load
import pygame
import pickle
import neat
import os
import random

# CONSTANTS
WIN_WIDTH = 500
WIN_HEIGHT = 780
GENERATIONS = 0
# Loading all the bird images in a list
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird1.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird2.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird3.png')))]

# Loading rest of images
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','pipe.png')))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bg.png')))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','base.png')))

# Basic initalizations
pygame.init()
pygame.font.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Fonts 
STAT_FONT = pygame.font.SysFont('comicsans', 50)
GEN_FONT = pygame.font.SysFont('comicsans', 30)

# Creating a bird class for the bird in the game

class Bird:
    IMGS = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.x
        self.img_count = 0
        self.img = self.IMGS[0]
    
    def jump(self):
        self.vel = - 10
        self.tick_count = 0
        self.height = self.x
    
    def move(self):
        self.tick_count += 1
        # equation from physics s = ut + 0.5at^2
        displacement = self.vel*self.tick_count + 0.5*(3)*(self.tick_count)**2

        if displacement >= 16:
            displacement = 16
        
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


    def Draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        
        new = blitRotateCenter(win, self.img, (self.x,self.y), self.tilt)
        win.blit(new[0], new[1])
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# Creating a pipe class
class Pipe:
    VEL = 5
    GAP = 200
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.passed = False
        self.top = 0
        self.bottom = 0

        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BOTTOM_PIPE = PIPE_IMAGE
        self.setHeight()
    
    def setHeight(self):
        self.height = random.randrange(50,420)
        self.top = self.height - self.TOP_PIPE.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
    
    def Draw(self, win):
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom))
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True
        
        return False

class Base:
    VEL = 5
    IMG = BASE_IMAGE
    WIDTH = IMG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        elif self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def Draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: rotated_image and new x, y
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    return (rotated_image,new_rect.topleft)



def drawWindow(win, birds, pipes, base, score, gen, alive):
    win.blit(BG_IMAGE, (0,0))
    for bird in birds:
        bird.Draw(win)
    
    for pipe in pipes:
        pipe.Draw(win)
    
    text = STAT_FONT.render(f'Score :{score}', True, (255,255,255))
    win.blit(text, (WIN_WIDTH - 15 - text.get_width(), 10))
    # text_gen = GEN_FONT.render(f'Generation :{gen}', True, (255,255,255))
    # text_gen = GEN_FONT.render(f'Generation :{gen}', True, (255,255,255))
    # win.blit(text_gen, (15 , 10))
    # text_alive = GEN_FONT.render(f'Alive : {alive}', True, (255,255,255))
    # win.blit(text_alive, (15 , 40))

    base.Draw(win)
    pygame.display.update()

def main(genemos, config):
    global GENERATIONS
    GENERATIONS += 1
    run = True
    birds = []
    net = []
    ge = []

    for _id, genemo in genemos:
        genemo.fitness = 0
        ge.append(genemo)
        net.append(neat.nn.FeedForwardNetwork.create(genemo, config))
        birds.append(Bird(230,350))
        
    pipes = [Pipe(600)]
    base = Base(710)
    clock = pygame.time.Clock()
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        rem = []
        add_pipe = False
        
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes)>1 and pipes[0].x+pipe.TOP_PIPE.get_width() < birds[0].x:
                pipe_index = 1
        else:
            run = False
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = net[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()
            
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    net.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x  < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        
        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(600))

        for pipe in rem:
            pipes.remove(pipe)
        
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                ge[x].fitness -= 1
                birds.pop(x)
                net.pop(x)
                ge.pop(x)
        if score > 50:
            run = False
            break
        base.move() 
        drawWindow(win, birds, pipes, base, score, GENERATIONS, len(birds))

def run(config_path):
    config = neat.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation, config_path)

    # for creating population
    # p = neat.Population(config)

    # forgetting stats
    # p.add_reporter(neat.StdOutReporter(True))
    # p.add_reporter(neat.StatisticsReporter())

    # running the fitness fuction
    # winner = p.run(main, 50)
    # print(winner)
    # saving Best Neural network
    # with open('BEST_BIRD.bin','wb') as file:
    #     pickle.dump(winner, file)
    
    best = None
    with open('BEST_BIRD.bin','rb') as file:
        best = pickle.load(file)
    
    main([(0,best)], config)
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)