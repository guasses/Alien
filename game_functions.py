import sys
from time import sleep

import pygame

from bullet import Bullet
from alien import Alien

def check_events(ai_setting,screen,status,play_button,sb,ship,aliens,bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_setting,screen,ship,bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_setting,screen,status,play_button,sb,ship,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_setting,screen,status,play_button,sb,ship,aliens,bullets,mouse_x,mouse_y):
    """在玩家单机play按钮时开始游戏"""
    button_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not status.game_active:
        #重置游戏设置
        ai_setting.initialize_dynamic_setting()
        #隐藏光标
        pygame.mouse.set_visible(False)
        #重置游戏统计信息
        status.reset_status()
        status.game_active = True

        #重置记分牌图像
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        #清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        #创建一群新的外星人，并让飞船居中
        create_fleet(ai_setting,screen,ship,aliens)
        ship.center_ship()

def check_keydown_events(event,ai_setting,screen,ship,bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_setting,screen,ship,bullets)
    elif event.key == pygame.K_q:
        sys.exit()

def fire_bullet(ai_setting,screen,ship,bullets):
    #创建一颗子弹，并将其加入编组bullets中,限制子弹数量
        if len(bullets) < ai_setting.bullets_allowed:
            new_bullet = Bullet(ai_setting,screen,ship)
            bullets.add(new_bullet)

def check_keyup_events(event,ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def update_screen(ai_setting,screen,status,sb,ship,aliens,bullets,play_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    #每次循环都会重绘图像
    screen.fill(ai_setting.bg_color)
    ship.blitme()
    aliens.draw(screen)
    #在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    #显示得分
    sb.show_score()

    #如果游戏处于非活动状态就绘制play按钮
    if not status.game_active:
        play_button.draw_button()
    #让每次绘制的屏幕可见
    pygame.display.flip()

def update_bullets(ai_setting,screen,status,sb,ship,bullets,aliens):
    """更新子弹的位置，并删除已消失的子弹"""
    #更新子弹的位置
    bullets.update()

    #删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
            
    check_bullet_alien_collisions(ai_setting,screen,status,sb,ship,bullets,aliens)

def check_bullet_alien_collisions(ai_setting,screen,status,sb,ship,bullets,aliens):
    """
        如果有子弹击中了外星人就删除子弹和外星人
        全部击落就删除现有的子弹并新建一群外星人
    """
    collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)

    if collisions:
        for aliens in collisions.values():
            status.score += ai_setting.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(status,sb)
    
    if len(aliens) == 0:
        #删除现有的子弹并新建一群外星人
        #如果整群外星人被消灭，就提高一个等级
        bullets.empty()
        ai_setting.increase_speed()

        #提高等级
        status.level += 1
        sb.prep_level()
        
        create_fleet(ai_setting,screen,ship,aliens)

def get_number_aliens_x(ai_setting,alien_width):
    """计算每行可容纳多少个外星人"""
    #外星人间距为外星人宽度
    available_space_x = ai_setting.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_setting,ship_height,alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = (ai_setting.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def create_alien(ai_setting,screen,aliens,alien_number,row_number):
    """创建一个外星人并将其放在当前行"""
    alien = Alien(ai_setting,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_setting,screen,ship,aliens):
    """创建外星人群"""
    #创建一个外星人，并计算一行可容纳多少个外星人
    alien = Alien(ai_setting,screen)
    number_aliens_x = get_number_aliens_x(ai_setting,alien.rect.width)
    number_rows = get_number_rows(ai_setting,ship.rect.height,
                                  alien.rect.height)
    #创建一行外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_setting,screen,aliens,alien_number,row_number)

def check_fleet_edges(ai_setting,aliens):
    """有外星人到达边缘时采取响应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_setting,aliens)
            break

def change_fleet_direction(ai_setting,aliens):
    """将整群外星人下移，并改变他们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_setting.fleet_drop_speed
    ai_setting.fleet_direction *= -1

def ship_hit(ai_setting,status,screen,sb,ship,aliens,bullets):
    """响应被外星人撞到的飞船"""
    if status.ships_left > 0:
        #将ships_left - 1
        status.ships_left -= 1

        #更新记分牌
        sb.prep_ships()

        #清空外星人和子弹列表
        aliens.empty()
        bullets.empty()

        #创建一群新的外星人，并将飞船放到屏幕底端中央
        create_fleet(ai_setting,screen,ship,aliens)
        ship.center_ship()
        
        #暂停
        sleep(0.5)
    else:
        status.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_setting,status,screen,sb,ship,aliens,bullets):
    """检查是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #向飞船被撞到一样处理
            ship_hit(ai_setting,status,screen,sb,ship,aliens,bullets)
            break

def update_aliens(ai_setting,status,screen,sb,ship,aliens,bullets):
    """检查是否有外星人在屏幕边缘"""
    """更新外星人群中所有外星人的位置"""
    check_fleet_edges(ai_setting,aliens)
    aliens.update()

    #检测外星人与飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_setting,status,screen,ship,aliens,bullets)

    #检查是否有外星人到达屏幕底端
    check_aliens_bottom(ai_setting,status,screen,sb,ship,aliens,bullets)

def check_high_score(status,sb):
    """检查是否诞生了新的最高分"""
    if status.score > status.high_score:
        status.high_score = status.score
        sb.prep_high_score()
