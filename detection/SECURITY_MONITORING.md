# Real-Time Security Monitoring Module - Documentation

## 🔒 Overview

The security monitoring module extends the object detection feature with real-time video surveillance capabilities. It captures live video from webcams or IP cameras, runs YOLOv5 object detection on each frame, and automatically logs security events.

## ✨ Key Features

### 1. **Live Video Streaming**
- Captures video from webcam or IP camera
- Real-time MJPEG streaming to web browser
- Configurable camera source selection

### 2. **Intelligent Object Detection**
- Detects specific security-relevant classes: `person`, `car`, `dog`, `cat`, `truck`, `motorcycle`
- Adjustable confidence threshold
- Frame-by-frame YOLOv5 inference
- Color-coded bounding boxes for different object types

### 3. **Automatic Event Logging**
- Timestamps all detections
- Saves detection data in JSON format
- Maintains rolling log (last 1000 events)
- Includes object class, confidence, and coordinates

### 4. **Auto-Snapshot on Person Detection**
- Automatically saves image when person detected
- Annotated images with bounding boxes
- Organized in `media/security/snapshots/`
- Filenames include timestamp and detected classes

### 5. **Live Dashboard**
- Real-time statistics display
- Current detection count
- Total persons detected
- Streaming video feed with annotations
- Live detection list with confidence scores

---

## 📁 File Structure

```
detection/
├── object_detector.py          # Enhanced with SecurityCamera class
├── views.py                    # Added 6 new security monitoring views
├── urls.py                     # Added 6 new security endpoints
└── templates/detection/
    ├── security_monitor.html   # Live monitoring dashboard
    └── security_logs.html      # Historical logs viewer

media/
└── security/
    ├── snapshots/             # Auto-saved security snapshots
    └── detection_log.json     # Detection event log
```

---

## 🚀 Usage Guide

### Accessing the Security Monitor

1. **Navigate to Security Monitor:**
   ```
   http://127.0.0.1:8000/detection/security/
   ```

2. **Select Camera Source:**
   - Default Webcam (0)
   - Alternative webcam (1, 2, etc.)
   - IP Camera URL (e.g., `rtsp://...`)

3. **Configure Target Classes:**
   - Select which object types to detect
   - Multiple selection supported
   - Default: person, car, dog, cat, truck, motorcycle

4. **Start Monitoring:**
   - Click "Start Monitoring" button
   - Camera activates and video feed begins
   - Detections appear in real-time

5. **View Live Detections:**
   - Statistics panel shows counts
   - Detection list updates every second
   - Annotated video stream shows bounding boxes

6. **Stop Monitoring:**
   - Click "Stop Monitoring" button
   - Camera releases gracefully
   - Data preserved in logs

---

## 🔧 Technical Implementation

### Core Components

#### 1. **SecurityCamera Class** (`object_detector.py`)

**Purpose:** Manages camera capture, detection processing, and event logging

**Key Methods:**

```python
# Initialize security camera
def __init__(self, camera_source=0, detector=None, target_classes=None, 
             snapshot_dir='media/security/snapshots', 
             log_file='media/security/detection_log.json')
```
- **camera_source:** Camera index or IP URL
- **detector:** Pre-loaded YOLOv5 detector
- **target_classes:** List of classes to detect
- **snapshot_dir:** Where to save snapshots
- **log_file:** JSON log file path

```python
# Connect to camera
def connect_camera(self)
```
- Opens video capture device
- Sets frame size (640x480) and FPS (30)
- Returns True if successful

```python
# Detect objects in single frame
def detect_frame(self, frame)
```
- Runs YOLOv5 on frame
- Filters by target classes
- Returns detections with timestamps

```python
# Draw bounding boxes on frame
def annotate_frame(self, frame, detections)
```
- Color-codes by object class
- Thicker boxes for persons (priority)
- Adds timestamp overlay
- Shows detection count

```python
# Save snapshot when event occurs
def save_snapshot(self, frame, detections)
```
- Generates filename with timestamp
- Includes detected class names
- Saves to snapshots directory
- Returns file path

```python
# Log detection to JSON file
def log_detection(self, detections, snapshot_path=None)
```
- Creates structured log entry
- Appends to JSON log file
- Maintains last 1000 entries
- Includes all detection metadata

```python
# Main processing pipeline
def process_frame(self, frame)
```
- Detects objects
- Annotates frame
- Auto-saves if person detected
- Logs all events
- Thread-safe frame updates

