import pygame
import sys
import random
from enum import Enum

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 初始化音效系统

# 加载音效
eat_sound = pygame.mixer.Sound('eat.wav')
gameover_sound = pygame.mixer.Sound('gameover.wav')

# 游戏常量
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 颜色定义
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0)
}

# 食物类型枚举
class FoodType(Enum):
    NORMAL = 1
    SPEED_UP = 2
    SPEED_DOWN = 3
    WALL_PASS = 4

# 蛇类
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.color = COLORS['GREEN']
        self.score = 0
        self.speed = 5  
        self.wall_pass = False
        self.growth_points = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        if not self.wall_pass and \
           (new[0] < 0 or new[0] >= GRID_WIDTH or \
            new[1] < 0 or new[1] >= GRID_HEIGHT):
            return False
        if new in self.positions[2:]:
            return False
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.speed = 5  # 将重置后的速度也改为5
        self.wall_pass = False

# 食物类
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = COLORS['RED']
        self.type = FoodType.NORMAL
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1),
                        random.randint(0, GRID_HEIGHT-1))
        self.type = random.choice(list(FoodType))
        if self.type == FoodType.NORMAL:
            self.color = COLORS['RED']
        elif self.type == FoodType.SPEED_UP:
            self.color = COLORS['YELLOW']
        elif self.type == FoodType.SPEED_DOWN:
            self.color = COLORS['BLUE']
        elif self.type == FoodType.WALL_PASS:
            self.color = COLORS['WHITE']

# 游戏主类
class Game:
    def __init__(self, speed=5):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪食蛇游戏')
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.snake.speed = speed  # 设置蛇的初始速度
        self.food = Food()
        self.level = 1
        self.obstacles = []
        self.paused = False  # 添加暂停状态变量

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    if self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    if self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)
                elif event.key == pygame.K_SPACE:  # 添加空格键暂停/继续功能
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:  # 添加ESC键退出功能
                    return "exit_to_menu"
        return None

    def draw_grid(self):
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                r = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, COLORS['WHITE'], r, 1)
                
    def update(self):
        key_action = self.handle_keys()
        if key_action == "exit_to_menu":
            return "exit_to_menu"  # 返回到菜单
            
        if self.paused:  # 如果游戏暂停，不更新游戏状态
            return False
            
        if not self.snake.update():
            gameover_sound.play()  # 播放游戏结束音效
            self.snake.reset()
            self.level = 1
            self.obstacles = []
            return True  # 游戏结束
    
            # 检查食物碰撞
        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.snake.score += 10
            eat_sound.play()  # 播放吃食物音效
            if self.food.type == FoodType.SPEED_UP:
                self.snake.speed += 2
            elif self.food.type == FoodType.SPEED_DOWN:
                self.snake.speed = max(5, self.snake.speed - 2)
            elif self.food.type == FoodType.WALL_PASS:
                self.snake.wall_pass = True
            self.food.randomize_position()
            self.snake.growth_points += 1

            # 升级检查
            if self.snake.growth_points >= 5:
                self.level += 1
                self.snake.growth_points = 0
                # 添加新的障碍物
                self.obstacles.append((random.randint(0, GRID_WIDTH-1),
                                     random.randint(0, GRID_HEIGHT-1)))
        
        return False  # 游戏继续

    def draw(self, screen):
        screen.fill(COLORS['BLACK'])
        self.draw_grid()

        # 绘制障碍物
        for obs in self.obstacles:
            pygame.draw.rect(screen, COLORS['WHITE'],
                           (obs[0]*GRID_SIZE, obs[1]*GRID_SIZE,
                            GRID_SIZE, GRID_SIZE))

        # 绘制蛇
        for p in self.snake.positions:
            pygame.draw.rect(screen, self.snake.color,
                           (p[0]*GRID_SIZE, p[1]*GRID_SIZE,
                            GRID_SIZE, GRID_SIZE))

        # 绘制食物
        pygame.draw.rect(screen, self.food.color,
                       (self.food.position[0]*GRID_SIZE,
                        self.food.position[1]*GRID_SIZE,
                        GRID_SIZE, GRID_SIZE))

        # 显示分数和等级
        try:
            font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 36)  # 使用中文字体
        except:
            font = pygame.font.Font(None, 36)  # 如果找不到中文字体，使用默认字体
            
        score_text = font.render(f'分数: {self.snake.score}', True, COLORS['WHITE'])
        level_text = font.render(f'等级: {self.level}', True, COLORS['WHITE'])
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        
        # 如果游戏暂停，显示暂停文本
        if self.paused:
            try:
                pause_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 72)  # 使用中文字体
            except:
                pause_font = pygame.font.Font(None, 72)  # 如果找不到中文字体，使用默认字体
            pause_text = pause_font.render("暂停", True, COLORS['WHITE'])
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(pause_text, pause_rect)

    def run(self):
        while True:
            game_over = self.update()
            if game_over:
                return
                
            self.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.snake.speed)

if __name__ == '__main__':
    game = Game()
    game.run()