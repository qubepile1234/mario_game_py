# import random
from tools import *  # 导入工具函数
from settings import *  # 导入游戏设置
from level_data import *
from random import random

vec = pg.math.Vector2  # 创建二维向量别名


class EnemyBase(pg.sprite.Sprite):
    """敌人基类，处理敌人的共同属性和方法"""
    def __init__(self, sprite_sheet_path, initial_pos=None, scaled_w=100, scaled_h=100):
        pg.sprite.Sprite.__init__(self)
        self.set_scale(scaled_w, scaled_h)
        self.sheet = load_image(sprite_sheet_path)
        self.load_from_sheet()
        self.walking_timer = pg.time.get_ticks()
        self.image_index = 4
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        
        if initial_pos:
            self.pos = vec(initial_pos)
        else:
            self.pos = vec(300, GROUND_HEIGHT - 70)
            
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.landing = False
        self.dead = False
        self.direction = 1  # 1表示向右，-1表示向左
        
        # 敌人特有的属性
        self.move_speed = 2
        self.change_direction_timer = 0
        self.direction_change_interval = 2000  # 每2秒可能改变方向
        
        # 设置初始位置（添加这行）
        self.rect.midbottom = self.pos
            
    def set_scale(self, scaled_w, scaled_h):
        self.scaled_w = scaled_w
        self.scaled_h = scaled_h
            
    def update(self, horizontal_lines, vertical_lines):
        """更新敌人状态，需要传入碰撞体组进行碰撞检测"""
            
        self.acc = vec(0, GRAVITY)
        
        # 自动移动 - 只会左右移动或向下走，不会向上
        self.vel.x = self.direction * self.move_speed
        
        # 随机改变方向（有一定概率）
        current_time = pg.time.get_ticks()
        if current_time - self.change_direction_timer > self.direction_change_interval:
            if random() < 0.3:  # 30%的概率改变方向
                self.direction *= -1
            self.change_direction_timer = current_time

        # 动画更新
        if self.vel.x > 0:
            self.walk('right', self.walk_frame_count)
        elif self.vel.x < 0:
            self.walk('left', self.walk_frame_count)
        else:
            self.image_index = 0
            
        # 空中状态处理
        if not self.landing:
            if self.vel.x > 0:
                self.image_index = self.walk_frame_count + 1
            else: 
                self.image_index = (self.walk_frame_count + 2) * 2 - 1
            
        self.image = self.frames[self.image_index]
        
        # 重力
        self.vel.y += GRAVITY
        if self.vel.y > TERMINAL_VELOCITY:
            self.vel.y = TERMINAL_VELOCITY
            
        # 位置更新
        self.pos += self.vel
        self.rect.midbottom = self.pos
        
        # 检测碰撞
        self.check_collisions(horizontal_lines, vertical_lines)
        
    def check_collisions(self, horizontal_lines, vertical_lines):
        """检测碰撞并处理"""
        # 重置着陆状态
        self.landing = False
        
        # 检测垂直线碰撞（墙壁）
        vertical_collisions = pg.sprite.spritecollide(self, vertical_lines, False)
        for line in vertical_collisions:
            # 计算实际碰撞距离，考虑敌人的移动方向
            if self.vel.x > 0:  # 向右移动碰到墙壁
                # 如果敌人从右侧接近墙壁
                if self.rect.right >= line.rect.left and self.rect.right - self.vel.x <= line.rect.left:
                    self.pos.x = line.rect.left - self.rect.width/2
                    self.direction = -1  # 转向
                    self.vel.x = -self.move_speed
            elif self.vel.x < 0:  # 向左移动碰到墙壁
                # 如果敌人从左侧接近墙壁
                if self.rect.left <= line.rect.right and self.rect.left - self.vel.x >= line.rect.right:
                    self.pos.x = line.rect.right + self.rect.width/2
                    self.direction = 1  # 转向
                    self.vel.x = self.move_speed
            self.rect.midbottom = self.pos
        
        # 检测水平线碰撞（地面/平台）
        horizontal_collisions = pg.sprite.spritecollide(self, horizontal_lines, False)
        
        # 用于记录是否找到可站立的地面
        found_ground = False
        
        for line in horizontal_collisions:
            # 检查敌人是否在水平线上方
            # if self.rect.bottom >= line.rect.top:
                # 从上方落到平台上
                if (self.vel.y > 0 and  # 正在下落
                    self.rect.bottom > line.rect.top and  # 当前帧底部低于平台顶部
                    self.rect.bottom - self.vel.y <= line.rect.top + E_PLUS):  # 上一帧底部在平台上方
                    
                    self.acc.y = 0
                    self.vel.y = 0
                    self.pos.y = line.rect.top
                    self.landing = True
                    found_ground = True
                    self.rect.midbottom = self.pos
                    break  # 只处理一个有效的碰撞
                
                # 从下方撞到平台底部（修正条件）
                elif (self.vel.y < 0 and  # 正在上升
                      self.rect.top < line.rect.bottom and  # 当前帧顶部低于平台底部
                      self.rect.top - self.vel.y >= line.rect.bottom):  # 上一帧顶部在平台底部下方
                    
                    self.vel.y = 0
                    self.pos.y = line.rect.bottom + self.rect.height
                    self.rect.midbottom = self.pos
        
        # # 如果没有检测到任何水平线碰撞，检查是否接近地面
        # if not found_ground and self.pos.y >= GROUND_HEIGHT:
        #     # 敌人已经在地面或低于地面，重置到地面
        #     self.acc.y = 0
        #     self.vel.y = 0
        #     self.pos.y = GROUND_HEIGHT
        #     self.landing = True
        #     self.rect.midbottom = self.pos
        
        # 检查是否掉出地图
        if self.pos.y > GROUND_HEIGHT + 200:
            self.dead = True
            self.kill()
    
    def walk(self, facing, walk_frame_count=3):
        """
        处理行走动画
        walk_frame_count为走路的frame,0为站立
        """
        if self.image_index == 0:
            self.image_index += 1
            self.walking_timer = pg.time.get_ticks()
        else:
            animation_speed = 130 - (abs(self.vel.x) * 6)
            if (pg.time.get_ticks() - self.walking_timer > animation_speed):
                self.image_index += 1
                self.walking_timer = pg.time.get_ticks()
        
        if facing == 'right':
            if self.image_index > walk_frame_count + 1:
                self.image_index = 0
        elif facing == 'left':
            if self.image_index > ((walk_frame_count + 2) * 2 - 2):
                # 左走最后一frame
                self.image_index = walk_frame_count + 2
                # +1为右跳跃,加2为左站立
            if self.image_index < walk_frame_count + 2:
                self.image_index = walk_frame_count + 2

    def get_image(self, x, y, width, height, scaled_w=100, scaled_h=100):
        """
        从精灵表中提取单个图像并缩放
        
        参数:
            x, y: 在精灵表中的坐标
            width, height: 截取区域的宽高
            scaled_w, scaled_h: 缩放百分比，默认为100,100表示原大小
                50,20表示宽度变为50%，高度变为20%
                200,200表示宽度和高度都变为200%
        """
        image = pg.Surface([width, height])
        rect = image.get_rect()
        # 从精灵表中截取指定区域
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(WHITE)  # 设置白色为透明色
        
        # 计算缩放后的尺寸（使用百分比）
        new_width = int(rect.width * scaled_w / 100)
        new_height = int(rect.height * scaled_h / 100)
        
        # 缩放图像
        image = pg.transform.scale(image, (new_width, new_height))
        return image





