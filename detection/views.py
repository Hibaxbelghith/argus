from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import DetectionResult
from .forms import ImageUploadForm
from .object_detector import get_detector, get_security_camera
import os
from pathlib import Path
import json


@login_required
def detection_home(request):
    """
    Main page for object detection - upload form and recent detections
    """
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the detection result with the uploaded image
            detection = form.save(commit=False)
            detection.user = request.user
            detection.save()
            
            # Redirect to processing view
            return redirect('detection:process', pk=detection.pk)
    else:
        form = ImageUploadForm()
    
    # Get user's recent detections
    recent_detections = DetectionResult.objects.filter(user=request.user)[:10]
    
    context = {
        'form': form,
        'recent_detections': recent_detections,
    }
    return render(request, 'detection/detection.html', context)


@login_required
def process_detection(request, pk):
    """
    Process the uploaded image with YOLOv5
    """
    detection = get_object_or_404(DetectionResult, pk=pk, user=request.user)
    
    # Check if already processed
    if detection.annotated_image:
        return redirect('detection:result', pk=pk)
    
    try:
        # Get the object detector
        detector = get_detector(model_name='yolov5s', confidence_threshold=0.25)
        
        # Get paths
        original_path = detection.original_image.path
        
        # Create annotated image path
        annotated_filename = f"annotated_{Path(detection.original_image.name).name}"
        annotated_relative = os.path.join('detections', 'annotated', annotated_filename)
        annotated_path = os.path.join(settings.MEDIA_ROOT, annotated_relative)
        
        # Process the image
        results = detector.process_image(original_path, annotated_path)
        
        # Update detection record
        detection.objects_detected = results['count']
        detection.set_detection_data(results['detections'])
        
        # Save annotated image path if created
        if results['annotated_image']:
            detection.annotated_image = annotated_relative
        
        detection.save()
        
        messages.success(request, f"✅ Detected {results['count']} object(s) in the image!")
        
    except Exception as e:
        messages.error(request, f"❌ Error processing image: {str(e)}")
        return redirect('detection:home')
    
    return redirect('detection:result', pk=pk)


@login_required
def detection_result(request, pk):
    """
    Display detection results with annotated image
    """
    detection = get_object_or_404(DetectionResult, pk=pk, user=request.user)
    
    # Parse detection data
    detections = detection.get_detection_data()
    
    context = {
        'detection': detection,
        'detections': detections,
    }
    return render(request, 'detection/result.html', context)


@login_required
def detection_history(request):
    """
    View all detection history for the current user
    """
    detections = DetectionResult.objects.filter(user=request.user)
    
    context = {
        'detections': detections,
    }
    return render(request, 'detection/history.html', context)


@login_required
def delete_detection(request, pk):
    """
    Delete a detection result
    """
    detection = get_object_or_404(DetectionResult, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Delete associated files
        if detection.original_image:
            if os.path.exists(detection.original_image.path):
                os.remove(detection.original_image.path)
        
        if detection.annotated_image:
            if os.path.exists(detection.annotated_image.path):
                os.remove(detection.annotated_image.path)
        
        detection.delete()
        messages.success(request, "Detection result deleted successfully!")
        return redirect('detection:history')
    
    return render(request, 'detection/delete_confirm.html', {'detection': detection})


# ==================== REAL-TIME SECURITY MONITORING VIEWS ====================

@login_required
def security_monitor(request):
    """
    Real-time security monitoring dashboard
    Display live camera feed with object detection
    """
    context = {
        'camera_available': True,
        'target_classes': ['person', 'car', 'dog', 'cat', 'truck', 'motorcycle'],
    }
    return render(request, 'detection/security_monitor.html', context)


@login_required
@require_http_methods(["POST"])
def start_security_camera(request):
    """
    Start the security camera monitoring
    
    Expected POST data:
        - camera_source: Camera index (default: 0) or IP camera URL
        - target_classes: JSON array of classes to detect
    
    Returns:
        JSON response with status
    """
    try:
        # Get parameters from request
        camera_source = request.POST.get('camera_source', '0')
        
        # Convert to int if it's a number
        try:
            camera_source = int(camera_source)
        except ValueError:
            pass  # Keep as string for IP camera URLs
        
        # Get target classes
        target_classes_json = request.POST.get('target_classes', '[]')
        target_classes = json.loads(target_classes_json) if target_classes_json else None
        
        # Get or create security camera instance
        security_cam = get_security_camera(
            camera_source=camera_source,
            target_classes=target_classes
        )
        
        # Start monitoring in background thread
        success = security_cam.start_monitoring_thread()
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Security monitoring started',
                'camera_source': str(camera_source)
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to connect to camera'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def stop_security_camera(request):
    """
    Stop the security camera monitoring
    
    Returns:
        JSON response with status
    """
    try:
        security_cam = get_security_camera()
        security_cam.stop_monitoring()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Security monitoring stopped'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def generate_video_stream():
    """
    Generator function for video streaming
    Yields frames from security camera in multipart format
    """
    security_cam = get_security_camera()
    
    while security_cam.is_running:
        # Get current annotated frame
        frame_bytes = security_cam.get_frame_for_streaming()
        
        if frame_bytes:
            # Yield frame in multipart format for MJPEG streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # Small delay if no frame available
            import time
            time.sleep(0.1)


@login_required
def video_feed(request):
    """
    Stream video feed with real-time object detection
    
    Returns:
        StreamingHttpResponse with MJPEG stream
    """
    return StreamingHttpResponse(
        generate_video_stream(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@login_required
def get_detections_data(request):
    """
    Get latest detection data for frontend display
    
    Returns:
        JSON response with current detections and statistics
    """
    try:
        security_cam = get_security_camera()
        detection_data = security_cam.get_latest_detections()
        
        return JsonResponse({
            'status': 'success',
            'data': detection_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'data': {
                'detections': [],
                'count': 0,
                'total_detections': 0,
                'person_count': 0
            }
        })


@login_required
def security_logs(request):
    """
    View security detection logs
    Display historical detection events
    """
    log_file = 'media/security/detection_log.json'
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
                # Reverse to show newest first
                logs.reverse()
                
                # Add person_detected flag to each log entry
                for log in logs:
                    log['person_detected'] = any(
                        det.get('class') == 'person' 
                        for det in log.get('detections', [])
                    )
        except (json.JSONDecodeError, IOError):
            logs = []
    
    context = {
        'logs': logs[:100],  # Show last 100 entries
        'total_logs': len(logs)
    }
    return render(request, 'detection/security_logs.html', context)

