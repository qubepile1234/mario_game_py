# import random
from tools import *  # 导入工具函数
from settings import *  # 导入游戏设置

vec = pg.math.Vector2  # 创建二维向量别名


class Mario(pg.sprite.Sprite):
    """马里奥角色类，处理玩家控制、动画和物理效果"""
    
    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        self.sheet = load_image('mario.png')  # 加载精灵图
        self.load_from_sheet()  # 从精灵图中提取动画帧
        self.walking_timer = pg.time.get_ticks()  # 行走动画计时器
        self.image_index = 4  # 当前显示的动画帧索引
        self.image = self.frames[0]  # 当前显示的图像
        self.rect = self.image.get_rect()  # 获取图像矩形区域
        self.pos = vec(WIDTH * 0.5, GROUND_HEIGHT - 70)  # 初始位置（屏幕中央偏上）
        self.vel = vec(0, 0)  # 速度向量
        self.acc = vec(0, 0)  # 加速度向量
        self.landing = False  # 是否着陆标志
        self.dead = False  # 死亡标志

    def update(self):
        """每帧更新马里奥状态"""
        self.acc = vec(0, GRAVITY)  # 重置加速度，只保留重力
        
        keys = pg.key.get_pressed()  # 获取按键状态
        
        # 向右移动处理
        if keys[pg.K_RIGHT]:
            self.walk('right')  # 播放向右行走动画
            if self.vel.x > 0:  # 如果已经在向右移动
                self.acc.x = TURNAROUND  # 使用转向加速度
            if self.vel.x <= 0:  # 如果静止或向左移动
                self.acc.x = ACC  # 使用正常加速度
            self.pos.x += 5  # 直接移动位置（可能用于碰撞检测前的预移动）
        
        # 向左移动处理
        elif keys[pg.K_LEFT]:
            self.walk('left')  # 播放向左行走动画
            if self.vel.x < 0:  # 如果已经在向左移动
                self.acc.x = -TURNAROUND  # 使用转向加速度
            if self.vel.x >= 0:  # 如果静止或向右移动
                self.acc.x = -ACC  # 使用正常加速度
        
        # 没有水平移动按键
        else:
            self.image_index = 0  # 切换到站立帧
        
        # 限制最大速度
        if abs(self.vel.x) < MAX_SPEED:
            self.vel.x += self.acc.x  # 在限速内增加速度
        elif keys[pg.K_LEFT]:
            self.vel.x = -MAX_SPEED  # 达到向左最大速度
        elif keys[pg.K_RIGHT]:
            self.vel.x = MAX_SPEED  # 达到向右最大速度
        
        # 跳跃处理
        if keys[pg.K_SPACE]:
            if self.landing:  # 只有在地面上才能跳跃
                self.vel.y = -JUMP  # 设置跳跃速度
        
        # 空中状态处理
        if not self.landing:
            self.image_index = 4  # 切换到跳跃帧
        
        self.image = self.frames[self.image_index]  # 更新当前显示图像
        
        # 物理计算：摩擦力
        self.acc.x += self.vel.x * FRICTION
        # 物理计算：速度更新
        self.vel += self.acc
        # 物理计算：位置更新（使用运动学公式）
        self.pos += self.vel + 0.5 * self.acc

        # 更新矩形位置
        self.rect.midbottom = self.pos

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
        image.set_colorkey(BLACK)  # 设置黑色为透明色
        # 缩放图像到合适大小
        image = pg.transform.scale(image,
                                   (int(rect.width * MARIO_SIZE),
                                    int(rect.height * MARIO_SIZE)))
        return image


class Collider(pg.sprite.Sprite):
    """碰撞体类，用于检测碰撞的不可见区域"""
    
    def __init__(self, x, y, width, height,color=None):
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        self.image = pg.Surface((width, height)).convert()  # 创建碰撞区域表面
        if color:
            self.image.fill(color)  # 有颜色就填充
        else:
            self.image.set_alpha(0)  # 否则透明（保持原有行为）
        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标