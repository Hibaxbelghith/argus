# Camera Setup Guide for Security Monitor

## Overview
The Security Monitor supports three types of video sources:
1. **Webcam** - Physical camera connected to your computer
2. **Video File** - Pre-recorded video for testing
3. **IP Camera** - Network camera or phone camera app

## Problem: "Camera Not Available"

If you see the error "Camera 0 is not available", it means:
- No physical webcam is connected to your computer
- Windows camera permissions are disabled
- The webcam is being used by another application

## Solution 1: Use a Test Video File (Recommended for Testing)

### Step 1: Get a Test Video
Download a sample video from:
- https://sample-videos.com/
- https://www.pexels.com/videos/
- Any MP4/AVI video with people, cars, or objects

### Step 2: Place Video in Media Folder
```powershell
# Example: Copy video to media folder
Copy-Item "C:\Downloads\test_video.mp4" -Destination "e:\Django\argus\media\"
```

### Step 3: Use Video in Security Monitor
1. Navigate to: http://127.0.0.1:8000/detection/security/
2. Select **"Video File"** from Camera Source Type dropdown
3. Enter path: `media/test_video.mp4` (or full path: `e:\Django\argus\media\test_video.mp4`)
4. Click "Start Monitoring"

### Step 4: Test from Command Line
```powershell
# Test video file detection
cd e:\Django\argus
.\venv\Scripts\activate
python manage.py shell
```

Then in Python shell:
```python
import cv2
from detection.object_detector import get_security_camera

# Test with video file
camera = get_security_camera()
camera.connect_camera('media/test_video.mp4')
print(f"Camera connected: {camera.is_running}")
camera.disconnect_camera()
```

## Solution 2: Enable Windows Webcam

### Check Camera Access
1. Open **Settings** → **Privacy & Security** → **Camera**
2. Enable "Let apps access your camera"
3. Enable "Let desktop apps access your camera"

### Test Camera in Windows
1. Open **Camera** app (Windows built-in)
2. If it works there, it should work in Django

### Check Camera in Device Manager
1. Press `Win + X` → **Device Manager**
2. Expand **Cameras** or **Imaging Devices**
3. Right-click camera → **Enable Device**

### Test from Python
```python
import cv2

# Test each camera index
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✓ Camera {i} is available")
        ret, frame = cap.read()
        if ret:
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print(f"✗ Camera {i} not available")
```

## Solution 3: Use IP Camera or Phone

### Option A: Phone as Webcam
Install one of these apps on your phone:
- **DroidCam** (Android/iOS): https://www.dev47apps.com/
- **IP Webcam** (Android): Play Store
- **EpocCam** (iOS): App Store

#### Using DroidCam:
1. Install DroidCam on phone and PC
2. Connect phone and PC to same WiFi
3. Open DroidCam app, note the IP address (e.g., 192.168.1.100:4747)
4. In Security Monitor:
   - Select **"IP Camera"**
   - Enter: `http://192.168.1.100:4747/video`

#### Using IP Webcam:
1. Install IP Webcam app
2. Start server in app
3. Note the URL (e.g., 192.168.1.100:8080)
4. In Security Monitor:
   - Select **"IP Camera"**
   - Enter: `http://192.168.1.100:8080/video`

### Option B: RTSP Camera
If you have an IP camera with RTSP:
```
rtsp://username:password@192.168.1.100:554/stream
```

### Test IP Camera
```python
import cv2

# Test IP camera stream
url = "http://192.168.1.100:8080/video"
cap = cv2.VideoCapture(url)

if cap.isOpened():
    print("✓ IP camera connected")
    ret, frame = cap.read()
    if ret:
        print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
else:
    print("✗ Cannot connect to IP camera")
```

## Troubleshooting

### Error: "OpenCV: camera index out of range"
**Cause**: No physical camera detected  
**Solution**: Use video file or IP camera instead

### Error: "Failed to open video file"
**Cause**: File path is incorrect  
**Solution**: 
- Use absolute path: `e:\Django\argus\media\test.mp4`
- Or relative from project root: `media/test.mp4`
- Check file exists: `Test-Path "e:\Django\argus\media\test.mp4"`

### Error: "Cannot connect to IP camera"
**Cause**: Network issues or wrong URL  
**Solution**:
- Check phone and PC are on same WiFi
- Test URL in browser first
- Try different URL formats (http vs rtsp)
- Check firewall settings

### Video Feed Shows "Loading..." Forever
**Cause**: Camera not started or crashed  
**Solution**:
1. Check browser console (F12) for errors
2. Check Django terminal for error messages
3. Try stopping and restarting monitoring
4. Restart Django server: `Ctrl+C`, then `python manage.py runserver`

### Low FPS or Laggy Video
**Cause**: Video resolution too high or slow CPU  
**Solution**:
- Use lower resolution video (720p instead of 1080p)
- Reduce FPS in `object_detector.py` (change `time.sleep(0.1)` to `time.sleep(0.2)`)
- Use webcam instead of high-res IP camera

## Quick Reference

### Camera Source Examples

| Type | Example Value | Notes |
|------|---------------|-------|
| Webcam | `0` | Default webcam |
| Webcam | `1` or `2` | Additional webcams |
| Video File | `media/test.mp4` | Relative path |
| Video File | `e:\Django\argus\media\test.mp4` | Absolute path |
| IP Camera | `http://192.168.1.100:8080/video` | IP Webcam app |
| IP Camera | `http://192.168.1.100:4747/video` | DroidCam |
| RTSP | `rtsp://admin:password@192.168.1.100:554/stream` | IP camera |

### Recommended Testing Workflow
1. **Start with video file** (easiest to test)
2. **Try phone as webcam** (if you need live feed)
3. **Fix physical webcam** (for permanent setup)

### Common File Extensions Supported
- `.mp4` - Most common, best compatibility
- `.avi` - Windows standard
- `.mov` - Apple/QuickTime
- `.mkv` - High quality
- `.webm` - Web video

## Next Steps

Once you have a working camera source:
1. Start monitoring from http://127.0.0.1:8000/detection/security/
2. Watch for detections in real-time
3. Check snapshots in `media/security/snapshots/`
4. View detection logs in `media/security/detection_log.json`
5. Access security logs page at http://127.0.0.1:8000/detection/security/logs/

## Need Help?

1. Check Django terminal output for error messages
2. Open browser console (F12) for JavaScript errors
3. Test camera source with provided Python code snippets
4. Verify file paths exist: `Test-Path "path\to\file.mp4"`
5. Ensure OpenCV is installed: `pip show opencv-python`
