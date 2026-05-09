# 无人机实时监控系统

## 项目简介

这是一个基于YOLOv8目标检测算法的无人机实时监控Web应用系统。该系统支持用户认证、图片/视频上传、实时目标检测、模型切换等功能，为无人机安全监控提供了完整的解决方案。

## 功能特性

### 1. 用户认证与权限管理
- 用户注册功能（首次使用时注册管理员账户）
- 用户登录/登出功能
- 基于Session的身份验证
- SQLite数据库存储用户信息

### 2. 监控面板功能
- **文件上传**：支持上传本地图片和视频文件
- **预览功能**：支持实时预览上传的图片和视频
- **开始检测**：一键启动目标检测
- **模型切换**：支持在多个预训练模型之间切换
- **检测间隔设置**：可自定义视频检测的时间间隔（毫秒）
- **摄像头占位**：无文件时显示"摄像头1"占位符

### 3. 检测功能
- **图片检测**：对单张图片进行无人机目标检测
- **视频检测**：对视频进行实时流式检测
- **跳帧检测**：为提高效率，支持按时间间隔进行检测
- **检测结果展示**：在原图上标注检测框和置信度

### 4. 结果展示
- **检测结果轮播**：以轮播图形式展示最新检测结果
- **检测目标列表**：右侧显示检测到的无人机信息（位置、置信度、时间）
- **历史记录**：所有检测结果保存在历史下拉列表中
- **详情查看**：点击历史记录可查看详细信息

### 5. 视频流处理
- **实时视频流**：通过MJPEG流推送检测结果
- **线程安全**：使用线程安全的队列管理视频流
- **断点续传**：支持视频流的启动和停止

## 技术架构

### 后端技术栈
- **Web框架**：Flask
- **目标检测**：YOLOv8 (Ultralytics)
- **数据库**：SQLite3
- **视频处理**：OpenCV
- **图像处理**：PIL (Pillow)

### 前端技术栈
- **UI框架**：Bootstrap 5
- **交互逻辑**：原生JavaScript
- **轮播组件**：Bootstrap Carousel

## 项目结构

```
app/
├── app.py                  # Flask主应用入口
├── model_manager.py        # 模型管理和视频处理模块
├── database.py            # 数据库操作模块
├── register_spd.py        # SPD模块注册（解决模型加载问题）
├── requirements.txt       # Python依赖包
├── start.bat             # Windows启动脚本
├── static/
│   ├── css/
│   │   └── style.css     # 自定义样式
│   ├── js/
│   │   └── main.js       # 前端交互逻辑
│   ├── uploads/          # 上传文件存储
│   └── crops/            # 裁剪目标存储
├── templates/
│   ├── login.html        # 登录页面
│   ├── register.html     # 注册页面
│   └── monitor.html      # 主监控页面
└── README.md             # 项目文档
```

## 安装部署

### 环境要求
- Python 3.9+
- Windows操作系统
- CUDA支持（可选，用于GPU加速）

### 安装步骤

1. **克隆项目**
```bash
cd app
```

2. **创建虚拟环境**（推荐）
```bash
python -m venv venv
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **准备模型文件**
   - 将预训练的YOLOv8模型文件放置在指定位置（参照model_manager.py中的路径配置）
   - 确保model1和model2的权重文件存在

5. **启动应用**
```bash
python app.py
```
或直接运行启动脚本：
```bash
start.bat
```

6. **访问应用**
打开浏览器访问：http://localhost:5000

## 使用指南

### 首次使用
1. 访问系统会自动跳转到注册页面
2. 填写用户名和密码注册管理员账户
3. 注册成功后自动跳转到登录页面
4. 使用注册的账户登录

### 图片检测流程
1. 点击文件输入框，选择本地图片
2. 预览选中的图片
3. 点击"开始检测"按钮
4. 查看下方的检测结果和右侧的检测目标列表

### 视频检测流程
1. 点击文件输入框，选择本地视频
2. 预览视频，可以先播放查看
3. 设置检测间隔（默认100ms）
4. 点击"开始检测"按钮
5. 系统会以视频流形式展示检测结果

### 模型切换
1. 在监控面板顶部的下拉框中选择模型
2. 点击"切换模型"按钮
3. 系统会使用新模型进行后续检测

## API接口文档

### 用户认证
- `GET /register` - 注册页面
- `POST /register` - 提交注册信息
- `GET /login` - 登录页面
- `POST /login` - 提交登录信息
- `GET /logout` - 登出

### 监控页面
- `GET /monitor` - 主监控页面

### 文件操作
- `POST /api/upload` - 上传文件
- `GET /uploads/<filename>` - 获取上传的文件
- `GET /crops/<filename>` - 获取裁剪的目标图片

### 检测接口
- `POST /api/detect` - 执行检测
- `POST /api/switch_model` - 切换模型

### 视频流接口
- `POST /api/video/start` - 启动视频流
- `GET /api/video/stream/<video_id>` - 获取视频流
- `GET /api/video/frame/<video_id>` - 获取当前帧和检测结果
- `POST /api/video/stop/<video_id>` - 停止视频流

## 核心模块说明

### ModelManager类 (model_manager.py)
负责模型的加载、推理和视频处理：
- `predict_image()` - 单张图片预测
- `process_video_stream()` - 视频流处理，支持跳帧检测
- `crop_detection_from_frame()` - 从帧中裁剪检测目标
- `draw_detections()` - 在图片上绘制检测框

### Database类 (database.py)
负责用户数据管理：
- `create_user()` - 创建用户
- `verify_user()` - 验证用户
- `has_admin()` - 检查是否已存在管理员

### VideoStreamManager类 (app.py)
负责视频流管理：
- `start_stream()` - 启动视频流
- `get_frame()` - 获取视频帧
- `stop_stream()` - 停止视频流

## 注意事项

1. **模型路径**：请确保model_manager.py中配置的模型路径正确
2. **文件大小**：建议上传的视频文件不要过大，以确保流畅性
3. **检测间隔**：检测间隔越小，CPU/GPU占用越高，可根据设备性能调整
4. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Edge）

## 开发计划

- [ ] 支持多路摄像头同时监控
- [ ] 添加检测结果导出功能
- [ ] 支持实时RTSP流输入
- [ ] 添加更多检测类别
- [ ] 优化视频流性能
- [ ] 添加告警功能

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系项目维护者。
