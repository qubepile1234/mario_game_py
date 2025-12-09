from enemy import *  # 导入精灵相关的所有类和函数
from mario import *  # 导入精灵相关的所有类和函数
from Collider import *  # 导入精灵相关的所有类和函数

class Level(pg.sprite.Sprite):
    """使用线段碰撞体的关卡类"""
    
    def __init__(self):
        """初始化关卡，设置所有游戏元素"""
        self.set_mario()      # 创建马里奥角色
        self.set_enemies()    # 创建敌人
        self.mario.pos = vec(WIDTH * 0.5, GROUND_HEIGHT - 70)  # 初始位置
        self.set_line_colliders()  # 设置线段碰撞体
        self.set_group()      # 组合所有碰撞体组

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

    def set_mario(self):
        """创建马里奥角色实例"""
        self.mario = Mario()
    
    def set_enemies(self):
        """创建敌人实例"""
        self.enemies = pg.sprite.Group()  # 敌人组
        
        # 添加敌人2 - 放在马里奥右侧
        enemy2 = Enemy2((500, GROUND_HEIGHT - 70))  # 改为600，确保在屏幕内
        self.enemies.add(enemy2)
        
        # 添加敌人1 - 放在水管上
        enemy1 = Enemy1((250, GROUND_HEIGHT - 150))  # 放在水管顶部
        self.enemies.add(enemy1)
        
        # 创建所有敌人的组（用于碰撞检测）
        self.all_enemies = pg.sprite.Group(self.enemies)
    
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
        
        
        
    
    def check_enemy_collisions1111(self):
        """检测马里奥与敌人的碰撞"""
        enemies_hit = pg.sprite.spritecollide(self.mario, self.all_enemies, False)
        
        for enemy in enemies_hit:
            # 马里奥从上方踩到敌人
            if (self.mario.vel.y > 0 and 
                self.mario.rect.bottom < enemy.rect.centery and
                abs(self.mario.rect.bottom - enemy.rect.top) < 20):
                
                # 马里奥反弹
                self.mario.vel.y = -JUMP * 0.7
                # 敌人死亡
                enemy.dead = True
                enemy.kill()
                # 从enemies组中移除
                self.enemies.remove(enemy)
                # 加分或其他效果
                print("踩到敌人！")
            
            # 马里奥碰到敌人侧面或上面（受伤）
            else:
                if not self.mario.dead:
                    print("马里奥受伤！")
                    # 这里可以添加受伤效果，比如无敌时间、生命减少等
                    # self.mario.hurt()
    
    def create_pipe(self, x, y, width, height, color=None):
        """
        创建水管碰撞体并添加到对应的组中
        """
        if color is None:
            color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        
        pipe_top_y = y - height
        
        pipe_top = LineCollider(x, pipe_top_y, width, 'horizontal', color=color)
        pipe_left = LineCollider(x, pipe_top_y, height, 'vertical', color=color)
        pipe_right = LineCollider(x + width - 1, pipe_top_y, height, 'vertical', color=color)
        
        self.horizontal_lines.add(pipe_top)
        self.vertical_lines.add(pipe_left, pipe_right)
        
        return (pipe_top, pipe_left, pipe_right)
    
    def set_line_colliders(self):
        """使用线段构建所有碰撞体"""
        self.horizontal_lines = pg.sprite.Group()  # 水平线组
        self.vertical_lines = pg.sprite.Group()    # 垂直线组
        
        # 地面
        ground_line = LineCollider(0, GROUND_HEIGHT, MAP_WIDTH, 'horizontal', color=(0,222,0))
        self.horizontal_lines.add(ground_line)
        
        # 左侧墙壁
        wall_left = LineCollider(0, 0, HEIGHT, 'vertical', color=(255,0,0))
        self.vertical_lines.add(wall_left)
        
        # 右侧墙壁
        wall_right = LineCollider(MAP_WIDTH-1, 0, HEIGHT, 'vertical', color=(0,255,255))
        self.vertical_lines.add(wall_right)
        
        # 创建水管
        self.pipe1 = self.create_pipe(40, GROUND_HEIGHT, 40, 80, color=(221,112,112))
        self.pipe2 = self.create_pipe(200, GROUND_HEIGHT, 83, 120, color=(22,22,131))
        # 可以添加更多水管
     
    def set_group(self):
        """将所有碰撞体组合在一起"""
        self.all_colliders = pg.sprite.Group()
        self.all_colliders.add(*self.horizontal_lines, *self.vertical_lines)

    def check_collide(self):
        """检测马里奥与所有线段碰撞体的碰撞"""
        self.horizontal_collisions = pg.sprite.spritecollide(self.mario, self.horizontal_lines, False)
        self.vertical_collisions = pg.sprite.spritecollide(self.mario, self.vertical_lines, False)
        
        self.on_ground = False
        for line in self.horizontal_collisions:
            if (self.mario.vel.y >= 0 and 
                abs(self.mario.rect.bottom - line.rect.top) < 5):
                self.on_ground = True
                self.ground_line = line
                # self.mario.landing = True  # 这里设置landing状态
                break

    def adjust_collisions(self):
        """处理所有碰撞"""
        self.mario.landing = False
        self.adjust_horizontal_collisions()
        self.adjust_vertical_collisions()
        
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
        
        if not found_ground:
            self.mario.landing = False

    def adjust_vertical_collisions(self):
        """处理垂直线碰撞（水平方向）"""
        for line in self.vertical_collisions:
            standing_on_connected_horizontal = False
            if hasattr(self, 'ground_line'):
                if (self.ground_line.rect.left <= line.rect.x <= self.ground_line.rect.right and
                    abs(self.ground_line.rect.top - line.rect.y) < 5):
                    standing_on_connected_horizontal = True
            
            if standing_on_connected_horizontal:
                if (self.mario.vel.x > 0 and 
                    self.mario.rect.right > line.rect.left and
                    self.mario.rect.right - self.mario.vel.x <= line.rect.left):
                    self.mario.pos.x = line.rect.left - self.mario.rect.width/2
                    self.mario.vel.x = 0
                elif (self.mario.vel.x < 0 and 
                    self.mario.rect.left < line.rect.right and
                    self.mario.rect.left - self.mario.vel.x >= line.rect.right):
                    self.mario.pos.x = line.rect.right + self.mario.rect.width/2
                    self.mario.vel.x = 0
            else:
                if self.mario.vel.x > 0:
                    self.mario.pos.x = line.rect.left - self.mario.rect.width/2
                    self.mario.vel.x = 0
                elif self.mario.vel.x < 0:
                    self.mario.pos.x = line.rect.right + self.mario.rect.width/2
                    self.mario.vel.x = 0

    def check_dead(self):
        """检查马里奥是否死亡"""
        if self.mario.pos.y > GROUND_HEIGHT + 50:
            self.mario.dead = True
        if self.mario.pos.x > MAP_WIDTH + 20:
            self.mario.dead = True