import cv2
import os


def extract_frames_from_videos(video_folder, output_folder):
    """
    批量读取视频文件，并将每一帧保存为图片。

    :param video_folder: 包含视频文件的文件夹路径
    :param output_folder: 保存帧图片的根文件夹路径
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    files_count= 1
    # 遍历视频文件夹中的所有文件
    for video_filename in os.listdir(video_folder):
        video_path = os.path.join(video_folder, video_filename)
        # 检查是否为视频文件（可以根据需要扩展支持更多格式）
        if not video_filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            print(f"Skipping non-video file: {video_filename}")
            continue


        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video file: {video_filename}")
            continue

        print(f"Processing video: {video_filename}")

        frame_count = 1
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # 读取结束

            # 保存帧图片
            frame_path = os.path.join(output_folder, f"V_BIRD_{files_count:03d}1_{frame_count:04d}.png")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

        cap.release()
        print(f"Saved {frame_count} frames to {output_folder}")
        files_count += 1
    print("All videos processed.")


# 示例用法
if __name__ == "__main__":
    video_folder = "C:/data/video"  # 替换为包含视频文件的文件夹路径
    output_folder = "D:\BaiduNetdiskDownload\Drone-detection-dataset-master\Data\image1"  # 替换为保存帧图片的目标文件夹路径
    extract_frames_from_videos(video_folder, output_folder)