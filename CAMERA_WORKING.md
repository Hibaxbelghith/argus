# Camera Setup Summary

## ✅ GOOD NEWS: Camera is Available!

The test utility found **Camera 0 is working** on your system:
- Resolution: 640x480
- Index: 0 (default webcam)

## How to Use the Security Monitor

### Quick Start
1. **Start Django server** (if not running):
   ```powershell
   cd e:\Django\argus
   e:\Django\argus\venv\Scripts\python.exe manage.py runserver
   ```

2. **Open Security Monitor**:
   - Navigate to: http://127.0.0.1:8000/detection/security/
   
3. **Start Monitoring**:
   - Camera Source Type: **Webcam** (default)
   - Select Webcam: **Default Webcam (0)**
   - Target Classes: Keep defaults (person, car, dog, etc.)
   - Click "**Start Monitoring**"

4. **Watch Live Feed**:
   - Video will appear in the "Live Feed" box
   - Detections will show in "Live Detections" sidebar
   - Statistics update in real-time

### What You Should See
- ✅ Live video feed from your webcam
- ✅ Bounding boxes around detected objects (green for others, red for persons)
- ✅ Detection list with confidence scores
- ✅ Auto-saved snapshots when persons detected
- ✅ Detection logs in JSON format

### Where to Find Saved Data
- **Snapshots**: `media/security/snapshots/`
- **Detection Logs**: `media/security/detection_log.json`

## Testing Camera Without Django

If you want to test the camera directly:
```powershell
cd e:\Django\argus
e:\Django\argus\venv\Scripts\python.exe test_camera.py
```

This will show:
- Available webcams
- Video file status
- Recommendations

## Alternative: Test Video File

If you want to test with a video file instead:

1. **Download a sample video**:
   - Visit: https://sample-videos.com/
   - Download any MP4 video (search for "people walking" for best results)

2. **Place in media folder**:
   ```powershell
   # Example: Copy downloaded video
   Copy-Item "C:\Users\YourName\Downloads\sample.mp4" -Destination "e:\Django\argus\media\test_video.mp4"
   ```

3. **Use in Security Monitor**:
   - Camera Source Type: **Video File**
   - Video File Path: `media/test_video.mp4`
   - Click "Start Monitoring"

## Troubleshooting

### If Camera Still Doesn't Work
1. **Close other applications** using the camera (Zoom, Skype, Teams, etc.)
2. **Check Windows permissions**:
   - Settings → Privacy & Security → Camera
   - Enable "Let apps access your camera"
   - Enable "Let desktop apps access your camera"
3. **Restart Django server**: Press Ctrl+C, then run again
4. **Try video file instead** (see above)

### If Video Feed Shows "Loading..."
1. Check browser console (F12) for JavaScript errors
2. Check Django terminal for Python errors
3. Try stopping and starting monitoring again
4. Refresh the page (F5)

### Low FPS or Laggy
- Normal for 640x480 with YOLOv5 on CPU
- Expected FPS: 5-10 frames per second
- If too slow, use video file with lower resolution

## Features to Try

Once monitoring is working:

1. **Auto-Snapshot on Person Detection**:
   - Walk in front of camera
   - Check `media/security/snapshots/` folder
   - Snapshots saved automatically with timestamp

2. **Detection Logging**:
   - Open `media/security/detection_log.json`
   - See all detections with timestamps and confidence scores

3. **Security Logs Page**:
   - Visit: http://127.0.0.1:8000/detection/security/logs/
   - View formatted logs with person detection highlighting

4. **Object Detection History**:
   - Visit: http://127.0.0.1:8000/detection/
   - Upload static images for detection
   - View history: http://127.0.0.1:8000/detection/history/

## Next Steps

1. **Start the security monitor** with your webcam
2. **Test person detection** by walking in front of camera
3. **Check saved snapshots** in media/security/snapshots/
4. **View detection logs** in media/security/detection_log.json
5. **Try different target classes** (car, cat, dog, etc.)

## Need More Help?

See detailed guides:
- `detection/CAMERA_SETUP.md` - Complete camera setup guide
- `detection/SECURITY_MONITORING.md` - Feature documentation
- `detection/QUICKSTART.md` - Quick reference

## Summary

✅ **Camera 0 is available and working**  
✅ **All code is ready to use**  
✅ **Security monitor is fully functional**  

Just start the Django server and navigate to the security monitor page!
