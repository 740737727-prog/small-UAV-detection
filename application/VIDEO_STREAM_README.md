# 视频跳帧检测功能说明

## 功能概述

新增的视频跳帧检测功能实现了高效的视频目标检测，通过跳帧检测和帧插值技术，在保持检测精度的同时大幅降低了CPU占用。

## 主要特性

1. **跳帧检测**：每100ms（可配置）执行一次YOLO推理
2. **帧插值**：非推理帧复用上一帧检测结果，保持视觉连续性
3. **实时视频流**：使用MJPEG流式传输到前端
4. **动态检测间隔**：用户可自定义检测间隔（10-1000ms）

## 使用方法

### 1. 启动系统

```bash
cd app
conda activate YOLO-GPU
python app.py
```

或者直接运行：
```bash
cd app
start.bat
```

### 2. 上传视频

1. 在浏览器中访问 `http://localhost:5000`
2. 登录或注册账户
3. 点击"选择文件"按钮，选择一个视频文件（支持.mp4, .avi, .mov, .mkv格式）

### 3. 配置检测参数

在开始检测前，可以调整：
- **检测间隔**：默认为100ms，范围10-1000ms
  - 较小值：检测更频繁，但CPU占用更高
  - 较大值：CPU占用更低，但检测延迟更高
- **模型选择**：可在model1和model2之间切换

### 4. 开始检测

点击"开始检测"按钮，系统会：
1. 上传视频到服务器
2. 启动视频处理线程
3. 通过MJPEG流实时播放带检测框的视频
4. 实时更新检测结果到右侧面板

## 技术实现

### 后端（model_manager.py）

```python
# 核心方法：process_video_stream
def process_video_stream(self, video_path, detect_interval_ms=100, enable_interpolation=True):
    # 记录上次推理时间
    last_detect_time = 0
    
    for each frame in video:
        current_time = now()
        
        # 检查是否需要推理
        if current_time - last_detect_time >= detect_interval_ms:
            # 执行YOLO推理
            results = model(frame)
            detections = process_results(results)
            last_detect_time = current_time
        else:
            # 复用上一帧检测结果
            detections = last_detections.copy()
        
        # 在每一帧上画框
        processed_frame = draw_boxes(frame, detections)
        yield processed_frame, detections
```

### 视频流管理器（app.py）

- 使用多线程处理视频，避免阻塞主进程
- 队列缓存处理好的帧，确保流畅播放
- 线程安全的数据访问，防止并发问题

### 前端（main.js）

- MJPEG流实时显示
- 定时轮询更新检测结果
- 页面卸载时自动清理资源

## 文件修改

### 新增文件

无

### 修改文件

1. `app/model_manager.py` - 添加视频跳帧检测功能
2. `app/app.py` - 添加视频流API和管理器
3. `app/templates/monitor.html` - 添加检测间隔配置和视频流显示
4. `app/static/js/main.js` - 添加视频流处理逻辑

## 性能优化建议

1. **检测间隔**：
   - 对于快速移动目标，建议使用50-100ms
   - 对于慢速目标，可以使用150-200ms
   
2. **模型选择**：
   - model1（标准YOLOv8）：速度快，适合实时检测
   - model2（带SPD模块）：精度高，但推理时间更长

3. **硬件**：
   - 建议使用GPU加速（本项目已配置YOLO-GPU环境）
   - CPU模式下建议增加检测间隔到200-300ms

## 故障排除

### 问题：视频流卡顿

- **解决方案**：增加检测间隔，降低帧率
- **检查**：服务器CPU占用率，如过高则减少检测频率

### 问题：检测框延迟

- **解决方案**：减小检测间隔
- **注意**：这会增加CPU占用

### 问题：无法启动视频流

- **检查**：确保已激活YOLO-GPU环境
- **检查**：视频文件格式是否支持
- **查看**：服务器控制台错误日志

## 下一步改进

1. 实现真正的帧间插值（线性插值检测框位置）
2. 添加视频暂停/继续功能
3. 支持多个视频同时处理
4. 添加检测统计信息（FPS、检测数量等）
5. 优化内存使用，避免长时间处理内存泄漏
