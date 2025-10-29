def demo(request):
	return render(request, 'voicecontrol/demo.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import vosk
import sounddevice as sd
import difflib
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage
from .models import VoiceCommand



MODEL_PATH = os.path.join(settings.BASE_DIR, "voicecontrol", "vosk-model-small-en-us-0.15")

def recognize_speech(audio_path):
	if not os.path.exists(MODEL_PATH):
		return None, "Model not found. Download and place Vosk model at: {}".format(MODEL_PATH)
	import wave
	try:
		wf = wave.open(audio_path, "rb")
		# Allow different formats, Vosk will handle it
		model = vosk.Model(MODEL_PATH)
		rec = vosk.KaldiRecognizer(model, wf.getframerate())
		results = []
		while True:
			data = wf.readframes(4000)
			if len(data) == 0:
				break
			if rec.AcceptWaveform(data):
				results.append(json.loads(rec.Result()))
		results.append(json.loads(rec.FinalResult()))
		wf.close()
		text = " ".join([r.get("text", "") for r in results])
		return text.strip(), None
	except Exception as e:
		return None, f"Recognition error: {str(e)}"


@csrf_exempt
def voice_command(request):
	if request.method == "POST" and request.FILES.get("audio"):
		audio_file = request.FILES["audio"]

		# Save the uploaded file
		import tempfile
		temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
		temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
		temp_input.write(audio_file.read())
		temp_input.close()
		temp_output.close()

		# Convert webm to WAV using ffmpeg
		import subprocess
		try:
			subprocess.run([
				'ffmpeg', '-i', temp_input.name,
				'-ar', '16000',  # 16kHz sample rate
				'-ac', '1',      # mono
				'-y',            # overwrite
				temp_output.name
			], check=True, capture_output=True)
		except subprocess.CalledProcessError as e:
			os.remove(temp_input.name)
			os.remove(temp_output.name)
			return JsonResponse({
				"error": "Audio conversion failed. Make sure ffmpeg is installed.",
				"recognized": "",
				"action": ""
			})
		except FileNotFoundError:
			os.remove(temp_input.name)
			os.remove(temp_output.name)
			return JsonResponse({
				"error": "ffmpeg not found. Please install ffmpeg.",
				"recognized": "",
				"action": ""
			})

		# Recognize speech
		command_text, error = recognize_speech(temp_output.name)

		# Clean up temp files
		os.remove(temp_input.name)
		os.remove(temp_output.name)

		response = {}
		if error:
			response["error"] = error
			response["recognized"] = ""
			response["action"] = ""
		else:
			response["recognized"] = command_text
			text = command_text.lower()
			found = False

			# Load commands from DB
			commands = VoiceCommand.objects.filter(enabled=True)
			for cmd_obj in commands:
				cmd = cmd_obj.text.lower()
				synonyms = [cmd] + [s.strip().lower() for s in cmd_obj.synonyms.split(',') if s.strip()]
				for phrase in synonyms:
					ratio = difflib.SequenceMatcher(None, phrase, text).ratio()
					if ratio > 0.7 or phrase in text:
						response["action"] = f"{cmd_obj.text.capitalize()} action triggered."
						found = True
						break
				if found:
					break
			if not found:
				response["action"] = "No valid command detected."
		return JsonResponse(response)
	return JsonResponse({"error": "Invalid request."}, status=400)