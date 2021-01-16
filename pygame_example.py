import sys, pygame
import time

pygame.init()

size = width, height = 640, 480
speed = [1, 1]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball0 = pygame.image.load("intro_ball.gif")
ballrect = ball0.get_rect()
r = 0
frametime = time.perf_counter()
counter = 0
delta = 0
while True:
    start = time.perf_counter()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ball = pygame.transform.rotate(ball0,r)
    r+=0

    ballrect = ballrect.move(speed)

    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    #pygame.display.flip()   # Updates whole display, can be "slow" depending on the screen update needs
    pygame.display.update(ballrect)     # "dirty rectangle" method is faster
    #time.sleep(0.01)
    counter += 1
    delta += (time.perf_counter() - start)
    if (counter % 100) == 0:
        print(f'FPS = {1.0/(delta/100)}')
        delta = 0