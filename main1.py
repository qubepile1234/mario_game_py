# 导入自定义模块
from level7 import *  # 导入简化关卡相关的所有类和函数
from mario import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精update灵相关的所有类和函数


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

    def new(self):
        """开始新游戏，初始化游戏资源"""
        # 创建关卡表面（用于绘制关卡内容）
        self.level_surface = pg.Surface((WIDTH, HEIGHT)).convert()
        
        
        # 加载并处理背景图像
        self.background = load_image('level3.png')  # 加载背景图片
        self.background = pg.transform.scale(self.background, (MAP_WIDTH, HEIGHT))
        
        self.back_rect = self.background.get_rect()  # 获取背景图片的矩形区域
        
        self.level = Level()  # 创建关卡实例
        # 清空并重新填充 all_group
        self.all_group.empty()  # 清空所有精灵
        
        
        self.all_group.add(self.level.mario)  # 将马里奥添加到精灵组

        mario_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, Mario))
            
      
        
    # 添加所有敌人到精灵组
        if hasattr(self.level, 'enemies') and self.level.enemies:
            #如果 self.level 有 enemies 属性，并且 enemies 属性不为空（有内容），则执行后面的代码"
            for enemy in self.level.enemies:
                self.all_group.add(enemy)
        enemy_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, (Enemy1, Enemy2)))
        
        # 添加所有碰撞体到精灵组
        if hasattr(self.level, 'all_colliders'):
            self.all_group.add(*self.level.all_colliders)
        

    def run(self):
        """游戏主循环"""
        while self.playing:  # 当游戏处于运行状态时
            self.clock.tick(FPS)  # 控制游戏帧率
            self.events()  # 处理事件
            self.update()  # 更新游戏状态
            self.draw()  # 绘制游戏画面
        
        # 游戏结束后显示结束画面
        self.show_end_screen()
              
    def update1(self):
        """更新游戏状态 - 支持双向摄像机移动"""
        
            # 双向摄像机跟随系统
        self.update_camera()
        if not self.game_over:
            self.all_group.update()  # 更新所有精灵:马里奥状态
            self.level.update()  # 更新关卡状态
            
            
            # 双向摄像机跟随系统
            # self.update_camera()
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True  # 标记游戏结束
                self.playing = False   # 停止游戏主循环


    def update2(self):
        """更新游戏状态 - 支持双向摄像机移动"""
        # 双向摄像机跟随系统
        self.update_camera()
        
        if not self.game_over:
            # 更新所有精灵
            for sprite in self.all_group:
                # 根据精灵类型调用不同的update方法
                if isinstance(sprite, (Enemy1, Enemy2)):  # 如果是敌人
                    sprite.update(self.level.horizontal_lines, self.level.vertical_lines)
                elif isinstance(sprite, Mario):  # 如果是马里奥
                    sprite.update()
                # 其他精灵（如碰撞体）可能不需要update
                # elif hasattr(sprite, 'update'):
                    # sprite.update()
            
            # 更新关卡状态
            self.level.update()
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True  # 标记游戏结束
                self.playing = False   # 停止游戏主循环


    def update(self):
        """更新游戏状态"""
        self.update_camera()
        
        if not self.game_over:
            # 使用安全的更新方法
            # self.level.mario.update()
            
            self.safe_update_sprites()
            
            # 更新关卡状态
            self.level.update()
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True
                self.playing = False


    def update3333(self):
        """更新游戏状态"""
        # 更新摄像机
        self.update_camera()
        
        if not self.game_over:
            # 手动更新每个精灵（根据类型调用不同的update方法）
            sprites_to_update = list(self.all_group.sprites())
            for sprite in sprites_to_update:
                if isinstance(sprite, (Enemy1, Enemy2)):  # 如果是敌人
                    if not sprite.dead:  # 只有未死亡的敌人才更新
                        sprite.update(self.level.horizontal_lines, self.level.vertical_lines)
                elif isinstance(sprite, Mario):  # 如果是马里奥
                    sprite.update()
                # 碰撞体不需要update
            
            # 更新关卡状态（包括碰撞检测）
            self.level.update()
            
            # 移除已死亡的敌人
            dead_enemies = []
            for sprite in sprites_to_update:
                if isinstance(sprite, (Enemy1, Enemy2)):
                    if sprite.dead:
                        dead_enemies.append(sprite)
            
            for enemy in dead_enemies:
                enemy.kill()  # 从所有组中移除
                self.all_group.remove(enemy)
                if enemy in self.level.enemies:
                    self.level.enemies.remove(enemy)
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True  # 标记游戏结束
                self.playing = False   # 停止游戏主循环

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
                        self.screen.blit(sprite.image, (screen_x, screen_y))
                    except Exception as e:
                        print(f"绘制精灵失败: {e}, 精灵类型: {type(sprite)}")
            
            # 3. 显示调试信息
            font = pg.font.Font(None, 24)
            
            # 计算各种精灵数量
            enemy_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, (Enemy1, Enemy2)))
            mario_count = sum(1 for sprite in self.all_group.sprites() if isinstance(sprite, Mario))
            collider_count = len(self.all_group.sprites()) - enemy_count - mario_count
            
            debug_text = [
                f"num_of_sprites: {len(self.all_group.sprites())}",
                f"mario: {mario_count}",
                f"enemy: {enemy_count}",
                f"collider_count: {collider_count}",
                f"viewpoint: ({self.viewpoint.x}, {self.viewpoint.y})",
                f"mario_pos: ({int(self.level.mario.pos.x)}, {int(self.level.mario.pos.y)})"
            ]
            
            for i, text in enumerate(debug_text):
                text_surface = font.render(text, True, (255, 0, 0))
                self.screen.blit(text_surface, (10, 10 + i * 25))
            
            pg.display.flip()
            
            
    def draw33(self):
        """绘制游戏画面 - 修复版"""
        if not self.game_over:
            self.screen.fill(WHITE)
            
            # 1. 绘制背景（使用视口截取）
            self.screen.blit(self.background, (0, 0), self.viewpoint)
            
            # 2. 手动绘制所有精灵，应用摄像机偏移
            for sprite in self.all_group:
                # 计算屏幕坐标：世界坐标 - 摄像机位置
                screen_x = sprite.rect.x - self.viewpoint.x
                screen_y = sprite.rect.y - self.viewpoint.y
                
                # 优化：只绘制在屏幕范围内的精灵
                if self.is_sprite_visible(screen_x, screen_y, sprite.rect.width, sprite.rect.height):
                    self.screen.blit(sprite.image, (screen_x, screen_y))
            
            # 3. 显示敌人数量（调试用）
            font = pg.font.Font(None, 24)
            enemy_count = sum(1 for sprite in self.all_group if isinstance(sprite, (Enemy1, Enemy2)))
            enemy_text = font.render(f"Enemies: {enemy_count}", True, (255, 0, 0))
            self.screen.blit(enemy_text, (10, 10))
            
            pg.display.flip()

    def update_camera_not_use(self):
        """更新摄像机位置 - 支持左右双向移动"""
        
        # 向右移动时的摄像机跟随
        if self.level.mario.vel.x > 0:  # 向右移动
            if self.level.mario.pos.x > WIDTH * 0.55 + self.viewpoint.x:
                self.viewpoint.x += int(self.level.mario.vel.x * 1.5)
        
        # 向左移动时的摄像机跟随（新增）
        elif self.level.mario.vel.x < 0:  # 向左移动
            if self.level.mario.pos.x < WIDTH * 0.25 + self.viewpoint.x:
                self.viewpoint.x += int(self.level.mario.vel.x * 1.5)  # 注意这里是加负值
        
        # 确保摄像机不会移出地图边界,待研究
        self.clamp_camera_position()


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


    def update_camera_not3(self):
        """混合摄像机系统 - 结合预测和边界框"""
        # 获取马里奥状态
        mario_x = self.level.mario.pos.x
        mario_vel_x = self.level.mario.vel.x
        mario_acc_x = self.level.mario.acc.x
        
        # 基础目标位置（马里奥居中）
        base_target = mario_x - WIDTH // 2
        
        # 预测偏移（基于速度和加速度）
        prediction_strength = min(1.0, abs(mario_vel_x) / 15.0)  # 速度越快，预测越强
        look_ahead_distance = 80 * prediction_strength  # 最大向前看80像素
        
        if mario_vel_x > 0:
            predicted_target = base_target + look_ahead_distance
        elif mario_vel_x < 0:
            predicted_target = base_target - look_ahead_distance
        else:
            predicted_target = base_target
        
        # 边界框检查
        mario_screen_x = mario_x - self.viewpoint.x
        left_boundary = WIDTH * 0.25
        right_boundary = WIDTH * 0.75
        
        # 如果马里奥接近边界，调整目标位置
        if mario_screen_x < left_boundary:
            boundary_correction = mario_screen_x - left_boundary
            predicted_target += boundary_correction
        elif mario_screen_x > right_boundary:
            boundary_correction = mario_screen_x - right_boundary
            predicted_target += boundary_correction
        
        # 限制摄像机位置
        map_width = self.background.get_width()
        final_target = max(0, min(predicted_target, map_width - WIDTH))
        
        # 动态平滑度（高速时响应更快）
        base_smooth = 0.1
        speed_factor = min(1.0, abs(mario_vel_x) / 20.0)
        dynamic_smooth = base_smooth * (1.0 + speed_factor)
        
        # 应用平滑移动
        self.viewpoint.x += (final_target - self.viewpoint.x) * dynamic_smooth


    def update_camera_(self):
        """高级摄像机系统 - 更多可调参数"""
        # 获取马里奥状态
        mario_x = self.level.mario.pos.x
        mario_vel_x = self.level.mario.vel.x
        
        # 可调参数
        CENTER_WEIGHT = 0.7          # 居中权重
        PREDICTION_WEIGHT = 0.3      # 预测权重
        MAX_LOOK_AHEAD = 100         # 最大向前看距离
        BASE_SMOOTH = 0.1            # 基础平滑度
        MAX_SMOOTH_BOOST = 2.0       # 最大平滑度提升
        
        # 基础目标位置（马里奥居中）
        base_target = mario_x - WIDTH // 2
        
        # 预测目标
        prediction_strength = min(1.0, abs(mario_vel_x) / 15.0)
        look_ahead_distance = MAX_LOOK_AHEAD * prediction_strength
        
        if mario_vel_x > 0:
            prediction_target = base_target + look_ahead_distance
        elif mario_vel_x < 0:
            prediction_target = base_target - look_ahead_distance
        else:
            prediction_target = base_target
        
        # 结合居中和预测
        weighted_target = base_target * CENTER_WEIGHT + prediction_target * PREDICTION_WEIGHT
        
        # 边界框检查
        mario_screen_x = mario_x - self.viewpoint.x
        left_boundary = WIDTH * 0.25
        right_boundary = WIDTH * 0.75
        
        # 边界修正
        boundary_correction = 0
        if mario_screen_x < left_boundary:
            boundary_correction = mario_screen_x - left_boundary
        elif mario_screen_x > right_boundary:
            boundary_correction = mario_screen_x - right_boundary
        
        # 最终目标
        final_target = weighted_target + boundary_correction
        
        # 限制摄像机位置
        map_width = self.background.get_width()
        final_target = max(0, min(final_target, map_width - WIDTH))
        
        # 动态平滑度
        speed_factor = min(1.0, abs(mario_vel_x) / 20.0)
        dynamic_smooth = BASE_SMOOTH * (1.0 + speed_factor * (MAX_SMOOTH_BOOST - 1.0))
        
        # 应用平滑移动
        self.viewpoint.x += (final_target - self.viewpoint.x) * dynamic_smooth


    def update_camera_not_use(self):
        """更新摄像机位置 - 改进的摄像机跟随系统"""
        
        # 获取马里奥的当前位置和速度
        mario_x = self.level.mario.pos.x
        mario_vel_x = self.level.mario.vel.x
        
        # 计算马里奥在屏幕上的相对位置
        mario_screen_x = mario_x - self.viewpoint.x
        
        # 摄像机跟随逻辑
        if mario_vel_x > 0:  # 向右移动
            # 当马里奥移动到屏幕右侧55%区域时，摄像机跟随
            if mario_screen_x > WIDTH * 0.55:
                # 平滑跟随：摄像机移动速度基于马里奥速度，但不完全相同
                camera_speed = max(2, min(8, abs(mario_vel_x) * 1.2))
                self.viewpoint.x += int(camera_speed)
        
        elif mario_vel_x < 0:  # 向左移动
            # 当马里奥移动到屏幕左侧25%区域时，摄像机跟随
            if mario_screen_x < WIDTH * 0.25:
                # 平滑跟随：摄像机移动速度基于马里奥速度
                camera_speed = max(2, min(8, abs(mario_vel_x) * 1.2))
                self.viewpoint.x -= int(camera_speed)
        
        # 限制摄像机位置，确保不会超出地图边界
        self.clamp_camera_position1()

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


    def clamp_camera_position2(self):
        """限制摄像机位置，确保不会超出地图边界+-20"""
        # 摄像机左边界（不能小于0）
        min_camera_x = 0 - 20#相机能看到地图边界-20
        if self.viewpoint.x < min_camera_x:
            self.viewpoint.x = min_camera_x

        # 摄像机右边界（不能超过地图宽度减去屏幕宽度）
        map_width = self.background.get_width()  # 背景图片宽度就是地图宽度
        max_camera_x = map_width - WIDTH
        # max_camera_x = map_width + 20 #相机能看到地图边界+20
        if self.viewpoint.x > max_camera_x:
            self.viewpoint.x = max_camera_x
##############################################################
    def events(self):
        """处理游戏事件"""
        for event in pg.event.get():  # 遍历所有事件
            if event.type == pg.QUIT:  # 如果点击关闭窗口
                self.playing = False  # 结束游戏
            
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


