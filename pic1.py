from PIL import Image, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
from datetime import datetime

# ============================================================
# 核心图像处理函数
# ============================================================

def fix_white_background(input_path, output_path, 
                        color_tolerance=15,
                        min_brightness=220,
                        max_brightness=255,
                        preserve_edges=True,
                        edge_smoothing=1.0):
    """
    修复白色背景染色：将接近白色但不是纯白色的像素修复为纯白色
    
    参数:
        color_tolerance: 颜色容忍度（标准差阈值），值越小要求越接近纯白色
        min_brightness: 最小亮度阈值，只处理比这个值更亮的像素
        max_brightness: 最大亮度阈值，避免处理已经纯白的部分
        preserve_edges: 是否保留边缘（防止纯白区域扩大）
        edge_smoothing: 边缘平滑度（0-2），值越大过渡越自然
    """
    # 读取图像
    img = Image.open(input_path)
    original = img.copy()
    
    # 转换为RGBA以支持透明度
    img = img.convert('RGBA')
    data = np.array(img)
    
    # 分离通道
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
    # 计算亮度（0-255）
    brightness = (r.astype(np.float32) + g + b) / 3.0
    
    # 计算颜色标准差（判断是否接近白色）
    # 白色像素的RGB三个值应该非常接近
    color_std = np.std([r, g, b], axis=0)
    
    # 创建主要掩码：接近白色且亮度足够高
    is_near_white = color_std < color_tolerance
    is_bright = brightness > min_brightness
    # 可选：避免处理已经纯白的部分
    is_not_pure_white = brightness < max_brightness
    
    # 组合条件
    if max_brightness < 255:
        mask = is_near_white & is_bright & is_not_pure_white
    else:
        mask = is_near_white & is_bright
    
    # 如果启用边缘保护，需要特殊处理
    if preserve_edges:
        # 创建一个距离场，距离纯白像素越远，处理强度越低
        from scipy.ndimage import distance_transform_edt
        
        # 找到纯白像素（RGB都接近255）
        pure_white_mask = (r > 250) & (g > 250) & (b > 250)
        
        if np.any(pure_white_mask):
            # 计算每个像素到最近纯白像素的距离
            distances = distance_transform_edt(~pure_white_mask)
            
            # 根据距离创建权重（距离越近，权重越高）
            max_dist = np.max(distances)
            if max_dist > 0:
                weights = 1.0 - (distances / max_dist) * edge_smoothing
                weights = np.clip(weights, 0, 1)
                
                # 将权重应用到掩码
                weighted_mask = mask.astype(np.float32) * weights
                mask = weighted_mask > 0.5
    
    # 应用白色替换
    result = data.copy()
    
    # 直接替换为纯白色
    result[mask, 0] = 255  # R
    result[mask, 1] = 255  # G
    result[mask, 2] = 255  # B
    # Alpha通道保持不变
    
    # 保存结果
    result_img = Image.fromarray(result, 'RGBA')
    
    # 如果是JPG格式，需要转换为RGB并保存
    if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
        result_img = result_img.convert('RGB')
    
    result_img.save(output_path, quality=95)
    
    # 计算统计信息
    total_pixels = mask.size
    replaced_pixels = np.sum(mask)
    replaced_percentage = replaced_pixels / total_pixels * 100
    
    stats = {
        'original': original,
        'result': result_img,
        'mask': mask,
        'total_pixels': total_pixels,
        'replaced_pixels': replaced_pixels,
        'replaced_percentage': replaced_percentage,
        'color_std_distribution': color_std.flatten(),
        'brightness_distribution': brightness.flatten()
    }
    
    return result_img, stats

# ============================================================
# 增强版本：智能白色背景检测
# ============================================================

