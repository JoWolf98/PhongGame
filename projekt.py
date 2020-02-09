import pygame
import pygame.locals


class Board(object):
    """
    Odpowiada za rysowanie okna gry.
    """

    def __init__(self, width, height):
        """
        Konstruktor planszy :width,height:
        """
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption('Pong')

    def draw(self, *args):
        """
        Rysuje okno gry
        args: lista obiektów do narysowania
        """
        background = (219, 227, 222)
        self.surface.fill(background)
        for drawable in args:
            drawable.draw_on(self.surface)


        pygame.display.update()


class PongGame(object):
    """
    Łączy wszystkie elementy gry w całość.
    """

    def __init__(self, width, height):
        pygame.init()
        self.board = Board(width, height)
        # zegar którego użyjemy do kontrolowania szybkości rysowania kolejnych klatek gry
        self.fps_clock = pygame.time.Clock()
        self.ball = Ball(width=20, height=20, x=width/2, y=height/2)
        self.player1 = Racket(width=80, height=20, x=width/2 - 40, y=height - 40)
        self.player2 = Racket(width=80, height=20, x=width/2 - 40, y=20, color=(0, 0, 0))
        self.judge = Judge(self.board, self.ball, self.player2, self.ball)

        dane = []
        file = open('konfiguracyjny', 'r')
        for line in file:
            dane.append((int(line.split(":")[0])))

        file.close()

        if int(dane[2])==1:
            self.ai = Ai(self.player2, self.ball)

    def run(self):
        """
        Główna pętla programu
        """
        while not self.handle_events():
            # działaj w pętli do momentu otrzymania sygnału do wyjścia
            self.ball.move(self.board, self.player1, self.player2)
            self.board.draw(
                self.ball,
                self.player1,
                self.player2,
                self.judge,
            )
            dane = []
            file = open('konfiguracyjny', 'r')
            for line in file:
                dane.append((int(line.split(":")[0])))

            file.close()
            if int(dane[2]) == 1:
                self.ai.move()

            self.fps_clock.tick(30)

    def handle_events(self):
        """
        Obsługa zdarzeń systemowych, tutaj zinterpretujemy np. ruchy myszką
        """
        pause=False
        for event in pygame.event.get():               #get events from the queue
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True

            if event.type == pygame.locals.MOUSEMOTION:
                # myszka steruje ruchem pierwszego gracza
                x, y = event.pos                          #event.pos, aby uzyskać aktualne współrzędne wskaźnika myszy. Ta metoda zwraca parę wartości reprezentujących pozycję x i pozycję y wskaźnika myszy.
                self.player1.move(x)


            # poruszanie sie za pomoca klawiatury dla drugiego gracza

            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_LEFT:
                    self.player2.move_key(-20)
                if event.key==pygame.K_RIGHT:
                    self.player2.move_key(20)

            if event.type == pygame.KEYDOWN:                #zmiana szybkosci piłki za pomoca klawiszy 1-9
                if event.key == pygame.K_1:
                    self.ball.x_speed = 1
                    self.ball.y_speed = 1
                if event.key == pygame.K_2:
                    self.ball.x_speed = 2
                    self.ball.y_speed = 2
                if event.key == pygame.K_3:
                    self.ball.x_speed = 3
                    self.ball.y_speed = 3
                if event.key == pygame.K_4:
                    self.ball.x_speed = 4
                    self.ball.y_speed = 4
                if event.key == pygame.K_5:
                    self.ball.x_speed = 5
                    self.ball.y_speed = 5
                if event.key == pygame.K_6:
                    self.ball.x_speed = 6
                    self.ball.y_speed = 6
                if event.key == pygame.K_7:
                    self.ball.x_speed = 7
                    self.ball.y_speed = 7
                if event.key == pygame.K_8:
                    self.ball.x_speed = 8
                    self.ball.y_speed = 8
                if event.key == pygame.K_9:
                    self.ball.x_speed = 9
                    self.ball.y_speed = 9

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:               #za reset punktow odpowiada delete
                    self.judge.score[0] = 0
                    self.judge.score[1] = 0
                    self.ball.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:                 #za pauzowanie gry odpowiada space
                    pause=True                                  #za wznawianei gry odpowiada enter
                elif event.key == pygame.K_KP_ENTER:
                    pause =False

            if pause == True:
                pygame.time.delay(3000)
            if pause == False:
                pygame.time.delay(0)
                continue

