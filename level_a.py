from enemy import *  # 导入精灵相关的所有类和函数
from mario import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精灵相关的所有类和函数
import random

class Level(pg.sprite.Sprite):
    """使用线段碰撞体的关卡类"""
    
    def __init__(self, level_data=None):
        """初始化关卡，设置所有游戏元素
        
        参数:
            level_data: 关卡数据字典，如果为None则使用默认关卡1
        """
        # 初始化碰撞体组
        self.horizontal_lines = pg.sprite.Group()  # 水平线组
        self.vertical_lines = pg.sprite.Group()    # 垂直线组
        
        # 设置关卡数据
        if level_data is None:
            self.set_level(level1_data)
        else:
            self.set_level(level_data)
            
        # self.set_group()      # 组合所有碰撞体组
        # self.set_mario()      # 创建马里奥角色
        # self.set_enemies()    # 创建敌人
        
        

    def set_default_level_data(self):
        """设置默认关卡1的数据"""
        level1 = {
            'ground': [[0, GROUND_HEIGHT, MAP_WIDTH, (0, 222, 0)]],
            'wall': [
                [0, 0, HEIGHT, (255, 0, 0)],  # 左侧墙壁
                [MAP_WIDTH-1, 0, HEIGHT, (0, 255, 255)]  # 右侧墙壁
            ],
            'pipe': [
                [320, GROUND_HEIGHT, 40, 120, (221, 112, 112)],
                [200, GROUND_HEIGHT, 83, 280, (22, 22, 131)]
            ],
            'enemy': [
                [1,(40, GROUND_HEIGHT - 150),50,50],
                [2,(20, GROUND_HEIGHT - 150),200,200],
                [2,(500, GROUND_HEIGHT - 70),400,400],
               # '''类型,位置,缩放比例w,h'''
            ],
            'mario': [(WIDTH * 0.5), (GROUND_HEIGHT - 70)]
        }
        self.set_level(level1)
        # 可能有level2但暂时搁置

    def set_level(self, level_data):
        """根据关卡数据字典设置关卡
        
        参数:
            level_data: 关卡数据字典，包含'ground'、'wall'、'pipe'键
        """
        # 清空现有的碰撞体
        self.horizontal_lines.empty()
        self.vertical_lines.empty()
        
        # 设置地面
        for ground in level_data.get('ground', []):
            self.set_ground(ground)
            
        # 设置墙壁
        for wall in level_data.get('wall', []):
            self.set_wall(wall)
            
        # 设置水管
        for pipe in level_data.get('pipe', []):
            self.set_pipe(pipe)
            
        #设置enemy
        self.set_enemies(level_data)
        mario_data=level_data.get('mario', [])
        self.set_mario(mario_data)      # 创建马里奥角色

        self.set_group()      # 组合所有碰撞体组
                

    def set_ground(self, ground_data):
        """设置地面碰撞体
        
        参数:
            ground_data: 地面数据列表 [x, y, length, color]
        """
        if len(ground_data) >= 4:
            x, y, length, color = ground_data[:4]
            ground_line = LineCollider(x=x, y=y, length=length, 
                                       orientation='horizontal', color=color)
            self.horizontal_lines.add(ground_line)

    def set_wall(self, wall_data):
        """设置墙壁碰撞体
        
        参数:
            wall_data: 墙壁数据列表 [x, y, length, color]
        """
        if len(wall_data) >= 4:
            x, y, length, color = wall_data[:4]
            wall_line = LineCollider(x=x, y=y, length=length, 
                                     orientation='vertical', color=color)
            self.vertical_lines.add(wall_line)

    def set_pipe(self, pipe_data):
        """设置水管碰撞体
        
        参数:
            pipe_data: 水管数据列表 [x, y, width, height, color]
        """
        if len(pipe_data) >= 5:
            x, y, width, height, color = pipe_data[:5]
            self.create_pipe(x, y, width, height, color)

    def update(self):
        """每帧更新关卡状态"""
        # 更新所有敌人
        for enemy in self.enemies:
            enemy.update(self.horizontal_lines, self.vertical_lines)
        
        # 更新马里奥
        self.check_collide()  # 检测碰撞
        self.adjust_collisions()  # 处理碰撞
        self.check_dead()     # 检查玩家是否死亡
        
        # 检查马里奥与敌人的碰撞
        self.check_enemy_collisions()

    def set_mario(self,mario_data):
        """创建马里奥角色实例"""
        self.mario = Mario()
        self.mario.pos = vec(mario_data[0], mario_data[1])  # 初始位置
        
    
    def set_enemies(self,level_data):
        """创建敌人实例"""
        self.enemies = pg.sprite.Group()  # 敌人组
        
        # 添加敌人2 - 放在马里奥右侧
        # enemy2 = Enemy2((500, GROUND_HEIGHT - 70))  # 改为600，确保在屏幕内
        # self.enemies.add(enemy2)
        
        # 添加敌人1 - 放在水管上
        # enemy1 = Enemy1((40, GROUND_HEIGHT - 150))  # 放在水管顶部
        # self.enemies.add(enemy1)
        
        for enemy in level_data.get('enemy', []):
            self.set_enemy(enemy)
        
        # 创建所有敌人的组（用于碰撞检测）
        self.all_enemies = pg.sprite.Group(self.enemies)
    
    def set_enemy(self, enemy_data):
        if(enemy_data[0]==1):
        # 添加敌人1
            enemy_type1 = Enemy1(enemy_data[1],enemy_data[2],enemy_data[3])
            # enemy_type1.set_scale(enemy_data[2],enemy_data[3])
            self.enemies.add(enemy_type1)
            
        elif(enemy_data[0]==2):
        # 添加敌人2
            enemy_type2 = Enemy2(enemy_data[1],enemy_data[2],enemy_data[3]) 
            enemy_type2.set_scale(enemy_data[2],enemy_data[3])
            self.enemies.add(enemy_type2)
        
    def check_enemy_collisions(self):
        """检测马里奥与敌人的碰撞"""
        # 创建一个临时列表，避免在遍历时修改
        enemies_to_check = list(self.all_enemies.sprites())
        
        for enemy in enemies_to_check:
            # 检查马里奥是否与敌人碰撞
            if pg.sprite.collide_rect(self.mario, enemy):
                # 马里奥从上方踩到敌人
                if (self.mario.vel.y > 0 and 
                    self.mario.rect.bottom < enemy.rect.centery and
                    abs(self.mario.rect.bottom - enemy.rect.top) < 20):
                    
                    # 马里奥反弹
                    self.mario.vel.y = -JUMP * 0.7
                    # 标记敌人死亡
                    enemy.dead = True
                    # 从enemies组中移除
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    if enemy in self.all_enemies:
                        self.all_enemies.remove(enemy)
                    print("踩到敌人！")
                
                # 马里奥碰到敌人侧面或上面（受伤）
                else:
                    if not self.mario.dead:
                        print("马里奥受伤！")
                        # 这里可以添加受伤效果
                        # self.mario.hurt()
    
    def create_pipe(self, x, y, width, height, color=None):
        """
        创建水管碰撞体并添加到对应的组中
        
        参数:
            x, y (int): 水管底部中心位置坐标
            width (int): 水管宽度
            height (int): 水管高度（从地面向上）
            color: 水管颜色，默认为随机颜色
        """
        if color is None:
            color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        
        # 计算水管顶部位置（y坐标从地面向上）
        pipe_top_y = y - height
        
        # 创建水管的三个线段碰撞体
        pipe_top = LineCollider(x, pipe_top_y, width, 'horizontal', color=color)
        pipe_left = LineCollider(x, pipe_top_y, height, 'vertical', color=color)
        pipe_right = LineCollider(x + width - 1, pipe_top_y, height, 'vertical', color=color)
        
        # 将碰撞体添加到对应的组中
        self.horizontal_lines.add(pipe_top)
        self.vertical_lines.add(pipe_left, pipe_right)
        
        return (pipe_top, pipe_left, pipe_right)
    
    def set_group(self):
        """将所有碰撞体组合在一起"""
        # 创建包含所有线段的组
        self.all_colliders = pg.sprite.Group()
        self.all_colliders.add(*self.horizontal_lines, *self.vertical_lines)

    def check_collide(self):
        """检测马里奥与所有线段碰撞体的碰撞"""
        self.horizontal_collisions = pg.sprite.spritecollide(self.mario, self.horizontal_lines, False)
        self.vertical_collisions = pg.sprite.spritecollide(self.mario, self.vertical_lines, False)
        
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
        
        # 处理水平线碰撞（垂直方向） - 先处理这个，因为它会影响马里奥的位置
        self.adjust_horizontal_collisions()
        
        # 处理垂直线碰撞（水平方向）
        self.adjust_vertical_collisions()
        
        # 如果没有水平碰撞，确保马里奥不会停留在空中
        if not self.horizontal_collisions and not self.on_ground:
            self.mario.landing = False

    def adjust_horizontal_collisions(self):
        """处理水平线碰撞（垂直方向）"""
        found_ground = False
        
        for line in self.horizontal_collisions:
            # 从上方落到水平线上
            if (self.mario.vel.y > 0 and 
                self.mario.rect.bottom > line.rect.top and
                self.mario.rect.bottom - self.mario.vel.y <= line.rect.top):
                
                self.mario.acc.y = 0
                self.mario.vel.y = 0
                self.mario.pos.y = line.rect.top
                self.mario.landing = True
                found_ground = True
                break
                
            # 从下方碰撞水平线底部
            elif (self.mario.vel.y < 0 and 
                  self.mario.rect.top < line.rect.bottom and
                  self.mario.rect.top - self.mario.vel.y >= line.rect.bottom):
                
                self.mario.vel.y = 0
                self.mario.pos.y = line.rect.bottom + self.mario.rect.height
        
        # 如果没有找到可以站立的水平线，确保马里奥不会停留在空中
        if not found_ground:
            self.mario.landing = False

    def adjust_vertical_collisions(self):
        """处理垂直线碰撞（水平方向）"""
        for line in self.vertical_collisions:
            # 检查马里奥是否站在与这条垂直线相连的水平线上
            standing_on_connected_horizontal = False
            if hasattr(self, 'ground_line'):
                # 如果马里奥站在水平线上，并且这条水平线与当前垂直线相连
                if (
                    self.mario.landing==True and
                    self.ground_line.rect.left <= line.rect.x <= self.ground_line.rect.right and
                    abs(self.ground_line.rect.top - line.rect.y) < 5):
                    standing_on_connected_horizontal = True
            
            # 如果马里奥站在与这条垂直线相连的水平线上，允许他移动通过
            if standing_on_connected_horizontal:
                # 只有当马里奥试图穿过垂直线时才阻止他
                if (self.mario.vel.x > 0 and 
                    self.mario.rect.right > line.rect.left and
                    self.mario.rect.right - self.mario.vel.x <= line.rect.left):
                    # 向右移动时碰到垂直线
                    self.mario.pos.x = line.rect.left - self.mario.rect.width/2
                    self.mario.vel.x = 0
                elif (self.mario.vel.x < 0 and 
                    self.mario.rect.left < line.rect.right and
                    self.mario.rect.left - self.mario.vel.x >= line.rect.right):
                    # 向左移动时碰到垂直线
                    self.mario.pos.x = line.rect.right + self.mario.rect.width/2
                    self.mario.vel.x = 0
            else:
                # 标准水平碰撞处理
                if self.mario.vel.x > 0:  # 向右移动时碰撞
                    self.mario.pos.x = line.rect.left - self.mario.rect.width/2
                    self.mario.vel.x = 0
                elif self.mario.vel.x < 0:  # 向左移动时碰撞
                    self.mario.pos.x = line.rect.right + self.mario.rect.width/2
                    self.mario.vel.x = 0

    def check_dead(self):
        """检查马里奥是否死亡"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:
            self.mario.dead = True
        # 同时检查是否走出地图右边界
        if self.mario.pos.x > MAP_WIDTH + 20:
            self.mario.dead = True