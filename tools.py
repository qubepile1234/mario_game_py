import os  # 导入操作系统接口模块
import pygame as pg  # 导入Pygame库并简写为pg


def load_image(filename):
    """
    加载图像文件的工具函数
    
    参数:
        filename (str): 图像文件名（包括扩展名）
        
    返回:
        Surface: Pygame图像表面对象
        
    功能说明:
        这个函数负责从项目的资源目录中加载图像文件。
        它会自动构建正确的文件路径，确保无论程序从哪个目录运行，
        都能正确找到图像资源。
    """
    # 获取当前Python文件的绝对路径的目录名
    # os.path.abspath(__file__) 获取当前文件的绝对路径
    # os.path.dirname() 获取该路径的目录部分
    src = os.path.dirname(os.path.abspath(__file__))
    
    # 构建图像文件的完整路径
    # os.path.join() 智能拼接路径，自动处理不同操作系统的路径分隔符
    # 假设项目结构为：
    # project/
    #   ├── main.py (调用此函数的文件)
    #   └── resources/
    #       └── graphics/
    #           └── 图像文件
    path = os.path.join(src, 'resources', 'graphics', filename)
    
    # 使用Pygame加载图像并返回Surface对象
    # pg.image.load() 是Pygame加载图像的标准方法
    # 支持多种格式：PNG, JPG, GIF, BMP等
    return pg.image.load(path)