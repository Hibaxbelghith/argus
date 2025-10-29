from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import EmotionDetectionEvent
from deepface import DeepFace
import tempfile
import os

def live_emotion_page(request):
	return render(request, 'emotion/live.html')
@csrf_exempt
def detect_emotion(request):
	if request.method == 'POST' and request.FILES.get('image'):
		image_file = request.FILES['image']
		with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img:
			for chunk in image_file.chunks():
				temp_img.write(chunk)
			temp_img_path = temp_img.name
		try:
			result = DeepFace.analyze(temp_img_path, actions=['emotion'], enforce_detection=False)
			# Handle multiple faces (list) or single face (dict)
			if isinstance(result, list):
				face = result[0]
			else:
				face = result
			emotion = face['dominant_emotion']
			confidence = float(face['emotion'][emotion])
			event = EmotionDetectionEvent.objects.create(
				emotion=emotion,
				confidence=confidence
			)
			os.remove(temp_img_path)
			return JsonResponse({
				'emotion': emotion,
				'confidence': confidence,
				'event_id': event.id
			})
		except Exception as e:
			print("Emotion detection error:", e)
			if os.path.exists(temp_img_path):
				os.remove(temp_img_path)
			return JsonResponse({'error': str(e)}, status=500)
	return JsonResponse({'error': 'No image uploaded'}, status=400)
