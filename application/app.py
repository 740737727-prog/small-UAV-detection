import sys
import os
import cv2
import threading
import queue
import time
from collections import defaultdict

# 首先注册SPD模块
sys.path.insert(0, os.path.dirname(__file__))
import register_spd
register_spd.register_spd_module()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, Response
from functools import wraps
import uuid
from database import Database
from model_manager import ModelManager

app = Flask(__name__)
app.secret_key = 'drone_monitor_secret_key_123'

# 确保MP4视频文件的MIME类型映射
import mimetypes
mimetypes.add_type('video/mp4', '.mp4')

db = Database()
model_manager = ModelManager()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
CROPS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'crops')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPS_FOLDER, exist_ok=True)

# 视频流管理器
class VideoStreamManager:
    def __init__(self):
        self.streams = {}
        self.lock = threading.Lock()
    
    def start_stream(self, video_id, video_path, detect_interval_ms=100):
        with self.lock:
            if video_id in self.streams:
                self.stop_stream(video_id)
            
            self.streams[video_id] = {
                'frame_queue': queue.Queue(maxsize=10),
                'current_frame': None,
                'detections': [],
                'running': True,
                'video_path': video_path
            }
            
            thread = threading.Thread(target=self._process_stream, 
                                     args=(video_id, video_path, detect_interval_ms))
            thread.daemon = True
            thread.start()
    
    def _process_stream(self, video_id, video_path, detect_interval_ms):
        for frame, detections in model_manager.process_video_stream(video_path, detect_interval_ms):
            with self.lock:
                if video_id not in self.streams or not self.streams[video_id]['running']:
                    break
                
                self.streams[video_id]['current_frame'] = frame.copy()
                self.streams[video_id]['detections'] = detections
                
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    try:
                        if self.streams[video_id]['frame_queue'].full():
                            self.streams[video_id]['frame_queue'].get_nowait()
                        self.streams[video_id]['frame_queue'].put_nowait(frame_bytes)
                    except:
                        pass
    
    def get_frame(self, video_id):
        with self.lock:
            if video_id not in self.streams:
                return None
            try:
                return self.streams[video_id]['frame_queue'].get(timeout=1.0)
            except:
                return None
    
    def get_detections(self, video_id):
        with self.lock:
            if video_id in self.streams:
                return self.streams[video_id]['detections']
            return []
    
    def get_current_frame_with_detections(self, video_id):
        with self.lock:
            if video_id not in self.streams:
                return None, []
            return self.streams[video_id]['current_frame'], self.streams[video_id]['detections'].copy()
    
    def stop_stream(self, video_id):
        with self.lock:
            if video_id in self.streams:
                self.streams[video_id]['running'] = False
                del self.streams[video_id]

