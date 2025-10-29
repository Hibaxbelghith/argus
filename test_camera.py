"""
Quick test script to verify camera setup for Security Monitor
Usage: python test_camera.py
"""

import cv2
import os

def test_webcams():
    """Test all available webcam indices"""
    print("=" * 50)
    print("TESTING WEBCAMS")
    print("=" * 50)
    
    available_cameras = []
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✓ Camera {i}: AVAILABLE")
                print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
                available_cameras.append(i)
            else:
                print(f"✗ Camera {i}: Failed to read frame")
            cap.release()
        else:
            print(f"✗ Camera {i}: NOT AVAILABLE")
    
    return available_cameras

def test_video_file(file_path):
    """Test video file access"""
    print("\n" + "=" * 50)
    print(f"TESTING VIDEO FILE: {file_path}")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"✗ File does not exist: {file_path}")
        return False
    
    cap = cv2.VideoCapture(file_path)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            print(f"✓ Video file opened successfully")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"  FPS: {fps}")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  Total frames: {frame_count}")
            cap.release()
            return True
        else:
            print(f"✗ Failed to read frame from video file")
            cap.release()
            return False
    else:
        print(f"✗ Failed to open video file")
        return False

def test_ip_camera(url):
    """Test IP camera/stream URL"""
    print("\n" + "=" * 50)
    print(f"TESTING IP CAMERA: {url}")
    print("=" * 50)
    
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print("✓ Connected to IP camera")
        ret, frame = cap.read()
        if ret:
            print(f"✓ Receiving video stream")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            cap.release()
            return True
        else:
            print("✗ Connected but failed to read frame")
            cap.release()
            return False
    else:
        print("✗ Failed to connect to IP camera")
        return False

def main():
    print("\n=== SECURITY MONITOR - CAMERA TEST UTILITY ===\n")
    
    # Test webcams
    webcams = test_webcams()
    
    # Test video file if it exists
    video_paths = [
        "media/test_video.mp4",
        "media/test.mp4",
        "media/sample.mp4",
    ]
    
    print("\n" + "=" * 50)
    print("CHECKING FOR VIDEO FILES")
    print("=" * 50)
    
    video_found = False
    for path in video_paths:
        if os.path.exists(path):
            print(f"Found: {path}")
            test_video_file(path)
            video_found = True
        else:
            print(f"Not found: {path}")
    
    if not video_found:
        print("\n⚠ No test video files found in media/ folder")
        print("  Download sample video from: https://sample-videos.com/")
        print("  Place it in media/ folder as 'test_video.mp4'")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if webcams:
        print(f"✓ {len(webcams)} webcam(s) available: {webcams}")
        print(f"  Use source: {webcams[0]} (default)")
    else:
        print("✗ No webcams detected")
    
    if video_found:
        print("✓ Video files available for testing")
    else:
        print("⚠ No video files found (download sample for testing)")
    
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)
    
    if webcams:
        print("1. Use webcam (recommended)")
        print(f"   Camera Source: {webcams[0]}")
    elif video_found:
        print("1. Use video file for testing")
        print("   Camera Source Type: Video File")
        print(f"   Path: {video_paths[0]}")
    else:
        print("1. Download a test video:")
        print("   - Visit: https://sample-videos.com/")
        print("   - Download any MP4 video")
        print("   - Place in: media/test_video.mp4")
        print("\n2. Or use phone as webcam:")
        print("   - Install 'IP Webcam' or 'DroidCam' app")
        print("   - Camera Source Type: IP Camera")
        print("   - URL: http://YOUR_PHONE_IP:PORT/video")
    
    print("\nFor detailed setup instructions, see:")
    print("  detection/CAMERA_SETUP.md")

if __name__ == "__main__":
    main()