class EnemyBase1(pg.sprite.Sprite):
    """敌人基类，处理敌人的共同属性和方法"""
    def __init__(self, sprite_sheet_path, initial_pos=None,scaled_w=100,scaled_h=100):
        pg.sprite.Sprite.__init__(self)
        self.set_scale(scaled_w,scaled_h)
        # self.scaled_w=scaled_w
        # self.scaled_h=scaled_h
        self.sheet = load_image(sprite_sheet_path)
        self.load_from_sheet()
        self.walking_timer = pg.time.get_ticks()
        self.image_index = 4
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        
        if initial_pos:
            self.pos = vec(initial_pos)
        else:
            self.pos = vec(300, GROUND_HEIGHT - 70)
            
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.landing = False
        self.dead = False
        self.direction = 1  # 1表示向右，-1表示向左
        
        # 敌人特有的属性
        self.move_speed = 2
        self.change_direction_timer = 0
        self.direction_change_interval = 2000  # 每2秒可能改变方向
        
        # 设置初始位置（添加这行）
        self.rect.midbottom = self.pos
            
    def set_scale(self,scaled_w,scaled_h):
        self.scaled_w=scaled_w
        self.scaled_h=scaled_h
            
    def update(self, horizontal_lines, vertical_lines):
        """更新敌人状态，需要传入碰撞体组进行碰撞检测"""
        self.acc = vec(0, GRAVITY)
        
        # 自动移动 - 只会左右移动或向下走，不会向上
        self.vel.x = self.direction * self.move_speed
        
        # 随机改变方向（有一定概率）
        current_time = pg.time.get_ticks()
        if current_time - self.change_direction_timer > self.direction_change_interval:
            if random() < 0.3:  # 30%的概率改变方向
                self.direction *= -1
            self.change_direction_timer = current_time

        # 动画更新
        if self.vel.x > 0:
            self.walk('right',self.walk_frame_count)
        elif self.vel.x < 0:
            self.walk('left',self.walk_frame_count)
        else:
            self.image_index = 0
            
        # 空中状态处理
        if not self.landing:
            if self.vel.x >0:
                self.image_index = self.walk_frame_count+1
            else : 
                self.image_index= (self.walk_frame_count+2)*2-1
            
        self.image = self.frames[self.image_index]
        
        # 重力
        self.vel.y += GRAVITY
        if self.vel.y > TERMINAL_VELOCITY:
            self.vel.y = TERMINAL_VELOCITY
            
        # 位置更新
        self.pos += self.vel
        self.rect.midbottom = self.pos
        
        # 检测碰撞
        self.check_collisions(horizontal_lines, vertical_lines)
        
    def check_collisions111(self, horizontal_lines, vertical_lines):
        """检测碰撞并处理"""
        # 重置着陆状态
        self.landing = False
        
        # 检测垂直线碰撞（墙壁）
        vertical_collisions = pg.sprite.spritecollide(self, vertical_lines, False)
        for line in vertical_collisions:
            if self.vel.x > 0:  # 向右移动碰到墙壁
                self.pos.x = line.rect.left - self.rect.width/2
                self.direction = -1  # 转向
                self.vel.x = -self.move_speed
            elif self.vel.x < 0:  # 向左移动碰到墙壁
                self.pos.x = line.rect.right + self.rect.width/2
                self.direction = 1  # 转向
                self.vel.x = self.move_speed
            self.rect.midbottom = self.pos
        
        # 检测水平线碰撞（地面/平台）
        horizontal_collisions = pg.sprite.spritecollide(self, horizontal_lines, False)
        for line in horizontal_collisions:
            # 从上方落到平台上
            if (self.vel.y > 0 and 
                self.rect.bottom > line.rect.top and
                self.rect.bottom - self.vel.y <= line.rect.top):
                
                self.acc.y = 0
                self.vel.y = 0
                self.pos.y = line.rect.top
                self.landing = True
                self.rect.midbottom = self.pos
                
            # 从下方撞到平台底部
            elif (self.vel.y < 0 and 
                  self.rect.top < line.rect.bottom and
                  self.rect.top - self.vel.y >= line.rect.bottom):
                
                self.vel.y = 0
                self.pos.y = line.rect.bottom + self.rect.height
                self.rect.midbottom = self.pos
        
        # 检查是否掉出地图
        if self.pos.y > GROUND_HEIGHT + 200:
            self.dead = True
            self.kill()
   
   
   
   
    def check_collisions(self, horizontal_lines, vertical_lines):
        """检测碰撞并处理，使用与马里奥相同的线段碰撞逻辑"""
        # 重置着陆状态
        self.landing = False
        
        # 检测水平线碰撞（地面/平台）
        horizontal_collisions = pg.sprite.spritecollide(self, horizontal_lines, False)
        
        for line in horizontal_collisions:
            # 从上方落到水平线上
            if (self.vel.y > 0 and 
                self.rect.bottom > line.rect.top and
                self.rect.bottom - self.vel.y <= line.rect.top):
                
                self.acc.y = 0
                self.vel.y = 0
                self.pos.y = line.rect.top
                self.landing = True
                self.rect.midbottom = self.pos
                break  # 只处理第一个有效的碰撞
                
            # 从下方撞到平台底部
            elif (self.vel.y < 0 and 
                  self.rect.top < line.rect.bottom and
                  self.rect.top - self.vel.y >= line.rect.bottom):
                
                self.vel.y = 0
                self.pos.y = line.rect.bottom + self.rect.height
                self.rect.midbottom = self.pos
        
        # 检测垂直线碰撞（墙壁）
        vertical_collisions = pg.sprite.spritecollide(self, vertical_lines, False)
        
        # 处理水管边缘的线（使用扩展碰撞检测）
        processed_collisions = []
        for line in vertical_collisions:
            # 检查这条线是否是水管边缘
            if hasattr(line, 'is_pipe_edge') and line.is_pipe_edge:
                # 为水管边缘的线创建一个扩展的碰撞检测区域
                expanded_rect = line.rect.copy()
                # 左右各扩展3像素（使用与马里奥相同的值）
                expanded_rect.x -= 3
                expanded_rect.width += 6
                
                # 如果敌人与扩展区域碰撞，则添加到处理列表中
                if self.rect.colliderect(expanded_rect):
                    processed_collisions.append(line)
            else:
                processed_collisions.append(line)
        
        # 处理所有垂直碰撞
        for line in processed_collisions:
            # 检查这条线是否是水管边缘
            is_pipe_edge = hasattr(line, 'is_pipe_edge') and line.is_pipe_edge
            
            if is_pipe_edge:
                # 对于水管边缘的线，使用更大的碰撞距离
                collision_distance = 3
                if self.vel.x > 0:  # 向右移动
                    if (self.rect.right + collision_distance > line.rect.left and
                        self.rect.right - self.vel.x <= line.rect.left):
                        self.pos.x = line.rect.left - self.rect.width/2 - collision_distance
                        self.direction = -1  # 转向
                        self.vel.x = -self.move_speed
                elif self.vel.x < 0:  # 向左移动
                    if (self.rect.left - collision_distance < line.rect.right and
                        self.rect.left - self.vel.x >= line.rect.right):
                        self.pos.x = line.rect.right + self.rect.width/2 + collision_distance
                        self.direction = 1  # 转向
                        self.vel.x = self.move_speed
                self.rect.midbottom = self.pos
            else:
                # 标准水平碰撞处理
                if self.vel.x > 0:  # 向右移动碰到墙壁
                    self.pos.x = line.rect.left - self.rect.width/2
                    self.direction = -1  # 转向
                    self.vel.x = -self.move_speed
                elif self.vel.x < 0:  # 向左移动碰到墙壁
                    self.pos.x = line.rect.right + self.rect.width/2
                    self.direction = 1  # 转向
                    self.vel.x = self.move_speed
                self.rect.midbottom = self.pos
        
        # 检查是否掉出地图
        if self.pos.y > GROUND_HEIGHT + 200:
            self.dead = True
            self.kill()
           
    
    def walk(self, facing,walk_frame_count=3):
        """
        处理行走动画
        walk_frame_count为走路的frame,0为站立
        """
        if self.image_index == 0:
            self.image_index += 1
            self.walking_timer = pg.time.get_ticks()
        else:
            animation_speed = 130 - (abs(self.vel.x) * 6)
            if (pg.time.get_ticks() - self.walking_timer > animation_speed):
                self.image_index += 1
                self.walking_timer = pg.time.get_ticks()
        
        if facing == 'right':
            if self.image_index > walk_frame_count+1:
                self.image_index = 0
        elif facing == 'left':
            if self.image_index > ((walk_frame_count+2)*2-2):
                #左走最后一frame
                self.image_index = walk_frame_count+2
                #+1为右跳跃,加2为左站立
            if self.image_index < walk_frame_count+2:
                self.image_index = walk_frame_count+2
    
    def get_image1(self, x, y, width, height):
        """从精灵表中提取单个图像"""
        image = pg.Surface([width, height])
        rect = image.get_rect()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(WHITE)
        image = pg.transform.scale(image,
                                   (int(rect.width * MARIO_SIZE),
                                    int(rect.height * MARIO_SIZE)))
        return image

    def get_image(self, x, y, width, height, scaled_w=100, scaled_h=100):
        """
        从精灵表中提取单个图像并缩放
        
        参数:
            x, y: 在精灵表中的坐标
            width, height: 截取区域的宽高
            scaled_w, scaled_h: 缩放百分比，默认为100,100表示原大小
                50,20表示宽度变为50%，高度变为20%
                200,200表示宽度和高度都变为200%
        """
        image = pg.Surface([width, height])
        rect = image.get_rect()
        # 从精灵表中截取指定区域
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(WHITE)  # 设置白色为透明色
        
        # 计算缩放后的尺寸（使用百分比）
        new_width = int(rect.width * scaled_w / 100)
        new_height = int(rect.height * scaled_h / 100)
        
        # 缩放图像
        image = pg.transform.scale(image, (new_width, new_height))
        return image