def smart_fix_white_background(input_path, output_path,
                              adaptive_tolerance=True,
                              target_white_level=0.98):
    """
    智能修复白色背景染色
    自动检测图像中的白色区域并修复
    
    参数:
        adaptive_tolerance: 是否自适应调整颜色容忍度
        target_white_level: 目标白色程度（0-1），1表示纯白色
    """
    # 读取图像
    img = Image.open(input_path)
    original = img.copy()
    
    # 转换为RGBA
    img = img.convert('RGBA')
    data = np.array(img)
    
    # 分离通道
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
    # 计算亮度和颜色特征
    brightness = (r.astype(np.float32) + g + b) / 3.0
    color_std = np.std([r, g, b], axis=0)
    
    # 自动检测白色区域
    # 1. 找到可能的白色区域（高亮度，低颜色偏差）
    candidate_mask = (brightness > 200) & (color_std < 30)
    
    if np.any(candidate_mask):
        # 分析候选区域的统计特征
        candidate_brightness = brightness[candidate_mask]
        candidate_std = color_std[candidate_mask]
        
        # 自动确定参数
        if adaptive_tolerance:
            # 基于候选区域的标准差分布确定容忍度
            std_95 = np.percentile(candidate_std, 95)
            color_tolerance = min(30, max(10, std_95 * 1.5))
            
            # 基于候选区域的亮度分布确定亮度阈值
            brightness_10 = np.percentile(candidate_brightness, 10)
            min_brightness = max(200, brightness_10 - 10)
        else:
            color_tolerance = 15
            min_brightness = 220
    else:
        # 如果没有明显白色区域，使用保守参数
        color_tolerance = 10
        min_brightness = 230
    
    # 创建最终掩码
    is_near_white = color_std < color_tolerance
    is_bright = brightness > min_brightness
    
    # 如果是自适应模式，使用软阈值
    if adaptive_tolerance:
        # 计算每个像素的"白色程度"分数
        std_score = 1.0 - np.clip(color_std / color_tolerance, 0, 1)
        brightness_score = np.clip((brightness - min_brightness) / (255 - min_brightness), 0, 1)
        white_score = std_score * brightness_score
        
        # 根据目标白色程度应用渐变修复
        mask = white_score > (1 - target_white_level)
        
        # 对边缘像素使用渐变修复（更自然）
        soft_mask = white_score
        
        # 应用渐变修复
        result = data.copy().astype(np.float32)
        
        # 对每个通道应用渐变修复
        for i in range(3):
            channel = result[:, :, i]
            # 渐变修复：像素值 = 原值*(1-权重) + 255*权重
            channel = channel * (1 - soft_mask) + 255 * soft_mask
            result[:, :, i] = np.clip(channel, 0, 255)
        
        result = result.astype(np.uint8)
    else:
        # 硬阈值修复
        mask = is_near_white & is_bright
        
        result = data.copy()
        result[mask, 0] = 255  # R
        result[mask, 1] = 255  # G
        result[mask, 2] = 255  # B
    
    # 保存结果
    result_img = Image.fromarray(result, 'RGBA')
    
    if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
        result_img = result_img.convert('RGB')
    
    result_img.save(output_path, quality=95)
    
    # 统计信息
    total_pixels = mask.size
    replaced_pixels = np.sum(mask)
    replaced_percentage = replaced_pixels / total_pixels * 100
    
    stats = {
        'original': original,
        'result': result_img,
        'mask': mask,
        'total_pixels': total_pixels,
        'replaced_pixels': replaced_pixels,
        'replaced_percentage': replaced_percentage,
        'auto_params': {
            'color_tolerance': color_tolerance,
            'min_brightness': min_brightness
        }
    }
    
    return result_img, stats

# ============================================================
# 批量处理函数
# ============================================================

