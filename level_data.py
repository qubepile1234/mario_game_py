from settings import *
INNER_MARGIN=(-1,6)#(x,y)
                # 创建水管内部矩形碰撞体（比水管实际尺寸小某某像素）
# PIPE_DISTANCE=0
PIPE_DISTANCE=1
                            # 当马里奥距离水管边缘x像素时就触发碰撞
BACKGROUND='background2.jpg'

E_PLUS=5# 5像素范围内都视为碰撞,如果没有跳跃可以设置为0，enemy的

ENEMY_JUMP=16 #如果这个值太小,上面的E_PLUS可能需要再改,15时plus可以=0

M_PLUS=10# 5像素范围内都视为碰撞，马里奥的

# 关卡1数据（现有）
level1_data = {
    'ground': [[0, GROUND_HEIGHT, MAP_WIDTH, (0, 222, 0)]],
    'wall': [
        [0, 0, HEIGHT, (255, 0, 0)],  # 左侧墙壁
        [MAP_WIDTH-1, 0, HEIGHT, (0, 255, 255)]  # 右侧墙壁
    ],
    'pipe': [
        [320+60, GROUND_HEIGHT, 40, 120, (221, 112, 112)],
        [200+60, GROUND_HEIGHT, 83, 280, (22, 22, 131)],
        [500, GROUND_HEIGHT-200, 400, 40, (20, 20, 150)],
        [500, GROUND_HEIGHT-20, 400, 40, (20, 20, 150)],
        
    ],
    'enemy': [
        [2,(120, GROUND_HEIGHT - 150),70,70],
        [2,(20, GROUND_HEIGHT - 150),200,200],
        [2,(500, GROUND_HEIGHT - 70),400,400],
        [2,(1200, GROUND_HEIGHT - 150),200,200],
        [0,(520,GROUND_HEIGHT),20,20],
        [0,(540,GROUND_HEIGHT),20,20],
        [0,(570,GROUND_HEIGHT),20,20],
        [0,(50,GROUND_HEIGHT),20,20],
        [0,(70,GROUND_HEIGHT),20,20],
        [-1,(MAP_WIDTH-400,GROUND_HEIGHT),9,7]
    ],
    'mario': [(WIDTH * 0.5+200), (GROUND_HEIGHT - 70)]
}

# 关卡2数据（新）
level2_data = {
    'ground': [[0, GROUND_HEIGHT, MAP_WIDTH, (0, 100, 0)]],  # 深绿色地面
    'wall': [
        [0, 0, HEIGHT, (255, 100, 100)],  # 浅红色左侧墙壁
        [MAP_WIDTH-1, 0, HEIGHT, (100, 255, 255)]  # 浅青色右侧墙壁
    ],
    'pipe': [
        [120, GROUND_HEIGHT, 83, 250, (221, 112, 112)],
        [300, GROUND_HEIGHT, 83, 80, (20, 20, 150)],
        [500, GROUND_HEIGHT, 10, 350, (20, 20, 150)],
        [700, GROUND_HEIGHT, 200, 180, (20, 20, 150)],
        [1200, GROUND_HEIGHT, 200, 300, (20, 20, 150)],
        [500, GROUND_HEIGHT-450, 10, 400, (20, 20, 150)],
        ##########################################
        [280, GROUND_HEIGHT-400, 100, 10, (20, 20, 150)],
        [300, GROUND_HEIGHT-200, 83, 10, (20, 20, 150)],
        [500, GROUND_HEIGHT-300, 200, 10, (20, 20, 150)],
        [700, GROUND_HEIGHT-300, 100, 10, (20, 20, 150)],
        [700, GROUND_HEIGHT-300, 300, 10, (20, 20, 150)],
        [MAP_WIDTH-500, GROUND_HEIGHT-200, 400, 40, (20, 20, 150)],
        [MAP_WIDTH-500, GROUND_HEIGHT-20, 400, 40, (20, 20, 150)],
        
    ],
    'enemy': [
        [1,(200, GROUND_HEIGHT - 150),80,160],
        [1,(400, GROUND_HEIGHT - 150),80,160],
        [2,(100, GROUND_HEIGHT - 150),220,220],
        [0,(300,GROUND_HEIGHT - 200),30,30],
        [0,(350,GROUND_HEIGHT - 200),30,30],
        [0,(400,GROUND_HEIGHT - 200),30,30],
        [-1,(MAP_WIDTH-400,GROUND_HEIGHT),9,7]
        
    ],
    'mario': [(WIDTH * 0.5), (GROUND_HEIGHT - 100)]  # 不同起始位置
}

# 关卡3数据（新）
level3_data = {
    'ground': [
        [0, GROUND_HEIGHT, 300, (0, 150, 0)],  # 第一段地面
        [400, GROUND_HEIGHT, 300, (0, 150, 0)],  # 第二段地面（有缺口）
        [800, GROUND_HEIGHT, 300, (0, 150, 0)],  # 第三段地面
        [1200, GROUND_HEIGHT, MAP_WIDTH, (0, 222, 0)]
        
    ],
    'wall': [
        [0, 0, HEIGHT, (200, 0, 0)],  # 左侧墙壁
        [MAP_WIDTH-1, 0, HEIGHT, (0, 200, 200)]  # 右侧墙壁
    ],
    'pipe': [
        [250, GROUND_HEIGHT, 40, 100, (180, 80, 80)],
        [700, GROUND_HEIGHT, 60, 180, (80, 80, 180)],
        [900, GROUND_HEIGHT, 50, 120, (80, 180, 80)]
    ],
    'enemy': [
        [1,(150, GROUND_HEIGHT - 150),90,170],
        [2,(450, GROUND_HEIGHT - 100),240,240],
        [2,(750, GROUND_HEIGHT - 150),240,240],
        [0,(200,GROUND_HEIGHT - 250),40,40],
        [0,(600,GROUND_HEIGHT - 250),40,40],
        [0,(800,GROUND_HEIGHT - 250),40,40],
        [-1,(MAP_WIDTH-400,GROUND_HEIGHT),9,7]
    ],
    'mario': [(WIDTH * 0.5+100), (GROUND_HEIGHT - 150)]
}