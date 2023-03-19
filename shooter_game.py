from pygame import *
from random import randint
from time import time as timer

#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
# mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

#шрифты и надписи
font.init()
font1 = font.SysFont('Arial', 80)
win = font1.render("YOU WIN!", True, (0, 200, 0))
lose = font1.render("YOU LOSE!", True, (200, 0, 0))
font2 = font.SysFont('Arial', 36)
font3 = font.SysFont('Arial', 50)

# нам нужны такие картинки:
img_back = "galaxy.jpg" # фон игры
img_hero = "rocket.png" # герой
img_enemy = "ufo.png" # враг
img_asteroid = "asteroid.png" # астероид
img_bullet = "bullet.png" # пуля

score = 0 # сбито кораблей
max_lost = 10 # проиграли, если пропустили столько
lost = 0 # пропущено кораблей
goal = 15 # сколько надо для выигрыша
life = 3 # сколько жизней

# класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
  # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)

        # каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
  # метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# класс главного игрока
class Player(GameSprite):
    # метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 80:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 165:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > win_height - 200:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < win_height - 105:
            self.rect.y += self.speed
  # метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx-7, self.rect.top, 15, 20, -20)
        bullets.add(bullet)

# класс спрайта-врага   
class Enemy(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = 0
            self.rect.x = randint(80, win_width - 80)
            return False
        
        return True

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

# Создаем окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# создаем спрайты
ship = Player(img_hero, 5, win_height - 165, 80, 100, 5)

monsters = sprite.Group()
x_monsters = []
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 3))
    monsters.add(monster)

bullets = sprite.Group()

asteroid = Asteroid(img_asteroid, randint(80, win_width - 80), -40, 80, 90, randint(5, 10))
is_asteroid_fly = False

rel_time = False
num_fire = 0

# переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
# Основной цикл игры:
run = True # флаг сбрасывается кнопкой закрытия окна
while run:
    # событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False

        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 10 and rel_time == False:
                    num_fire += 1
                    # fire_sound.play()
                    ship.fire()
                if num_fire >= 10 and rel_time == False:
                    last_time = timer()
                    rel_time = True

    if not finish:
        # обновляем фон
        window.blit(background,(0,0))

        # производим движения спрайтов
        ship.update()
        monsters.update() 

        # обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window) 
        bullets.update()
        bullets.draw(window)

        if rel_time == True:
            now_time = timer()

            if now_time - last_time < 3:
                reload = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False

        if randint(1, 150) == 1 and is_asteroid_fly == False:
            is_asteroid_fly = True

        if is_asteroid_fly:
            if not asteroid.update():
                is_asteroid_fly = False
            else:
                asteroid.reset()
        

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width-200), -40,80, 50, randint(1,3))
            monsters.add(monster)

        if sprite.spritecollide(ship,monsters, True) or sprite.collide_rect(ship, asteroid):
            life -= 1
            asteroid.rect.y = win_height

        if lost >= max_lost or life == 0:
            finish = True
            window.blit(lose, (200, 200))

        if score >= goal:
            finish = True
            window.blit(win, (200, 200)) 
        

        # пишем текст на экране
        text = font2.render("Счет: " + str(score)+ f'/{goal}', 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Пропущено: " + str(lost) + f'/{max_lost}', 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        if life == 3:
            color_life = ((0, 255, 0)) 
        elif life == 2:
            color_life = ((255, 186, 0))
        else: 
            color_life = ((255, 0, 0))

        text_life = font3.render('Жизней: '+ str(life) + '/3', 1, color_life)
        window.blit(text_life, (win_width-220, 20))

        display.update()
    
    else:
        time.delay(3000)
        finish = False
        score = 0
        lost = 0
        life = 3

        for m in monsters:
            m.kill()
        for b in bullets:
            b.kill()

        for i in range(1,6):
            monster = Enemy(img_enemy, randint(80, win_width-200), -40,80, 50, randint(1,3))
            monsters.add(monster)
        
    # цикл срабатывает каждую 0.05 секунд
    time.Clock().tick(90)