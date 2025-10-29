# Argus: Plateforme de Sécurité Personnalisée

## Project Overview
Argus is an intelligent surveillance platform that integrates facial recognition, object/person detection, movement detection, and voice command detection for security actions.

## Voice Command Detection
Control security actions (lock/unlock doors, trigger/disarm alarm, open garage, turn on lights) using natural voice commands and synonyms.

**Demo:**
- Go to `/voicecontrol/demo/` to test live voice commands.

**Admin CRUD (Voice):**
- Staff can manage voice commands and synonyms in the dashboard (card links to admin CRUD for staff, demo for users).

## Quick Setup
1. Clone repo
2. Create & activate virtual env (Python 3.11):
	`python -m venv venv && .\venv\Scripts\Activate`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py runserver`
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Troubleshooting
- Use Python 3.11