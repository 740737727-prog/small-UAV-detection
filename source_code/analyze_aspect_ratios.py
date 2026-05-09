import os
from PIL import Image
from collections import defaultdict

def get_image_resolutions(directory):
    resolutions = defaultdict(int)
    images_dir = os.path.join(directory, 'images')

    if not os.path.exists(images_dir):
        print(f"Directory not found: {images_dir}")
        return resolutions

    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            img_path = os.path.join(images_dir, filename)
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                    resolution = f"{width}x{height}"
                    resolutions[resolution] += 1
            except Exception as e:
                print(f"Error processing {img_path}: {e}")

    return resolutions

def main():
    base_path = r"E:\low attitude object dect\ultralytics-main"

    datasets = {
        'train': os.path.join(base_path, 'train'),
        'valid': os.path.join(base_path, 'valid'),
        'test': os.path.join(base_path, 'test')
    }

    for name, path in datasets.items():
        print(f"\n{'='*50}")
        print(f"{name.upper()} 数据集图片像素分辨率统计")
        print(f"{'='*50}")

        if not os.path.exists(path):
            print(f"路径不存在: {path}")
            continue

        resolutions = get_image_resolutions(path)

        if not resolutions:
            print("未找到图片文件")
            continue

        total = sum(resolutions.values())
        print(f"总图片数: {total}")
        print(f"\n像素分辨率 (宽x高) | 图片数量 | 占比")
        print("-" * 45)

        for resolution in sorted(resolutions.keys(), key=lambda x: (int(x.split('x')[0]), int(x.split('x')[1]))):
            count = resolutions[resolution]
            percentage = (count / total) * 100
            print(f"   {resolution}   |    {count:4d}    | {percentage:5.2f}%")

if __name__ == "__main__":
    main()