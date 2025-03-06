import pygame
import sys
from menu import Menu
from main import Game, WINDOW_WIDTH, WINDOW_HEIGHT

# 初始化Pygame
pygame.init()

# 游戏状态枚举
class GameState:
    MENU = 0
    PLAYING = 1

# 游戏管理器类
class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪食蛇游戏')
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game = None
        
    def run(self):
        while True:
            if self.state == GameState.MENU:
                # 处理菜单
                action = self.menu.handle_events()
                if action == "start_game":
                    # 从菜单切换到游戏
                    self.game = Game(speed=self.menu.selected_speed)
                    # 设置蛇的颜色为选择的皮肤颜色
                    self.game.snake.color = self.menu.get_selected_skin_color()
                    self.state = GameState.PLAYING
                self.menu.draw(self.screen)
            
            elif self.state == GameState.PLAYING:
                # 处理游戏
                game_over = self.game.update()
                if game_over == True:
                    # 游戏结束，更新玩家数据并返回菜单
                    self.menu.update_player_data(self.game.snake.score, self.game.level)
                    self.state = GameState.MENU
                elif game_over == "exit_to_menu":
                    # 玩家按ESC键返回菜单
                    self.state = GameState.MENU
                else:
                    self.game.draw(self.screen)
            
            pygame.display.update()
            if self.state == GameState.PLAYING:
                self.clock.tick(self.game.snake.speed)
            else:
                self.clock.tick(60)

if __name__ == "__main__":
    manager = GameManager()
    manager.run()