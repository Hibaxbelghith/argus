# Object Detection Feature - Setup Guide

## Overview
This detection app adds YOLOv5-based object detection capabilities to your Django application. Users can upload images, detect objects, and view annotated results with bounding boxes.

## Features
- ✅ Image upload with drag-and-drop support
- ✅ YOLOv5 object detection (80+ object classes)
- ✅ Annotated images with bounding boxes and labels
- ✅ Detection history and management
- ✅ User authentication required
- ✅ Bootstrap 5 responsive UI

## Installation Steps

### 1. Install Required Packages
```powershell
pip install -r requirements.txt
```

This will install:
- torch and torchvision (PyTorch for deep learning)
- opencv-python (image processing)
- Pillow (image handling)
- yolov5 (object detection)

### 2. Run Migrations
```powershell
python manage.py makemigrations detection
python manage.py migrations
```

### 3. Create Media Directories
The media directories will be created automatically, but you can create them manually:
```powershell
New-Item -ItemType Directory -Path "media\detections\original" -Force
New-Item -ItemType Directory -Path "media\detections\annotated" -Force
```

### 4. Download YOLOv5 Model
The first time you run a detection, PyTorch will automatically download the YOLOv5 model (~14MB for yolov5s). This happens automatically on first use.

### 5. Run the Development Server
```powershell
python manage.py runserver
```

### 6. Access the Detection Feature
Navigate to: `http://127.0.0.1:8000/detection/`

## File Structure
```
detection/
├── __init__.py
├── admin.py              # Admin interface configuration
├── apps.py               # App configuration
├── forms.py              # Image upload form
├── models.py             # DetectionResult model
├── object_detector.py    # YOLOv5 detection logic ⭐
├── tests.py              # Unit tests
├── urls.py               # URL routing
├── views.py              # View functions
├── migrations/
│   └── __init__.py
└── templates/
    └── detection/
        ├── detection.html      # Main upload page ⭐
        ├── result.html         # Results display
        ├── history.html        # Detection history
        └── delete_confirm.html # Delete confirmation
```

## Usage

### For Users
1. Log in to your account
2. Navigate to the Detection page
3. Upload an image (JPG, PNG, BMP up to 10MB)
4. Wait for processing (usually 1-3 seconds)
5. View the annotated image with detected objects
6. Download or manage your detection history

### For Developers

#### Customize Detection Settings
Edit `detection/views.py` in the `process_detection` function:
```python
detector = get_detector(
    model_name='yolov5s',  # Options: yolov5s, yolov5m, yolov5l, yolov5x
    confidence_threshold=0.25  # Adjust threshold (0.0 to 1.0)
)
```

#### Model Variants
- `yolov5s` - Small, fast (14MB)
- `yolov5m` - Medium (40MB)
- `yolov5l` - Large (90MB)
- `yolov5x` - Extra large (166MB)

## API Endpoints

- `GET /detection/` - Main detection page with upload form
- `POST /detection/` - Submit image for detection
- `GET /detection/process/<id>/` - Process uploaded image
- `GET /detection/result/<id>/` - View detection results
- `GET /detection/history/` - View all detections
- `POST /detection/delete/<id>/` - Delete a detection

## Troubleshooting

### Issue: Module not found errors
**Solution:** Make sure all packages are installed:
```powershell
pip install torch torchvision opencv-python Pillow yolov5
```

### Issue: CUDA errors
**Solution:** YOLOv5 will automatically use CPU if CUDA is not available. For CPU-only:
```python
# In object_detector.py, you can force CPU:
self.model = torch.hub.load('ultralytics/yolov5', self.model_name, device='cpu')
```

### Issue: Slow detection
**Solution:** 
1. Use a smaller model (`yolov5s` instead of `yolov5x`)
2. Reduce image size before detection
3. Enable GPU support if available

### Issue: Images not displaying
**Solution:** Check that `MEDIA_URL` and `MEDIA_ROOT` are configured in settings.py and URLs are properly set up

## Security Considerations

1. **File Upload Validation**: Form validates file size (10MB) and extensions
2. **Authentication Required**: All views require login
3. **User Isolation**: Users can only see their own detections
4. **File Storage**: Media files are stored outside the code directory

## Performance Tips

1. **Use a smaller model** for faster detection
2. **Implement caching** for repeated detections
3. **Consider async processing** for large batches
4. **Add image resizing** before detection
5. **Use CDN** for static files in production

## Next Steps

1. ✅ Test the feature with various images
2. ✅ Adjust confidence threshold for your use case
3. ✅ Customize the UI to match your design
4. ✅ Add more features (batch processing, video detection, etc.)
5. ✅ Deploy to production with proper media file handling

## Support

For issues or questions:
1. Check Django logs for errors
2. Verify all packages are installed
3. Ensure migrations are applied
4. Check file permissions for media directory

## Credits

- YOLOv5 by Ultralytics
- PyTorch for deep learning
- OpenCV for image processing
