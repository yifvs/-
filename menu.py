import pygame
import sys
import json
import os
from enum import Enum

# 菜单状态枚举
class MenuState(Enum):
    MAIN = 0
    SETTINGS = 1
    SKINS = 2
    ACHIEVEMENTS = 3
    DIFFICULTY = 4

# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        try:
            self.font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 36)  # 使用中文字体
        except:
            self.font = pygame.font.Font(None, 36)  # 如果找不到中文字体，使用默认字体
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# 菜单类
class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.background = (50, 50, 50)
        self.selected_speed = 5  # 默认速度
        try:
            self.title_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 72)  # 使用中文字体
            self.subtitle_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 36)  # 使用中文字体
        except:
            self.title_font = pygame.font.Font(None, 72)  # 如果找不到中文字体，使用默认字体
            self.subtitle_font = pygame.font.Font(None, 36)  # 如果找不到中文字体，使用默认字体
        self.setup_buttons()
        self.load_player_data()
        
    def setup_buttons(self):
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = self.screen_height // 2 - 50
        
        # 主菜单按钮
        self.main_buttons = [
            Button(self.screen_width//2 - button_width//2, start_y, 
                   button_width, button_height, "开始游戏", (0, 100, 0), (0, 150, 0)),
            Button(self.screen_width//2 - button_width//2, start_y + button_height + button_spacing, 
                   button_width, button_height, "难度选择", (100, 100, 0), (150, 150, 0)),
            Button(self.screen_width//2 - button_width//2, start_y + 2 * (button_height + button_spacing), 
                   button_width, button_height, "皮肤选择", (0, 0, 100), (0, 0, 150)),
            Button(self.screen_width//2 - button_width//2, start_y + 3 * (button_height + button_spacing), 
                   button_width, button_height, "成就", (100, 0, 100), (150, 0, 150)),
            Button(self.screen_width//2 - button_width//2, start_y + 4 * (button_height + button_spacing), 
                   button_width, button_height, "退出", (100, 0, 0), (150, 0, 0))
        ]
        
        # 难度选择按钮
        self.difficulty_buttons = []
        difficulties = [("简单", 5), ("中等", 8), ("困难", 12)]
        for i, (diff_name, speed_value) in enumerate(difficulties):
            x = self.screen_width//2 - button_width//2 + (i - 1) * (button_width + button_spacing)
            y = start_y + (i // 3) * (button_height + button_spacing)
            self.difficulty_buttons.append({
                "button": Button(x, y, button_width, button_height, diff_name, (0, 100, 100), (0, 150, 150)),
                "value": speed_value,
                "name": diff_name
            })
        
        # 皮肤选择按钮
        self.skin_buttons = []
        skins = [("绿色", (0, 255, 0)), ("蓝色", (0, 0, 255)), ("黄色", (255, 255, 0)), ("紫色", (128, 0, 128))]
        
        for i, (skin_name, skin_color) in enumerate(skins):
            x = self.screen_width//4 + (i % 2) * (button_width + button_spacing)
            y = start_y + (i // 2) * (button_height + button_spacing)
            self.skin_buttons.append({
                "button": Button(x, y, button_width//2, button_height, skin_name, skin_color, tuple(min(c+50, 255) for c in skin_color)),
                "color": skin_color,
                "name": skin_name,
                "unlocked": i < 2  # 默认解锁前两个皮肤
            })
            
        # 返回按钮 (用于非主菜单状态)
        self.back_button = Button(50, self.screen_height - 80, 150, 50, "返回", (100, 100, 100), (150, 150, 150))
        
    def load_player_data(self):
        # 默认玩家数据
        self.player_data = {
            "highest_score": 0,
            "highest_level": 1,
            "current_skin": "绿色",
            "unlocked_skins": ["绿色", "蓝色"],
            "achievements": []
        }
        
        # 尝试加载已存在的数据
        try:
            if os.path.exists("player_data.json"):
                with open("player_data.json", "r", encoding="utf-8") as f:
                    self.player_data = json.load(f)
                    
                # 更新皮肤解锁状态
                for skin_button in self.skin_buttons:
                    skin_button["unlocked"] = skin_button["name"] in self.player_data["unlocked_skins"]
        except Exception as e:
            print(f"加载玩家数据失败: {e}")
    
    def save_player_data(self):
        try:
            with open("player_data.json", "w", encoding="utf-8") as f:
                json.dump(self.player_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存玩家数据失败: {e}")
    
    def update_player_data(self, score, level):
        if score > self.player_data["highest_score"]:
            self.player_data["highest_score"] = score
        
        if level > self.player_data["highest_level"]:
            self.player_data["highest_level"] = level
            
            # 解锁新皮肤
            if level >= 5 and "黄色" not in self.player_data["unlocked_skins"]:
                self.player_data["unlocked_skins"].append("黄色")
                for skin in self.skin_buttons:
                    if skin["name"] == "黄色":
                        skin["unlocked"] = True
                        
            if level >= 10 and "紫色" not in self.player_data["unlocked_skins"]:
                self.player_data["unlocked_skins"].append("紫色")
                for skin in self.skin_buttons:
                    if skin["name"] == "紫色":
                        skin["unlocked"] = True
        
        self.save_player_data()
    
    def get_selected_skin_color(self):
        for skin in self.skin_buttons:
            if skin["name"] == self.player_data["current_skin"]:
                return skin["color"]
        return (0, 255, 0)  # 默认绿色
    
    def draw(self, screen):
        screen.fill(self.background)
        
        if self.state == MenuState.MAIN:
            # 绘制标题
            title = self.title_font.render("贪食蛇游戏", True, (255, 255, 255))
            screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # 绘制最高分和等级
            score_text = self.subtitle_font.render(f"最高分: {self.player_data['highest_score']}", True, (255, 255, 255))
            level_text = self.subtitle_font.render(f"最高等级: {self.player_data['highest_level']}", True, (255, 255, 255))
            screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, 180))
            screen.blit(level_text, (self.screen_width//2 - level_text.get_width()//2, 220))
            
            # 绘制按钮
            for button in self.main_buttons:
                button.draw(screen)
                
            # 绘制开发者信息
            try:
                dev_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 20)  # 使用较小的字体
            except:
                dev_font = pygame.font.Font(None, 20)  # 如果找不到中文字体，使用默认字体
            dev_info = dev_font.render("开发者: 王康业 | 版本: 1.0.0", True, (180, 180, 180))
            screen.blit(dev_info, (self.screen_width//2 - dev_info.get_width()//2, self.screen_height - 30))
                
        elif self.state == MenuState.SKINS:
            # 绘制标题
            title = self.title_font.render("皮肤选择", True, (255, 255, 255))
            screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # 添加皮肤解锁说明
            unlock_info = self.subtitle_font.render("黄色皮肤：达到5级解锁   紫色皮肤：达到10级解锁", True, (255, 215, 0))
            screen.blit(unlock_info, (self.screen_width//2 - unlock_info.get_width()//2, 160))
            
            # 绘制皮肤按钮
            for skin in self.skin_buttons:
                if skin["unlocked"]:
                    skin["button"].draw(screen)
                else:
                    # 绘制锁定的皮肤
                    pygame.draw.rect(screen, (100, 100, 100), skin["button"].rect, border_radius=10)
                    pygame.draw.rect(screen, (255, 255, 255), skin["button"].rect, 2, border_radius=10)
                    
                    # 绘制锁图标
                    lock_text = self.subtitle_font.render("🔒", True, (255, 255, 255))
                    screen.blit(lock_text, (skin["button"].rect.centerx - lock_text.get_width()//2, 
                                           skin["button"].rect.centery - lock_text.get_height()//2))
            
            # 显示当前选择的皮肤
            current_text = self.subtitle_font.render(f"当前皮肤: {self.player_data['current_skin']}", True, (255, 255, 255))
            screen.blit(current_text, (self.screen_width//2 - current_text.get_width()//2, self.screen_height - 150))
            
            # 绘制返回按钮
            self.back_button.draw(screen)
            
        elif self.state == MenuState.DIFFICULTY:
            # 绘制标题
            title = self.title_font.render("难度选择", True, (255, 255, 255))
            screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # 绘制难度说明
            descriptions = [
                "简单：速度较慢，适合新手",
                "中等：速度适中，挑战性增加",
                "困难：速度较快，考验反应能力"
            ]
            for i, desc in enumerate(descriptions):
                desc_text = self.subtitle_font.render(desc, True, (200, 200, 200))
                screen.blit(desc_text, (self.screen_width//2 - desc_text.get_width()//2, 180 + i*40))
            
            # 绘制难度按钮
            for diff in self.difficulty_buttons:
                diff["button"].draw(screen)
                if diff["value"] == self.selected_speed:
                    pygame.draw.rect(screen, (255, 255, 255), diff["button"].rect, 3, border_radius=10)
            
            # 显示当前选择的难度
            current_diff = "简单" if self.selected_speed == 5 else "中等" if self.selected_speed == 8 else "困难"
            current_text = self.subtitle_font.render(f"当前难度: {current_diff}", True, (255, 255, 255))
            screen.blit(current_text, (self.screen_width//2 - current_text.get_width()//2, self.screen_height - 150))
            
            # 绘制返回按钮
            self.back_button.draw(screen)
            
        elif self.state == MenuState.ACHIEVEMENTS:
            # 绘制标题
            title = self.title_font.render("成就", True, (255, 255, 255))
            screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # 显示成就列表
            achievements = [
                {"name": "初出茅庐", "desc": "达到5级", "unlocked": self.player_data["highest_level"] >= 5},
                {"name": "蛇王", "desc": "达到10级", "unlocked": self.player_data["highest_level"] >= 10},
                {"name": "高分达人", "desc": "获得500分", "unlocked": self.player_data["highest_score"] >= 500},
                {"name": "贪食之王", "desc": "获得1000分", "unlocked": self.player_data["highest_score"] >= 1000}
            ]
            
            y_pos = 200
            for achievement in achievements:
                color = (255, 255, 255) if achievement["unlocked"] else (150, 150, 150)
                name_text = self.subtitle_font.render(achievement["name"], True, color)
                desc_text = self.subtitle_font.render(achievement["desc"], True, color)
                
                # 调整文本位置和间距
                screen.blit(name_text, (self.screen_width//2 - 200, y_pos))
                screen.blit(desc_text, (self.screen_width//2 + 20, y_pos))
                
                # 显示解锁状态
                status = "✓" if achievement["unlocked"] else "✗"
                status_text = self.subtitle_font.render(status, True, color)
                screen.blit(status_text, (self.screen_width//2 + 200, y_pos))
                
                y_pos += 80  # 增加垂直间距
            
            # 绘制返回按钮
            self.back_button.draw(screen)
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_clicked = True
        
        if self.state == MenuState.MAIN:
            # 处理主菜单按钮
            for i, button in enumerate(self.main_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_clicked):
                    if i == 0:  # 开始游戏
                        return "start_game"
                    elif i == 1:  # 难度选择
                        self.state = MenuState.DIFFICULTY
                    elif i == 2:  # 皮肤选择
                        self.state = MenuState.SKINS
                    elif i == 3:  # 成就
                        self.state = MenuState.ACHIEVEMENTS
                    elif i == 4:  # 退出
                        pygame.quit()
                        sys.exit()
        
        elif self.state == MenuState.SKINS:
            # 处理皮肤选择
            for skin in self.skin_buttons:
                skin["button"].check_hover(mouse_pos)
                if skin["unlocked"] and skin["button"].is_clicked(mouse_pos, mouse_clicked):
                    self.player_data["current_skin"] = skin["name"]
                    self.save_player_data()
            
            # 处理返回按钮
            self.back_button.check_hover(mouse_pos)
            if self.back_button.is_clicked(mouse_pos, mouse_clicked):
                self.state = MenuState.MAIN
                
        elif self.state == MenuState.ACHIEVEMENTS:
            # 处理返回按钮
            self.back_button.check_hover(mouse_pos)
            if self.back_button.is_clicked(mouse_pos, mouse_clicked):
                self.state = MenuState.MAIN
                
        elif self.state == MenuState.DIFFICULTY:
            # 处理难度选择
            for diff in self.difficulty_buttons:
                diff["button"].check_hover(mouse_pos)
                if diff["button"].is_clicked(mouse_pos, mouse_clicked):
                    self.selected_speed = diff["value"]
                    self.state = MenuState.MAIN
            
            # 处理返回按钮
            self.back_button.check_hover(mouse_pos)
            if self.back_button.is_clicked(mouse_pos, mouse_clicked):
                self.state = MenuState.MAIN
                
        return None