stream_manager = VideoStreamManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if not db.has_admin():
        return redirect(url_for('register'))
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('monitor'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if db.has_admin():
        if 'user_id' in session:
            return redirect(url_for('monitor'))
        else:
            return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            if db.create_user(username, password):
                return redirect(url_for('login'))
            else:
                return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not db.has_admin():
        return redirect(url_for('register'))
    if 'user_id' in session:
        return redirect(url_for('monitor'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = db.verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('monitor'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/monitor')
@login_required
def monitor():
    user = db.get_user(session['user_id'])
    return render_template('monitor.html', 
                         user=user,
                         current_model=model_manager.get_current_model(),
                         available_models=model_manager.get_available_models())

@app.route('/api/models', methods=['GET'])
@login_required
def get_models():
    return jsonify({
        'current': model_manager.get_current_model(),
        'available': model_manager.get_available_models()
    })

@app.route('/video/<filename>')
@login_required
def serve_video(filename):
    """专门的视频服务路由，确保正确的MIME类型"""
    return send_from_directory(UPLOAD_FOLDER, filename, mimetype='video/mp4')

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No filename'}), 400
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    # 视频文件用专门的视频服务路由
    if ext.lower() in ['.mp4', '.webm', '.ogg', '.avi']:
        file_url = url_for('serve_video', filename=unique_filename)
    else:
        file_url = url_for('static', filename=f'uploads/{unique_filename}')
    
    return jsonify({'success': True, 'url': file_url, 'filename': unique_filename})

@app.route('/api/switch_model', methods=['POST'])
@login_required
def switch_model():
    model_name = request.json.get('model_name')
    if model_manager.switch_model(model_name):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid model name'})

@app.route('/api/detect', methods=['POST'])
@login_required
def detect():
    # 检查是否是已上传的文件
    uploaded_filename = request.form.get('filename')
    
    if uploaded_filename:
        # 使用已上传的文件
        filename = uploaded_filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
    else:
        # 新上传文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
    
    file_ext = os.path.splitext(filename)[1].lower()
    is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv']
    
    try:
        if is_video:
            # 视频处理：获取第一帧进行初始检测
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return jsonify({'success': False, 'error': 'Cannot read video'})
            
            first_frame_path = os.path.join(UPLOAD_FOLDER, f"first_{filename}.jpg")
            cv2.imwrite(first_frame_path, frame)
            cap.release()
            
            # 对第一帧进行检测
            first_dets = model_manager.predict_image(first_frame_path)
            result_image = os.path.join(UPLOAD_FOLDER, f"result_{filename}.jpg")
            model_manager.draw_detections(first_frame_path, first_dets, result_image)
            
            cropped_images = []
            for det in first_dets:
                crop_filename = model_manager.crop_detection(first_frame_path, det['bbox'], CROPS_FOLDER)
                cropped_images.append({
                    'bbox': det['bbox'],
                    'confidence': det['confidence'],
                    'crop': crop_filename
                })
            
            return jsonify({
                'success': True,
                'type': 'video',
                'original': filename,
                'result': f"result_{filename}.jpg",
                'first_frame': f"first_{filename}.jpg",
                'detections': cropped_images
            })
        else:
            detections = model_manager.predict_image(filepath)
            result_filename = f"result_{filename}"
            result_path = os.path.join(UPLOAD_FOLDER, result_filename)
            model_manager.draw_detections(filepath, detections, result_path)
            
            cropped_images = []
            for det in detections:
                crop_filename = model_manager.crop_detection(filepath, det['bbox'], CROPS_FOLDER)
                cropped_images.append({
                    'bbox': det['bbox'],
                    'confidence': det['confidence'],
                    'crop': crop_filename
                })
            
            return jsonify({
                'success': True,
                'type': 'image',
                'original': filename,
                'result': result_filename,
                'detections': cropped_images
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/crops/<filename>')
def crop_file(filename):
    return send_from_directory(CROPS_FOLDER, filename)

# 视频流相关API
@app.route('/api/video/start', methods=['POST'])
@login_required
def start_video_stream():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    video_id = request.json.get('video_id')
    filename = request.json.get('filename')
    detect_interval = request.json.get('detect_interval', 100)
    
    if not video_id or not filename:
        return jsonify({'success': False, 'error': 'Missing parameters'})
    
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(video_path):
        return jsonify({'success': False, 'error': 'Video file not found'})
    
    stream_manager.stop_stream(video_id)
    stream_manager.start_stream(video_id, video_path, detect_interval)
    return jsonify({'success': True})

@app.route('/api/video/frame/<video_id>')
@login_required
def get_video_frame_with_detections(video_id):
    """获取当前帧和检测结果，包括裁剪图"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    frame, detections = stream_manager.get_current_frame_with_detections(video_id)
    
    if frame is None:
        return jsonify({'success': False, 'error': 'Video stream not found'})
    
    # resize到640*640
    if frame.shape[0] != 640 or frame.shape[1] != 640:
        frame_resized = cv2.resize(frame, (640, 640))
        scale_x = 640 / frame.shape[1]
        scale_y = 640 / frame.shape[0]
    else:
        frame_resized = frame.copy()
        scale_x = 1.0
        scale_y = 1.0
    
    # 在帧上画检测框
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
        cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"Drone {det['confidence']:.2f}"
        cv2.putText(frame_resized, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # 保存处理后的帧图片
    frame_filename = f"frame_{uuid.uuid4().hex}.jpg"
    frame_path = os.path.join(UPLOAD_FOLDER, frame_filename)
    cv2.imwrite(frame_path, frame_resized)
    
    # 生成裁剪图（放大无人机以便清晰显示）
    cropped_images = []
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
        
        # 稍微放大裁剪框，让无人机更清晰
        pad = 20
        h, w = frame_resized.shape[:2]
        x1_pad = max(0, x1 - pad)
        y1_pad = max(0, y1 - pad)
        x2_pad = min(w, x2 + pad)
        y2_pad = min(h, y2 + pad)
        
        crop = frame_resized[y1_pad:y2_pad, x1_pad:x2_pad]
        if crop.size > 0:
            crop_resized = cv2.resize(crop, (640, 640))
            crop_filename = f"stream_crop_{uuid.uuid4().hex}.jpg"
            crop_path = os.path.join(CROPS_FOLDER, crop_filename)
            cv2.imwrite(crop_path, crop_resized)
            cropped_images.append({
                'bbox': [int(x1/scale_x), int(y1/scale_y), int(x2/scale_x), int(y2/scale_y)],
                'confidence': det['confidence'],
                'crop': crop_filename
            })
    
    return jsonify({
        'success': True,
        'frame': frame_filename,
        'detections': cropped_images
    })

@app.route('/api/video/stream/<video_id>')
@login_required
def video_stream(video_id):
    if 'user_id' not in session:
        return '', 403
    
    def generate():
        while True:
            frame = stream_manager.get_frame(video_id)
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/video/detections/<video_id>')
@login_required
def get_video_detections(video_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    detections = stream_manager.get_detections(video_id)
    
    cropped_images = []
    for det in detections:
        cropped_images.append({
            'bbox': det['bbox'],
            'confidence': det['confidence'],
            'crop': None
        })
    
    return jsonify({
        'success': True,
        'detections': cropped_images
    })

@app.route('/api/video/stop/<video_id>', methods=['POST'])
@login_required
def stop_video_stream(video_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    stream_manager.stop_stream(video_id)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)