import cv2
import os
import sys

def convert_video_to_standard(input_path, output_path=None):
    """将视频转换为标准MP4格式，确保浏览器兼容"""
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_converted.mp4"

    cap = cv2.VideoCapture(input_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"输入视频: {input_path}")
    print(f"FPS: {fps}, 分辨率: {width}x{height}, 帧数: {frame_count}")

    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_num += 1
        if frame_num % 30 == 0:
            print(f"已处理 {frame_num}/{frame_count} 帧...")

    cap.release()
    out.release()

    print(f"转换完成: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_video = sys.argv[1]
        output_video = sys.argv[2] if len(sys.argv) > 2 else None
        convert_video_to_standard(input_video, output_video)
    else:
        print("用法: python convert_video.py <输入视频路径> [输出视频路径]")
