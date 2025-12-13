class PipeInnerCollider(Collider):
    """水管内部碰撞体类，用于防止马里奥进入水管内部"""
    
    def __init__(self, x, y, width, height, image_path="1.jpg", margin_y=INNER_MARGIN[1]):
        """
        初始化水管内部碰撞体
        
        参数:
            x, y (int): 水管内部左上角坐标
            width (int): 水管内部宽度
            height (int): 水管内部高度
            image_path (str): 贴图文件路径，默认为"1.jpg"
            margin_y (int): 图片向上延伸的像素数，默认为0
        """
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        
        self.margin_y = margin_y
        
        try:
            # 尝试加载图片
            original_image = load_image(image_path).convert_alpha()
            img_width, img_height = original_image.get_size()
            
            # 计算目标尺寸（包含空气贴图部分）
            target_width = width
            target_height = height + margin_y
            
            # 创建目标Surface
            self.image = pg.Surface((target_width, target_height), pg.SRCALPHA).convert_alpha()
            
            # 更高效的平铺方法：使用循环和裁剪
            for y_pos in range(0, target_height, img_height):
                for x_pos in range(0, target_width, img_width):
                    # 计算当前块的尺寸
                    block_width = min(img_width, target_width - x_pos)
                    block_height = min(img_height, target_height - y_pos)
                    
                    if block_width > 0 and block_height > 0:
                        # 从原图片中裁剪出对应大小的块
                        tile_block = original_image.subsurface((0, 0, block_width, block_height))
                        
                        # 如果块尺寸小于原图片尺寸，需要调整大小
                        if block_width < img_width or block_height < img_height:
                            tile_block = pg.transform.scale(tile_block, (block_width, block_height))
                        
                        # 绘制到目标Surface
                        self.image.blit(tile_block, (x_pos, y_pos))
            
        except (FileNotFoundError, pg.error) as e:
            # 如果图片加载失败，创建黑色矩形作为后备
            print(f"警告: 无法加载图片 {image_path}，错误: {e}，使用黑色矩形代替")
            self.image = pg.Surface((width, height + margin_y), pg.SRCALPHA).convert_alpha()
            self.image.fill((0, 0, 0, 255))  # 黑色，不透明
        
        # 碰撞体矩形（实际有碰撞的区域）
        self.collision_rect = pg.Rect(x, y, width, height)
        
        # 显示矩形（包含空气贴图部分）
        self.display_rect = pg.Rect(x, y - margin_y, width, height + margin_y)
        
        # Sprite的rect设置为显示矩形，以便正确显示
        self.rect = self.display_rect
        
        # 标记为水管内部碰撞体
        self.is_pipe_inner = True
        self.only_horizontal = True  # 只处理水平碰撞
        self.image_path = image_path  # 保存图片路径，以便后续可能需要重载
        
        # 保存原始位置信息
        self.collision_x = x
        self.collision_y = y
        self.collision_width = width
        self.collision_height = height

    def get_collision_rect(self):
        """获取实际碰撞的矩形区域"""
        return self.collision_rect


class PipeInnerCollider(Collider):
    """水管内部碰撞体类，用于防止马里奥进入水管内部"""
    
    def __init__(self, x, y, width, height, image_path="1.jpg", margin_y=INNER_MARGIN[1]):
        """
        初始化水管内部碰撞体
        
        参数:
            x, y (int): 水管内部左上角坐标
            width (int): 水管内部宽度
            height (int): 水管内部高度
            image_path (str): 贴图文件路径，默认为"1.jpg"
            margin_y (int): 图片向上延伸的像素数，默认为0
        """
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        
        self.margin_y = margin_y
        
        try:
            # 尝试加载图片
            original_image = load_image(image_path).convert_alpha()
            img_width, img_height = original_image.get_size()
            
            # 计算目标尺寸（包含空气贴图部分）
            target_width = width
            target_height = height + margin_y
            
            # 创建目标Surface
            self.image = pg.Surface((target_width, target_height), pg.SRCALPHA).convert_alpha()
            
            # 计算水平和垂直方向需要重复的次数
            repeat_x = max(1, target_width // img_width + (1 if target_width % img_width > 0 else 0))
            repeat_y = max(1, target_height // img_height + (1 if target_height % img_height > 0 else 0))
            
            # 图片填充（平铺）逻辑
            for i in range(repeat_x):
                for j in range(repeat_y):
                    # 计算源图片的裁剪区域
                    src_x = 0
                    src_y = 0
                    src_width = min(img_width, target_width - i * img_width)
                    src_height = min(img_height, target_height - j * img_height)
                    
                    # 只取源图片的有效部分
                    src_rect = pg.Rect(src_x, src_y, src_width, src_height)
                    tile_surface = original_image.subsurface(src_rect) if src_width > 0 and src_height > 0 else None
                    
                    if tile_surface:
                        # 计算目标位置
                        dest_x = i * img_width
                        dest_y = j * img_height
                        
                        # 计算目标区域的裁剪
                        dest_width = min(img_width, target_width - dest_x)
                        dest_height = min(img_height, target_height - dest_y)
                        
                        if dest_width > 0 and dest_height > 0:
                            # 如果图片大小与目标区域不匹配，调整大小
                            if dest_width != src_width or dest_height != src_height:
                                tile_surface = pg.transform.scale(tile_surface, (dest_width, dest_height))
                            
                            # 绘制到目标Surface
                            self.image.blit(tile_surface, (dest_x, dest_y))
            
            print(f"图片处理完成: {image_path}, 原始尺寸: {img_width}x{img_height}, "
                  f"目标尺寸: {target_width}x{target_height}, 重复: {repeat_x}x{repeat_y}")
            
        except (FileNotFoundError, pg.error) as e:
            # 如果图片加载失败，创建黑色矩形作为后备
            print(f"警告: 无法加载图片 {image_path}，错误: {e}，使用黑色矩形代替")
            self.image = pg.Surface((width, height + margin_y), pg.SRCALPHA).convert_alpha()
            self.image.fill((0, 0, 0, 255))  # 黑色，不透明
        
        # 碰撞体矩形（实际有碰撞的区域）
        self.collision_rect = pg.Rect(x, y, width, height)
        
        # 显示矩形（包含空气贴图部分）
        self.display_rect = pg.Rect(x, y - margin_y, width, height + margin_y)
        
        # Sprite的rect设置为显示矩形，以便正确显示
        self.rect = self.display_rect
        
        # 标记为水管内部碰撞体
        self.is_pipe_inner = True
        self.only_horizontal = True  # 只处理水平碰撞
        self.image_path = image_path  # 保存图片路径，以便后续可能需要重载
        
        # 保存原始位置信息
        self.collision_x = x
        self.collision_y = y
        self.collision_width = width
        self.collision_height = height

    def get_collision_rect(self):
        """获取实际碰撞的矩形区域"""
        return self.collision_rect
    
    
class EnemyBase(pg.sprite.Sprite):
    """敌人基类，处理敌人的共同属性和方法"""
    
    # ... 前面的代码保持不变 ...
    
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
            
            
            