```python
# Start monitoring in background thread
def start_monitoring_thread(self)
```
- Connects camera
- Starts processing loop
- Non-blocking (daemon thread)
- Returns success status

```python
# Stop monitoring gracefully
def stop_monitoring(self)
```
- Sets stop flag
- Waits for thread completion
- Releases camera resources

---

#### 2. **Django Views** (`views.py`)

**Six new views added:**

##### `security_monitor(request)` - Dashboard Page
```python
@login_required
def security_monitor(request):
```
- Renders main monitoring interface
- Provides camera controls
- Shows live statistics
- **Template:** `security_monitor.html`

##### `start_security_camera(request)` - Start API
```python
@login_required
@require_http_methods(["POST"])
def start_security_camera(request):
```
- **POST Parameters:**
  - `camera_source`: Camera index or URL
  - `target_classes`: JSON array of classes
- Initializes SecurityCamera instance
- Starts background monitoring thread
- **Returns:** JSON with status

##### `stop_security_camera(request)` - Stop API
```python
@login_required
@require_http_methods(["POST"])
def stop_security_camera(request):
```
- Stops active monitoring
- Releases camera resources
- **Returns:** JSON with status

##### `video_feed(request)` - Video Stream
```python
@login_required
def video_feed(request):
```
- Streams MJPEG video
- Uses generator function
- Serves annotated frames
- **Content-Type:** `multipart/x-mixed-replace`

##### `get_detections_data(request)` - Detection API
```python
@login_required
def get_detections_data(request):
```
- Returns current detections
- Includes statistics
- **Returns:** JSON with:
  - `detections`: List of current objects
  - `count`: Current frame count
  - `total_detections`: Cumulative total
  - `person_count`: Total persons detected

##### `security_logs(request)` - Logs Viewer
```python
@login_required
def security_logs(request):
```
- Reads detection log file
- Displays last 100 events
- Shows timestamps, classes, snapshots
- **Template:** `security_logs.html`

---

#### 3. **URL Endpoints** (`urls.py`)

```python
# Security monitoring endpoints
path('security/', views.security_monitor, name='security_monitor'),
path('security/start/', views.start_security_camera, name='start_camera'),
path('security/stop/', views.stop_security_camera, name='stop_camera'),
path('security/feed/', views.video_feed, name='video_feed'),
path('security/detections/', views.get_detections_data, name='get_detections'),
path('security/logs/', views.security_logs, name='security_logs'),
```

---

## 📊 Data Structures

### Detection Object
```json
{
  "class": "person",
  "confidence": 0.89,
  "bbox": {
    "xmin": 120,
    "ymin": 80,
    "xmax": 340,
    "ymax": 450
  },
  "timestamp": "2025-10-29T15:30:45.123456"
}
```

### Log Entry
```json
{
  "timestamp": "2025-10-29T15:30:45.123456",
  "detection_count": 2,
  "detections": [
    {
      "class": "person",
      "confidence": 0.89,
      "bbox": {...}
    },
    {
      "class": "car",
      "confidence": 0.76,
      "bbox": {...}
    }
  ],
  "snapshot": "media/security/snapshots/snapshot_20251029_153045_person_car.jpg",
  "camera_source": "0"
}
```

---

## 🎨 Frontend Features

### Live Dashboard (`security_monitor.html`)

**Components:**
1. **Video Container:** Displays live annotated feed
2. **Control Panel:** Camera selection and start/stop
3. **Statistics Cards:**
   - Current detections
   - Total persons detected
   - Total detections
4. **Live Detections List:** Real-time object list
5. **Status Indicator:** Animated pulse when active

**JavaScript Features:**
- Auto-polling detection API (1 second intervals)
- Dynamic UI updates
- MJPEG streaming integration
- Graceful cleanup on page unload

---

## 🔐 Security Considerations

1. **Authentication Required:** All views use `@login_required`
2. **CSRF Protection:** POST requests include CSRF tokens
3. **Resource Management:** Proper camera release on stop
4. **Thread Safety:** Lock-protected frame access
5. **Log Rotation:** Auto-limiting to 1000 entries

---

## ⚙️ Configuration Options

### Camera Source
```python
# Webcam
camera_source = 0  # Default webcam
camera_source = 1  # Second webcam

# IP Camera (RTSP)
camera_source = "rtsp://username:password@192.168.1.100:554/stream"

# HTTP Stream
camera_source = "http://192.168.1.100:8080/video"
```

### Target Classes
```python
target_classes = ['person', 'car', 'dog']  # Only detect these
target_classes = None  # Use default security classes
```

