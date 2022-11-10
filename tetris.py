import pygame
import random

pygame.init()

width = 360
height = 480
size = 24
fps = 60
numberOfCols = 10
numberOfRows = 20
clock = pygame.time.Clock()
game_window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Super Tetris!")

counter = 0
speedUp = False

grid = [pygame.Rect(x*size, y*size, size, size) for x in range(numberOfCols%10, numberOfCols) for y in range(numberOfRows%20, numberOfRows)]

image1 = pygame.image.load('tile001.png')
image2 = pygame.image.load('tile002.png')
image3 = pygame.image.load('tile003.png')
image4 = pygame.image.load('tile004.png')
image5 = pygame.image.load('tile005.png')
image6 = pygame.image.load('tile006.png')
image7 = pygame.image.load('tile007.png')

font_30 = pygame.font.SysFont('Costantia', 32)
font_50 = pygame.font.SysFont('Costantia', 50)
font_80 = pygame.font.SysFont('Costantia', 80)

assets = {
    1: image1,
    2: image2,
    3: image3,
    4: image4,
    5: image5,
    6: image6,
    7: image7
}

running = True
pause = False


class Piece():
    FIGURES = {
        'I' : [[(1,0), (1,1), (1,2), (1,3)], [(0,2), (1,2), (2,2), (3,2)], [(2,0), (2,1), (2,2), (2,3)], [(0,1), (1,1), (2,1), (3,1)]],
        'O' : [[(0,0), (0,1), (1,0), (1,1)]],
        'J' : [[(0,0), (1,0), (1,1), (1,2)], [(0,1), (0,2), (1,1), (2,1)], [(1,0), (1,1), (1,2), (2,2)], [(0,1), (1,1), (2,0), (2,1)]],
        'L' : [[(0,2), (1,0), (1,1), (1,2)], [(0,1), (1,1), (2,1), (2,2)], [(1,0), (1,1), (1,2), (2,0)], [(0,0), (0,1), (1,1), (2,1)]],
        'S' : [[(0,1), (0,2), (1,0), (1,1)], [(0,1), (1,1), (1,2), (2,2)], [(1,1), (1,2), (2,0), (2,1)], [(0,0), (1,0), (1,1), (2,1)]],
        'Z' : [[(0,0), (0,1), (1,1), (1,2)], [(0,2), (1,1), (1,2), (2,1)], [(1,0), (1,1), (2,1), (2,2)], [(0,1), (1,0), (1,1), (2,0)]],
        'T' : [[(0,1), (1,0), (1,1), (1,2)], [(0,1), (1,1), (1,2), (2,1)], [(1,0), (1,1), (1,2), (2,1)], [(0,1), (1,0), (1,1), (2,1)]]
    }

    TYPES = ['I', 'I', 'O', 'J', 'L', 'T', 'S', 'Z']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = 0
        self.type = random.choice(self.TYPES)
        self.shape = self.FIGURES[self.type]
        self.dummyX = self.x + self.getSomething('pos', 1, 0)
        self.dummyY = self.y + self.getSomething('pos', 0, 0)
        self.color = random.randint(1,4)

    def state(self, index):
        return self.shape[(self.rotation + index) % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)
        self.dummyX = self.x + self.getSomething('pos', 1, 0)
        self.dummyY = self.y + self.getSomething('pos', 0, 0)

    def getSomething(self, Sthing, getSthing, whatShape):
        #1 for width, 0 for height
        currentShape = self.state(whatShape)
        min = 99
        max = 0
        for i in range(4):
            max = currentShape[i][getSthing] if currentShape[i][getSthing] > max else max
            min = currentShape[i][getSthing] if currentShape[i][getSthing] < min else min
        if Sthing.upper() == 'LENGTH':
            return max - min + 1
        elif Sthing.upper() == 'POS': #1 for X and 0 for Y
            return min