class coin(EnemyBase):
    def __init__(self, initial_pos=None, scaled_w=100,scaled_h=100):
        # original_image = pg.image.load('enemy.png').convert_alpha()
        # self.pic= pg.transform.scale(original_image, (20, 20))
        super().__init__('coin.png', initial_pos, scaled_w, scaled_h)
        # 可以覆盖基类的默认属性
        self.move_speed = 3
        self.direction_change_interval = 2000
        
        
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []
        
        scaled_h=self.scaled_h
        scaled_w=self.scaled_w
        
        self.walk_frame_count=1
        
        # 加coin的帧（需要根据实际的enemy.png调整坐标）
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h))  # 站立/移动帧1
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h)) # 移动帧2
        
        # 跳跃/下落帧
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h))
        
        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)
        
        # 合并所有帧
        self.frames = self.right_frames + self.left_frames


class princess(EnemyBase):
    def __init__(self, initial_pos=None, scaled_w=100,scaled_h=100):
        # original_image = pg.image.load('enemy.png').convert_alpha()
        # self.pic= pg.transform.scale(original_image, (20, 20))
        super().__init__('himesama.jpg', initial_pos, scaled_w, scaled_h)
        # 可以覆盖基类的默认属性
        self.move_speed = 0
        self.direction_change_interval = 2000
        
        
      
        
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []
        
        scaled_h=self.scaled_h
        scaled_w=self.scaled_w
        
        self.walk_frame_count=1
        
        princessx=1400
        princessy=1900
        # 加princess的帧（需要根据实际的enemy.png调整坐标）
        self.right_frames.append(self.get_image(0, 0, princessx, princessy,scaled_w,scaled_h))  # 站立/移动帧1
        self.right_frames.append(self.get_image(0, 0, princessx, princessy,scaled_w,scaled_h)) # 移动帧2
        
        # 跳跃/下落帧
        self.right_frames.append(self.get_image(0, 0, princessx, princessy,scaled_w,scaled_h))
        
        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)
        
        # 合并所有帧
        self.frames = self.right_frames + self.left_frames



