import pandas as pd
import matplotlib.pyplot as plt

lambda_box = 7.5
lambda_cls = 0.5
lambda_dfl = 1.5

def calculate_total_loss(df):
    df['train/total_loss'] = lambda_box * df['train/box_loss'] + lambda_cls * df['train/cls_loss'] + lambda_dfl * df['train/dfl_loss']
    df['val/total_loss'] = lambda_box * df['val/box_loss'] + lambda_cls * df['val/cls_loss'] + lambda_dfl * df['val/dfl_loss']
    return df

def plot_loss_curves(csv_file, title, output_file):
    df = pd.read_csv(csv_file)
    df = calculate_total_loss(df)
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(df['epoch'], df['train/total_loss'], label='train_loss', color='blue', linewidth=2)
    plt.plot(df['epoch'], df['val/total_loss'], label='val_loss', color='red', linewidth=2)
    
    plt.xlabel('Epoch')
    plt.ylabel('Total Loss')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    
    plt.savefig(output_file, dpi=150)
    plt.show()
    
    print(f"{title}")
    print(f"  Final Train Loss: {df['train/total_loss'].iloc[-1]:.4f}")
    print(f"  Final Val Loss: {df['val/total_loss'].iloc[-1]:.4f}")

if __name__ == '__main__':
    csv_file1 = r'E:/wyf低空目标检测/ultralytics-main/model/results.csv'
    csv_file2 = r'E:/wyf低空目标检测/ultralytics-main/model/results2.csv'
    
    plot_loss_curves(csv_file1, 'Base Model - Total Loss', 'base_model_loss.png')
    plot_loss_curves(csv_file2, 'Improve Model - Total Loss', 'improve_model_loss.png')
    
    print("\n图片已保存: base_model_loss.png, improve_model_loss.png")