class Tetris():
    def __init__(self):
        self.board = [[0 for j in range(numberOfCols)] for i in range(numberOfRows)]
        self.level = 1
        self.nextFigure = None
        self.shadowFigure = None
        self.gameOver = False
        self.score = 0
        self.newInstance()

    def info(self):
        print(self.currentFigure.state(0))
        print('width = {}'.format(self.currentFigure.getSomething('length', 1, 0)))
        print('height = {}'.format(self.currentFigure.getSomething('length', 0, 0)))
        print('current x = {}'.format(self.currentFigure.dummyX))
        print('current y = {}'.format(self.currentFigure.dummyY))


    def fall(self):
        self.currentFigure.y += 1
        self.currentFigure.dummyY += 1
        if self.touchBorder():
            self.currentFigure.y -= 1
            self.currentFigure.dummyY -= 1
            self.freeze()

    def move(self, direction):
        self.currentFigure.x += direction
        self.currentFigure.dummyX += direction
        if self.touchBorder():
            self.currentFigure.x -= direction
            self.currentFigure.dummyX -= direction

    def dropBottom(self):
        if not self.gameOver:
            while not self.touchBorder():
                self.currentFigure.y += 1
                self.currentFigure.dummyY += 1
            self.currentFigure.y -= 1
            self.currentFigure.dummyY -= 1
            self.freeze()

    def checkRow(self):
        isContinue = False
        for y in range(numberOfRows-1, numberOfRows%20, -1):
            isFull = True
            for x in range(numberOfCols):
                if self.board[y][x] == 0:
                    isFull = False
                    break
            if isFull:
                del self.board[y]
                self.board.insert(0, [0 for i in range(numberOfCols)])
                isContinue = True
                self.score += 10*self.level
        if isContinue:
            self.checkRow()

    def rotate(self):
        nextX = self.currentFigure.x + self.currentFigure.getSomething('pos', 1, 1)
        if self.currentFigure.dummyY > 0:
            if not (nextX < 0 or nextX + self.currentFigure.getSomething('length', 1, 1) > numberOfCols):
                self.currentFigure.rotate()

    def freeze(self):
        currentShape = self.currentFigure.state(0)
        for x, y in currentShape:
            self.board[x+self.currentFigure.y][y+self.currentFigure.x] = self.currentFigure.color
        self.checkRow()
        self.newInstance()
        if self.touchBorder():
            self.gameOver = True

    def touchBorder(self):
        if self.currentFigure.dummyY >= 0:
            if self.currentFigure.dummyX < 0 or self.currentFigure.dummyX + self.currentFigure.getSomething('length', 1, 0) > numberOfCols:
                return True
            if self.currentFigure.dummyY + self.currentFigure.getSomething('length', 0, 0) > numberOfRows:
                return True
            for x, y in self.currentFigure.state(0):
                if self.board[x + self.currentFigure.y][y + self.currentFigure.x] > 0:
                    return True
        return False

    def newInstance(self):
        if not self.nextFigure:
            self.nextFigure = Piece(3, -1)
        self.currentFigure = self.nextFigure
        self.nextFigure = Piece(3, -1)

test = Tetris()

text2 = font_50.render('LOSER!', True, (255, 255, 255))
text3 = font_30.render('Press Q to Quit!', True, (255, 255, 255))
text4 = font_30.render('Press R to Restart!', True, (255, 255, 255))

while running:
    game_window.fill((0, 0, 0))
    pygame.draw.rect(game_window, (255, 255, 255), (-5, -5, 250, 490), 5)
    pygame.draw.rect(game_window, (255, 255, 255), (240, -5, 120, 100), 5)
    pygame.draw.rect(game_window, (255, 255, 255), (240, 90, 120, 100), 5)

    text = font_50.render(f'{test.score}', True, (255, 255, 255))
    game_window.blit(text, (250, 110))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                test.move(-1)
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                test.move(1)
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                test.rotate()
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                speedUp = True
            if event.key == pygame.K_SPACE:
                test.dropBottom()
            if event.key == pygame.K_p:
                pause = not pause
            if event.key == pygame.K_r:
                pause = False
                test.__init__()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                speedUp = False
    #Falling
    counter += 1
    if counter > 10000:
        counter = 0
    if not pause:
        if counter % (fps // (test.level * 2)) == 0 or speedUp:
            if not test.gameOver:
                test.fall()

    # [pygame.draw.rect(game_window, (40, 40, 40), i_rect, 1) for i_rect in grid]

    #Display current figure
    for x, y in test.currentFigure.state(0):
        if test.currentFigure.dummyY >= numberOfRows%20:
            img = assets[test.currentFigure.color]
            game_window.blit(img, ((y+test.currentFigure.x)*size, (x+test.currentFigure.y)*size))
            pygame.draw.rect(game_window, (255, 255, 255), ((y+test.currentFigure.x)*size, (x+test.currentFigure.y)*size, size, size), 1)

    #Display upcoming figure
    if test.nextFigure:
        for x, y in test.nextFigure.state(0):
            img = assets[test.nextFigure.color]
            game_window.blit(img, ((y+11)*size, (x+1)*size))

    #Display fixed figures
    for i in range(numberOfRows):
        for j in range(numberOfCols):
            if test.board[i][j] > 0:
                value = test.board[i][j]
                img = assets[value]
                game_window.blit(img, (j*size, i*size))
                pygame.draw.rect(game_window, (255, 255, 255), (j*size, i*size, size, size), 1)

    if test.gameOver:
        rect = pygame.Rect(40, 100, width-80, height-250)
        pygame.draw.rect(game_window, (0, 0, 0), rect)
        pygame.draw.rect(game_window, (255, 0, 0), rect, 2)

        game_window.blit(text2, (rect.centerx-text2.get_width()//2, rect.y+20))
        game_window.blit(text3, (rect.centerx-text3.get_width()//2, rect.y+80))
        game_window.blit(text4, (rect.centerx-text4.get_width()//2, rect.y+110))

    clock.tick(fps)
    pygame.display.flip()
pygame.quit()