class Enemy1(EnemyBase):
    """敌人类型1"""
    def __init__(self, initial_pos=None, scaled_w=100,scaled_h=100):
        # original_image = pg.image.load('enemy.png').convert_alpha()
        # self.pic= pg.transform.scale(original_image, (20, 20))
        super().__init__('enemy2.png', initial_pos, scaled_w, scaled_h)
        # 可以覆盖基类的默认属性
        self.move_speed = 1
        self.direction_change_interval = 1500
    
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []
        
        scaled_h=self.scaled_h
        scaled_w=self.scaled_w
        
        self.walk_frame_count=2
        
        # 加载敌人1的帧（需要根据实际的enemy.png调整坐标）
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h))  # 站立/移动帧1
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h)) # 移动帧2
        self.right_frames.append(self.get_image(15+110, 0, 110, 110,scaled_w,scaled_h)) # 移动帧3
        
        # 跳跃/下落帧
        self.right_frames.append(self.get_image(15, 0, 110, 110,scaled_w,scaled_h))
        
        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)
        
        # 合并所有帧
        self.frames = self.right_frames + self.left_frames


class Enemy21_if_jump_has_bug_use_this(EnemyBase):
    """敌人类型2（原enemy2类）"""
    def __init__(self, initial_pos=None, scaled_w=100,scaled_h=100):
        super().__init__('mario21.png', initial_pos, scaled_w,scaled_h)
        # 敌人2的特有属性
        self.move_speed = 2
        self.direction_change_interval = 2500
    
    
    
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []

        scaled_w=self.scaled_w
        scaled_h=self.scaled_h
        
        
        self.walk_frame_count=3

        # 加载向右动画帧（从精灵图中截取特定区域）
        self.right_frames.append(
            self.get_image(178, 96*0, 16, 16*2,scaled_w,scaled_h))  # 站立帧
        self.right_frames.append(
            self.get_image(80, 96*0, 16, 16*2,scaled_w,scaled_h))   # 行走帧1
        self.right_frames.append(
            self.get_image(96, 96*4, 16, 16*2,scaled_w,scaled_h))   # 行走帧2
        self.right_frames.append(
            self.get_image(112, 96*4, 16, 16*2,scaled_w,scaled_h))  # 行走帧3（修正了y坐标）
        self.right_frames.append(
            self.get_image(112, 96*4, 16, 16*2,scaled_w,scaled_h))  # 行走帧4（修正了y坐标）
        self.right_frames.append(
            self.get_image(144, 96*3, 16, 16*2,scaled_w,scaled_h))  # 跳跃帧（修正了y坐标）

        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)

        # 合并所有动画帧
        self.frames = self.right_frames + self.left_frames

