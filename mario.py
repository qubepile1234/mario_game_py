# import random
from tools import *  # 导入工具函数
from settings import *  # 导入游戏设置

vec = pg.math.Vector2  # 创建二维向量别名


class Mario(pg.sprite.Sprite):
    """马里奥角色类，处理玩家控制、动画和物理效果"""
    
    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        self.sheet = load_image('mario21.png')  # 加载精灵图
        self.load_from_sheet()  # 从精灵图中提取动画帧
        self.walking_timer = pg.time.get_ticks()  # 行走动画计时器
        self.image_index = 4  # 当前显示的动画帧索引
        self.image = self.frames[0]  # 当前显示的图像
        self.rect = self.image.get_rect()  # 获取图像矩形区域
        # self.pos = vec(WIDTH * 0.5, GROUND_HEIGHT - 70)  # 初始位置（屏幕中央偏上）
        # self.pos = vec(900, GROUND_HEIGHT - 70)  # 初始位置（屏幕中央偏上）
        self.vel = vec(0, 0)  # 速度向量
        self.acc = vec(0, 0)  # 加速度向量
        self.landing = False  # 是否着陆标志
        self.dead = False  # 死亡标志
        
        
        self.death_animation_time = 0  # 死亡动画计时器，不知道是什么意思
        self.death_animation_duration = 1000  # 死亡动画持续时间（毫秒）
        self.death_velocity_y = -15  # 死亡时向上的初速度
        self.death_spin_speed = 10  # 死亡旋转速度
        
        
        # 生命值系统
        self.max_health = 100  # 最大生命值
        self.health = self.max_health  # 当前生命值
        self.health_regen_per_frame = 4  # 每帧恢复的生命值
        self.last_regen_time = pg.time.get_ticks()  # 上次恢复生命值的时间
        self.regen_interval = 16  # 恢复生命值的间隔（毫秒），大约60FPS
        self.health_bar_width = 60  # 生命条宽度
        self.health_bar_height = 8  # 生命条高度

    def update(self):
        """每帧更新马里奥状态"""
        
        # 如果已经死亡，执行死亡动画
        if self.dead:
            self.death_animation()
            return
        
        self.acc = vec(0, GRAVITY)  # 重置加速度，只保留重力
        
        keys = pg.key.get_pressed()  # 获取按键状态
                
        if keys[pg.K_r] and not self.dead:
            #输入法需为英文
            self.die()
            return  # 死亡后不再处理其他逻辑
        
        # 生命值恢复系统
        self.health_regen()
        
        # 检查生命值是否耗尽
        if self.health <= 0 and not self.dead:
            self.die()
            return
        
        # 向右移动处理
        if keys[pg.K_RIGHT]:
            # self.walk('right')  # 按右键播放向右行走动画
            if self.vel.x >= 0:  # 如果已经在向右移动
                self.acc.x = ACC  # 使用正常加速度
            # if self.vel.x < 0:  # 如果静止或向左移动
            else:
                self.acc.x = TURNAROUND  # 使用转向加速度
                
        
        # 向左移动处理
        elif keys[pg.K_LEFT]:
            # self.walk('left')  # 是按左键播放向左行走动画
            if self.vel.x <= 0:  # 如果已经在向左移动
                self.acc.x = -ACC  # 使用正常加速度
            # if self.vel.x >= 0:  # 如果静止或向右移动
            else:
                self.acc.x = -TURNAROUND  # 使用转向加速度
                
        # speedx=self.vel.x
        # ax=self.acc.x
        # if int(speedx + ax) > 0:  # 如果已经在向右移动
        #         ax -= FRICTION  # 速度大于0减速
        #         if int(speedx + ax) < 0:  # 减速后如果速度小于0
        #             speedx = 0  # 直接设为0，防止反向移动
        # elif int(speedx + ax) < 0:  # 如果向左移动
        #         ax += FRICTION  # 速度小于0减速
        #         if int(speedx + ax) > 0:  # 减速后如果速度大于0
        #             speedx = 0  # 直接设为0，防止反向移动
                    
        # if speedx==0:
        #     self.vel.x = speedx  # 直接设为0，防止反向移动
        ###################################
        else:
            # 没有按键时应用摩擦力
            if abs(self.vel.x) > 0:
                # 摩擦力方向与速度方向相反
                friction_direction = -1 if self.vel.x > 0 else 1
                self.acc.x = friction_direction * FRICTION
                
                # 如果摩擦力会使速度反向，则直接停止
                if abs(self.vel.x) <= FRICTION:
                    self.vel.x = 0
                    self.acc.x = 0
        # 应用加速度到速度
        self.vel.x += self.acc.x
        ####################################
        # 限制最大水平速度
        if abs(self.vel.x) > MAX_SPEED:
            self.vel.x = MAX_SPEED if self.vel.x > 0 else -MAX_SPEED
        # 更新动画状态
        if self.vel.x > 0:  # 如果已经在向右移动
            self.walk('right') 
        elif self.vel.x < 0:  # 如果向左移动
            self.walk('left') 
        else:                     #没有水平移动
            self.image_index = 0  # 切换到站立帧
        
        # 跳跃处理
        if keys[pg.K_SPACE]:
            if self.landing:  # 只有在地面上才能跳跃
                self.vel.y = -JUMP  # 设置跳跃速度=跳跃力量
                #获得向上的加速度,质量为1,故加速度=速度
        
        # 空中状态处理
        if not self.landing:
            if self.vel.x > 0:  # 如果已经在向右移动
                self.image_index = 4  # 切换到跳跃帧
            elif self.vel.x < 0:        # 如果已经在向左移动
                self.image_index = 9  # 切换到跳跃帧
            else :        
                self.image_index = 10  # 切换到跳跃帧
                
    
        
        self.image = self.frames[self.image_index]  # 更新当前显示图像
        
        self.vel.y += GRAVITY
        # 限制最大下落速度（防止速度无限增大）
        if self.vel.y > TERMINAL_VELOCITY:  # 需要定义 TERMINAL_VELOCITY
            self.vel.y = TERMINAL_VELOCITY

        # 物理计算：位置更新（使用运动学公式）
        self.pos += self.vel#每一帧等于1秒,pos+vel 

        # 更新矩形位置
        self.rect.midbottom = self.pos

    def health_regen(self):
        """生命值恢复系统"""
        current_time = pg.time.get_ticks()
        
        # 每隔一定时间恢复生命值
        if current_time - self.last_regen_time > self.regen_interval:
            # 恢复生命值，但不超过最大值
            self.health += self.health_regen_per_frame
            if self.health > self.max_health:
                self.health = self.max_health
            self.last_regen_time = current_time

    def change_health(self, amount):
        """
        外部调用修改生命值的方法
        
        参数:
            amount (int): 生命值变化量，正数为增加，负数为减少
        """
        self.health += amount
        
        # 限制生命值范围
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0
            
        print(f"马里奥生命值变化: {amount:+d}, 当前生命值: {self.health}")
        # 如果生命值降到0以下，触发死亡
        if self.health <= 0 and not self.dead:
            self.die()
            
    def get_health_percentage(self):
        """获取当前生命值百分比"""
        return self.health / self.max_health
    
    def set_health_percentage(self,health):
        '''设置生命值'''
        self.health=health
        
    def s_hurt(self):
        '''标准伤害'''
        self.health = self.health - 4

    def draw_health_bar(self, screen, x, y):
        """
        绘制生命值条（可选的UI功能）
        
        参数:
            screen: Pygame屏幕表面
            x, y: 生命条绘制的左上角坐标
        """
        # 计算生命条填充宽度
        fill_width = int(self.health_bar_width * self.get_health_percentage())
        
        # 绘制生命条背景（红色）
        pg.draw.rect(screen, (255, 0, 0), 
                    (x, y, self.health_bar_width, self.health_bar_height))
        # 绘制当前生命值（绿色）
        pg.draw.rect(screen, (0, 255, 0), 
                    (x, y, fill_width, self.health_bar_height))
        
        # 绘制生命条边框
        pg.draw.rect(screen, (255, 255, 255), 
                    (x, y, self.health_bar_width, self.health_bar_height), 1)
        
        # 显示生命值文字
        font = pg.font.Font(None, 20)
        health_text = font.render(f"HP: {self.health}/{self.max_health}", 
                                 True, (255, 255, 255))
        screen.blit(health_text, (x, y - 20))


    def die(self):
        """马里奥死亡"""
        if not self.dead:
            self.death_animation_time = pg.time.get_ticks()
            # 设置死亡时的物理效果
            self.vel.y = self.death_velocity_y  # 向上弹起
            self.vel.x = 0  # 水平速度归零
            self.death_animation()#完善后使用
            print("马里奥死亡！按R键触发")
            self.dead = True
            

    def death_animation(self):
        """死亡动画,待完善,现在是一点作用也没有"""
        current_time = pg.time.get_ticks()
        elapsed_time = current_time - self.death_animation_time
        
        # 如果动画时间结束，不再更新位置
        # if elapsed_time >= self.death_animation_duration:
            # 可以在这里重置关卡或显示游戏结束画面
            # return
        
        # 死亡动画期间的物理效果
        # 重力仍然作用
        self.vel.y += GRAVITY * 0.5  # 使用较小的重力，让死亡动画更夸张
        
        # 应用速度更新位置
        self.pos += self.vel
        
        # 更新矩形位置
        self.rect.midbottom = self.pos
        
        # 旋转效果（可选）
        if elapsed_time < self.death_animation_duration / 2:
            # 前半段时间旋转
            rotation_angle = (elapsed_time * self.death_spin_speed) % 360
            self.image = pg.transform.rotate(self.frames[self.image_index], rotation_angle)
        else:
            # 后半段时间逐渐消失
            alpha = 255 - int(255 * (elapsed_time - self.death_animation_duration/2) / (self.death_animation_duration/2))
            if alpha < 0:
                alpha = 0
            self.image.set_alpha(alpha)

    def calculate_animation_speed(self):
        """根据移动速度计算动画播放速度"""
        if self.vel.x == 0:  # 静止时
            animation_speed = 130  # 默认动画速度
        elif self.vel.x > 0:  # 向右移动
            animation_speed = 130 - (self.vel.x * 12)  # 速度越快动画越快
        else:  # 向左移动
            animation_speed = 130 - (self.vel.x * 12 * -1)  # 速度越快动画越快
        return animation_speed

    def walk(self, facing):
        """处理行走动画
        
        参数:
            facing (str): 面向方向 'right' 或 'left'
        """
        if self.image_index == 0:  # 如果当前是站立帧
            self.image_index += 1  # 切换到下一帧
            self.walking_timer = pg.time.get_ticks()  # 重置计时器
        else:
            # 根据动画速度判断是否切换到下一帧
            if (pg.time.get_ticks() - self.walking_timer > 
                    self.calculate_animation_speed()):
                self.image_index += 1
                self.walking_timer = pg.time.get_ticks()
        
        # 向右行走动画循环
        if facing == 'right':
            if self.image_index > 3:  # 超过最后一帧
                self.image_index = 0  # 回到第一帧
        
        # 向左行走动画循环
        if facing == 'left':
            if self.image_index > 8:  # 超过向左动画的最后一帧
                self.image_index = 5  # 回到向左动画的第一帧
            if self.image_index < 5:  # 如果索引在向右动画范围内
                self.image_index = 5  # 切换到向左动画

    def load_from_sheet(self):
        """从精灵表中加载所有动画帧"""
        self.right_frames = []  # 向右动画帧列表
        self.left_frames = []   # 向左动画帧列表

        # 加载向右动画帧（从精灵图中截取特定区域）
        #x, y, width, height
        self.right_frames.append(
            self.get_image(178, 32, 12, 16))  # 站立帧
        self.right_frames.append(
            self.get_image(80, 32, 15, 16))   # 行走帧1
        self.right_frames.append(
            self.get_image(96, 32, 16, 16))   # 行走帧2
        self.right_frames.append(
            self.get_image(112, 32, 16, 16))  # 行走帧3
        self.right_frames.append(
            self.get_image(144, 32, 16, 16))  # 跳跃帧

        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)  # 水平翻转
            self.left_frames.append(new_image)

        # 合并所有动画帧
        self.frames = self.right_frames + self.left_frames
        self.frames.append(self.get_image(144+16, 32, 16, 16))# 跳跃帧

    def get_image(self, x, y, width, height):
        """从精灵表中提取单个图像
        
        参数:
            x, y (int): 在精灵表中的坐标
            width, height (int): 截取区域的宽高
            
        返回:
            Surface: 处理后的图像
        """
        image = pg.Surface([width, height])  # 创建表面
        rect = image.get_rect()
        # 从精灵表中截取指定区域
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        # image.set_colorkey(BLACK)  # 设置白色为透明色
        image.set_colorkey(WHITE)  # 设置白色为透明色
        # 缩放图像到合适大小
        image = pg.transform.scale(image,
                                   (int(rect.width * MARIO_SIZE),
                                    int(rect.height * MARIO_SIZE)))
        return image

