from level_data import *
from tools import *  # 导入工具函数
from settings import *  # 导入游戏设置

vec = pg.math.Vector2  # 创建二维向量别名
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
        
        
# from tools import *  # 导入工具函数
# from settings import *  # 导入游戏设置

# vec = pg.math.Vector2  # 创建二维向量别名

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

class PipeInnerCollider2(Collider):
    """水管内部碰撞体类，用于防止马里奥进入水管内部"""
    
    def __init__(self, x, y, width, height, image_path="1.jpg"):
        """
        初始化水管内部碰撞体
        
        参数:
            x, y (int): 水管内部左上角坐标
            width (int): 水管内部宽度
            height (int): 水管内部高度
            image_path (str): 贴图文件路径，默认为"./1.jpg"
        """
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        
        try:
            # 尝试加载图片
            # self.image = pg.image.load(image_path).convert_alpha()
            self.image = load_image(image_path).convert_alpha()
            
            # 如果图片尺寸与需求不符，缩放图片
            if self.image.get_width() != width or self.image.get_height() != height:
                self.image = pg.transform.scale(self.image, (width, height))
                
        except (FileNotFoundError, pg.error):
            # 如果图片加载失败，创建黑色矩形作为后备
            print(f"警告: 无法加载图片 {image_path}，使用黑色矩形代替")
            self.image = pg.Surface((width, height)).convert()
            self.image.fill((0, 0, 0))  # 黑色
        
        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标
        
        # 标记为水管内部碰撞体
        self.is_pipe_inner = True
        self.only_horizontal = True  # 只处理水平碰撞
        self.image_path = image_path  # 保存图片路径，以便后续可能需要重载
        
        
class PipeInnerCollider1(Collider):
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
            self.image = load_image(image_path).convert_alpha()
            
            # 如果图片尺寸与需求不符，调整图片大小
            # 注意：我们加载的图片高度是 height + margin_y
            target_width = width
            target_height = height + margin_y
            
            if (self.image.get_width() != target_width or 
                self.image.get_height() != target_height):
                self.image = pg.transform.scale(self.image, (target_width, target_height))
                
        except (FileNotFoundError, pg.error):
            # 如果图片加载失败，创建黑色矩形作为后备
            print(f"警告: 无法加载图片 {image_path}，使用黑色矩形代替")
            self.image = pg.Surface((width, height + margin_y)).convert()
            self.image.fill((0, 0, 0))  # 黑色
        
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
            target_height = height + margin_y*2 + 1
            # target_height = height
            
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
        self.collision_rect = pg.Rect(x, y, 0, 0)
        # self.collision_rect = pg.Rect(x, y, width, height)
        
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
    

class PipeInnerCollider_test(Collider):
    """水管内部碰撞体类，用于防止马里奥进入水管内部"""
    
    def __init__(self, x, y, width, height, image_path="1.jpg"):
        """
        初始化水管内部碰撞体
        
        参数:
            x, y (int): 水管内部左上角坐标
            width (int): 水管内部宽度
            height (int): 水管内部高度
            image_path (str): 贴图文件路径，默认为"./1.jpg"
        """
        pg.sprite.Sprite.__init__(self)  # 调用父类构造函数
        
        # try:
            # 尝试加载图片
            # self.image = pg.image.load(image_path).convert_alpha()
        #     self.image = load_image(image_path).convert_alpha()
            
        #     # 如果图片尺寸与需求不符，缩放图片
        #     if self.image.get_width() != width or self.image.get_height() != height:
        #         self.image = pg.transform.scale(self.image, (width, height))
                
        # except (FileNotFoundError, pg.error):
        #     # 如果图片加载失败，创建黑色矩形作为后备
        #     print(f"警告: 无法加载图片 {image_path}，使用黑色矩形代替")
        #     self.image = pg.Surface((width, height)).convert()
        #     self.image.fill((0, 0, 0))  # 黑色
        color=(0,0,0)
        self.image=pg.Surface((0,0)).convert()
        # self.image=pg.Surface((width,height)).convert()
        self.image.fill(color)
        
        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标
        
        # 标记为水管内部碰撞体
        self.is_pipe_inner = True
        self.only_horizontal = True  # 只处理水平碰撞
        # self.image_path = image_path  # 保存图片路径，以便后续可能需要重载
        
        