class Enemy22_add_jumo_not_use(EnemyBase):
    """敌人类型2（原enemy2类）"""
    def __init__(self, initial_pos=None, scaled_w=100, scaled_h=100):
        super().__init__('mario21.png', initial_pos, scaled_w, scaled_h)
        # 敌人2的特有属性
        self.move_speed = 2
        self.direction_change_interval = 2500
        self.jump_probability = 1.0 / 32.0  # 1/16的跳跃概率
        self.enemy_jump = 10  # 跳跃高度
    
    def update(self, horizontal_lines, vertical_lines):
        """
        更新敌人状态，需要传入碰撞体组进行碰撞检测
        重写以添加跳跃功能
        """
        self.acc = vec(0, GRAVITY)
        
        # 自动移动 - 只会左右移动或向下走，不会向上
        self.vel.x = self.direction * self.move_speed
        
        # 随机改变方向（有一定概率）
        current_time = pg.time.get_ticks()
        if current_time - self.change_direction_timer > self.direction_change_interval:
            if random() < 0.3:  # 30%的概率改变方向
                self.direction *= -1
            self.change_direction_timer = current_time
        
        # 随机跳跃 - 1/16的概率跳跃（当敌人在地面上时）
        if self.landing and random() < self.jump_probability:
            self.vel.y = -self.enemy_jump
            self.landing = False

        # 动画更新
        if self.vel.x > 0:
            self.walk('right', self.walk_frame_count)
        elif self.vel.x < 0:
            self.walk('left', self.walk_frame_count)
        else:
            self.image_index = 0
            
        # 空中状态处理
        if not self.landing:
            if self.vel.x > 0:
                self.image_index = self.walk_frame_count + 1
            else: 
                self.image_index = (self.walk_frame_count + 2) * 2 - 1
            
        self.image = self.frames[self.image_index]
        
        # 重力
        self.vel.y += GRAVITY
        if self.vel.y > TERMINAL_VELOCITY:
            self.vel.y = TERMINAL_VELOCITY
            
        # 位置更新
        self.pos += self.vel
        self.rect.midbottom = self.pos
        
        # 检测碰撞
        self.check_collisions(horizontal_lines, vertical_lines)
    
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []

        scaled_w = self.scaled_w
        scaled_h = self.scaled_h
        
        self.walk_frame_count = 3

        # 加载向右动画帧（从精灵图中截取特定区域）
        self.right_frames.append(
            self.get_image(178, 96 * 0, 16, 16 * 2, scaled_w, scaled_h))  # 站立帧
        self.right_frames.append(
            self.get_image(80, 96 * 0, 16, 16 * 2, scaled_w, scaled_h))   # 行走帧1
        self.right_frames.append(
            self.get_image(96, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))   # 行走帧2
        self.right_frames.append(
            self.get_image(112, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))  # 行走帧3
        self.right_frames.append(
            self.get_image(112, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))  # 行走帧4（与帧3相同）
        self.right_frames.append(
            self.get_image(144, 96 * 3, 16, 16 * 2, scaled_w, scaled_h))  # 跳跃帧

        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)

        # 合并所有动画帧
        self.frames = self.right_frames + self.left_frames
        
        
        