def batch_fix_white_background(input_folder, output_folder, 
                              color_tolerance=15,
                              min_brightness=220,
                              use_smart_mode=False):
    """
    批量修复白色背景染色
    
    参数:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径
        color_tolerance: 颜色容忍度
        min_brightness: 最小亮度
        use_smart_mode: 是否使用智能模式
    """
    # 确保输出文件夹存在
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的图片格式
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp']
    
    # 收集所有图片文件
    input_files = []
    for ext in image_extensions:
        input_files.extend(Path(input_folder).glob(f'*{ext}'))
        input_files.extend(Path(input_folder).glob(f'*{ext.upper()}'))
    
    if not input_files:
        return [], []
    
    # 处理统计
    processed_files = []
    failed_files = []
    
    print(f"找到 {len(input_files)} 张图片需要处理")
    
    for img_file in input_files:
        try:
            # 生成输出文件名
            output_file = output_path / f"fixed_{img_file.name}"
            
            # 处理图片
            if use_smart_mode:
                result_img, stats = smart_fix_white_background(
                    str(img_file),
                    str(output_file)
                )
            else:
                result_img, stats = fix_white_background(
                    str(img_file),
                    str(output_file),
                    color_tolerance=color_tolerance,
                    min_brightness=min_brightness
                )
            
            processed_files.append({
                'input': str(img_file),
                'output': str(output_file),
                'stats': stats
            })
            
            print(f"✓ 成功处理: {img_file.name} ({stats['replaced_percentage']:.1f}% 像素被修复)")
            
        except Exception as e:
            failed_files.append({
                'file': str(img_file),
                'error': str(e)
            })
            print(f"✗ 处理失败: {img_file.name} - {e}")
    
    return processed_files, failed_files

# ============================================================
# 可视化函数
# ============================================================

