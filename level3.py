from tools import *  # 导入工具函数
from settings import *  # 导入游戏设置

vec = pg.math.Vector2  # 创建二维向量别名

class LineCollider(pg.sprite.Sprite):
    """线段碰撞体类，分为水平线和垂直线"""
    
    def __init__(self, x, y, length, orientation, color=None):
        """
        初始化线段碰撞体
        
        参数:
            x, y (int): 线段起点坐标
            length (int): 线段长度
            orientation (str): 线段方向 'horizontal' 或 'vertical'
            color: 线段颜色，用于调试
        """
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        
        self.orientation = orientation  # 线段方向
        
        # 根据方向设置碰撞体尺寸
        if orientation == 'horizontal':
            width, height = length, 1  # 水平线：长度=width，高度=1像素
        else:  # vertical
            width, height = 1, length  # 垂直线：宽度=1像素，长度=height
            
        self.image = pg.Surface((width, height)).convert()  # 创建碰撞区域表面
        if color:
            self.image.fill(color)  # 有颜色就填充
        else:
            self.image.set_alpha(0)  # 否则透明（保持原有行为）
            
        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标


from Mario import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精灵相关的所有类和函数

class Level(pg.sprite.Sprite):
    """使用线段碰撞体的关卡类"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_line_colliders()  # 设置线段碰撞体
        self.set_group()      # 组合所有碰撞体组

        
    def update(self):
        """每帧更新关卡状态"""
        self.check_collide()  # 检测碰撞
        self.adjust_collisions()  # 处理碰撞
        self.check_dead()     # 检查玩家是否死亡

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()
    
    def set_line_colliders(self):
        """使用线段构建所有碰撞体"""
        self.horizontal_lines = pg.sprite.Group()  # 水平线组
        self.vertical_lines = pg.sprite.Group()    # 垂直线组
        
        # 地面 - 使用水平线
        ground_y = GROUND_HEIGHT
        ground_length = MAP_WIDTH
        ground_line = LineCollider(0, ground_y, ground_length, 'horizontal', color=(0,222,0))
        self.horizontal_lines.add(ground_line)
        
        # 左侧墙壁 - 使用垂直线
        wall_left = LineCollider(0, 0, HEIGHT, 'vertical', color=(255,0,0))
        self.vertical_lines.add(wall_left)
        
        # 右侧墙壁 - 使用垂直线
        wall_right = LineCollider(MAP_WIDTH-1, 0, HEIGHT, 'vertical', color=(0,255,255))
        self.vertical_lines.add(wall_right)
        
        # 管道1 - 使用线段构建
        pipe1_x, pipe1_y = 40, GROUND_HEIGHT-40
        pipe1_width, pipe1_height = 40, 80
        
        # 管道顶部（水平线）
        pipe1_top = LineCollider(pipe1_x, pipe1_y, pipe1_width, 'horizontal', color=(221,112,112))
        self.horizontal_lines.add(pipe1_top)
        
        # 管道左侧（垂直线）
        pipe1_left = LineCollider(pipe1_x, pipe1_y, pipe1_height, 'vertical', color=(221,112,112))
        self.vertical_lines.add(pipe1_left)
        
        # 管道右侧（垂直线）
        pipe1_right = LineCollider(pipe1_x + pipe1_width - 1, pipe1_y, pipe1_height, 'vertical', color=(221,112,112))
        self.vertical_lines.add(pipe1_right)
        
        # 管道2 - 使用线段构建
        pipe2_x, pipe2_y = 200, GROUND_HEIGHT-80
        pipe2_width, pipe2_height = 83, 120
        
        # 管道顶部（水平线）
        pipe2_top = LineCollider(pipe2_x, pipe2_y, pipe2_width, 'horizontal', color=(22,22,131))
        self.horizontal_lines.add(pipe2_top)
        
        # 管道左侧（垂直线）
        pipe2_left = LineCollider(pipe2_x, pipe2_y, pipe2_height, 'vertical', color=(22,22,131))
        self.vertical_lines.add(pipe2_left)
        
        # 管道右侧（垂直线）
        pipe2_right = LineCollider(pipe2_x + pipe2_width - 1, pipe2_y, pipe2_height, 'vertical', color=(22,22,131))
        self.vertical_lines.add(pipe2_right)
     
    def set_group(self):
        """将所有碰撞体组合在一起"""
        # 创建包含所有线段的组
        self.all_colliders = pg.sprite.Group()
        self.all_colliders.add(*self.horizontal_lines, *self.vertical_lines)

    def check_collide(self):
        """检测马里奥与所有线段碰撞体的碰撞"""
        # 分别检测水平线和垂直线的碰撞
        self.horizontal_collisions = pg.sprite.spritecollide(self.mario, self.horizontal_lines, False)
        self.vertical_collisions = pg.sprite.spritecollide(self.mario, self.vertical_lines, False)
        
        # 检查马里奥是否站在任何水平线上
        self.on_ground = False
        for line in self.horizontal_collisions:
            # 检查是否站在水平线上
            if (self.mario.vel.y >= 0 and 
                abs(self.mario.rect.bottom - line.rect.top) < 5):
                self.on_ground = True
                self.ground_line = line  # 记录站在哪条线上
                break

    def adjust_collisions(self):
        """处理所有碰撞"""
        # 先假设马里奥没有站在任何物体上
        self.mario.landing = False
        
        # 处理垂直线碰撞（水平方向）
        self.adjust_vertical_collisions()
        
        # 处理水平线碰撞（垂直方向）
        self.adjust_horizontal_collisions()
        
        # 如果没有水平碰撞，确保马里奥不会停留在空中
        if not self.horizontal_collisions and not self.on_ground:
            self.mario.landing = False

    def adjust_vertical_collisions(self):
        """处理垂直线碰撞（水平方向）"""
        for line in self.vertical_collisions:
            # 水平碰撞处理
            if self.mario.vel.x > 0:  # 向右移动时碰撞
                self.mario.pos.x = line.rect.left - self.mario.rect.width/2
                self.mario.vel.x = 0
            elif self.mario.vel.x < 0:  # 向左移动时碰撞
                self.mario.pos.x = line.rect.right + self.mario.rect.width/2
                self.mario.vel.x = 0

    def adjust_horizontal_collisions(self):
        """处理水平线碰撞（垂直方向）"""
        found_ground = False
        
        for line in self.horizontal_collisions:
            # 从上方落到水平线上
            if (self.mario.vel.y > 0 and 
                self.mario.rect.bottom > line.rect.top and
                self.mario.rect.bottom - self.mario.vel.y <= line.rect.top):
                
                self.mario.acc.y = 0        # 重置垂直加速度
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = line.rect.top  # 放置在线段顶部
                self.mario.landing = True   # 标记为着陆状态
                found_ground = True
                break  # 只需要处理一个顶部碰撞
            
            # 从下方碰撞水平线底部
            elif (self.mario.vel.y < 0 and 
                  self.mario.rect.top < line.rect.bottom and
                  self.mario.rect.top - self.mario.vel.y >= line.rect.bottom):
                
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = line.rect.bottom + self.mario.rect.height
                # 注意：这种情况下不应该设置 landing = True
        
        # 如果没有找到可以站立的水平线，确保马里奥不会停留在空中
        if not found_ground:
            self.mario.landing = False

    def check_dead(self):
        """检查马里奥是否死亡（掉出地图底部）"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:  # 如果掉到地面以下一定距离
            self.mario.dead = True  # 标记为死亡状态
        # 同时检查是否走出地图右边界
        if self.mario.pos.x > MAP_WIDTH + 20:  # 如果走出地图右边界
            self.mario.dead = True  # 也可以标记为完成关卡，这里简单处理为死亡