### Frame Processing
```python
# In run_monitoring() method
frame_skip = 2  # Process every 2nd frame (better performance)
frame_skip = 1  # Process every frame (higher accuracy)
```

### Confidence Threshold
```python
detector = get_detector(
    model_name='yolov5s',
    confidence_threshold=0.25  # Adjust 0.0 to 1.0
)
```

---

## 📈 Performance Optimization

### Tips for Better Performance:

1. **Frame Skipping:** Process every Nth frame
   ```python
   if frame_count % frame_skip == 0:
       self.process_frame(frame)
   ```

2. **Lower Resolution:** Reduce camera resolution
   ```python
   camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

3. **Faster Model:** Use yolov5s instead of yolov5x

4. **Target Filtering:** Only detect necessary classes

5. **Reduce Polling:** Increase detection update interval

---

## 🐛 Troubleshooting

### Camera Not Opening
**Issue:** "Failed to open camera: 0"
**Solution:**
- Check camera permissions
- Try different camera index (1, 2, etc.)
- Verify camera not in use by another app
- For IP cameras, test URL in VLC first

### Low Frame Rate
**Issue:** Video stream is choppy
**Solution:**
- Increase `frame_skip` value
- Reduce camera resolution
- Use yolov5s model
- Close other applications

### High CPU Usage
**Issue:** CPU at 100%
**Solution:**
- Increase frame skip
- Lower detection frequency
- Reduce resolution
- Enable GPU if available

### Detection Log Too Large
**Issue:** Log file growing too big
**Solution:**
- Log auto-limits to 1000 entries
- Manual cleanup:
  ```python
  import json
  with open('media/security/detection_log.json', 'w') as f:
      json.dump([], f)
  ```

---

## 🔄 Workflow Example

```
User clicks "Start Monitoring"
    ↓
Frontend sends POST to /security/start/
    ↓
View calls start_security_camera()
    ↓
SecurityCamera.start_monitoring_thread()
    ↓
Background thread: run_monitoring()
    ↓
Loop: Read frame → Detect → Annotate → Log
    ↓
Frontend polls /security/detections/ every 1s
    ↓
Frontend displays live stats & detections
    ↓
Frontend loads video from /security/feed/
    ↓
Person detected → Auto-save snapshot
    ↓
User clicks "Stop Monitoring"
    ↓
Camera released, thread stops
```

---

## 📝 API Reference

### Start Camera
```http
POST /detection/security/start/
Content-Type: multipart/form-data

camera_source=0
target_classes=["person","car"]
```

**Response:**
```json
{
  "status": "success",
  "message": "Security monitoring started",
  "camera_source": "0"
}
```

### Stop Camera
```http
POST /detection/security/stop/
```

**Response:**
```json
{
  "status": "success",
  "message": "Security monitoring stopped"
}
```

### Get Detections
```http
GET /detection/security/detections/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "detections": [...],
    "count": 2,
    "total_detections": 45,
    "person_count": 12,
    "timestamp": "2025-10-29T15:30:45.123456"
  }
}
```

---

## 🎯 Use Cases

1. **Home Security:** Monitor front door for visitors
2. **Office Security:** Detect unauthorized access
3. **Parking Lot:** Track vehicle entries
4. **Pet Monitoring:** Detect pet activity
5. **Warehouse:** Monitor for movement
6. **Store Security:** Customer counting

---

## 📦 Dependencies

Already included in `requirements.txt`:
- `torch` - PyTorch for YOLOv5
- `opencv-python` - Video capture and processing
- `ultralytics` - YOLOv5 implementation
- `Pillow` - Image handling

---

## 🚀 Next Steps

1. ✅ Test with webcam
2. ✅ Verify detections are logged
3. ✅ Check snapshot auto-save
4. ✅ Review security logs
5. ✅ Customize target classes
6. ✅ Adjust confidence threshold
7. ✅ Deploy to production

---

## 💡 Future Enhancements

- Multi-camera support
- Email/SMS alerts on person detection
- Zone-based detection (ROI)
- Motion detection pre-filtering
- Cloud storage integration
- Mobile app notifications
- Face recognition integration
- Recording mode (save video clips)

---

## 📞 Support

For issues:
1. Check Django logs
2. Verify camera permissions
3. Test camera in other apps
4. Review detection logs
5. Check network for IP cameras

---

**Module Version:** 1.0.0  
**Last Updated:** October 29, 2025  
**Author:** Argus Security Team
