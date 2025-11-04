from sprites import *  # 导入精灵相关的所有类和函数


class Level(pg.sprite.Sprite):
    """简化关卡类，只有平坦地面"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_ground()     # 设置地面碰撞体
        self.set_group()      # 组合所有碰撞体组

    def set_group(self):
        """将地面组合成碰撞检测组"""
        self.ground_group = pg.sprite.Group(self.ground_collider)
    #!
    def update(self):
        """每帧更新关卡状态"""
        self.check_collide()  # 检测碰撞
        #?为什么没有水平调整,因为这里是平坦地面，没有障碍物,也没写水平调整函数
        self.adjust_y()       # 垂直方向位置调整
        self.check_dead()     # 检查玩家是否死亡

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()

    def set_ground(self):
        """设置单一连续的地面碰撞体，宽度为窗口的两倍"""
        # 创建单一地面碰撞体，宽度为1600像素（800*2）
        map_width = WIDTH * 2  # 1600像素
        self.ground_collider = Collider(0, GROUND_HEIGHT, map_width, 60)

    def check_collide(self):
        """检测马里奥与地面的碰撞"""
        self.ground_collide = pg.sprite.collide_rect(self.mario, self.ground_collider)

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
        if self.mario.pos.x > WIDTH * 2:  # 如果走出地图右边界
            self.mario.dead = True  # 也可以标记为完成关卡，这里简单处理为死亡