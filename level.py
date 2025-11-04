from sprites import *  # 导入精灵相关的所有类和函数


class Level(pg.sprite.Sprite):
    """关卡类，负责管理游戏中的地形、碰撞检测和玩家交互"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_ground()     # 设置地面碰撞体
        self.set_pipes()      # 设置管道碰撞体
        self.set_steps()      # 设置台阶碰撞体
        self.set_group()      # 组合所有碰撞体组

    def set_group(self):
        """将地面、管道和台阶组合成一个碰撞检测组"""
        self.ground_step_pipe_group = pg.sprite.Group(self.ground_group,
                                                      self.pipe_group,
                                                      self.step_group)

    def update(self):
        """每帧更新关卡状态"""
        self.check_collide()  # 检测碰撞
        self.adjust_x()       # 水平方向位置调整
        self.adjust_y()       # 垂直方向位置调整
        self.check_dead()     # 检查玩家是否死亡
        # print(self.mario.pos) # 调试：打印马里奥位置

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()

    def set_ground(self):
        """设置地面碰撞体，定义游戏中的地面区域"""
        # 创建四个地面矩形碰撞体，参数为(x, y, width, height)
        ground_rect1 = Collider(0, GROUND_HEIGHT, 2953, 60)        # 第一段地面
        ground_rect2 = Collider(3048, GROUND_HEIGHT, 635, 60)      # 第二段地面
        ground_rect3 = Collider(3819, GROUND_HEIGHT, 2735, 60)     # 第三段地面
        ground_rect4 = Collider(6647, GROUND_HEIGHT, 2300, 60)     # 第四段地面

        # 将地面碰撞体添加到组中
        self.ground_group = pg.sprite.Group(ground_rect1,
                                            ground_rect2,
                                            ground_rect3,
                                            ground_rect4)

    def set_pipes(self):
        """设置管道碰撞体，定义游戏中的管道障碍物"""
        # 创建六个管道碰撞体，高度不同表示管道露出地面的高度不同
        pipe1 = Collider(1202, 452, 83, 80)   # 较短的管道
        pipe2 = Collider(1631, 409, 83, 140)  # 中等高度的管道
        pipe3 = Collider(1973, 366, 83, 170)  # 较高的管道
        pipe4 = Collider(2445, 366, 83, 170)  # 较高的管道
        pipe5 = Collider(6989, 452, 83, 82)   # 较短的管道
        pipe6 = Collider(7675, 452, 83, 82)   # 较短的管道

        # 将管道碰撞体添加到组中
        self.pipe_group = pg.sprite.Group(pipe1, pipe2,
                                          pipe3, pipe4,
                                          pipe5, pipe6)

    def set_steps(self):
        """设置台阶碰撞体，创建游戏中的平台和阶梯结构"""
        # 创建多个台阶碰撞体，形成复杂的平台结构
        
        # 第一组台阶（向上阶梯）
        step1 = Collider(5745, 495, 40, 44)
        step2 = Collider(5788, 452, 40, 88)
        step3 = Collider(5831, 409, 40, 132)
        step4 = Collider(5874, 366, 40, 176)
        
        # 第二组台阶（平台和向下阶梯）
        step5 = Collider(6001, 366, 40, 176)  # 平台
        step6 = Collider(6044, 408, 40, 40)   # 向下第一阶
        step7 = Collider(6087, 452, 40, 40)   # 向下第二阶
        step8 = Collider(6130, 495, 40, 40)   # 向下第三阶
        
        # 第三组台阶（向上阶梯）
        step9 = Collider(6345, 495, 40, 40)
        step10 = Collider(6388, 452, 40, 40)
        step11 = Collider(6431, 409, 40, 40)
        step12 = Collider(6474, 366, 40, 40)
        step13 = Collider(6517, 366, 40, 176)  # 平台
        
        # 第四组台阶（平台和向下阶梯）
        step14 = Collider(6644, 366, 40, 176)  # 平台
        step15 = Collider(6687, 408, 40, 40)   # 向下第一阶
        step16 = Collider(6728, 452, 40, 40)   # 向下第二阶
        step17 = Collider(6771, 495, 40, 40)   # 向下第三阶
        
        # 第五组台阶（高塔结构，连续向上）
        step18 = Collider(7760, 495, 40, 40)
        step19 = Collider(7803, 452, 40, 40)
        step20 = Collider(7845, 409, 40, 40)
        step21 = Collider(7888, 366, 40, 40)
        step22 = Collider(7931, 323, 40, 40)
        step23 = Collider(7974, 280, 40, 40)
        step24 = Collider(8017, 237, 40, 40)
        step25 = Collider(8060, 194, 40, 40)
        step26 = Collider(8103, 194, 40, 360)  # 高平台
        
        # 单独的台阶
        step27 = Collider(8488, 495, 40, 40)

        # 将所有台阶添加到组中
        self.step_group = pg.sprite.Group(step1, step2,
                                          step3, step4,
                                          step5, step6,
                                          step7, step8,
                                          step9, step10,
                                          step11, step12,
                                          step13, step14,
                                          step15, step16,
                                          step17, step18,
                                          step19, step20,
                                          step21, step22,
                                          step23, step24,
                                          step25, step26,
                                          step27)

    def check_collide(self):
        """检测马里奥与各种碰撞体的碰撞"""
        self.ground_collide = pg.sprite.spritecollideany(self.mario, self.ground_group)  # 地面碰撞
        self.pipe_collide = pg.sprite.spritecollideany(self.mario, self.pipe_group)      # 管道碰撞
        self.step_collide = pg.sprite.spritecollideany(self.mario, self.step_group)      # 台阶碰撞

    def adjust_x(self):
        """水平方向碰撞处理，防止马里奥穿过障碍物"""
        # 管道碰撞处理
        if self.pipe_collide:
            if self.mario.pos.y > self.pipe_collide.rect.y + 10:  # 确保是从侧面碰撞，不是从上方
                if self.mario.vel.x > 0:  # 向右移动时碰撞
                    self.mario.pos.x -= 5  # 向右回退
                    self.mario.vel.x = 0   # 停止水平移动
                if self.mario.vel.x < 0:   # 向左移动时碰撞
                    self.mario.pos.x = 5   # 向左回退（这里可能有误，应该是+=5？）
                    self.mario.vel.x = 0   # 停止水平移动
        
        # 台阶碰撞处理（与管道类似）
        if self.step_collide:
            if self.mario.pos.y > self.step_collide.rect.y + 10:
                if self.mario.vel.x > 0:
                    self.mario.pos.x -= 5
                    self.mario.vel.x = 0
                if self.mario.vel.x < 0:
                    self.mario.pos.x = 5
                    self.mario.vel.x = 0

    def adjust_y(self):
        """垂直方向碰撞处理，处理跳跃和下落"""
        # 地面碰撞处理
        if self.ground_collide:
            if self.ground_collide.rect.top < self.mario.pos.y:  # 从上方落到地面
                self.mario.acc.y = 0        # 重置垂直加速度
                self.mario.vel.y = 0        # 重置垂直速度
                self.mario.pos.y = self.ground_collide.rect.top  # 放置在地面上
            self.mario.landing = True       # 标记为着陆状态
        
        else:
            self.mario.landing = False      # 标记为未着陆状态
        
        # 管道顶部碰撞处理
        if self.pipe_collide:
            if self.mario.vel.y > 0:        # 下落过程中
                if self.pipe_collide.rect.top < self.mario.pos.y:  # 落在管道上
                    self.mario.acc.y = 0
                    self.mario.vel.y = 0
                    self.mario.pos.y = self.pipe_collide.rect.top
                self.mario.landing = True
        
        # 台阶顶部碰撞处理
        if self.step_collide:
            if self.mario.vel.y > 0:        # 下落过程中
                if self.step_collide.rect.top < self.mario.pos.y:  # 落在台阶上
                    self.mario.acc.y = 0
                    self.mario.vel.y = 0
                    self.mario.pos.y = self.step_collide.rect.top
                self.mario.landing = True

    def check_dead(self):
        """检查马里奥是否死亡（掉出地图底部）"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:  # 如果掉到地面以下一定距离
            self.mario.dead = True  # 标记为死亡状态