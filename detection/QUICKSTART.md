# 🚀 Quick Start Guide - Real-Time Security Monitoring

## Step-by-Step Setup

### 1. Ensure Dependencies Installed
```powershell
# All required packages should already be installed
# If not, run:
pip install torch torchvision opencv-python ultralytics Pillow
```

### 2. Apply Migrations (if needed)
```powershell
E:/Django/argus/venv/Scripts/python.exe manage.py migrate
```

### 3. Start Django Server
```powershell
E:/Django/argus/venv/Scripts/python.exe manage.py runserver
```

### 4. Access Security Monitor
Open browser and navigate to:
```
http://127.0.0.1:8000/detection/security/
```

### 5. Start Monitoring
1. Select camera source (default: 0 for webcam)
2. Choose target classes to detect
3. Click **"Start Monitoring"**
4. Video feed will appear with live detections

### 6. View Live Detections
- **Statistics Panel:** Shows counts in real-time
- **Detection List:** Updates every second
- **Video Feed:** Annotated with bounding boxes

### 7. Access Security Logs
Navigate to:
```
http://127.0.0.1:8000/detection/security/logs/
```

---

## 🎯 Quick Test

### Test with Webcam:
1. Go to `http://127.0.0.1:8000/detection/security/`
2. Click "Start Monitoring"
3. Wave at camera - should detect "person"
4. Check snapshots in: `media/security/snapshots/`
5. View logs at: `http://127.0.0.1:8000/detection/security/logs/`

---

## 📋 Features at a Glance

| Feature | Location | Description |
|---------|----------|-------------|
| **Live Monitor** | `/detection/security/` | Real-time video feed with detection |
| **Security Logs** | `/detection/security/logs/` | Historical detection events |
| **Image Detection** | `/detection/` | Upload & detect (original feature) |
| **Detection History** | `/detection/history/` | Past uploaded images |
| **Auto Snapshots** | `media/security/snapshots/` | Saved when person detected |
| **JSON Logs** | `media/security/detection_log.json` | Structured log data |

---

## ⚙️ Quick Configuration

### Change Detection Sensitivity
Edit `detection/object_detector.py`:
```python
# Line ~34
self.model.conf = 0.25  # Lower = more detections (0.0-1.0)
```

### Change Target Classes
In Security Monitor UI:
- Hold Ctrl and click multiple classes
- Or edit `detection/views.py` line ~151

### Change Frame Processing Rate
Edit `detection/object_detector.py`:
```python
# Line ~473 in run_monitoring()
frame_skip = 2  # Process every 2nd frame (adjust 1-5)
```

---

## 🐛 Common Issues & Fixes

### Issue: Camera not found
**Fix:** 
- Try camera source 1 or 2
- Check Windows Camera app works
- Grant browser camera permissions

### Issue: Slow performance
**Fix:**
- Increase `frame_skip` to 3 or 4
- Use yolov5s (already default)
- Close other programs

### Issue: No detections
**Fix:**
- Lower confidence threshold (currently 0.25)
- Ensure good lighting
- Check target classes selected

---

## 📊 What Gets Detected?

**Default Security Classes:**
- 👤 person
- 🚗 car
- 🐕 dog
- 🐈 cat
- 🚚 truck
- 🏍️ motorcycle

**Note:** YOLOv5 can detect 80+ classes total, but security mode filters to these relevant ones.

---

## 📸 Snapshot Behavior

**Auto-Save Triggers:**
- ✅ Person detected → Snapshot saved
- ❌ Only car detected → No snapshot
- ✅ Person + car detected → Snapshot saved

**Snapshot Location:**
```
media/security/snapshots/snapshot_20251029_153045_person_car.jpg
                         └─────┬─────┘ └──┬──┘ └────┬────┘
                            timestamp    time  detected_classes
```

---

## 🔄 Typical Workflow

```
1. Login to Django app
2. Navigate to Security Monitor
3. Click "Start Monitoring"
4. Camera activates
5. Objects detected in real-time
6. Person walks by → Snapshot auto-saved
7. Stats update live
8. Click "Stop Monitoring" when done
9. Review logs for all events
```

---

## 🎨 UI Overview

### Security Monitor Dashboard
```
┌─────────────────────────────────────────────────┐
│  Argus Security    [Image] [Live] [Logs] [User] │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────┐    ┌──────────────┐  │
│  │                      │    │  Statistics  │  │
│  │   Live Video Feed    │    │  Current: 2  │  │
│  │   [Annotated]        │    │  Persons: 5  │  │
│  │                      │    │  Total: 23   │  │
│  └──────────────────────┘    └──────────────┘  │
│                                                  │
│  [Camera: 0▼] [Classes▼]     ┌──────────────┐  │
│  [Start Monitoring]          │ Live Detect  │  │
│                              │ • person 89% │  │
│                              │ • car 76%    │  │
│                              └──────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 📝 API Endpoints

Quick reference for developers:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/detection/security/` | Dashboard page |
| POST | `/detection/security/start/` | Start camera |
| POST | `/detection/security/stop/` | Stop camera |
| GET | `/detection/security/feed/` | Video stream |
| GET | `/detection/security/detections/` | Detection data |
| GET | `/detection/security/logs/` | Logs page |

---

## 🎯 Testing Checklist

- [ ] Server starts without errors
- [ ] Can access security monitor page
- [ ] Camera activates when clicking "Start"
- [ ] Video feed displays in browser
- [ ] Objects detected and shown in list
- [ ] Statistics update in real-time
- [ ] Snapshot saved when person detected
- [ ] Can view security logs
- [ ] Can stop monitoring cleanly
- [ ] No camera errors in console

---

## 💡 Pro Tips

1. **Test with phone:** Hold up phone with images to test detection
2. **Multiple people:** Detects and counts each person separately
3. **Lighting matters:** Good lighting = better detection
4. **Distance:** Best results within 1-10 meters
5. **Angle:** Face camera directly for best detection
6. **Background:** Simple backgrounds work better

---

## 📞 Need Help?

1. Check `detection/SECURITY_MONITORING.md` for detailed docs
2. Review Django server console for errors
3. Check `media/security/detection_log.json` for logged events
4. Verify camera works in other apps first
5. Test with different camera sources

---

## 🎉 You're Ready!

The security monitoring module is fully set up and ready to use. Navigate to:

**`http://127.0.0.1:8000/detection/security/`**

Click "Start Monitoring" and watch the magic happen! 🚀

---

**Quick Links:**
- 📸 Image Detection: `/detection/`
- 🎥 Live Monitor: `/detection/security/`
- 📋 Security Logs: `/detection/security/logs/`
- 📜 History: `/detection/history/`
