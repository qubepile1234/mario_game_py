from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import sys

def process_image_with_gray_replacement(input_path, output_path, 
                                       gray_tolerance=30, 
                                       dark_threshold=50,
                                       show_plot=True):
    """
    将接近灰色且较暗的像素替换为白色，并提供可视化比较
    """
    # 读取图像
    img = Image.open(input_path)
    original = img.copy()
    
    # 转换为RGBA（如果原始图像没有透明度，会添加不透明通道）
    img = img.convert('RGBA')
    data = np.array(img)
    
    # 分离通道
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
    # 计算亮度和颜色均匀度
    brightness = (r + g + b) / 3.0
    
    # 计算颜色标准差（用于判断是否接近灰色）
    # 对于灰色像素，RGB三个值应该非常接近
    color_std = np.std([r, g, b], axis=0)
    
    # 创建掩码：颜色接近灰色且较暗
    is_gray = color_std < gray_tolerance
    is_dark = brightness < dark_threshold
    mask = is_gray & is_dark
    
    # 应用白色替换（保留原始透明度）
    result = data.copy()
    result[mask, 0] = 255  # R
    result[mask, 1] = 255  # G
    result[mask, 2] = 255  # B
    # Alpha通道保持不变
    
    # 保存结果
    result_img = Image.fromarray(result, 'RGBA')
    result_img.save(output_path, 'PNG')
    
    # 如果显示图表
    if show_plot:
        # 创建可视化比较
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 原始图像
        axes[0, 0].imshow(original)
        axes[0, 0].set_title('原始图像')
        axes[0, 0].axis('off')
        
        # 处理后的图像
        axes[0, 1].imshow(result_img)
        axes[0, 1].set_title('处理后的图像')
        axes[0, 1].axis('off')
        
        # 亮度分布
        axes[0, 2].hist(brightness.flatten(), bins=50, color='gray', alpha=0.7)
        axes[0, 2].axvline(x=dark_threshold, color='r', linestyle='--', label=f'暗度阈值={dark_threshold}')
        axes[0, 2].set_title('亮度分布')
        axes[0, 2].set_xlabel('亮度')
        axes[0, 2].set_ylabel('像素数量')
        axes[0, 2].legend()
        
        # 颜色标准差分布
        axes[1, 0].hist(color_std.flatten(), bins=50, color='blue', alpha=0.7)
        axes[1, 0].axvline(x=gray_tolerance, color='r', linestyle='--', label=f'灰度容忍度={gray_tolerance}')
        axes[1, 0].set_title('颜色标准差分布')
        axes[1, 0].set_xlabel('颜色标准差')
        axes[1, 0].set_ylabel('像素数量')
        axes[1, 0].legend()
        
        # 被替换的像素（掩码可视化）
        axes[1, 1].imshow(mask, cmap='gray')
        axes[1, 1].set_title(f'被替换的像素区域\n（共{np.sum(mask)}个像素）')
        axes[1, 1].axis('off')
        
        # 差异对比
        diff = np.abs(result[:, :, :3].astype(np.float32) - data[:, :, :3].astype(np.float32))
        diff_sum = np.sum(diff, axis=2) / 3.0
        im_diff = axes[1, 2].imshow(diff_sum, cmap='hot')
        axes[1, 2].set_title('颜色差异热图')
        axes[1, 2].axis('off')
        plt.colorbar(im_diff, ax=axes[1, 2])
        
        plt.tight_layout()
        
        # 生成对比图文件名
        comparison_name = f"comparison_{Path(output_path).stem}.png"
        plt.savefig(comparison_name, dpi=150, bbox_inches='tight')
        print(f"对比图已保存为: {comparison_name}")
        
        if is_interactive():
            plt.show()
        else:
            plt.close()
    
    # 打印统计信息
    total_pixels = mask.size
    replaced_percentage = np.sum(mask) / total_pixels * 100
    
    print("\n处理完成！")
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"总像素数: {total_pixels}")
    print(f"替换像素数: {np.sum(mask)}")
    print(f"替换比例: {replaced_percentage:.2f}%")
    print(f"灰度容忍度: {gray_tolerance}")
    print(f"暗度阈值: {dark_threshold}")
    
    return result_img, mask

