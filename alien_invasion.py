import pygame
from pygame.sprite import Group

from settings import Settings
from ship import Ship
import game_functions as gf
from game_status import GameStatus
from button import Button
from scoreboard import Scoreboard

def run_game():
    #初始化游戏并创建一个屏幕对象
    pygame.init()
    ai_setting = Settings()
    screen = pygame.display.set_mode(
        (ai_setting.screen_width,ai_setting.screen_height))
    pygame.display.set_caption("Alien Invasion")
    #创建一艘飞船
    ship = Ship(ai_setting,screen)
    #创建一个用于存储子弹的编组
    bullets = Group()
    #创建一个外星人编组
    aliens = Group()
    #创建外星人群
    gf.create_fleet(ai_setting,screen,ship,aliens)
    #创建一个用于存储游戏统计信息的实例
    status = GameStatus(ai_setting)
    sb = Scoreboard(ai_setting,screen,status)
    #创建按钮
    play_button = Button(ai_setting,screen,"Play")
    
    #开始游戏的主循环
    while True:
        gf.check_events(ai_setting,screen,status,play_button,sb,ship,aliens,bullets)
        
        if status.game_active:
            ship.update()
            gf.update_bullets(ai_setting,screen,status,sb,ship,bullets,aliens)
            gf.update_aliens(ai_setting,status,screen,sb,ship,aliens,bullets)
            
        gf.update_screen(ai_setting,screen,status,sb,ship,aliens,bullets,play_button)

run_game()