class Enemy2(EnemyBase):
    """敌人类型2（原enemy2类）"""
    def __init__(self, initial_pos=None, scaled_w=100, scaled_h=100):
        super().__init__('mario21.png', initial_pos, scaled_w, scaled_h)
        # 敌人2的特有属性
        self.move_speed = 2
        self.direction_change_interval = 2500
        self.jump_probability = 1.0 / 128.0  # 1/32的跳跃概率
        self.enemy_jump = ENEMY_JUMP  # 跳跃高度
        self.jump_cooldown = 16*10  # 跳跃冷却时间
    
    def update(self, horizontal_lines, vertical_lines):
        """
        更新敌人状态，需要传入碰撞体组进行碰撞检测
        重写以添加跳跃功能
        """
        # if self.dead:  # 如果敌人已死亡，不再更新
            # return
            
        self.acc = vec(0, GRAVITY)
        
        # 自动移动 - 只会左右移动或向下走，不会向上
        self.vel.x = self.direction * self.move_speed
        
        # 随机改变方向（有一定概率）
        current_time = pg.time.get_ticks()
        if current_time - self.change_direction_timer > self.direction_change_interval:
            if random() < 0.3:  # 30%的概率改变方向
                self.direction *= -1
            self.change_direction_timer = current_time
        
        # 随机跳跃 - 1/32的概率跳跃（当敌人在地面上时）
        if (self.landing and 
            random() < self.jump_probability and 
            self.jump_cooldown <= 0):
            
            self.vel.y = -self.enemy_jump
            self.landing = False
            self.jump_cooldown = 500  # 设置500毫秒的跳跃冷却时间
        elif self.jump_cooldown > 0:
            self.jump_cooldown -= 16  # 假设60fps，每帧减少约16毫秒
            
            
            
        #    测试bug片段,可删除 # 随机跳跃 - 1/16的概率跳跃（当敌人在地面上时）
        # if self.landing and random() < self.jump_probability:
        #     self.vel.y = -self.enemy_jump
        #     self.landing = False
            
            

        # 动画更新
        if self.vel.x > 0:
            self.walk('right', self.walk_frame_count)
        elif self.vel.x < 0:
            self.walk('left', self.walk_frame_count)
        else:
            self.image_index = 0
            
        # 空中状态处理
        if not self.landing:
            if self.vel.x > 0:
                self.image_index = self.walk_frame_count + 1
            else: 
                self.image_index = (self.walk_frame_count + 2) * 2 - 1
            
        self.image = self.frames[self.image_index]
        
        # 重力
        self.vel.y += GRAVITY
        if self.vel.y > TERMINAL_VELOCITY:
            self.vel.y = TERMINAL_VELOCITY
            
        # 位置更新
        self.pos += self.vel
        self.rect.midbottom = self.pos
        
        # 检测碰撞
        self.check_collisions(horizontal_lines, vertical_lines)
    
    def load_from_sheet(self):
        """从精灵表中加载动画帧"""
        self.right_frames = []
        self.left_frames = []

        scaled_w = self.scaled_w
        scaled_h = self.scaled_h
        
        self.walk_frame_count = 3

        # 加载向右动画帧（从精灵图中截取特定区域）
        self.right_frames.append(
            self.get_image(178, 96 * 0, 16, 16 * 2, scaled_w, scaled_h))  # 站立帧
        self.right_frames.append(
            self.get_image(80, 96 * 0, 16, 16 * 2, scaled_w, scaled_h))   # 行走帧1
        self.right_frames.append(
            self.get_image(96, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))   # 行走帧2
        self.right_frames.append(
            self.get_image(112, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))  # 行走帧3
        self.right_frames.append(
            self.get_image(112, 96 * 4, 16, 16 * 2, scaled_w, scaled_h))  # 行走帧4（与帧3相同）
        self.right_frames.append(
            self.get_image(144, 96 * 3, 16, 16 * 2, scaled_w, scaled_h))  # 跳跃帧

        # 通过翻转创建向左动画帧
        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)

        # 合并所有动画帧
        self.frames = self.right_frames + self.left_frames