class Drawable(object):
    """
    Klasa bazowa dla rysowanych obiektów
    """

    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface([width, height], pygame.SRCALPHA, 32).convert_alpha()           #Creates a new copy of the surface with the desired pixel format
        self.rect = self.surface.get_rect(x=x, y=y)                                                   #Zwraca nowy prostokąt pokrywający całą powierzchnię.

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)                                                           #  narysuj jeden obraz na innym


class Ball(Drawable):
    """
    Piłeczka, sama kontroluje swoją prędkość i kierunek poruszania się.
    """
    pygame.init()
    def __init__(self, width, height, x, y, color=(230, 28, 102), x_speed=3, y_speed=3):

        super(Ball, self).__init__(width, height, x, y, color)
        pygame.draw.ellipse(self.surface, self.color, [0, 0, self.width, self.height])                  #zrob szybkosc piłki konfigurwalna
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.start_x = x
        self.start_y = y


    def bounce_y(self):
        """
        Odwraca wektor prędkości w osi Y
        """
        self.y_speed *= -1

    def bounce_x(self):
        """
        Odwraca wektor prędkości w osi X
        """
        self.x_speed *= -1

    def reset(self):

        self.rect.x, self.rect.y = self.start_x, self.start_y  #wracamy piłka do położenia poczatkowego, wektor predkosci w osi Y zostaje odwrócony
        self.bounce_y()

    def move(self, board, *args):

        self.rect.x += self.x_speed            # poruszamy nasza pilka
        self.rect.y += self.y_speed

        if self.rect.x < 0 or self.rect.x > board.surface.get_width():
            self.bounce_x()

        if self.rect.y < 0 or self.rect.y > board.surface.get_height():
            self.bounce_y()

        for racket in args:
            if self.rect.colliderect(racket.rect):
                self.bounce_y()


class Racket(Drawable):

    wymiary = []
    file = open('konfiguracyjny', 'r')
    for line in file:
        wymiary.append((int(line.split(":")[0])))
    file.close()

    def __init__(self, width, height, x, y, color=(0, 255, 255), max_speed=10):  #tworzymy nasza rakiete prostokat
        super(Racket, self).__init__(width, height, x, y, color)
        self.max_speed = max_speed
        self.surface.fill(color)


    def move(self, x):
        # metoda pozwoli nam przesunac rakietke w dane miejsce
        delta = x - self.rect.x
        if abs(delta) > self.max_speed:
            delta = self.max_speed if delta > 0 else -self.max_speed
        self.rect.x += delta

    def move_key(self, b):
        self.rect.x= self.rect.x+b


class Ai(object):
    """
    Przeciwnik, steruje swoją rakietką na podstawie obserwacji piłeczki.
    """
    def __init__(self, racket, ball):
        dane = []
        file = open('konfiguracyjny', 'r')
        for line in file:
            dane.append((int(line.split(":")[0])))

        file.close()

        self.ball = ball
        self.racket = racket
        self.racket.max_speed=int(dane[3])
        print(self.racket.max_speed)

    def move(self):
        x = self.ball.rect.centerx
        self.racket.move(x)


class Judge(object):
    """
    Sędzia gry
    """

    def __init__(self, board, ball, *args):
        self.ball = ball
        self.board = board
        self.rackets = args
        self.score = [0, 0]


        pygame.font.init()
        font_path = pygame.font.match_font('arial')
        self.font = pygame.font.Font(font_path, 64)

    def update_score(self, board_height):

        if self.ball.rect.y < 0:             #przydzielamy punkty i wracamy do poczatkowego ulozenia pileczki
            self.score[0] += 1
            self.ball.reset()
        elif self.ball.rect.y > board_height:
            self.score[1] += 1
            self.ball.reset()

    def draw_text(self, surface,  text, x, y):

        # Rysuje wskazany tekst we wskazanym miejscu

        text = self.font.render(text, True, (150, 150, 150))
        rect = text.get_rect()
        rect.center = x, y
        surface.blit(text, rect)

    def draw_on(self, surface):
        """
        Aktualizuje i rysuje wyniki
        """
        height = self.board.surface.get_height()
        self.update_score(height)

        width = self.board.surface.get_width()
        self.draw_text(surface, "Player1: {}".format(self.score[0]), width/2, height * 0.3)
        self.draw_text(surface, "Player2: {}".format(self.score[1]), width/2, height * 0.7)



# Ta część powinna być zawsze na końcu modułu (ten plik jest modułem)

if __name__ == "__main__":
    wymiary=[]
    file = open('konfiguracyjny', 'r')
    for line in file:
        wymiary.append((int(line.split(":")[0])))

    game = PongGame(wymiary[0], wymiary[1])

game.run()