def create_comparison_visualization(input_path, output_path, stats, save_path=None):
    """
    创建处理前后的对比可视化
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 原始图像
    axes[0, 0].imshow(stats['original'])
    axes[0, 0].set_title('原始图像')
    axes[0, 0].axis('off')
    
    # 处理后的图像
    axes[0, 1].imshow(stats['result'])
    axes[0, 1].set_title('修复后的图像')
    axes[0, 1].axis('off')
    
    # 修复区域掩码
    if 'mask' in stats:
        axes[0, 2].imshow(stats['mask'], cmap='gray')
        axes[0, 2].set_title(f'修复区域\n({stats["replaced_percentage"]:.1f}% 像素)')
        axes[0, 2].axis('off')
    
    # 颜色标准差分布
    if 'color_std_distribution' in stats:
        axes[1, 0].hist(stats['color_std_distribution'], bins=50, 
                        color='blue', alpha=0.7, range=(0, 50))
        axes[1, 0].axvline(x=15, color='r', linestyle='--', 
                          label='默认阈值(15)')
        axes[1, 0].set_title('颜色标准差分布')
        axes[1, 0].set_xlabel('颜色标准差')
        axes[1, 0].set_ylabel('像素数量')
        axes[1, 0].legend()
        axes[1, 0].set_xlim(0, 50)
    
    # 亮度分布
    if 'brightness_distribution' in stats:
        axes[1, 1].hist(stats['brightness_distribution'], bins=50, 
                        color='green', alpha=0.7, range=(0, 255))
        axes[1, 1].axvline(x=220, color='r', linestyle='--', 
                          label='亮度阈值(220)')
        axes[1, 1].set_title('亮度分布')
        axes[1, 1].set_xlabel('亮度')
        axes[1, 1].set_ylabel('像素数量')
        axes[1, 1].legend()
    
    # 差异对比
    if 'original' in stats and 'result' in stats:
        # 转换为numpy数组进行比较
        original_array = np.array(stats['original'].convert('RGB'))
        result_array = np.array(stats['result'].convert('RGB'))
        
        # 计算绝对差异
        diff = np.abs(result_array.astype(np.float32) - original_array.astype(np.float32))
        diff_sum = np.mean(diff, axis=2)
        
        im = axes[1, 2].imshow(diff_sum, cmap='hot', vmin=0, vmax=100)
        axes[1, 2].set_title('修复差异热图')
        axes[1, 2].axis('off')
        plt.colorbar(im, ax=axes[1, 2], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    
    # 保存或显示
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        plt.show()
        return None

# ============================================================
# GUI 应用程序
# ============================================================

class WhiteBackgroundFixerApp:
    """白色背景修复工具的GUI应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("白色背景染色修复工具")
        self.root.geometry("800x600")
        
        # 存储变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.color_tolerance = tk.IntVar(value=15)
        self.min_brightness = tk.IntVar(value=220)
        self.use_smart_mode = tk.BooleanVar(value=True)
        self.preserve_edges = tk.BooleanVar(value=True)
        
        # 处理状态
        self.processing = False
        self.progress_var = tk.DoubleVar(value=0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, 
                               text="白色背景染色修复工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 输入文件
        ttk.Label(file_frame, text="输入图片:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="浏览...", 
                  command=self.browse_input_file).grid(row=0, column=2, padx=5)
        
        # 输出文件
        ttk.Label(file_frame, text="输出图片:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="浏览...", 
                  command=self.browse_output_file).grid(row=1, column=2, padx=5)
        
        # 参数设置部分
        param_frame = ttk.LabelFrame(main_frame, text="处理参数", padding="10")
        param_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 颜色容忍度滑块
        ttk.Label(param_frame, text="颜色容忍度:").grid(row=0, column=0, sticky=tk.W)
        tolerance_scale = ttk.Scale(param_frame, from_=1, to=50, 
                                   variable=self.color_tolerance,
                                   orient=tk.HORIZONTAL, length=200)
        tolerance_scale.grid(row=0, column=1, padx=5)
        tolerance_label = ttk.Label(param_frame, textvariable=self.color_tolerance)
        tolerance_label.grid(row=0, column=2)
        
        # 亮度阈值滑块
        ttk.Label(param_frame, text="最小亮度:").grid(row=1, column=0, sticky=tk.W, pady=5)
        brightness_scale = ttk.Scale(param_frame, from_=150, to=250, 
                                    variable=self.min_brightness,
                                    orient=tk.HORIZONTAL, length=200)
        brightness_scale.grid(row=1, column=1, padx=5, pady=5)
        brightness_label = ttk.Label(param_frame, textvariable=self.min_brightness)
        brightness_label.grid(row=1, column=2, pady=5)
        
        # 处理模式选项
        ttk.Checkbutton(param_frame, text="使用智能模式（推荐）",
                       variable=self.use_smart_mode).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(param_frame, text="保护边缘（防止纯白区域扩大）",
                       variable=self.preserve_edges).grid(row=3, column=0, columnspan=3, sticky=tk.W)
        
        # 按钮部分
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="处理单张图片", 
                  command=self.process_single_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="批量处理文件夹", 
                  command=self.process_batch).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="生成对比图", 
                  command=self.create_comparison).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="退出", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # 参数说明
        help_frame = ttk.LabelFrame(main_frame, text="参数说明", padding="10")
        help_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        help_text = """颜色容忍度：控制什么算是"接近白色"，值越小要求越接近纯白色
最小亮度：只处理比这个值更亮的像素（白色是255）
智能模式：自动分析图片特征并调整参数
边缘保护：防止修复区域过度扩散到非白色区域"""
        
        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor=tk.W)
        
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择要处理的图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            # 自动生成输出文件名
            input_path = Path(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"fixed_{timestamp}_{input_path.name}"
            output_path = input_path.parent / output_filename
            self.output_path.set(str(output_path))
    
    def browse_output_file(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存处理后的图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.output_path.set(filename)
    
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def process_single_image(self):
        """处理单张图片"""
        if self.processing:
            return
        
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("错误", "请选择有效的输入文件")
            return
        
        if not output_path:
            messagebox.showerror("错误", "请指定输出文件路径")
            return
        
        # 在后台线程中处理图片
        self.processing = True
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self._process_single_image_thread)
        thread.daemon = True
        thread.start()
    
    def _process_single_image_thread(self):
        """处理单张图片的后台线程"""
        try:
            self.update_status("正在处理图片...")
            self.progress_var.set(30)
            
            input_path = self.input_path.get()
            output_path = self.output_path.get()
            
            if self.use_smart_mode.get():
                result_img, stats = smart_fix_white_background(
                    input_path,
                    output_path
                )
            else:
                result_img, stats = fix_white_background(
                    input_path,
                    output_path,
                    color_tolerance=self.color_tolerance.get(),
                    min_brightness=self.min_brightness.get(),
                    preserve_edges=self.preserve_edges.get()
                )
            
            self.progress_var.set(100)
            self.update_status(f"处理完成！修复了 {stats['replaced_percentage']:.1f}% 的像素")
            
            # 询问是否查看结果
            if messagebox.askyesno("完成", "图片处理完成！是否查看处理结果？"):
                result_img.show()
            
        except Exception as e:
            messagebox.showerror("处理错误", f"处理图片时出错:\n{str(e)}")
            self.update_status("处理失败")
        finally:
            self.processing = False
            self.progress_var.set(0)
    
    def process_batch(self):
        """批量处理文件夹"""
        if self.processing:
            return
        
        input_folder = filedialog.askdirectory(title="选择输入文件夹")
        if not input_folder:
            return
        
        output_folder = filedialog.askdirectory(title="选择输出文件夹", 
                                               mustexist=False)
        if not output_folder:
            return
        
        # 在后台线程中处理批量图片
        self.processing = True
        self.progress_var.set(0)
        
        thread = threading.Thread(
            target=self._process_batch_thread,
            args=(input_folder, output_folder)
        )
        thread.daemon = True
        thread.start()
    
    def _process_batch_thread(self, input_folder, output_folder):
        """批量处理的后台线程"""
        try:
            self.update_status("正在批量处理图片...")
            
            processed_files, failed_files = batch_fix_white_background(
                input_folder,
                output_folder,
                color_tolerance=self.color_tolerance.get(),
                min_brightness=self.min_brightness.get(),
                use_smart_mode=self.use_smart_mode.get()
            )
            
            self.progress_var.set(100)
            
            # 显示统计信息
            message = f"批量处理完成！\n"
            message += f"成功处理: {len(processed_files)} 张图片\n"
            message += f"处理失败: {len(failed_files)} 张图片"
            
            if failed_files:
                message += "\n\n失败的文件:\n"
                for f in failed_files[:5]:  # 只显示前5个失败的文件
                    message += f"  {Path(f['file']).name}\n"
                if len(failed_files) > 5:
                    message += f"  ...还有 {len(failed_files)-5} 个文件失败"
            
            self.update_status(message)
            
            messagebox.showinfo("批量处理完成", message)
            
        except Exception as e:
            messagebox.showerror("批量处理错误", f"批量处理时出错:\n{str(e)}")
            self.update_status("批量处理失败")
        finally:
            self.processing = False
            self.progress_var.set(0)
    
    def create_comparison(self):
        """生成对比图"""
        input_path = self.input_path.get()
        
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("错误", "请先选择有效的输入文件")
            return
        
        # 临时处理图片以获取统计信息
        try:
            self.update_status("正在生成对比图...")
            
            # 使用临时文件处理
            temp_output = Path(input_path).parent / f"temp_comparison_{Path(input_path).name}"
            
            if self.use_smart_mode.get():
                result_img, stats = smart_fix_white_background(
                    input_path,
                    str(temp_output)
                )
            else:
                result_img, stats = fix_white_background(
                    input_path,
                    str(temp_output),
                    color_tolerance=self.color_tolerance.get(),
                    min_brightness=self.min_brightness.get(),
                    preserve_edges=self.preserve_edges.get()
                )
            
            # 生成对比图
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_path = Path(input_path).parent / f"comparison_{timestamp}.png"
            
            create_comparison_visualization(
                input_path,
                str(temp_output),
                stats,
                save_path=str(comparison_path)
            )
            
            # 删除临时文件
            if temp_output.exists():
                temp_output.unlink()
            
            self.update_status(f"对比图已保存: {comparison_path.name}")
            
            messagebox.showinfo("成功", f"对比图已保存到:\n{comparison_path}")
            
        except Exception as e:
            messagebox.showerror("生成对比图错误", f"生成对比图时出错:\n{str(e)}")
            self.update_status("生成对比图失败")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

# ============================================================
# 命令行接口
# ============================================================

def main_cli():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='白色背景染色修复工具')
    parser.add_argument('input', help='输入文件或文件夹路径')
    parser.add_argument('-o', '--output', help='输出文件或文件夹路径')
    parser.add_argument('-t', '--tolerance', type=int, default=15,
                       help='颜色容忍度 (默认: 15)')
    parser.add_argument('-b', '--brightness', type=int, default=220,
                       help='最小亮度阈值 (默认: 220)')
    parser.add_argument('--smart', action='store_true',
                       help='使用智能模式')
    parser.add_argument('--batch', action='store_true',
                       help='批量处理文件夹')
    parser.add_argument('--gui', action='store_true',
                       help='启动GUI界面')
    parser.add_argument('--visualize', action='store_true',
                       help='生成可视化对比图')
    
    args = parser.parse_args()
    
    if args.gui:
        # 启动GUI
        app = WhiteBackgroundFixerApp()
        app.run()
        return
    
    if args.batch:
        # 批量处理模式
        input_folder = args.input
        output_folder = args.output or f"fixed_{Path(input_folder).name}"
        
        print(f"批量处理: {input_folder}")
        print(f"输出到: {output_folder}")
        print(f"参数: 颜色容忍度={args.tolerance}, 最小亮度={args.brightness}")
        if args.smart:
            print("模式: 智能模式")
        
        processed, failed = batch_fix_white_background(
            input_folder,
            output_folder,
            color_tolerance=args.tolerance,
            min_brightness=args.brightness,
            use_smart_mode=args.smart
        )
        
        print(f"\n处理完成!")
        print(f"成功处理: {len(processed)} 张图片")
        print(f"处理失败: {len(failed)} 张图片")
        
    else:
        # 单文件处理模式
        input_path = args.input
        
        if not os.path.exists(input_path):
            print(f"错误: 文件不存在 - {input_path}")
            return
        
        if args.output:
            output_path = args.output
        else:
            # 自动生成输出文件名
            input_path_obj = Path(input_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = input_path_obj.parent / f"fixed_{timestamp}_{input_path_obj.name}"
            output_path = str(output_path)
        
        print(f"处理文件: {input_path}")
        print(f"输出到: {output_path}")
        print(f"参数: 颜色容忍度={args.tolerance}, 最小亮度={args.brightness}")
        if args.smart:
            print("模式: 智能模式")
        
        if args.smart:
            result_img, stats = smart_fix_white_background(
                input_path,
                output_path
            )
        else:
            result_img, stats = fix_white_background(
                input_path,
                output_path,
                color_tolerance=args.tolerance,
                min_brightness=args.brightness
            )
        
        print(f"\n处理完成!")
        print(f"修复像素: {stats['replaced_pixels']} ({stats['replaced_percentage']:.1f}%)")
        
        if args.visualize:
            # 生成可视化对比图
            comparison_path = Path(output_path).parent / f"comparison_{Path(output_path).stem}.png"
            create_comparison_visualization(
                input_path,
                output_path,
                stats,
                save_path=str(comparison_path)
            )
            print(f"对比图已保存: {comparison_path}")

# ============================================================
# 快速使用函数
# ============================================================

def quick_fix(input_path, output_path=None, color_tolerance=15, min_brightness=220):
    """
    快速修复白色背景
    
    示例:
        quick_fix("input.jpg", "output.png")
        quick_fix("input.jpg")  # 自动生成输出文件名
    """
    if output_path is None:
        input_path_obj = Path(input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = input_path_obj.parent / f"fixed_{timestamp}_{input_path_obj.name}"
        output_path = str(output_path)
    
    result_img, stats = fix_white_background(
        input_path,
        output_path,
        color_tolerance=color_tolerance,
        min_brightness=min_brightness
    )
    
    print(f"快速修复完成!")
    print(f"输出文件: {output_path}")
    print(f"修复像素: {stats['replaced_pixels']} ({stats['replaced_percentage']:.1f}%)")
    
    return result_img

# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        main_cli()
    else:
        # 如果没有命令行参数，启动GUI
        print("启动白色背景染色修复工具...")
        app = WhiteBackgroundFixerApp()
        app.run()