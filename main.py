# 导入自定义模块
from level_plain import *  # 导入简化关卡相关的所有类和函数
from sprites import *  # 导入精灵相关的所有类和函数


class Game:
    """游戏主类，负责管理游戏循环、渲染和事件处理"""
    
    def __init__(self):
        """初始化游戏基础设置"""
        pg.init()  # 初始化pygame
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # 创建游戏窗口
        self.rect = self.screen.get_rect()  # 获取屏幕矩形区域
        pg.display.set_caption(TITLE)  # 设置窗口标题
        self.clock = pg.time.Clock()  # 创建时钟对象用于控制帧率
        self.playing = True  # 游戏运行状态标志
        self.game_over = False  # 游戏结束标志
        self.all_group = pg.sprite.Group()  # 创建精灵组，管理所有精灵
        self.viewpoint = self.rect  # 视口（摄像机）位置，初始为整个屏幕

    def new(self):
        """开始新游戏，初始化游戏资源"""
        # 创建关卡表面（用于绘制关卡内容）
        self.level_surface = pg.Surface((WIDTH, HEIGHT)).convert()
        
        # 加载并处理背景图像
        self.background = load_image('level.png')  # 加载背景图片
        self.back_rect = self.background.get_rect()  # 获取背景图片的矩形区域
        # 缩放背景图片
        self.background = pg.transform.scale(
            self.background,
            (int(self.back_rect.width * BACKGROUND_SIZE),  # 计算缩放后的宽度
             int(self.back_rect.height * BACKGROUND_SIZE))  # 计算缩放后的高度
        ).convert()
        
        self.level = Level()  # 创建关卡实例
        self.all_group.add(self.level.mario)  # 将马里奥添加到精灵组

    def run(self):
        """游戏主循环"""
        while self.playing:  # 当游戏处于运行状态时
            self.clock.tick(FPS)  # 控制游戏帧率
            self.events()  # 处理事件
            self.update()  # 更新游戏状态
            self.draw()  # 绘制游戏画面
        
        # 游戏结束后显示结束画面
        self.show_end_screen()

    def update(self):
        """更新游戏状态"""
        if not self.game_over:
            self.all_group.update()  # 更新所有精灵
            self.level.update()  # 更新关卡
            
            # 控制马里奥在屏幕左侧边界的行为
            if self.level.mario.pos.x < self.viewpoint.x + 15:
                self.level.mario.pos.x -= self.level.mario.vel.x
                
            # 当马里奥向右移动时，滚动视口（摄像机跟随）
            if self.level.mario.vel.x > 0:
                if self.level.mario.pos.x > WIDTH * 0.55 + self.viewpoint.x:
                    self.viewpoint.x += int(self.level.mario.vel.x * 1.1)  # 视口以稍快速度跟随
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True  # 标记游戏结束
                self.playing = False   # 停止游戏主循环

    def events(self):
        """处理游戏事件"""
        for event in pg.event.get():  # 遍历所有事件
            if event.type == pg.QUIT:  # 如果点击关闭窗口
                self.playing = False  # 结束游戏
            # elif event.type == pg.MOUSEBUTTONDOWN and self.game_over:
                # 在结束画面中处理鼠标点击
                # self.handle_end_screen_click(event.pos)

    def draw(self):
        """绘制游戏画面"""
        if not self.game_over:
            # 正常游戏绘制
            pg.display.flip()  # 更新整个显示表面
            
            # 创建背景的干净副本用于绘制精灵
            self.background_clean = self.background.copy()
            self.all_group.draw(self.background_clean)  # 在背景副本上绘制所有精灵
            
            # 将背景的可见部分绘制到屏幕上
            self.screen.blit(self.background, (0, 0), self.viewpoint)
            self.all_group.draw(self.screen)  # 在屏幕上绘制所有精灵

    def show_start_screen(self):
        """显示开始屏幕（暂未实现）"""
        end_background = load_image('final.png')
        end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))
        
        restart_img = load_image('restart.png')
        button_width = restart_img.get_width()
        button_height = restart_img.get_height()
        restart_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 - button_height)
        self.restart_rect = pg.Rect(restart_pos[0], restart_pos[1], button_width, button_height)
        
        
        pass

    def show_end_screen_past(self):
        """显示结束屏幕，包含背景和按钮"""
        # 加载结束画面背景
        end_background = load_image('final.png')
        end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))
        
        # 加载按钮图片
        restart_img = load_image('restart.png')
        exit_img = load_image('exit.png')
        
        # 计算按钮位置（垂直排列在屏幕中央）
        button_width = restart_img.get_width()
        button_height = restart_img.get_height()
        
        restart_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 - button_height - 10)
        exit_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 + 10)
        
        # 创建按钮矩形区域用于点击检测
        self.restart_rect = pg.Rect(restart_pos[0], restart_pos[1], button_width, button_height)
        self.exit_rect = pg.Rect(exit_pos[0], exit_pos[1], button_width, button_height)
        
        # 结束画面循环
        end_screen = True
        while end_screen:
            self.clock.tick(FPS)
            
            # 处理事件
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end_screen = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # 检查按钮点击
                    if self.restart_rect.collidepoint(event.pos):
                        # 重新开始游戏
                        self.restart_game()
                        end_screen = False
                    elif self.exit_rect.collidepoint(event.pos):
                        # 退出游戏
                        end_screen = False
            
            # 绘制结束画面
            self.screen.blit(end_background, (0, 0))
            self.screen.blit(restart_img, restart_pos)
            self.screen.blit(exit_img, exit_pos)
            
            pg.display.flip()
        
        pg.quit()

    def show_end_screen_past2(self):
        """显示结束屏幕，包含背景、统一大小的按钮和视觉效果"""
        # 加载结束画面背景
        end_background = load_image('final.png')
        end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))
    
        # 加载按钮图片
        restart_img_orig = load_image('restart.png')
        exit_img_orig = load_image('exit.png')
    
    # 统一按钮尺寸 - 使用两个按钮中较大的尺寸
        max_width = max(restart_img_orig.get_width(), exit_img_orig.get_width())
        max_height = max(restart_img_orig.get_height(), exit_img_orig.get_height())
    
        # 统一按钮尺寸（可以改变系数）
        button_width = int(max_width * 0.7)
        button_height = int(max_height * 0.7)
    
        # 缩放按钮图片到统一尺寸
        restart_img = pg.transform.scale(restart_img_orig, (button_width, button_height))
        exit_img = pg.transform.scale(exit_img_orig, (button_width, button_height))
    
    # 计算按钮位置（垂直排列在屏幕中央）
        restart_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 - button_height - 20)
        exit_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 + 20)
    
    # 创建按钮矩形区域用于点击检测
        self.restart_rect = pg.Rect(restart_pos[0], restart_pos[1], button_width, button_height)
        self.exit_rect = pg.Rect(exit_pos[0], exit_pos[1], button_width, button_height)
    
    # 视觉效果变量
        border_thickness = 3  # 边框厚度
        blink_interval = 500  # 闪烁间隔（毫秒）
        last_blink_time = pg.time.get_ticks()
        show_border = True    # 边框显示状态
        hover_restart = False # 鼠标悬停在重新开始按钮上
        hover_exit = False    # 鼠标悬停在退出按钮上
    
    # 结束画面循环
        end_screen = True
        while end_screen:
            current_time = pg.time.get_ticks()
            self.clock.tick(FPS)
        
        # 获取鼠标位置
            mouse_pos = pg.mouse.get_pos()
        
        # 更新悬停状态
            hover_restart = self.restart_rect.collidepoint(mouse_pos)
            hover_exit = self.exit_rect.collidepoint(mouse_pos)
        
        # 处理事件
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end_screen = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                # 检查按钮点击
                    if self.restart_rect.collidepoint(event.pos):
                    # 重新开始游戏
                        self.restart_game()
                        end_screen = False
                    elif self.exit_rect.collidepoint(event.pos):
                    # 退出游戏
                        end_screen = False
        
        # 闪烁效果 - 每500毫秒切换一次边框显示
            if current_time - last_blink_time > blink_interval:
                show_border = not show_border
                last_blink_time = current_time
        
        # 绘制结束画面
            self.screen.blit(end_background, (0, 0))
        
        # 绘制按钮
            self.screen.blit(restart_img, restart_pos)
            self.screen.blit(exit_img, exit_pos)
        
        # 绘制边框效果
            if show_border:
            # 重新开始按钮边框
                border_color = (255, 215, 0) if hover_restart else (255, 255, 255)  # 悬停时金色，否则白色
                pg.draw.rect(self.screen, border_color, self.restart_rect, border_thickness)
            
            # 退出按钮边框
                border_color = (255, 215, 0) if hover_exit else (255, 255, 255)  # 悬停时金色，否则白色
                pg.draw.rect(self.screen, border_color, self.exit_rect, border_thickness)
        
        # 悬停效果 - 按钮轻微放大
            if hover_restart:
                # 绘制放大的重新开始按钮
                hover_scale = 1.1
                hover_width = int(button_width * hover_scale)
                hover_height = int(button_height * hover_scale)
                hover_restart_img = pg.transform.scale(restart_img_orig, (hover_width, hover_height))
                hover_pos = (restart_pos[0] - (hover_width - button_width) // 2, 
                        restart_pos[1] - (hover_height - button_height) // 2)
                self.screen.blit(hover_restart_img, hover_pos)
        
            if hover_exit:
            # 绘制放大的退出按钮
                hover_scale = 1.1
                hover_width = int(button_width * hover_scale)
                hover_height = int(button_height * hover_scale)
                hover_exit_img = pg.transform.scale(exit_img_orig, (hover_width, hover_height))
                hover_pos = (exit_pos[0] - (hover_width - button_width) // 2, 
                        exit_pos[1] - (hover_height - button_height) // 2)
                self.screen.blit(hover_exit_img, hover_pos)
        
            pg.display.flip()
    
        pg.quit()

    def show_end_screen(self):
        """显示结束屏幕，包含背景和按钮效果"""
        # 加载资源
        end_background, restart_img_orig, exit_img_orig = self.load_end_screen_resources()
        
        # 统一按钮尺寸
        button_width, button_height, restart_img, exit_img = self.unify_button_size(
            restart_img_orig, exit_img_orig, scale_factor=0.7
        )
        
        # 设置按钮位置
        restart_pos, exit_pos, restart_rect, exit_rect = self.set_button_positions(
            button_width, button_height
        )
        
        # 结束画面主循环
        self.run_end_screen_loop(
            end_background, restart_img_orig, exit_img_orig,
            restart_img, exit_img, restart_pos, exit_pos,
            restart_rect, exit_rect, button_width, button_height
        )
        
        pg.quit()

    def load_end_screen_resources(self):
        """加载结束画面所需资源"""
        # 加载结束画面背景
        end_background = load_image('final.png')
        end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))
        
        # 加载按钮图片
        restart_img_orig = load_image('restart.png')
        exit_img_orig = load_image('exit.png')
        
        return end_background, restart_img_orig, exit_img_orig

    def unify_button_size(self, restart_img_orig, exit_img_orig, scale_factor=0.7):
        """统一按钮尺寸"""
        # 使用两个按钮中较大的尺寸
        max_width = max(restart_img_orig.get_width(), exit_img_orig.get_width())
        max_height = max(restart_img_orig.get_height(), exit_img_orig.get_height())
        
        # 统一按钮尺寸
        button_width = int(max_width * scale_factor)
        button_height = int(max_height * scale_factor)
        
        # 缩放按钮图片到统一尺寸
        restart_img = pg.transform.scale(restart_img_orig, (button_width, button_height))
        exit_img = pg.transform.scale(exit_img_orig, (button_width, button_height))
        
        return button_width, button_height, restart_img, exit_img

    def set_button_positions(self, button_width, button_height):
        """设置按钮位置"""
        # 计算按钮位置（垂直排列在屏幕中央）
        restart_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 - button_height - 20)
        exit_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 + 20)
        
        # 创建按钮矩形区域
        restart_rect = pg.Rect(restart_pos[0], restart_pos[1], button_width, button_height)
        exit_rect = pg.Rect(exit_pos[0], exit_pos[1], button_width, button_height)
        
        return restart_pos, exit_pos, restart_rect, exit_rect

    def run_end_screen_loop(self, end_background, restart_img_orig, exit_img_orig,
                        restart_img, exit_img, restart_pos, exit_pos,
                        restart_rect, exit_rect, button_width, button_height):
        """运行结束画面主循环"""
        # 视觉效果变量
        border_thickness = 3
        blink_interval = 500
        last_blink_time = pg.time.get_ticks()
        show_border = True
        
        # 结束画面循环
        end_screen = True
        while end_screen:
            current_time = pg.time.get_ticks()
            self.clock.tick(FPS)
            
            # 处理事件
            end_screen = self.handle_end_screen_events(restart_rect, exit_rect)
            if not end_screen:
                break
                
            # 获取鼠标位置和悬停状态
            mouse_pos = pg.mouse.get_pos()
            hover_restart = restart_rect.collidepoint(mouse_pos)
            hover_exit = exit_rect.collidepoint(mouse_pos)
            
            # 更新闪烁效果
            show_border, last_blink_time = self.update_blink_effect(
                current_time, last_blink_time, blink_interval, show_border
            )
            
            # 绘制结束画面
            self.draw_end_screen(
                end_background, restart_img, exit_img, restart_pos, exit_pos,
                restart_rect, exit_rect, hover_restart, hover_exit,
                show_border, border_thickness,
                restart_img_orig, exit_img_orig, button_width, button_height
            )
            
            pg.display.flip()

    def handle_end_screen_events(self, restart_rect, exit_rect):
        """处理结束画面事件"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            elif event.type == pg.MOUSEBUTTONDOWN:
                # 检查按钮点击
                if restart_rect.collidepoint(event.pos):
                    # 重新开始游戏
                    self.restart_game()
                    return False
                elif exit_rect.collidepoint(event.pos):
                    # 退出游戏
                    return False
        return True

    def update_blink_effect(self, current_time, last_blink_time, blink_interval, show_border):
        """更新边框闪烁效果"""
        if current_time - last_blink_time > blink_interval:
            show_border = not show_border
            last_blink_time = current_time
        return show_border, last_blink_time

    def draw_end_screen(self, end_background, restart_img, exit_img, 
                    restart_pos, exit_pos, restart_rect, exit_rect,
                    hover_restart, hover_exit, show_border, border_thickness,
                    restart_img_orig, exit_img_orig, button_width, button_height):
        """绘制结束画面"""
        # 绘制背景
        self.screen.blit(end_background, (0, 0))
        
        # 应用按钮效果
        self.apply_button_effects(
            restart_img, exit_img, restart_pos, exit_pos,
            restart_rect, exit_rect, hover_restart, hover_exit,
            show_border, border_thickness,
            restart_img_orig, exit_img_orig, button_width, button_height
        )

    def apply_button_effects(self, restart_img, exit_img, restart_pos, exit_pos,
                            restart_rect, exit_rect, hover_restart, hover_exit,
                            show_border, border_thickness,
                            restart_img_orig, exit_img_orig, button_width, button_height):
        """应用按钮效果（放大和边框闪烁）"""
        # 绘制正常按钮或悬停放大按钮
        self.draw_button_with_hover_effect(
            restart_img, restart_img_orig, restart_pos, restart_rect,
            hover_restart, button_width, button_height
        )
        
        self.draw_button_with_hover_effect(
            exit_img, exit_img_orig, exit_pos, exit_rect,
            hover_exit, button_width, button_height
        )
        
        # 绘制边框效果
        if show_border:
            self.draw_button_borders(
                restart_rect, exit_rect, hover_restart, hover_exit, border_thickness
            )

    def draw_button_with_hover_effect(self, button_img, button_img_orig, button_pos, button_rect,
                                    is_hovered, button_width, button_height):
        """绘制按钮并应用悬停放大效果"""
        if is_hovered:
            # 绘制放大的按钮
            hover_scale = 1.1
            hover_width = int(button_width * hover_scale)
            hover_height = int(button_height * hover_scale)
            hover_img = pg.transform.scale(button_img_orig, (hover_width, hover_height))
            hover_pos = (
                button_pos[0] - (hover_width - button_width) // 2,
                button_pos[1] - (hover_height - button_height) // 2
            )
            self.screen.blit(hover_img, hover_pos)
        else:
            # 绘制正常按钮
            self.screen.blit(button_img, button_pos)

    def draw_button_borders(self, restart_rect, exit_rect, hover_restart, hover_exit, border_thickness):
        """绘制按钮边框效果"""
        # 重新开始按钮边框
        border_color = (255, 215, 0) if hover_restart else (255, 255, 255)  # 悬停时金色，否则白色
        pg.draw.rect(self.screen, border_color, restart_rect, border_thickness)
        
        # 退出按钮边框
        border_color = (255, 215, 0) if hover_exit else (255, 255, 255)  # 悬停时金色，否则白色
        pg.draw.rect(self.screen, border_color, exit_rect, border_thickness)   
        
        
        
        
        
        

        def handle_end_screen_click(self, pos):
            """处理结束画面的鼠标点击事件"""
            if self.restart_rect.collidepoint(pos):
                self.restart_game()
            elif self.exit_rect.collidepoint(pos):
                self.playing = False

        def restart_game(self):
            """重新开始游戏"""
            # 重置游戏状态
            self.playing = True
            self.game_over = False
            self.viewpoint = self.rect
            
            # 重新初始化游戏
            self.all_group.empty()  # 清空精灵组
            self.new()  # 重新创建关卡
            
            # 重新开始游戏循环
            self.run()


# 游戏启动代码
game = Game()  # 创建游戏实例
game.show_start_screen()  # 显示开始屏幕
game.new()  # 初始化新游戏
game.run()  # 运行游戏主循环