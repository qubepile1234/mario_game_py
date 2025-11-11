from sprites import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精灵相关的所有类和函数

class Level(pg.sprite.Sprite):
    """简化关卡类，只有平坦地面，+墙壁"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_ground()     # 设置地面碰撞体
        self.set_wall()       # 设置墙壁碰撞体
        self.set_pipes()
        self.set_group()      # 组合所有碰撞体组

        
    def update(self):
        """每帧更新关卡状态"""
        self.check_collide()  # 检测碰撞
        self.adjust_wall()    # 墙壁碰撞处理
        self.adjust_pipe()    # 管道碰撞处理
        self.adjust_ground()  # 地面碰撞处理
        self.check_dead()     # 检查玩家是否死亡

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()
    
    def set_ground(self):
        """设置单一连续的地面碰撞体，宽度为窗口的两倍"""
        # 创建单一地面碰撞体，宽度为1600像素（800*2）
        ground_width = MAP_WIDTH  # 1600像素
        ground_height = PLAIN_HEIGHT+40  #水平面为20，地面比水平面高40
        self.ground_collider = Collider(0, GROUND_HEIGHT, ground_width, ground_height,color=(0,222,0))
     
    def set_wall(self):
        """设置墙壁碰撞体，定义游戏中的墙壁障碍物，防止玩家跳出世界"""
        self.wall_left = Collider(0, 0, 10, HEIGHT,color=(255,0,0))  # 左侧墙壁
        self.wall_right = Collider(MAP_WIDTH-10, 0, 10, HEIGHT,color=(0,255,255))  # 右侧墙壁

    def set_pipes(self):
        """设置管道碰撞体，定义游戏中的管道障碍物"""
        # 管道碰撞体，高度不同表示管道露出地面的高度不同
        self.pipe1 = Collider(40, GROUND_HEIGHT-40, 40, 80,color=(221,112,112))   # 较短的管道
        self.pipe2 = Collider(200, GROUND_HEIGHT-80, 83, 120,color=(22,22,131))  # 中等高度的管道
     
    def set_group(self):
        """将地面组合成碰撞检测组"""
        self.ground_group = pg.sprite.Group(self.ground_collider)
        # 将管道碰撞体添加到组中
        self.wall_group = pg.sprite.Group(self.wall_left,self.wall_right)
        self.pipe_group = pg.sprite.Group(self.pipe1, self.pipe2)
        
        # 创建一个包含所有碰撞体的组，用于绘制
        self.all_colliders = pg.sprite.Group(
            self.ground_collider, self.wall_left, self.wall_right, self.pipe1, self.pipe2
        )

    def check_collide(self):
        """检测马里奥的碰撞"""
        # 分别检测不同类型的碰撞
        self.wall_collide = pg.sprite.spritecollideany(self.mario, self.wall_group)
        self.pipe_collide = pg.sprite.spritecollideany(self.mario, self.pipe_group)
        self.ground_collide = pg.sprite.spritecollideany(self.mario, self.ground_group)

    def adjust_wall(self):
        """墙壁碰撞处理，防止马里奥穿过墙壁"""
        if self.wall_collide:
            if self.mario.vel.x > 0:  # 向右移动时碰撞
                self.mario.pos.x -= 1  # 向右回退
                self.mario.vel.x = 0   # 停止水平移动
            elif self.mario.vel.x < 0:  # 向左移动时碰撞
                self.mario.pos.x += 1   # 向左回退
                self.mario.vel.x = 0   # 停止水平移动

    def adjust_pipe(self):
        """管道碰撞处理，防止马里奥穿过管道"""
        if self.pipe_collide:
            # 水平碰撞处理
            if self.mario.vel.x > 0:  # 向右移动时碰撞
                self.mario.pos.x = self.pipe_collide.rect.left - self.mario.rect.width/2
                self.mario.vel.x = 0
            elif self.mario.vel.x < 0:  # 向左移动时碰撞
                self.mario.pos.x = self.pipe_collide.rect.right + self.mario.rect.width/2
                self.mario.vel.x = 0
            
            # 垂直碰撞处理 - 从上方落到管道上
            if (self.mario.vel.y > 0 and 
                self.mario.rect.bottom > self.pipe_collide.rect.top and
                self.mario.rect.bottom - self.mario.vel.y <= self.pipe_collide.rect.top):
                
                self.mario.acc.y = 0        # 重置垂直加速度
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = self.pipe_collide.rect.top  # 放置在管道顶部
                self.mario.landing = True   # 标记为着陆状态
            # 从下方碰撞管道底部
            elif (self.mario.vel.y < 0 and 
                  self.mario.rect.top < self.pipe_collide.rect.bottom and
                  self.mario.rect.top - self.mario.vel.y >= self.pipe_collide.rect.bottom):
                
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = self.pipe_collide.rect.bottom + self.mario.rect.height
                self.mario.landing = False

    def adjust_ground(self):
        """地面碰撞处理，处理跳跃和下落"""
        if self.ground_collide:
            # 从上方落到地面上
            if (self.mario.vel.y > 0 and 
                self.mario.rect.bottom > self.ground_collider.rect.top and
                self.mario.rect.bottom - self.mario.vel.y <= self.ground_collider.rect.top):
                
                self.mario.acc.y = 0        # 重置垂直加速度
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = self.ground_collider.rect.top  # 放置在地面上
                self.mario.landing = True   # 标记为着陆状态
        else:
            # 如果没有与地面碰撞，检查是否与管道碰撞（在adjust_pipe中已经处理）
            if not self.pipe_collide:
                self.mario.landing = False  # 标记为未着陆状态

    def check_dead(self):
        """检查马里奥是否死亡（掉出地图底部）"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:  # 如果掉到地面以下一定距离
            self.mario.dead = True  # 标记为死亡状态
        # 同时检查是否走出地图右边界
        if self.mario.pos.x > MAP_WIDTH + 20:  # 如果走出地图右边界
            self.mario.dead = True  # 也可以标记为完成关卡，这里简单处理为死亡