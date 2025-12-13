# 导入自定义模块
from level_data import *
from level_c import *  # 导入简化关卡相关的所有类和函数
from mario import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精update灵相关的所有类和函数
import math  # 用于数学计算和旋转

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
        self.viewpoint = self.rect # 视口（摄像机）位置，初始为整个屏幕

        
        
        # 关卡管理
        self.current_level = 1  # 当前关卡编号
        self.levels = {
            1: level1_data,
            2: level2_data,
            3: level3_data
        }


 # 成功动画相关变量
        self.success_animation = False  # 是否正在播放成功动画
        self.success_start_time = 0  # 成功动画开始时间
        self.mario_rise_start_y = 0  # 马里奥上升开始时的Y坐标
        self.show_congrats = False  # 是否显示祝贺文本
        self.congrats_start_time = 0  # 祝贺文本开始显示的时间
        self.game_ending = False  # 游戏正在结束中
        self.debug=True             #因为通关后再按左右空格马里奥会继续在success动画里上升一段，猜测是elapsed_time的问题，
        #但我们可以用一个小小变量即可解决，就是debug



    def success_event(self):
        """触发成功动画"""
        if not self.success_animation:
            print("恭喜！马里奥找到了公主！")
            self.success_animation = True
            self.success_start_time = pg.time.get_ticks()
            self.mario_rise_start_y = self.level.mario.pos.y
            
            # 停止马里奥的所有移动
            self.level.mario.vel = vec(0, 0)
            self.level.mario.acc = vec(0, 0)
            
            # 让马里奥面朝公主（假设公主在右边）
            if self.level.mario.pos.x < self.find_princess_position():
                self.level.mario.image_index = 0  # 朝右站立
            else:
                self.level.mario.image_index = 5  # 朝左站立
                
            self.level.mario.image = self.level.mario.frames[self.level.mario.image_index]


    def find_princess_position(self):
        """找到公主的位置"""
        for enemy in self.level.all_enemies:
            if isinstance(enemy, princess):
                return enemy.pos.x
        return self.level.mario.pos.x  # 默认值

    def update_success_animation(self):
        """更新成功动画"""
        current_time = pg.time.get_ticks()
        elapsed_time = current_time - self.success_start_time
        
        # 第一阶段：马里奥缓缓上升（3秒）
        if elapsed_time < 3000 and not self.show_congrats and self.debug:
            # 计算上升进度（0到1）
            progress = elapsed_time / 3000.0
            
            # 马里奥上升400像素，使用缓动函数让上升更平滑
            # 使用二次缓动函数：progress * progress
            ease_progress = progress * progress
            target_y = self.mario_rise_start_y - 400
            
            # 计算当前Y位置
            current_y = self.mario_rise_start_y + (target_y - self.mario_rise_start_y) * ease_progress
            
            # 更新马里奥位置
            self.level.mario.pos.y = current_y
            self.level.mario.rect.midbottom = self.level.mario.pos
            
            # 让马里奥缓慢旋转（可选）
            rotation_angle = progress * 360  # 3秒旋转一圈
            original_image = self.level.mario.frames[self.level.mario.image_index]
            self.level.mario.image = pg.transform.rotate(original_image, rotation_angle)
            
            # 更新摄像机跟随马里奥
            self.update_camera_for_success()
        
        # 第二阶段：显示祝贺文本（1秒）
        elif elapsed_time >= 3000 and elapsed_time < 4000 and self.debug:
            if not self.show_congrats:
                self.show_congrats = True
                self.congrats_start_time = current_time
            
            # 保持马里奥在最终位置
            final_y = self.mario_rise_start_y - 400
            self.level.mario.pos.y = final_y
            self.level.mario.rect.midbottom = self.level.mario.pos
            
            # 显示祝贺文本（在draw方法中处理）
            
        # 第三阶段：游戏正常结束
        elif elapsed_time >= 4000:
            # if not self.game_ending:
                print("游戏正常结束！")

                self.restart_success_value()
               
                # self.game_ending = True
                # self.game_over = True
                # self.playing = False
                self.events()
                

    def restart_success_value(self):
        # self.success_animation = False  # 是否正在播放成功动画
        self.success_start_time = 0  # 成功动画开始时间
        self.show_congrats = False  # 是否显示祝贺文本
        self.congrats_start_time = 0  # 祝贺文本开始显示的时间
        self.game_ending = False  # 游戏正在结束中
        self.debug=False
        
    def success_over_event(self):
        self.success_animation = False  # 是否正在播放成功动画
        self.debug=True


    def update_camera_for_success(self):
        """在成功动画中更新摄像机位置"""
        # 让摄像机跟随上升的马里奥
        target_x = self.level.mario.pos.x - WIDTH // 2
        target_y = self.level.mario.pos.y - HEIGHT // 2
        
        # 限制摄像机位置
        target_x = max(0, min(target_x, MAP_WIDTH - WIDTH))
        target_y = max(0, min(target_y, HEIGHT))  # 限制垂直移动范围
        
        # 平滑移动到目标位置
        self.viewpoint.x = target_x
        self.viewpoint.y = int(target_y)  # 添加垂直方向跟随



    def events(self):
        """处理游戏事件"""
        for event in pg.event.get():  # 遍历所有事件
            if event.type == pg.QUIT:  # 如果点击关闭窗口
                self.playing = False  # 结束游戏
            elif event.type == pg.KEYDOWN:  # 按键事件
                if event.key == pg.K_1:  # 按1键切换到关卡1
                    self.switch_level(1)
                elif event.key == pg.K_2:  # 按2键切换到关卡2
                    self.switch_level(2)
                elif event.key == pg.K_3:  # 按3键切换到关卡3
                    self.switch_level(3)
                elif event.key == pg.K_r:  # 按R键重新开始当前关卡
                    self.restart_current_level()
                else:#不可去除，因为否则上下空格其他键回导致下一条语句被执行
                    return 
                self.success_over_event()

                
    def switch_level(self, level_num):
        """切换到指定关卡"""
        if level_num in self.levels:
            print(f"切换到关卡 {level_num}")
            self.current_level = level_num
            self.game_over = False  # 重置游戏结束状态
            self.playing = True     # 确保游戏循环继续
            
            # 清理现有资源
            self.cleanup_before_restart()
            
            # 重置摄像机
            self.viewpoint = self.rect.copy()
            
            # 创建新关卡
            self.level = Level(self.levels[level_num])
            
            # 重新初始化精灵组
            self.reset_groups()
            
            
            
            # 显示切换提示
            self.show_level_transition(level_num)
            
            
    def restart_current_level(self):
        """重新开始当前关卡"""
        self.switch_level(self.current_level)
    
            
    def show_level_transition(self, level_num):
        """显示关卡切换提示"""
        
        # 创建半透明覆盖层
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # 半透明黑色
        
        # 创建字体
        font_large = pg.font.Font(None, 72)
        font_small = pg.font.Font(None, 36)
        
        # 渲染文本
        level_text = font_large.render(f"level {level_num}", True, (255, 255, 0))
            
        hint_text = font_small.render("press 1 2 3 to shift level,press R restart", True, (255, 255, 255))
        
        # 计算位置
        level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
        hint_rect = hint_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        
        # 绘制到屏幕
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(level_text, level_rect)
        self.screen.blit(hint_text, hint_rect)
        
        # 更新显示
        pg.display.flip()
        
        # 等待1秒
        pg.time.delay(1000)
    
            
    def reset_groups(self):
        """重置精灵组"""
        self.all_group.empty()  # 清空所有精灵
        
        # 添加马里奥
        self.all_group.add(self.level.mario)
        
        # 添加所有敌人
        if hasattr(self.level, 'enemies') and self.level.enemies:
            for enemy in self.level.enemies:
                self.all_group.add(enemy)
        
        # 添加所有碰撞体
        if hasattr(self.level, 'all_colliders'):
            self.all_group.add(*self.level.all_colliders)



    def new(self):
        """开始新游戏，初始化游戏资源"""
        # 创建关卡表面（用于绘制关卡内容）
        self.level_surface = pg.Surface((WIDTH, HEIGHT)).convert()
        
        
        # 加载并处理背景图像
        self.background = load_image(BACKGROUND)  # 加载背景图片
        self.background = pg.transform.scale(self.background, (MAP_WIDTH, HEIGHT))
        
        self.back_rect = self.background.get_rect()  # 获取背景图片的矩形区域
        
        self.level = Level(self.levels[1])  # 创建关卡实例
        
        
        # 重置精灵组
        self.reset_groups()
        
        
         # 显示初始提示
        self.show_level_transition(1)
                    
      
        

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
        self.update_camera()
        
                # 检查是否成功并触发成功动画
        if self.level.is_success() and not self.success_animation:
            self.success_event()
        
        
        # 如果正在播放成功动画，只更新成功动画
        if self.success_animation:
            self.update_success_animation()
        
        
        elif not self.game_over:
            # 使用安全的更新方法
            # self.level.mario.update()
            
            self.safe_update_sprites()
            
            # 更新关卡状态
            self.level.update()
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True
                self.playing = False


    def draw(self):
        """绘制游戏画面 - 修复版"""
        if not self.game_over:
            self.screen.fill(WHITE)
            
            # 1. 绘制背景（使用视口截取）
            self.screen.blit(self.background, (0, 0), self.viewpoint)
            
            # 2. 手动绘制所有精灵，应用摄像机偏移
            sprites_to_draw = list(self.all_group.sprites())
            
            for sprite in sprites_to_draw:
                # 计算屏幕坐标
                screen_x = sprite.rect.x - self.viewpoint.x
                screen_y = sprite.rect.y - self.viewpoint.y
                
                # 检查精灵是否在屏幕内
                if self.is_sprite_visible(screen_x, screen_y, sprite.rect.width, sprite.rect.height):
                    try:
                        # 如果是马里奥并且在成功动画中，使用旋转后的图像
                        if sprite == self.level.mario and self.success_animation:
                            self.screen.blit(sprite.image, (screen_x, screen_y))
                        else:
                            self.screen.blit(sprite.image, (screen_x, screen_y))
                    except Exception as e:
                        print(f"绘制精灵失败: {e}, 精灵类型: {type(sprite)}")
            
             # 3. 如果正在显示祝贺文本，绘制文本
            if self.show_congrats:
                self.draw_congratulations()
            
            
            # 4. 显示调试信息
            font = pg.font.Font(None, 24)
            
            # 计算各种精灵数量
            enemy_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, (Enemy1, Enemy2)))
            mario_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, Mario))
            collider_count = len(self.all_group.sprites()) - enemy_count - mario_count
            gold_count = self.level.get_gold_count()
            
            debug_text = [
                f"now level is: {self.current_level}",
                f"num of sprites: {len(self.all_group.sprites())}",
                f"mario: {mario_count}",
                f"have gold count: {gold_count}",
                f"enemy: {enemy_count}",
                f"collider_count: {collider_count}",
                f"viewpoint: ({self.viewpoint.x}, {self.viewpoint.y})",
                f"mario_pos: ({int(self.level.mario.pos.x)}, {int(self.level.mario.pos.y)})",
                f"animi: {'success' if self.success_animation else '正常游戏'}",
                
            ]
            
            # self.level.mario.draw_health_bar(self.screen,self.level.mario.pos.x,self.level.mario.pos.y-20)
            self.level.mario.draw_health_bar(self.screen,720,40)
            
            for i, text in enumerate(debug_text):
                text_surface = font.render(text, True, (255, 0, 0))
                self.screen.blit(text_surface, (10, 10 + i * 25))
            
            pg.display.flip()
            
            
            
    def draw_congratulations(self):
        """绘制祝贺文本"""
        # 创建半透明黑色背景
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 创建字体
        font_large = pg.font.Font(None, 72)
        font_small = pg.font.Font(None, 36)
        
        # 渲染文本
        congrats_text = font_large.render("great mario !!!", True, (255, 215, 0))  # 金色
        hint_text = font_small.render("success", True, (255, 255, 255))
        
        # 计算位置
        congrats_rect = congrats_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
        hint_rect = hint_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        
        # 绘制文本
        self.screen.blit(congrats_text, congrats_rect)
        self.screen.blit(hint_text, hint_rect)
        
        # 添加一些闪烁效果
        current_time = pg.time.get_ticks()
        if (current_time // 500) % 2 == 0:  # 每500毫秒闪烁一次
            # 绘制星星特效
            star_radius = 5
            for i in range(8):
                angle = i * 45
                x = WIDTH//2 + 150 * math.cos(math.radians(angle))
                y = HEIGHT//2 + 150 * math.sin(math.radians(angle))
                pg.draw.circle(self.screen, (255, 255, 0), (int(x), int(y)), star_radius)
            


    def update_camera(self):
        """简化的摄像机跟随系统"""
        # 始终让摄像机中心跟随马里奥
        target_x = self.level.mario.pos.x - WIDTH // 2
        
        # 限制摄像机位置
        map_width = self.background.get_width()
        target_x = max(0, min(target_x, MAP_WIDTH-WIDTH))
        # target_x = max(0, min(target_x, map_width - WIDTH)+500)
        
        # 平滑移动到目标位置
        # self.viewpoint.x += (target_x - self.viewpoint.x)
        # * 0.1
        self.viewpoint.x = target_x
        # self.viewpoint.x += 1




    def clamp_camera_position(self):
        """限制摄像机位置，确保不会超出地图边界"""
        # 获取背景图像的实际宽度
        # map_width = self.background.get_width()
        
        # 摄像机左边界（不能小于0）
        min_camera_x = 0
        
        # 摄像机右边界（不能超过地图宽度减去屏幕宽度）
        max_camera_x = max(0, MAP_WIDTH - WIDTH)
        
        # 应用边界限制
        if self.viewpoint.x < min_camera_x:
            self.viewpoint.x = min_camera_x
        elif self.viewpoint.x > max_camera_x:
            self.viewpoint.x = max_camera_x
            
    def draw_not_use(self):
        """绘制游戏画面 - 优化版本"""
        if not self.game_over:
            self.screen.fill(WHITE)
            #清空屏幕，以免出现重影情况
            self.screen.blit(self.background, (0, 0), self.viewpoint)
            #将背景的可见部分绘制到屏幕上
            self.all_group.draw(self.screen)
            # 在屏幕上绘制所有精灵
            pg.display.flip()
            #刷新
            
    def world_to_screen(self, world_x, world_y):
        """世界坐标转屏幕坐标"""
        return (world_x - self.viewpoint.x, world_y - self.viewpoint.y)
     
            
            
    def draw1(self):
        """绘制游戏画面 - 修复版"""
        if not self.game_over:
            self.screen.fill(WHITE)
            
            # 1. 绘制背景（使用视口截取）
            self.screen.blit(self.background, (0, 0), self.viewpoint)
            
            # 2. 手动绘制所有精灵，应用摄像机偏移
            for sprite in self.all_group:
                # 计算屏幕坐标：世界坐标 - 摄像机位置
                # screen_x = sprite.rect.x - self.viewpoint.x
                # screen_y = sprite.rect.y - self.viewpoint.y
                
                screen_x,screen_y = self.world_to_screen(sprite.rect.x,sprite.rect.y)
                
                
                # 优化：只绘制在屏幕范围内的精灵
                if self.is_sprite_visible(screen_x, screen_y, sprite.rect.width, sprite.rect.height):
                    self.screen.blit(sprite.image, (screen_x, screen_y))
            
            pg.display.flip()


    
    def is_sprite_visible(self, x, y, width, height):
        """检查精灵是否在屏幕可见范围内"""
        return (x + width >= 0 and x <= WIDTH and 
                y + height >= 0 and y <= HEIGHT)
                
                
                
                
                
            
            

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


    def show_end_screen(self):
        """显示结束屏幕，包含背景、统一大小的按钮和视觉效果"""
        # 加载结束画面背景
        end_background = load_image('final.png')
        end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))
    
        # 加载按钮图片
        restart_img_orig = load_image('restart.png')
        exit_img_orig = load_image('exit.png')
        
        # 使用两个按钮中较大的尺寸
        max_width = max(restart_img_orig.get_width(), exit_img_orig.get_width())
        max_height = max(restart_img_orig.get_height(), exit_img_orig.get_height())
        
        # 统一按钮尺寸
        button_width = int(max_width*0.7)
        button_height = int(max_height*0.7)
        
        # 统一按钮尺寸
        restart_img=self.button_size(restart_img_orig,button_height,button_width)
        exit_img=self.button_size(exit_img_orig,button_height,button_width)
        
            
    # 计算按钮位置（垂直排列在屏幕中央）
        restart_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 - button_height - 20)
        exit_pos = ((WIDTH - button_width) // 2, HEIGHT // 2 + 20)
    
    # 创建按钮矩形区域用于点击检测x,y,width,height
        self.restart_rect = pg.Rect(restart_pos[0], restart_pos[1], button_width, button_height)
        self.exit_rect = pg.Rect(exit_pos[0], exit_pos[1], button_width, button_height)
    ##############################################
    # 视觉效果变量
        border_thickness = 3  # 边框厚度
        blink_interval = 500  # 闪烁间隔（毫秒）
        last_blink_time = pg.time.get_ticks()
        show_border = True    # 边框显示状态
        hover_restart = False # 鼠标悬停在重新开始按钮上
        hover_exit = False    # 鼠标悬停在退出按钮上
    
    # 结束画面循环
        end_screen = True     #false为结束循环
        while end_screen:
            current_time = pg.time.get_ticks()
            self.clock.tick(FPS)
        
        # 获取鼠标位置
            mouse_pos = pg.mouse.get_pos()
        
        # 更新悬停状态
        #restart_rect, exit_rect 已经在上面定义好了
            hover_restart = self.restart_rect.collidepoint(mouse_pos)
            hover_exit = self.exit_rect.collidepoint(mouse_pos)
        
        # 处理事件
            for event in pg.event.get():
                #用户差掉了窗口
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

            if not end_screen:
                break
        # 绘制结束画面
            self.screen.blit(end_background, (0, 0))
        
        # 绘制按钮
            self.screen.blit(restart_img, restart_pos)
            self.screen.blit(exit_img, exit_pos)
        
        
        # 闪烁效果 - 每500毫秒切换一次边框显示
            if current_time - last_blink_time > blink_interval:
                show_border = not show_border
                last_blink_time = current_time
        
        # 绘制边框效果
            if show_border:
            # 重新开始按钮边框
                border_color = (255, 215, 0) if hover_restart else (255, 255, 255)  # 悬停时金色，否则白色
                pg.draw.rect(self.screen, border_color, self.restart_rect, border_thickness)
            
            # 退出按钮边框
                border_color = (255, 0, 0) if hover_exit else (255, 255, 255)  # 悬停时金色，否则白色
                pg.draw.rect(self.screen, border_color, self.exit_rect, border_thickness)
        
        # 悬停效果 - 按钮轻微放大
            if hover_restart:
                # 绘制放大的重新开始按钮
                self.draw_button_with_hover_effect(restart_img, restart_pos, button_width, button_height)
        
            if hover_exit:
            # 绘制放大的退出按钮
                self.draw_button_with_hover_effect(exit_img, exit_pos, button_width, button_height)

        # 更新显示
            pg.display.flip()
    
        pg.quit()


    def button_size(self, img_orig, height, width, scale_factor=0):
        """统一按钮尺寸
        scale_factor: 缩放比例，<=0表示使用传入尺寸
        0<scale_factor>0表示按比例缩放
        """
        if scale_factor <= 0:
        # 统一按钮尺寸
            button_width = int(width)
            button_height = int(height)
            
        elif scale_factor > 0:
            button_width = int(img_orig.get_width() * scale_factor)
            button_height = int(img_orig.get_height() * scale_factor)
        # 缩放按钮图片到统一尺寸
        button_img = pg.transform.scale(img_orig, (button_width, button_height))
        
        return button_img



    def draw_button_with_hover_effect(self, button_img, button_pos, button_width, button_height):
        """绘制按钮并应用悬停放大效果"""
            # 绘制放大的按钮
        hover_scale = 1.1
        hover_width = int(button_width * hover_scale)
        hover_height = int(button_height * hover_scale)
        hover_img = pg.transform.scale(button_img, (hover_width, hover_height))
        hover_pos = (
            button_pos[0] - (hover_width - button_width) // 2,
            button_pos[1] - (hover_height - button_height) // 2
        )
        self.screen.blit(hover_img, hover_pos)        
        
            
    def restart_game(self):
        """重新开始游戏"""
        # 重置游戏状态
        self.cleanup_before_restart()
        
        self.playing = True
        self.game_over = False
        self.viewpoint = self.rect.copy()  # 使用copy()避免引用问题
        
        self.clear_display()  # 清空显示画面
        
        # 重新创建关卡
        self.level = Level()
        
        # 重新初始化 all_group
        self.all_group.empty()
        
        # 重新添加所有精灵到组
        self.all_group.add(self.level.mario)
        
        # 添加所有敌人
        for enemy in self.level.enemies:
            self.all_group.add(enemy)
        
        # 添加所有碰撞体
        if hasattr(self.level, 'all_colliders'):
            self.all_group.add(*self.level.all_colliders)
        
        # 重新开始游戏循环
        self.run()


    def safe_update_sprites(self):
        """安全的精灵更新方法，避免索引越界"""
        try:
            # 创建精灵副本以避免在遍历时修改
            sprites_list = list(self.all_group.sprites())
            
            for sprite in sprites_list:
                try:
                    if isinstance(sprite, (Enemy1, Enemy2)):
                        if not sprite.dead:
                            sprite.update(self.level.horizontal_lines, self.level.vertical_lines)
                    elif isinstance(sprite, Mario):
                        sprite.update()
                except Exception as e:
                    print(f"更新精灵 {type(sprite)} 时出错: {e}")
                    # 从组中移除有问题的精灵
                    self.all_group.remove(sprite)
    
        except Exception as e:
            print(f"更新精灵组时出错: {e}")
            # 如果出错，重置all_group
            self.all_group.empty()
            self.all_group.add(self.level.mario)
            for enemy in self.level.enemies:
                self.all_group.add(enemy)
            if hasattr(self.level, 'all_colliders'):
                self.all_group.add(*self.level.all_colliders)



    def restart_game1(self):
        """重新开始游戏"""
        # 重置  游戏状态
        self.cleanup_before_restart()
        
        self.playing = True
        self.game_over = False
        self.viewpoint = self.rect
        
        self.clear_display()  # 清空显示画面
        
        # 重新创建关卡
        self.level = Level()
        
        # 重新添加精灵到组
        self.all_group.add(self.level.mario)
        self.all_group.add(self.level.all_colliders)
        
        # 重新设置摄像机位置
        self.viewpoint = self.screen.get_rect()        
        # 重新初始化游戏
        # self.new()  # 重新创建关卡
            
        # 重新开始游戏循环
        self.run()
        
    def cleanup_before_restart(self):
        """在重新开始游戏前进行必要的清理工作"""
        # 这里可以添加任何需要在重新开始游戏前执行的清理代码
        pg.event.clear()  # 清除事件队列
        self.all_group.empty()  # 清空精灵组
        
    def clear_display(self):
        """清空显示画面"""
        # 填充白色背景
        self.screen.fill((255,255,255))
        
        # 可选: 显示"重新开始..."提示
        font = pg.font.Font(None, 36)
        text = font.render("starting...", True, (111,111,111))
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, text_rect)
        
        # 立即更新显示
        pg.display.flip()
        
        # 短暂延迟让玩家看到提示
        pg.time.delay(500)


