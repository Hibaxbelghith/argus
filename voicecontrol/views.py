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


COMMAND_SYNONYMS = {
	"lock doors": ["lock the doors", "secure doors", "close doors", "shut doors"],
	"unlock doors": ["unlock the doors", "open doors", "release doors"],
	"trigger alarm": ["activate alarm", "sound alarm", "start alarm"],
	"disarm alarm": ["disable alarm", "turn off alarm", "stop alarm"],
	"open garage": ["open the garage", "raise garage door", "garage up"],
	"turn on lights": ["switch on lights", "lights on", "illuminate room", "turn the lights on"],
}
COMMAND_ACTIONS = {
	"lock doors": "Doors locked.",
	"trigger alarm": "Alarm triggered!",
	"unlock doors": "Doors unlocked.",
	"disarm alarm": "Alarm disarmed.",
	"open garage": "Garage opened.",
	"turn on lights": "Lights turned on.",
}

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
			# Fuzzy match against synonyms
			for cmd, synonyms in COMMAND_SYNONYMS.items():
				for phrase in [cmd] + synonyms:
					ratio = difflib.SequenceMatcher(None, phrase, text).ratio()
					if ratio > 0.7 or phrase in text:
						response["action"] = COMMAND_ACTIONS[cmd]
						found = True
						break
				if found:
					break
			if not found:
				# Fallback to keyword logic
				if "unlock" in text and "door" in text:
					response["action"] = COMMAND_ACTIONS["unlock doors"]
				elif "lock" in text and "door" in text:
					response["action"] = COMMAND_ACTIONS["lock doors"]
				elif "trigger" in text and "alarm" in text:
					response["action"] = COMMAND_ACTIONS["trigger alarm"]
				elif "disarm" in text and "alarm" in text:
					response["action"] = COMMAND_ACTIONS["disarm alarm"]
				elif "open" in text and "garage" in text:
					response["action"] = COMMAND_ACTIONS["open garage"]
				elif ("turn on" in text or "switch on" in text) and "light" in text:
					response["action"] = COMMAND_ACTIONS["turn on lights"]
				else:
					response["action"] = "No valid command detected."
		return JsonResponse(response)
	return JsonResponse({"error": "Invalid request."}, status=400)

