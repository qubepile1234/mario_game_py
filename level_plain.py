from sprites import *  # 导入精灵相关的所有类和函数


class Level(pg.sprite.Sprite):
    """简化关卡类，只有平坦地面，+墙壁"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_ground()     # 设置地面碰撞体
        self.set_wall()       # 设置墙壁碰撞体
        self.set_group()      # 组合所有碰撞体组

  
        
    def set_wall(self):
        """设置墙壁碰撞体，定义游戏中的墙壁障碍物，防止玩家跳出世界"""
        wall_left = Collider(0, 0, 10, HEIGHT,color=BLACK)  # 左侧墙壁
        wall_right = Collider(MAP_WIDTH-10, 0, 10, HEIGHT,color=BLACK)  # 右侧墙壁
        # 将管道碰撞体添加到组中
        self.wall_group = pg.sprite.Group(wall_left,wall_right)
        if hasattr(self, 'all_group'):
            self.ground_group.add(wall_left, wall_right)
            '''这段代码的意思是：

检查 self 对象是否有 all_group 这个属性

如果有，就执行 self.all_group.add(wall_left, wall_right)

如果没有，就跳过（避免报错）

🛡️ 为什么需要 hasattr()
防止 AttributeError 错误'''

        
    def update(self):
        """每帧更新关卡状态"""
        self.check_collide()  # 检测碰撞
        self.adjust_x()       # 水平方向位置调整
        self.adjust_y()       # 垂直方向位置调整
        self.check_dead()     # 检查玩家是否死亡

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()
        

    def set_ground(self):
        """设置单一连续的地面碰撞体，宽度为窗口的两倍"""
        # 创建单一地面碰撞体，宽度为1600像素（800*2）
        ground_width = MAP_WIDTH  # 1600像素
        ground_height = PLAIN_HEIGHT+40  #水平面为20，地面比水平面高40
        self.ground_collider = Collider(0, GROUND_HEIGHT, ground_width, ground_height)
        
    def set_group(self):
        """将地面组合成碰撞检测组"""
        self.ground_group = pg.sprite.Group(self.ground_collider)

    def check_collide(self):
        """检测马里奥的碰撞"""
        # self.ground_collide = pg.sprite.spritecollideany(self.mario, self.ground_group)  # 多地面碰撞
        self.wall_collide = pg.sprite.spritecollideany(self.mario, self.wall_group)      # wall碰撞
        self.ground_collide = pg.sprite.collide_rect(self.mario, self.ground_collider)#单一对象碰撞

    def adjust_x(self):
        """水平方向碰撞处理，防止马里奥穿过障碍物"""
        # 墙壁碰撞处理
        if self.wall_collide:
                if self.mario.vel.x > 0:  # 向右移动时碰撞
                    self.mario.pos.x -= 5  # 向右回退
                    self.mario.vel.x = 0   # 停止水平移动
                if self.mario.vel.x < 0:   # 向左移动时碰撞
                    self.mario.pos.x += 5   # 向左回退
                    self.mario.vel.x = 0   # 停止水平移动


    def adjust_y(self):
        """垂直方向碰撞处理，处理跳跃和下落"""
        # 地面碰撞处理
        if self.ground_collide:
            if self.ground_collider.rect.top < self.mario.pos.y:  # 从上方落到地面
                self.mario.acc.y = 0        # 重置垂直加速度
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = self.ground_collider.rect.top  # 放置在地面上
            self.mario.landing = True       # 标记为着陆状态
        else:
            self.mario.landing = False      # 标记为未着陆状态

    def check_dead(self):
        """检查马里奥是否死亡（掉出地图底部）"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:  # 如果掉到地面以下一定距离
            self.mario.dead = True  # 标记为死亡状态
        # 同时检查是否走出地图右边界
        if self.mario.pos.x > MAP_WIDTH + 20:  # 如果走出地图右边界
            self.mario.dead = True  # 也可以标记为完成关卡，这里简单处理为死亡