# 游戏配置设置文件
# 包含游戏运行所需的所有常量和参数

# 标题和窗口大小
TITLE = 'Mario'    # 游戏窗口标题
WIDTH = 800        # 游戏窗口宽度（像素）
HEIGHT = 600       # 游戏窗口高度（像素）

MAP_WIDTH = 2*800  # 地图宽度，设置为窗口宽度的两倍
PLAIN_HEIGHT = 20  # 平台高度（像素）

FPS = 60           # 游戏帧率（帧/秒），控制游戏运行流畅度

# 定义颜色（RGB格式）
GRAY = (100, 100, 100)  # 灰色，可能用于调试或UI元素
BLACK = (0, 0, 0)       # 黑色，通常用于透明色或背景
WHITE = (255, 255, 255) # 白色，通常用于文本或高亮
# 图片缩放比例
MARIO_SIZE = 2.5         # 马里奥精灵图的缩放倍数
BACKGROUND_SIZE = 1.000  # 背景图片的缩放倍数

# Mario 运动物理系数
ACC = 0.7          # 加速度：控制马里奥水平加速的快慢
GRAVITY = 1        # 重力：控制马里奥下落的速度
Slide_ground_friction = 0.12  # 滑动地面摩擦力：控制马里奥在滑动地面上的减速效果
Normal_ground_friction = 0.30 # 普通地面摩擦力：控制马里奥在普通地面上的减速效果
FRICTION = Normal_ground_friction     # 摩擦力：控制马里奥停止移动的阻力
JUMP = 20          # 跳跃力：控制马里奥跳跃的高度
TURNAROUND = 0.5   # 转向加速度：改变方向时的加速度
MAX_SPEED = 4.5      # 最大速度：限制马里奥水平移动的最高速度

# 地面高度
GROUND_HEIGHT = HEIGHT - 66  # 地面在屏幕上的y坐标（窗口高度减去66像素）