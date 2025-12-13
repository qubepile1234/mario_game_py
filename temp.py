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

    def events(self):
        """处理游戏事件"""
        for event in pg.event.get():  # 遍历所有事件
            if event.type == pg.QUIT:  # 如果点击关闭窗口
                self.playing = False  # 结束游戏
            elif event.type == pg.KEYDOWN:  # 按键事件
                # 如果正在播放成功动画，不允许切换关卡
                if not self.success_animation:
                    if event.key == pg.K_1:  # 按1键切换到关卡1
                        self.switch_level(1)
                    elif event.key == pg.K_2:  # 按2键切换到关卡2
                        self.switch_level(2)
                    elif event.key == pg.K_3:  # 按3键切换到关卡3
                        self.switch_level(3)
                    elif event.key == pg.K_r:  # 按R键重新开始当前关卡
                        self.restart_current_level()

    def update(self):
        """更新游戏状态"""
        # 更新摄像机
        self.update_camera()
        
        # 检查是否成功并触发成功动画
        if self.level.is_success() and not self.success_animation:
            self.success_event()
        
        # 如果正在播放成功动画，只更新成功动画
        if self.success_animation:
            self.update_success_animation()
        elif not self.game_over:
            # 使用安全的更新方法
            self.safe_update_sprites()
            
            # 更新关卡状态
            self.level.update()
            
            # 检查马里奥是否死亡
            if self.level.mario.dead:
                self.game_over = True
                self.playing = False

    def draw(self):
        """绘制游戏画面"""
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
            gold_count = self.level.get_gold_count()
            
            debug_text = [
                f"当前关卡: {self.current_level}",
                f"金币: {gold_count}",
                f"敌人数量: {enemy_count}",
                f"马里奥生命值: {self.level.mario.health}/{self.level.mario.max_health}",
                f"状态: {'成功动画' if self.success_animation else '正常游戏'}",
                f"马里奥位置: ({int(self.level.mario.pos.x)}, {int(self.level.mario.pos.y)})"
            ]
            
            # 绘制生命值条
            self.level.mario.draw_health_bar(self.screen, 720, 40)
            
            # 绘制调试信息
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
        congrats_text = font_large.render("伟大的马里奥", True, (255, 215, 0))  # 金色
        hint_text = font_small.render("游戏胜利！", True, (255, 255, 255))
        
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