def batch_process_images(input_folder, output_folder, 
                        gray_tolerance=30, 
                        dark_threshold=50,
                        file_extensions=['.png', '.jpg', '.jpeg', '.bmp']):
    """
    批量处理文件夹中的图片
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    processed_files = []
    failed_files = []
    
    # 收集所有支持的图片文件
    image_files = []
    for ext in file_extensions:
        image_files.extend(list(input_path.glob(f'*{ext}')))
        image_files.extend(list(input_path.glob(f'*{ext.upper()}')))  # 大写扩展名
    
    if not image_files:
        print(f"在文件夹 {input_folder} 中没有找到支持的图片文件。")
        return []
    
    print(f"找到 {len(image_files)} 张图片需要处理。")
    
    for img_file in image_files:
        output_file = output_path / f"processed_{img_file.name}"
        
        try:
            # 单处理时不显示图表
            result, mask = process_image_with_gray_replacement(
                str(img_file),
                str(output_file),
                gray_tolerance,
                dark_threshold,
                show_plot=False
            )
            processed_files.append(str(img_file))
            print(f"✓ 成功处理: {img_file.name}")
            
        except Exception as e:
            failed_files.append((img_file.name, str(e)))
            print(f"✗ 处理失败 {img_file.name}: {e}")
    
    # 打印批量处理统计信息
    print(f"\n{'='*50}")
    print(f"批量处理完成！")
    print(f"成功处理: {len(processed_files)} 张图片")
    print(f"处理失败: {len(failed_files)} 张图片")
    
    if failed_files:
        print("\n失败的文件列表：")
        for file_name, error in failed_files:
            print(f"  {file_name}: {error}")
    
    return processed_files

def is_interactive():
    """检查是否在交互模式下运行"""
    return sys.stdout.isatty()

def get_user_input(prompt, default=None, input_type=str):
    """获取用户输入，支持默认值"""
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    user_input = input(full_prompt).strip()
    
    if not user_input and default is not None:
        return default
    
    if input_type == int:
        try:
            return int(user_input)
        except ValueError:
            print(f"请输入有效的整数！使用默认值: {default}")
            return default
    elif input_type == float:
        try:
            return float(user_input)
        except ValueError:
            print(f"请输入有效的数字！使用默认值: {default}")
            return default
    
    return user_input

def main():
    """主交互函数"""
    print("=" * 60)
    print("图片灰度区域替换工具")
    print("=" * 60)
    print("功能：将接近灰色且较暗的像素替换为纯白色")
    print("=" * 60)
    
    # 选择处理模式
    print("\n请选择处理模式：")
    print("1. 单张图片处理")
    print("2. 批量图片处理（文件夹）")
    print("3. 退出")
    
    mode_choice = get_user_input("请输入选择(1-3)", "1", int)
    
    if mode_choice == 3:
        print("程序已退出。")
        return
    
    # 获取处理参数
    print("\n设置处理参数：")
    gray_tolerance = get_user_input("灰度容忍度 (默认: 30)", 30, int)
    dark_threshold = get_user_input("暗度阈值 (默认: 50)", 50, int)
    
    if mode_choice == 1:
        # 单张图片处理
        print("\n单张图片处理模式")
        print("-" * 40)
        
        # 获取输入图片路径
        while True:
            input_path = get_user_input("请输入输入图片路径")
            if os.path.exists(input_path):
                break
            print(f"错误：文件 '{input_path}' 不存在，请重新输入。")
        
        # 获取输出图片路径
        default_output = str(Path(input_path).parent / f"processed_{Path(input_path).name}")
        output_path = get_user_input("请输入输出图片路径", default_output)
        
        # 创建输出目录（如果需要）
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 处理图片
        try:
            print("\n开始处理图片...")
            result, mask = process_image_with_gray_replacement(
                input_path, 
                output_path,
                gray_tolerance=gray_tolerance,
                dark_threshold=dark_threshold,
                show_plot=True
            )
            
            print(f"\n单张图片处理完成！")
            print(f"输出文件: {output_path}")
            
        except Exception as e:
            print(f"\n处理图片时出错: {e}")
            import traceback
            traceback.print_exc()
    
    elif mode_choice == 2:
        # 批量图片处理
        print("\n批量图片处理模式")
        print("-" * 40)
        
        # 获取输入文件夹路径
        while True:
            input_folder = get_user_input("请输入输入文件夹路径")
            if os.path.exists(input_folder) and os.path.isdir(input_folder):
                break
            print(f"错误：文件夹 '{input_folder}' 不存在，请重新输入。")
        
        # 获取输出文件夹路径
        default_output = str(Path(input_folder).parent / f"processed_{Path(input_folder).name}")
        output_folder = get_user_input("请输入输出文件夹路径", default_output)
        
        # 确认是否开始处理
        print(f"\n即将开始批量处理：")
        print(f"输入文件夹: {input_folder}")
        print(f"输出文件夹: {output_folder}")
        print(f"灰度容忍度: {gray_tolerance}")
        print(f"暗度阈值: {dark_threshold}")
        
        confirm = get_user_input("是否开始处理？(y/n)", "y")
        
        if confirm.lower() in ['y', 'yes', '是']:
            try:
                print("\n开始批量处理...")
                processed_files = batch_process_images(
                    input_folder, 
                    output_folder,
                    gray_tolerance=gray_tolerance,
                    dark_threshold=dark_threshold
                )
                
                if processed_files:
                    print(f"\n批量处理完成！")
                    print(f"输出文件夹: {output_folder}")
                    print(f"共处理 {len(processed_files)} 张图片")
            except Exception as e:
                print(f"\n批量处理时出错: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("批量处理已取消。")
    
    # 询问是否继续
    print("\n" + "=" * 60)
    continue_choice = get_user_input("是否继续处理其他图片？(y/n)", "n")
    
    if continue_choice.lower() in ['y', 'yes', '是']:
        main()
    else:
        print("感谢使用，程序已退出。")

def quick_start():
    """快速启动函数，可以直接调用处理单张图片"""
    # 示例：快速处理单张图片
    input_img = "your_image.png"  # 替换为实际图片路径
    output_img = "result.png"
    
    # 调整参数以获得最佳效果
    result, mask = process_image_with_gray_replacement(
        input_img, 
        output_img,
        gray_tolerance=25,
        dark_threshold=40
    )
    
    return result, mask

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 等待用户按回车键退出（在非交互模式下）
    if not is_interactive():
        input("\n按回车键退出...")