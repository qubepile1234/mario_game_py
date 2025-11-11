
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
            width, height = length, 3  # 水平线：长度=width，高度=1像素
        else:  # vertical
            width, height = 3, length  # 垂直线：宽度=1像素，长度=height
            
        self.image = pg.Surface((width, height)).convert()  # 创建碰撞区域表面
        if color:
            self.image.fill(color)  # 有颜色就填充
        else:
            self.image.set_alpha(0)  # 否则透明（保持原有行为）
            
        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标
