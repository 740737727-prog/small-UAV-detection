import matplotlib.pyplot as plt
from PIL import Image

def merge_images(image_path1, image_path2, output_path):
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    axes[0].imshow(img1)
    axes[0].set_title('base_model', fontsize=14)
    axes[0].axis('off')
    
    axes[1].imshow(img2)
    axes[1].set_title('improve_model', fontsize=14)
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()
    print(f"合并后的图片已保存: {output_path}")

if __name__ == '__main__':
    image_path1 = r'E:\wyf低空目标检测\ultralytics-main\model\PR_curve.png'
    image_path2 = r'E:\wyf低空目标检测\ultralytics-main\model\PR_curve2.png'
    output_path = r'E:\wyf低空目标检测\ultralytics-main\model\pr_curve_comparison_combined.png'
    
    merge_images(image_path1, image_path2, output_path)
