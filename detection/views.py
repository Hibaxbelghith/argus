from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import DetectionResult
from .forms import ImageUploadForm
from .object_detector import get_detector
import os
from pathlib import Path


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
